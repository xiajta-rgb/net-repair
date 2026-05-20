# 网络诊断修复工具 - 检测体系与修复手册

## 一、检测体系架构

### 1.1 整体流程

```
┌─────────────────────────────────────────────────────────┐
│                    开始检测                               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  步骤1: 网络配置检测                                    │
│  ├─ 检测本机IP地址                                     │
│  ├─ 检测网关连通性                                     │
│  └─ 检测公网连通性                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  步骤2: DNS解析检测                                   │
│  ├─ 解析 github.com                                  │
│  ├─ 解析 baidu.com                                   │
│  └─ 检测公共DNS服务器                                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  步骤3: 端口连通性检测                                │
│  ├─ 检测443端口 (HTTPS)                              │
│  ├─ 检测代理端口 10808                                │
│  └─ 检测代理端口 7890                                 │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  步骤4: Git配置检测                                   │
│  ├─ 检测Git代理配置                                   │
│  ├─ 检测Git SSL验证                                   │
│  └─ 检测Git远程仓库                                   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   生成诊断报告                            │
│  ├─ 健康评分计算                                      │
│  ├─ 问题统计                                          │
│  └─ 修复建议                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 检测级别定义

| 级别 | 标识 | 颜色 | 说明 |
|------|------|------|------|
| 致命 | ! | 红色 | 网络完全不可用 |
| 严重 | x | 红色 | 核心功能不可用 |
| 警告 | / | 黄色 | 存在潜在问题 |
| 正常 | v | 绿色 | 检测通过 |

---

## 二、问题诊断与修复方案

### 2.1 网络配置问题

#### 问题: 本机IP获取失败

**症状:**
- IP显示为"检测失败"
- 可能显示为127.0.0.1

**原因分析:**
1. 网卡未启用
2. DHCP未获取IP
3. 网络适配器故障

**修复方案:**

**方案A: 启用网卡**
```powershell
# 管理员权限运行
Get-NetAdapter | Enable-NetAdapter
```

**方案B: 刷新IP配置**
```powershell
# 释放并重新获取IP
ipconfig /release
ipconfig /renew
```

**方案C: 重启网络服务**
```powershell
# 重启网络相关服务
net stop Dhcp
net start Dhcp
```

---

#### 问题: 网关不可达

**症状:**
- 网关显示红色
- Ping网关超时

**原因分析:**
1. 路由器故障
2. 网关IP配置错误
3. 物理连接问题

**修复方案:**

**方案A: 检查物理连接**
```
检查网线是否插好
检查路由器是否正常供电
尝试重启路由器
```

**方案B: 检查网关IP**
```powershell
# 查看当前网关
route print | findstr 0.0.0.0

# 手动设置网关
route add 0.0.0.0 mask 0.0.0.0 <网关IP>
```

**方案C: 重置网络栈**
```powershell
netsh winsock reset
netsh int ip reset
ipconfig /flushdns
# 重启电脑
```

---

### 2.2 DNS解析问题

#### 问题: 域名解析失败

**症状:**
- github.com解析失败
- 浏览器可以IP访问但不能域名访问

**原因分析:**
1. DNS服务器配置错误
2. DNS服务未启动
3. 防火墙拦截DNS

**修复方案:**

**方案A: 更换DNS服务器**
```powershell
# 设置阿里DNS
netsh interface ip set dns "以太网" static 223.5.5.5
netsh interface ip add dns "以太网" 8.8.8.8 index=2
```

**方案B: 刷新DNS缓存**
```powershell
ipconfig /flushdns
ipconfig /registerdns
ipconfig /release
ipconfig /renew
```

**方案C: 检查DNS服务**
```powershell
# 重启DNS客户端服务
net stop Dnscache
net start Dnscache
```

---

#### 问题: DNS解析缓慢

**症状:**
- 解析时间超过500ms
- 首次访问网站加载慢

**原因分析:**
1. DNS服务器响应慢
2. DNS缓存污染
3. 网络延迟高

**修复方案:**

**方案A: 使用快速DNS**
```
推荐DNS服务器:
- 阿里DNS: 223.5.5.5
- 腾讯DNS: 119.29.29.29
- Google DNS: 8.8.8.8
- Cloudflare DNS: 1.1.1.1
```

**方案B: 清理DNS缓存**
```powershell
ipconfig /flushdns
ipconfig /displaydns
```

---

### 2.3 端口连通性问题

#### 问题: 443端口不可达

**症状:**
- github.com:443 连接失败
- HTTPS网站无法访问

**原因分析:**
1. 防火墙拦截
2. 代理配置错误
3. 端口被屏蔽

**修复方案:**

**方案A: 检查防火墙规则**
```powershell
# 查看443端口规则
netsh advfirewall firewall show rule name=all | findstr 443

# 临时关闭防火墙测试
netsh advfirewall set allprofiles state off

# 开放443端口
netsh advfirewall firewall add rule name="Open 443" dir=in action=allow protocol=TCP localport=443
```

**方案B: 检查代理设置**
```powershell
# 查看系统代理
netsh winhttp show proxy

# 重置代理
netsh winhttp reset proxy
```

---

#### 问题: 代理端口未监听

**症状:**
- 10808/7890端口无响应
- 配置了代理但无法使用

**原因分析:**
1. 代理软件未启动
2. 代理端口配置错误
3. 代理软件崩溃

**修复方案:**

**方案A: 启动代理软件**
```
启动代理软件:
- Clash
- V2Ray
- Shadowrocket
- Surge
```

**方案B: 检查端口配置**
```
代理软件中检查:
1. HTTP代理端口
2. SOCKS5代理端口
3. 局域网共享是否开启
```

**方案C: 清除Git代理**
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
```

---

### 2.4 Git配置问题

#### 问题: Git代理无效

**症状:**
- Git拉取代码超时
- 代理配置了但不起作用

**原因分析:**
1. 代理端口不匹配
2. 代理软件未启动
3. 代理协议不支持

**修复方案:**

**方案A: 清除代理配置**
```bash
git config --global --unset http.proxy
git config --global --unset https.proxy
git config --global --list | grep proxy
```

**方案B: 重新配置代理**
```bash
# HTTP代理
git config --global http.proxy http://127.0.0.1:7890

# HTTPS代理
git config --global https.proxy http://127.0.0.1:7890
```

**方案C: 仅对GitHub设置代理**
```bash
git config --global --add url."https://github.com/".insteadOf "git@github.com:"
git config --global --add url."https://github.com/".insteadOf "https://github.com/"
```

---

#### 问题: GitHub 443端口连接失败

**症状:**
- git clone超时
- ssh git@github.com失败
- SSL证书错误

**原因分析:**
1. 网络限制443端口
2. 防火墙拦截
3. 代理配置错误

**修复方案:**

**方案A: 临时禁用SSL验证**
```bash
# 临时方案
git config --global http.sslVerify false

# 测试完成后恢复
git config --global http.sslVerify true
```

**方案B: 使用SSH替代HTTPS**
```bash
# 检查SSH key
ls -la ~/.ssh

# 生成SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# 测试连接
ssh -T git@github.com
```

**方案C: 使用国内镜像**
```bash
# Gitee镜像
git clone https://gitee.com/username/repo.git

# 设置GitHub镜像
git config --global url."https://hub.fastgit.xyz/".insteadOf "https://github.com/"
```

---

### 2.5 SSL证书问题

#### 问题: SSL证书验证失败

**症状:**
- SSL certificate error
- 证书链不完整

**原因分析:**
1. 代理SSL拦截
2. 系统时间错误
3. 证书被篡改

**修复方案:**

**方案A: 检查系统时间**
```
确保系统时间正确:
1. 自动同步时间
2. 手动校准时间
3. 时区设置正确
```

**方案B: 更新根证书**
```powershell
# Windows更新证书
certutil -syncWithUI
certutil -generateSSTFromPolicyStore %TEMP%\roots.sst
```

---

## 三、快速修复操作

### 3.1 一键修复清单

| 操作 | 命令 | 适用场景 |
|------|------|----------|
| 清除Git代理 | `git config --global --unset http.proxy` | 代理失效 |
| 禁用SSL验证 | `git config --global http.sslVerify false` | 证书错误 |
| 刷新DNS | `ipconfig /flushdns` | DNS问题 |
| 重置网络 | `netsh winsock reset` | 全面网络故障 |

### 3.2 修复优先级

```
优先级1 (立即执行):
├─ ipconfig /flushdns
└─ git config --global --unset http.proxy

优先级2 (如仍有问题):
├─ ipconfig /release && ipconfig /renew
└─ netsh winsock reset

优先级3 (最后手段):
└─ 重启电脑
```

---

## 四、常见问题场景

### 场景1: 公司网络限制

**症状:**
- GitHub无法访问
- 特定网站打不开

**解决方案:**
```bash
# 1. 检查代理
git config --global --get http.proxy

# 2. 清除代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 3. 使用SSH
ssh -T git@github.com
```

### 场景2: 代理软件冲突

**症状:**
- 代理开了反而更慢
- 部分网站反而打不开

**解决方案:**
```powershell
# 1. 关闭代理测试
netsh winhttp show proxy

# 2. 重置代理
netsh winhttp reset proxy

# 3. 只对Git设置代理
git config --global http.proxy http://127.0.0.1:7890
```

### 场景3: DNS污染

**症状:**
- ping得通但浏览器打不开
- QQ能上网页不行

**解决方案:**
```powershell
# 1. 刷新DNS
ipconfig /flushdns

# 2. 更换DNS
netsh interface ip set dns "以太网" static 223.5.5.5

# 3. 使用DoH
# 在浏览器设置中使用DNS over HTTPS
```

---

## 五、诊断报告解读

### 5.1 健康评分

| 评分 | 状态 | 说明 |
|------|------|------|
| 90-100 | 优秀 | 网络完全正常 |
| 70-89 | 良好 | 有轻微警告 |
| 50-69 | 一般 | 需要关注 |
| 30-49 | 较差 | 需要修复 |
| 0-29 | 严重 | 立即修复 |

### 5.2 统计指标

- **通过**: 检测项全部正常
- **警告**: 存在潜在问题
- **错误**: 核心功能受影响
- **致命**: 完全不可用

---

## 六、高级诊断

### 6.1 手动测试命令

```powershell
# 网络连通性
ping 223.5.5.5
ping github.com

# DNS测试
nslookup github.com
nslookup github.com 8.8.8.8

# 端口测试
Test-NetConnection github.com -Port 443

# 路由追踪
tracert github.com

# SSL测试
openssl s_client -connect github.com:443
```

### 6.2 日志分析

```powershell
# 查看系统日志
eventvwr.msc

# 网络诊断日志
Get-NetAdapterDiagnosticInfo

# IP配置
ipconfig /all
```

---

## 七、预防措施

1. **定期检查** - 每周运行一次诊断
2. **记录配置** - 保存正常时的配置
3. **代理备份** - 记录代理配置信息
4. **时间同步** - 确保系统时间准确

---

## 八、联系支持

如遇到复杂问题，请提供:
1. 诊断报告(.txt/.html)
2. 问题截图
3. 已尝试的修复方案
4. 网络环境描述(公司/家庭/特殊网络)
