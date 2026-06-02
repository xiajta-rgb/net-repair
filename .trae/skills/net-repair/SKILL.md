---
name: "net-repair"
description: "诊断并修复飞书/国内网站无法在浏览器中访问的问题（代理残留、DNS污染、WFP规则残留等）。当用户报告飞书链接打不开、浏览器无法访问但curl/python正常、或安全软件拦截时使用。"
---

# 网络修复工具 (Net Repair)

本技能用于诊断和修复Windows系统网络访问问题，特别是飞书（Feishu）、WPS等国内网站在浏览器中无法访问的问题。

## 问题特征

用户报告以下症状时，应使用本技能：
- 飞书官网/多维表格/WPS文档链接无法在浏览器中打开
- 但 curl / Python / 其他工具可以正常访问这些网站
- 其他同事的电脑正常，只有自己的电脑有问题
- 之前安装过腾讯电脑管家（QQPCRTP）
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

# 清除代理残留（如果有问题）
Remove-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" -Name ProxyServer -ErrorAction SilentlyContinue
Set-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" ProxyEnable 0
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

### 第四步：核心诊断 - 进程名拦截测试（关键！）

这是诊断腾讯电脑管家等安全软件残留WFP规则的核心方法：

创建测试脚本 `scripts/final_verify.py`：
```python
import socket
import ssl
import os
import sys

def test_https(host, port=443, timeout=10):
    try:
        sock = socket.create_connection((host, port), timeout=timeout)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ssock = ctx.wrap_socket(sock, server_hostname=host)
        version = ssock.version()
        ssock.close()
        sock.close()
        return True, version
    except Exception as e:
        return False, str(e)

print(f"当前进程: {os.path.basename(sys.executable)}")

# 测试飞书相关域名
test_cases = [
    ("www.baidu.com", "百度"),
    ("www.feishu.cn", "飞书官网"),
    ("xcnplmqtjyqc.feishu.cn", "飞书多维表格"),
]

for host, name in test_cases:
    ok, data = test_https(host)
    status = f"OK ({data})" if ok else f"FAIL - {data}"
    print(f"  {name}: {status}")
```

**运行后解读结果**：
- `python.exe` 能访问飞书，但进程名含"chrome"的无法访问
- 说明存在 **WFP（Windows Filtering Platform）进程名级拦截**
- 常见原因：腾讯电脑管家（QQPCRTP）的TAOKernelDriver驱动残留WFP规则

### 第五步：检查WFP过滤器

```powershell
# 需要管理员权限
netsh wfp show filters file=$env:TEMP\wfp_filters.xml
Select-String -Path "$env:TEMP\wfp_filters.xml" -Pattern "TAO|QQPC|feishu|chrome"
```

## 修复方案

### 方案一：清除WFP残留规则（需要管理员权限）

创建 PowerShell 脚本 `scripts/delete_wfp_filters.ps1`：

```powershell
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class WfpApi {
    [DllImport("fwpuclnt.dll", CharSet = CharSet.Unicode)]
    public static extern uint FwpmEngineOpen0(IntPtr serverName, uint authnService,
        IntPtr authIdentity, IntPtr session, out IntPtr engineHandle);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmEngineClose0(IntPtr engineHandle);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmFilterDeleteByKey0(IntPtr engineHandle, ref Guid filterKey);
    [DllImport("fwpuclnt.dll")]
    public static extern uint FwpmSubLayerDeleteByKey0(IntPtr engineHandle, ref Guid subLayerKey);
}
"@

$engineHandle = [IntPtr]::Zero
[WfpApi]::FwpmEngineOpen0([IntPtr]::Zero, 10, [IntPtr]::Zero, [IntPtr]::Zero, [ref]$engineHandle)

# 删除腾讯电脑管家TAONETFLOW相关过滤器
$taoFilters = @('e4a641e5-d35f-4726-8b3d-f026261818ab',
                 'ee90c253-3b67-49fe-bbed-f0c1d5660388',
                 '005c0421-7772-4d1b-acb7-6ed93ff89317')
$taoSublayer = '8c19c91f-4599-4931-b1cd-0da78dec1ede'

foreach ($guid in $taoFilters) {
    $g = [Guid]$guid
    [WfpApi]::FwpmFilterDeleteByKey0($engineHandle, [ref]$g) | Out-Null
}
$sl = [Guid]$taoSublayer
[WfpApi]::FwpmSubLayerDeleteByKey0($engineHandle, [ref]$sl) | Out-Null
[WfpApi]::FwpmEngineClose0($engineHandle) | Out-Null

# 重置网络协议栈
netsh winsock reset
ipconfig /flushdns

Write-Host "WFP过滤器已清除，请重启电脑"
```

### 方案二：停止并禁用相关服务

```powershell
# 以管理员身份运行
sc.exe stop TAOKernelDriver
sc.exe config TAOKernelDriver start=disabled
sc.exe stop TsNetHlpX64
sc.exe config TsNetHlpX64 start=disabled
```

### 方案三：清理注册表残留

```powershell
# 以管理员身份运行
$regPaths = @(
    "HKLM:\SOFTWARE\Tencent\QQPCMgr",
    "HKLM:\SYSTEM\CurrentControlSet\Services\TAOKernelDriver",
    "HKLM:\SYSTEM\CurrentControlSet\Services\TAOKernelEx64",
    "HKLM:\SYSTEM\CurrentControlSet\Services\TsNetHlpX64"
)
foreach ($path in $regPaths) {
    Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
}
```

## 关键结论

| 现象 | 根因 | 解决方案 |
|------|------|----------|
| python能访问飞书，chrome不行 | WFP进程名拦截 | 清除WFP过滤器，重启电脑 |
| python和chrome都不能访问 | 代理/DNS残留 | 清除代理配置，重置DNS |
| 所有工具都不能访问 | 网络层问题 | 检查路由器/DNS服务器 |
| 其他同事正常，唯独自己不行 | 安全软件残留 | 卸载安全软件，清除WFP规则 |

## 注意事项

1. **Winsock重置必须重启才能生效**：执行 `netsh winsock reset` 后必须重启电脑
2. **WFP规则在内核层**：用户态工具无法直接删除，需要管理员权限和WFP API
3. **腾讯电脑管家卸载后WFP规则仍残留**：即使卸载软件，其注册的过滤规则不会自动清除
4. **进程名拦截在TLS握手阶段**：WFP驱动在TLS ClientHello阶段检查进程名和SNI域名