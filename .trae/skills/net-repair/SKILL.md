---
name: "net-repair"
description: "诊断并修复飞书/国内网站无法在浏览器中访问的问题（代理残留、DNS污染、WFP规则残留、天融信Tipray拦截等）。当用户报告飞书链接打不开、浏览器无法访问但curl/python正常、或安全软件拦截时使用。"
---

# 网络修复工具 (Net Repair)

本技能用于诊断和修复Windows系统网络访问问题，特别是飞书（Feishu）、WPS等国内网站在浏览器中无法访问的问题。

## 问题特征

用户报告以下症状时，应使用本技能：
- 飞书官网/多维表格/WPS文档链接无法在浏览器中打开
- 但 curl / Python / 其他工具可以正常访问这些网站
- 其他同事的电脑正常，只有自己的电脑有问题
- 之前安装过腾讯电脑管家（QQPCRTP）或天融信终端安全（Tipray）
- 重启路由器、清除浏览器缓存、更换DNS均无效

## 诊断流程

### 第一步：排除代理/VPN残留

```powershell
# 检查系统代理注册表
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" |
    Select-Object ProxyEnable, ProxyServer, ProxyOverride

# 检查WinHTTP代理
netsh winhttp show proxy

# 检查环境变量代理
$env:http_proxy; $env:https_proxy; $env:ALL_PROXY

# 检查开机自启代理软件
Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" |
    Format-List *clash*, *v2ray*, *proxy*

# 清除代理残留（如果有问题）
Remove-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -ErrorAction SilentlyContinue
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" ProxyEnable 0

# 清除代理软件开机自启
Remove-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "com.lbyczf.clashwin" -ErrorAction SilentlyContinue
Remove-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "v2rayNAutoRun*" -ErrorAction SilentlyContinue
```

### 第二步：排除DNS污染

```powershell
# 清除DNS缓存
ipconfig /flushdns

# 测试飞书域名解析
nslookup xcnplmqtjyqc.feishu.cn

# 检查DNS服务器
Get-DnsClientServerAddress -AddressFamily IPv4
```

### 第三步：检查Hosts文件

```powershell
# 查看Hosts文件（排除被篡改）
Get-Content "$env:windir\System32\drivers\etc\hosts" |
    Where-Object { $_ -match '\S' -and $_ -notmatch '^\s*#' }
```

### 第四步：核心诊断 - SNI拦截测试（关键！）

这是诊断WFP驱动SNI拦截的核心方法。**关键区别**：WFP驱动在TLS握手阶段检查SNI域名，而非进程名。

```python
import socket, ssl, time

host = 'www.feishu.cn'
ip = '58.215.109.87'  # nslookup获取的IP

# 测试1: 直连IP（无SNI）— 如果OK说明网络层正常
sock = socket.create_connection((ip, 443), timeout=5)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ssock = ctx.wrap_socket(sock)  # 不传server_hostname
print(f"无SNI: OK ({ssock.version()})")
ssock.close()

# 测试2: 带SNI连接 — 如果FAIL说明SNI被拦截
sock = socket.create_connection((host, 443), timeout=5)
ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ssock = ctx.wrap_socket(sock, server_hostname=host)  # 传server_hostname
print(f"有SNI: OK ({ssock.version()})")
ssock.close()
```

**解读结果**：
| 无SNI | 有SNI | 结论 |
|--------|--------|------|
| OK | OK | 网络正常 |
| OK | FAIL | **WFP SNI拦截**（天融信/腾讯管家等） |
| FAIL | FAIL | 网络层问题（代理/DNS/路由） |

### 第五步：检查WFP过滤器和安全软件

```powershell
# 导出WFP过滤器（需要管理员权限）
netsh wfp show filters file=$env:TEMP\wfp_filters.xml

# 搜索已知拦截器
Select-String -Path "$env:TEMP\wfp_filters.xml" -Pattern "TAONETFLOW|ldwfp|Tipray|hnswfp"

# 检查安全软件进程
Get-Process | Where-Object { $_.Path -match "Tipray|LdTerm|QQPCMgr" } |
    Select-Object Name, Id, Path

# 检查安全软件驱动
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\ldwfp" -ErrorAction SilentlyContinue
Get-ItemProperty "HKLM:\SYSTEM\CurrentControlSet\Services\TAOKernelDriver" -ErrorAction SilentlyContinue
```

**已知拦截器**：
| 名称 | 驱动 | 来源 | 拦截方式 |
|------|------|------|----------|
| Tencent TAONETFLOW | TAOKernel64.sys | 腾讯电脑管家 | 按进程名+域名拦截 |
| ldwfp | ldwfp64.sys | 天融信Tipray终端安全 | 按SNI域名拦截 |
| hnswfpdriver | hnswfpdriver.sys | 华途数据防泄漏 | 按SNI域名拦截 |

## 修复方案

### 方案一：禁用天融信Tipray WFP驱动（最常见）

```powershell
# 以管理员身份运行
sc.exe stop ldwfp
sc.exe config ldwfp start=disabled

# 停止天融信相关进程
Get-Process | Where-Object { $_.Path -match "Tipray|LdTerm" } |
    ForEach-Object { Stop-Process -Id $_.Id -Force }

# 禁用天融信服务
$svcNames = @("LdTerm", "LdTermDaemon", "LdApprovalEx", "LdFileGate")
foreach ($svc in $svcNames) {
    sc.exe stop $svc 2>$null
    sc.exe config $svc start=disabled 2>$null
}

# 重置网络
netsh winsock reset
ipconfig /flushdns

# 重启电脑使驱动卸载生效
```

### 方案二：清除腾讯电脑管家WFP残留规则

```powershell
# 以管理员身份运行
sc.exe stop TAOKernelDriver
sc.exe config TAOKernelDriver start=disabled
sc.exe stop TsNetHlpX64
sc.exe config TsNetHlpX64 start=disabled

# 使用WFP API删除过滤器（见scripts/delete_wfp_filters.ps1）
netsh winsock reset
```

### 方案三：清除代理软件开机自启 + 重置代理

```powershell
# 清除Clash/v2rayN开机自启
Remove-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "com.lbyczf.clashwin" -ErrorAction SilentlyContinue
Remove-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" -Name "v2rayNAutoRun*" -ErrorAction SilentlyContinue

# 清除代理设置
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" ProxyEnable 0
Remove-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -ErrorAction SilentlyContinue
netsh winhttp reset proxy
```

## 关键结论

| 现象 | 根因 | 解决方案 |
|------|------|----------|
| 无SNI OK，有SNI FAIL | WFP SNI拦截（天融信/华途） | 禁用ldwfp/hnswfpdriver驱动，重启 |
| python OK，chrome FAIL | WFP进程名拦截（腾讯管家） | 清除TAONETFLOW过滤器，重启 |
| python和chrome都FAIL | 代理/DNS残留 | 清除代理配置，重置DNS |
| 所有工具都FAIL | 网络层问题 | 检查路由器/DNS服务器 |
| 重启后恢复但过一阵又不行 | 代理软件自启恢复代理 | 清除开机自启+禁用代理服务 |

## 注意事项

1. **Winsock重置必须重启才能生效**：执行 `netsh winsock reset` 后必须重启电脑
2. **内核驱动无法在线卸载**：WFP驱动（ldwfp/TAOKernelDriver）必须重启才能完全卸载
3. **天融信Tipray是公司管控软件**：禁用前需确认是否违反公司IT策略
4. **代理软件会自动恢复代理设置**：Clash/v2rayN开机自启会重新设置ProxyServer，需清除自启项
5. **SNI拦截在TLS握手阶段**：WFP驱动在TLS ClientHello阶段检查SNI域名，不是进程名
6. **腾讯管家卸载后WFP规则仍残留**：即使卸载软件，其注册的过滤规则不会自动清除