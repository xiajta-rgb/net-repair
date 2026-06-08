# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 核心诊断引擎
Professional Network & Git Diagnostic Tool
"""

import socket
import subprocess
import sys
import re
import time
import ipaddress
import os
import urllib.request
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum


class Severity(Enum):
    """故障严重级别"""
    CRITICAL = "致命"
    ERROR = "严重"
    WARNING = "警告"
    INFO = "正常"
    SUCCESS = "通过"


class NetworkComponent(Enum):
    """网络组件类型"""
    NETWORK_CARD = "网卡"
    GATEWAY = "网关"
    DNS = "DNS服务器"
    PROXY = "代理服务"
    PORT = "端口"
    GIT = "Git配置"
    SSL = "SSL证书"
    ROUTE = "路由"
    FIREWALL = "防火墙"
    WIFI = "无线网络"
    MTU = "MTU"
    CONNECTION = "连接"


@dataclass
class DiagnosticResult:
    """诊断结果数据类"""
    component: str
    test_name: str
    status: Severity
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict:
        return {
            "component": self.component,
            "test_name": self.test_name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "suggestion": self.suggestion,
            "timestamp": self.timestamp
        }


class NetworkDiagnosticEngine:
    """网络诊断引擎 - 核心检测逻辑"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._get_default_config()
        self.results: List[DiagnosticResult] = []
        self.platform = sys.platform

    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "test_domains": ["github.com", "www.baidu.com"],
            "test_dns": ["223.5.5.5", "8.8.8.8", "119.29.29.29"],
            "proxy_ports": [10808, 7890, 1080],
            "timeout": 3,
            "retry_count": 2
        }

    def _run_command(self, cmd: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        """执行系统命令"""
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)

    def _ping(self, host: str, count: int = 2) -> Tuple[bool, Optional[float], str]:
        """Ping测试 - 返回成功状态、延迟、错误信息"""
        cmd = ["ping", "-n", str(count), host] if self.platform == "win32" else ["ping", "-c", str(count), host]
        returncode, stdout, stderr = self._run_command(cmd, timeout=15)

        if returncode == 0:
            try:
                if self.platform == "win32":
                    match = re.search(r'平均\s*=\s*(\d+)ms', stdout)
                else:
                    match = re.search(r'avg.*?(\d+.\d+)', stdout)

                if match:
                    avg_time = float(match.group(1))
                    return True, avg_time, ""
                return True, None, ""
            except:
                return True, None, ""
        else:
            error_msg = "连接超时" if "timed out" in stdout.lower() or "100% loss" in stdout else "Ping失败"
            return False, None, error_msg

    def _port_test(self, host: str, port: int, timeout: int = 2) -> Tuple[bool, str]:
        """TCP端口检测"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                return True, ""
            else:
                return False, f"端口连接失败 (代码: {result})"
        except socket.timeout:
            return False, "连接超时"
        except socket.gaierror:
            return False, "DNS解析失败"
        except Exception as e:
            return False, str(e)

    def _dns_resolve(self, domain: str) -> Tuple[bool, Optional[str], float]:
        """DNS解析测试"""
        start_time = time.time()
        try:
            ip = socket.gethostbyname(domain)
            elapsed = (time.time() - start_time) * 1000
            return True, ip, elapsed
        except socket.gaierror as e:
            return False, None, 0
        except Exception as e:
            return False, None, 0

    def _get_local_ip(self) -> Optional[str]:
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return None

    def _get_default_gateway(self) -> Optional[str]:
        """获取默认网关"""
        if self.platform == "win32":
            returncode, stdout, _ = self._run_command(["route", "print"])
            if returncode == 0:
                match = re.search(r'0.0.0.0\s+0.0.0.0\s+(\d+\.\d+\.\d+\.\d+)', stdout)
                if match:
                    return match.group(1)
        else:
            returncode, stdout, _ = self._run_command(["ip", "route"])
            if returncode == 0:
                match = re.search(r'default via (\d+\.\d+\.\d+\.\d+)', stdout)
                if match:
                    return match.group(1)
        return None

    def _check_git_config(self) -> Dict[str, str]:
        """检测Git配置"""
        config = {}
        proxy_keys = ["http.proxy", "https.proxy", "http.proxy", "https.proxy"]

        for key in proxy_keys:
            returncode, stdout, _ = self._run_command(["git", "config", "--global", "--get", key])
            if returncode == 0 and stdout.strip():
                config[key] = stdout.strip()

        ssl_verify = self._get_git_ssl_verify()
        config["http.sslVerify"] = ssl_verify

        return config

    def _get_git_ssl_verify(self) -> str:
        """获取Git SSL验证配置"""
        returncode, stdout, _ = self._run_command(["git", "config", "--global", "--get", "http.sslVerify"])
        return stdout.strip() if returncode == 0 else "未设置"

    def _get_system_proxy(self) -> Optional[str]:
        """获取系统代理设置"""
        if self.platform == "win32":
            returncode, stdout, _ = self._run_command(["reg", "query", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", "/v", "ProxyEnable"])
            if returncode == 0 and "0x1" in stdout:
                returncode2, proxy_server, _ = self._run_command(["reg", "query", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", "/v", "ProxyServer"])
                if returncode2 == 0:
                    match = re.search(r'ProxyServer\s+REG_SZ\s+(.+)', proxy_server)
                    if match:
                        return match.group(1).strip()
        return None

    def _traceroute(self, host: str, max_hops: int = 30) -> List[str]:
        """路由追踪"""
        trace_results = []
        if self.platform == "win32":
            cmd = ["tracert", "-h", str(max_hops), "-w", "1000", host]
        else:
            cmd = ["traceroute", "-m", str(max_hops), "-w", "1", host]

        returncode, stdout, stderr = self._run_command(cmd, timeout=60)
        if returncode == 0:
            trace_results = stdout.split('\n')
        return trace_results

    def add_result(self, component: str, test_name: str, status: Severity, message: str,
                   details: Optional[str] = None, suggestion: Optional[str] = None):
        """添加诊断结果"""
        result = DiagnosticResult(
            component=component,
            test_name=test_name,
            status=status,
            message=message,
            details=details,
            suggestion=suggestion
        )
        self.results.append(result)

    def get_critical_issues(self) -> List[DiagnosticResult]:
        """获取所有严重问题"""
        return [r for r in self.results if r.status in [Severity.CRITICAL, Severity.ERROR]]

    def get_all_results(self) -> List[DiagnosticResult]:
        """获取所有诊断结果"""
        return self.results

    def clear_results(self):
        """清空诊断结果"""
        self.results = []

    def _check_network_adapters_status(self) -> Dict[str, any]:
        """检测网卡状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-Command",
                    "Get-NetAdapter | Where-Object {$_.Status -ne 'Not Present'} | Select-Object Name, Status, MacAddress | ConvertTo-Json"
                ], timeout=15)
                
                if returncode == 0 and stdout.strip():
                    import json
                    data = json.loads(stdout)
                    adapters = data if isinstance(data, list) else [data]
                    return {"success": True, "adapters": adapters}
            return {"success": False, "adapters": []}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_cable_connection(self) -> Tuple[bool, str]:
        """检测网线连接状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-Command",
                    "(Get-NetAdapter | Where-Object {$_.PhysicalMediaType -match 'Wireless|802.11'}).Count"
                ], timeout=10)
                
                if returncode == 0 and stdout.strip().isdigit():
                    is_wireless = int(stdout.strip()) > 0
                else:
                    is_wireless = False
                
                if is_wireless:
                    return True, "无线网络"
                
                returncode, stdout, _ = self._run_command([
                    "powershell", "-Command",
                    "Get-NetAdapter | Where-Object {$_.Status -eq 'Up' -and $_.PhysicalMediaType -notmatch 'Wireless'} | Measure-Object | Select-Object -ExpandProperty Count"
                ], timeout=10)
                
                if returncode == 0 and stdout.strip().isdigit() and int(stdout.strip()) > 0:
                    return True, "有线网络已连接"
                else:
                    return True, "网络已连接"
        except ValueError:
            return True, "网络已连接"
        except Exception as e:
            return True, f"检测中: {str(e)}"

    def _check_dhcp_status(self) -> Tuple[bool, Optional[str], str]:
        """检测DHCP服务状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-Command",
                    "Get-NetIPInterface -AddressFamily IPv4 | Where-Object {$_.Dhcp -eq 'Enabled'} | Measure-Object | Select-Object -ExpandProperty Count"
                ], timeout=10)
                
                if returncode == 0:
                    dhcp_enabled = int(stdout.strip()) > 0
                    if dhcp_enabled:
                        return True, "DHCP", "已启用"
                    else:
                        local_ip = self._get_local_ip()
                        if local_ip and not local_ip.startswith("169.254"):
                            return True, "静态IP", "未使用DHCP"
                        else:
                            return False, None, "DHCP未启用且无有效IP"
                        
                return False, None, "无法检测DHCP状态"
        except Exception as e:
            return False, None, f"检测失败: {str(e)}"

    def _check_ip_conflict(self) -> Tuple[bool, Optional[str]]:
        """检测IP地址冲突"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "arp", "-a"
                ], timeout=10)
                
                if returncode == 0:
                    lines = stdout.split('\n')
                    duplicates = []
                    seen_ips = {}
                    
                    for line in lines:
                        match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+([0-9a-f-]+)', line, re.IGNORECASE)
                        if match:
                            ip = match.group(1)
                            mac = match.group(2).replace('-', ':')
                            if ip in seen_ips:
                                return True, f"IP {ip} 可能有冲突 (MAC: {mac})"
                            seen_ips[ip] = mac
                            
                return False, None
        except Exception as e:
            return False, None

    def _check_hosts_file(self) -> Tuple[bool, Optional[List[str]], str]:
        """检测hosts文件"""
        try:
            if self.platform == "win32":
                hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
            else:
                hosts_path = "/etc/hosts"
                
            if os.path.exists(hosts_path):
                with open(hosts_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                custom_entries = []
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if re.match(r'^\d+\.\d+\.\d+\.\d+', line):
                            custom_entries.append(f"行{i}: {line}")
                
                if custom_entries:
                    return True, custom_entries, f"发现 {len(custom_entries)} 条自定义配置"
                else:
                    return True, [], "hosts文件正常，无自定义配置"
            else:
                return False, None, "hosts文件不存在"
        except Exception as e:
            return False, None, f"读取失败: {str(e)}"

    def _check_wifi_signal(self) -> Dict[str, any]:
        """检测WiFi信号强度"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-Command",
                    "Get-NetAdapter | Where-Object {$_.PhysicalMediaType -match 'Wireless|802.11' -and $_.Status -eq 'Up'} | Select-Object Name, Status | ConvertTo-Json"
                ], timeout=10)
                
                wifi_adapter = None
                if returncode == 0 and stdout.strip():
                    import json
                    data = json.loads(stdout)
                    if isinstance(data, dict):
                        wifi_adapter = data.get("Name")
                    elif isinstance(data, list) and len(data) > 0:
                        wifi_adapter = data[0].get("Name")
                
                if not wifi_adapter:
                    return {"connected": False, "reason": "no_wifi"}
                
                returncode2, stdout2, _ = self._run_command([
                    "netsh", "wlan", "show", "interfaces"
                ], timeout=10)
                
                if returncode2 == 0:
                    info = {"connected": True}
                    ssid_match = re.search(r'SSID\s*:\s*(.+)', stdout2)
                    if ssid_match:
                        raw_ssid = ssid_match.group(1).strip()
                        try:
                            info["ssid"] = bytes.fromhex(raw_ssid.replace(':', '')).decode('utf-8')
                        except:
                            profile_match = re.search(r'配置文件\s*:\s*(.+)', stdout2)
                            if not profile_match:
                                profile_match = re.search(r'Profile\s*:\s*(.+)', stdout2)
                            if profile_match:
                                info["ssid"] = profile_match.group(1).strip()
                            else:
                                info["ssid"] = raw_ssid
                    else:
                        profile_match = re.search(r'配置文件\s*:\s*(.+)', stdout2)
                        if not profile_match:
                            profile_match = re.search(r'Profile\s*:\s*(.+)', stdout2)
                        if profile_match:
                            info["ssid"] = profile_match.group(1).strip()
                    signal_match = re.search(r'信号\s*:\s*(\d+)%', stdout2)
                    if not signal_match:
                        signal_match = re.search(r'Signal\s*:\s*(\d+)%', stdout2)
                    if signal_match:
                        info["signal"] = int(signal_match.group(1))
                    channel_match = re.search(r'频道\s*:\s*(\d+)', stdout2)
                    if not channel_match:
                        channel_match = re.search(r'Channel\s*:\s*(\d+)', stdout2)
                    if channel_match:
                        info["channel"] = int(channel_match.group(1))
                    rate_match = re.search(r'接收速率\(Mbps\)\s*:\s*([\d.]+)', stdout2)
                    if not rate_match:
                        rate_match = re.search(r'Receive rate\(Mbps\)\s*:\s*([\d.]+)', stdout2)
                    if rate_match:
                        info["rate"] = int(float(rate_match.group(1)))
                    return info
                
                return {"connected": True}
            return {"connected": False, "reason": "unsupported"}
        except Exception as e:
            return {"connected": False, "error": str(e)}

    def _check_mtu(self) -> Dict[str, any]:
        """检测MTU设置"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "netsh", "interface", "ipv4", "show", "subinterfaces"
                ], timeout=10)
                
                if returncode == 0:
                    mtu_list = []
                    lines = stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('MTU') or line.startswith('-'):
                            continue
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                mtu_val = int(parts[0])
                                iface = ' '.join(parts[4:]) if len(parts) > 4 else ' '.join(parts[1:])
                                if mtu_val > 0 and 'Loopback' not in iface:
                                    mtu_list.append({"interface": iface, "mtu": mtu_val})
                            except ValueError:
                                continue
                    return {"success": True, "mtu_list": mtu_list}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_firewall_status(self) -> Dict[str, any]:
        """检测防火墙状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "netsh", "advfirewall", "show", "allprofiles", "state"
                ], timeout=10)
                
                if returncode == 0:
                    profiles = {}
                    current_profile = None
                    for line in stdout.split('\n'):
                        line = line.strip()
                        if '域配置文件' in line or 'Domain Profile' in line:
                            current_profile = "domain"
                        elif '专用配置文件' in line or 'Private Profile' in line:
                            current_profile = "private"
                        elif '公用配置文件' in line or 'Public Profile' in line:
                            current_profile = "public"
                        elif '启用' in line and current_profile:
                            profiles[current_profile] = True
                            current_profile = None
                        elif '关闭' in line and current_profile:
                            profiles[current_profile] = False
                            current_profile = None
                    return {"success": True, "profiles": profiles}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_network_connections(self) -> Dict[str, any]:
        """检测网络连接数统计"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "netstat", "-ano"
                ], timeout=10)
                
                if returncode == 0:
                    stats = {
                        "LISTENING": 0,
                        "ESTABLISHED": 0,
                        "TIME_WAIT": 0,
                        "CLOSE_WAIT": 0,
                        "SYN_SENT": 0,
                        "SYN_RECEIVED": 0
                    }
                    for line in stdout.split('\n'):
                        for state in stats:
                            if state in line:
                                stats[state] += 1
                    return {"success": True, "stats": stats}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_dns_config(self) -> Dict[str, any]:
        """检测DNS配置详情"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "ipconfig", "/all"
                ], timeout=10)
                
                if returncode == 0:
                    dns_servers = []
                    current_adapter = None
                    for line in stdout.split('\n'):
                        if '适配器' in line or 'adapter' in line.lower():
                            current_adapter = line.strip()
                        dns_match = re.search(r'DNS\s*服务器.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
                        if not dns_match:
                            dns_match = re.search(r'DNS Servers.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
                        if dns_match:
                            dns_servers.append(dns_match.group(1))
                    return {"success": True, "dns_servers": list(set(dns_servers))}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_network_speed(self) -> Dict[str, any]:
        """检测网络连接速率"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-Command",
                    "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object Name, LinkSpeed | ConvertTo-Json"
                ], timeout=10)
                
                if returncode == 0 and stdout.strip():
                    import json
                    data = json.loads(stdout)
                    adapters = data if isinstance(data, list) else [data]
                    speed_info = []
                    for a in adapters:
                        speed_info.append({
                            "name": a.get("Name", ""),
                            "speed": a.get("LinkSpeed", "未知")
                        })
                    return {"success": True, "adapters": speed_info}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_mtu_info(self) -> Dict[str, any]:
        """获取MTU详细信息（供API调用）"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "netsh", "interface", "ipv4", "show", "subinterfaces"
                ], timeout=10)
                
                if returncode == 0 and stdout:
                    mtu_list = []
                    lines = stdout.split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('MTU') or line.startswith('-'):
                            continue
                        parts = line.split()
                        if len(parts) >= 5:
                            try:
                                mtu_val = int(parts[0])
                                # 接口名从第5列开始（索引4）
                                iface = ' '.join(parts[4:])
                                if mtu_val > 0 and mtu_val < 10000 and 'Loopback' not in iface and 'loopback' not in iface.lower():
                                    mtu_list.append({
                                        "interface": iface, 
                                        "mtu": mtu_val,
                                        "status": "正常" if mtu_val == 1500 else ("偏低" if mtu_val < 1500 else "偏高")
                                    })
                            except (ValueError, IndexError):
                                continue
                    return {"success": True, "mtu_list": mtu_list}
            return {"success": False, "error": "命令执行失败或无输出"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_broadband_info(self) -> Dict[str, any]:
        """获取宽带/网络连接信息"""
        try:
            if self.platform == "win32":
                # 获取网络适配器信息 - 使用UTF-8输出
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-NoProfile", "-Command",
                    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object Name, InterfaceDescription, MacAddress, LinkSpeed, MediaType | ConvertTo-Json -Compress"
                ], timeout=10)
                
                info = {
                    "connection_type": "未知",
                    "adapter_name": "未知",
                    "mac_address": "未知",
                    "link_speed": "未知",
                    "media_type": "未知",
                    "dhcp_enabled": False,
                    "ip_address": "未获取",
                    "subnet_mask": "未获取",
                    "gateway": "未获取",
                    "dns_servers": []
                }
                
                if returncode == 0 and stdout and stdout.strip():
                    import json
                    try:
                        data = json.loads(stdout)
                        adapters = data if isinstance(data, list) else [data]
                        if adapters:
                            adapter = adapters[0]
                            info["adapter_name"] = str(adapter.get("Name", "未知"))
                            info["mac_address"] = str(adapter.get("MacAddress", "未知"))
                            info["link_speed"] = str(adapter.get("LinkSpeed", "未知"))
                            info["media_type"] = str(adapter.get("MediaType", "未知"))
                            
                            # 判断连接类型
                            media = info["media_type"].lower()
                            if "wireless" in media or "wi-fi" in media or "wifi" in media:
                                info["connection_type"] = "Wi-Fi无线"
                            elif "ethernet" in media or "802.3" in media:
                                info["connection_type"] = "以太网有线"
                    except Exception as e:
                        pass
                
                # 获取IP配置
                returncode2, stdout2, _ = self._run_command([
                    "ipconfig", "/all"
                ], timeout=10)
                
                if returncode2 == 0 and stdout2:
                    lines = stdout2.split('\n')
                    current_adapter = None
                    for line in lines:
                        if '适配器' in line or 'adapter' in line.lower():
                            current_adapter = line.strip()
                        if current_adapter and (info["adapter_name"] in current_adapter or info["adapter_name"].replace("-", " ") in current_adapter):
                            # DHCP
                            dhcp_match = re.search(r'DHCP\s*已启用| DHCP enabled', line)
                            if dhcp_match:
                                info["dhcp_enabled"] = True
                            # DNS
                            dns_match = re.search(r'DNS\s*服务器.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
                            if not dns_match:
                                dns_match = re.search(r'DNS Servers.*?:\s*(\d+\.\d+\.\d+\.\d+)', line)
                            if dns_match and dns_match.group(1) not in info["dns_servers"]:
                                info["dns_servers"].append(dns_match.group(1))
                
                return {"success": True, "info": info}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_ipv6_status(self) -> Dict[str, any]:
        """检测IPv6状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, stderr = self._run_command([
                    "powershell", "-NoProfile", "-Command",
                    "Get-NetIPv6Protocol | Select-Object -Property RouterDiscoveryEnabled, AddressingMode | ConvertTo-Json"
                ], timeout=10)
                
                ipv6_enabled = False
                has_global_ipv6 = False
                
                # 检查IPv6是否启用
                if returncode == 0 and stdout:
                    ipv6_enabled = True
                
                # 检查是否有IPv6地址
                returncode2, stdout2, _ = self._run_command([
                    "ipconfig", "/all"
                ], timeout=10)
                
                if returncode2 == 0 and stdout2:
                    if "IPv6" in stdout2 and ":" in stdout2:
                        has_global_ipv6 = True
                
                return {"success": True, "ipv6_enabled": ipv6_enabled, "has_global_ipv6": has_global_ipv6}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_dns_latency(self) -> Dict[str, any]:
        """检测各DNS服务器延迟"""
        dns_servers = [
            ("223.5.5.5", "阿里DNS"),
            ("119.29.29.29", "腾讯DNS"),
            ("8.8.8.8", "Google DNS"),
            ("1.1.1.1", "Cloudflare DNS"),
            ("9.9.9.9", "Quad9 DNS")
        ]
        
        results = []
        for dns_ip, dns_name in dns_servers:
            start_time = time.time()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.settimeout(2)
                # 简单测试：尝试DNS查询
                sock.sendto(b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06google\x03com\x00\x00\x01\x00\x01', (dns_ip, 53))
                sock.recvfrom(1024)
                latency = (time.time() - start_time) * 1000
                results.append({"dns": dns_ip, "name": dns_name, "latency": round(latency, 1), "available": True})
            except:
                results.append({"dns": dns_ip, "name": dns_name, "latency": 0, "available": False})
            finally:
                sock.close()
        
        return {"success": True, "dns_latency": results}

    def _check_bandwidth(self) -> Dict[str, any]:
        """估算带宽（通过下载测试）"""
        try:
            import tempfile
            import os
            
            test_url = "http://speedtest.tele2.net/1MB.zip"
            test_file = os.path.join(tempfile.gettempdir(), "bandwidth_test.dat")
            
            start_time = time.time()
            try:
                urllib.request.urlretrieve(test_url, test_file)
                download_time = time.time() - start_time
                file_size = os.path.getsize(test_file) if os.path.exists(test_file) else 0
                
                if download_time > 0 and file_size > 0:
                    speed_mbps = (file_size * 8) / (download_time * 1000000)
                    os.remove(test_file)
                    return {"success": True, "speed_mbps": round(speed_mbps, 2), "file_size": file_size, "download_time": round(download_time, 2)}
            except Exception as e:
                if os.path.exists(test_file):
                    os.remove(test_file)
                raise e
            
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_latency_jitter(self) -> Dict[str, any]:
        """检测网络延迟抖动"""
        try:
            gateway = self._get_default_gateway()
            if not gateway:
                return {"success": False, "error": "无法获取网关"}
            
            latencies = []
            for _ in range(10):
                success, latency, _ = self._ping(gateway, count=1)
                if success and latency:
                    latencies.append(latency)
                time.sleep(0.1)
            
            if len(latencies) >= 2:
                avg = sum(latencies) / len(latencies)
                variance = sum((x - avg) ** 2 for x in latencies) / len(latencies)
                std_dev = variance ** 0.5
                jitter = std_dev
                return {
                    "success": True,
                    "min": round(min(latencies), 2),
                    "max": round(max(latencies), 2),
                    "avg": round(avg, 2),
                    "jitter": round(jitter, 2),
                    "stability": "稳定" if jitter < 5 else ("一般" if jitter < 15 else "不稳定")
                }
            return {"success": False, "error": "采样不足"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_tcp_parameters(self) -> Dict[str, any]:
        """检测TCP优化参数"""
        try:
            if self.platform == "win32":
                params = {
                    "TcpWindowSize": "未知",
                    "TcpTimedWaitDelay": "未知",
                    "MaxUserPort": "未知"
                }
                
                # 使用PowerShell获取TCP参数
                returncode, stdout, _ = self._run_command([
                    "powershell", "-NoProfile", "-Command",
                    "netsh int tcp show global"
                ], timeout=10)
                
                if returncode == 0 and stdout:
                    for line in stdout.split('\n'):
                        line = line.strip()
                        if 'Receive Window' in line or 'Autotuning' in line:
                            params[line.split(':')[0].strip()] = line.split(':')[-1].strip() if ':' in line else line
                
                return {"success": True, "params": params}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_winsock_status(self) -> Dict[str, any]:
        """检测Winsock目录状态"""
        try:
            if self.platform == "win32":
                returncode, stdout, _ = self._run_command([
                    "netsh", "winsock", "show", "catalog"
                ], timeout=15)
                
                if returncode == 0:
                    # 统计已注册的LSP/SPP数量
                    lines = stdout.split('\n')
                    provider_count = 0
                    for line in lines:
                        if 'Provider' in line and 'GUID' in line:
                            provider_count += 1
                    return {"success": True, "provider_count": provider_count, "status": "正常" if provider_count < 100 else "异常(过多)"}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _discover_path_mtu(self, target: str = "8.8.8.8") -> Dict[str, any]:
        """路径MTU发现"""
        try:
            if self.platform == "win32":
                # 使用ping -f -l 测试不同大小的数据包
                mtu_values = [1500, 1492, 1480, 1400, 1380, 1300]
                discovered_mtu = 1500
                
                for mtu in mtu_values:
                    cmd = ["ping", "-n", "2", "-f", "-l", str(mtu - 28), target]  # -28 是IP和ICMP头
                    returncode, stdout, _ = self._run_command(cmd, timeout=5)
                    
                    if returncode == 0 and "TTL=" in stdout:
                        discovered_mtu = mtu
                        break
                    elif "需要拆分" in stdout or "packets" in stdout.lower():
                        discovered_mtu = mtu - 20
                        break
                
                return {"success": True, "discovered_mtu": discovered_mtu, "target": target}
            return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_speedtest_info(self) -> Dict[str, any]:
        """获取网速测试信息"""
        return self._check_bandwidth()

    def get_dns_latency_info(self) -> Dict[str, any]:
        """获取DNS延迟信息"""
        return self._check_dns_latency()

    def get_ipv6_info(self) -> Dict[str, any]:
        """获取IPv6状态信息"""
        return self._check_ipv6_status()

    def get_jitter_info(self) -> Dict[str, any]:
        """获取延迟抖动信息"""
        return self._check_latency_jitter()

    def get_tcp_params_info(self) -> Dict[str, any]:
        """获取TCP参数信息"""
        return self._check_tcp_parameters()

    def get_winsock_info(self) -> Dict[str, any]:
        """获取Winsock状态信息"""
        return self._check_winsock_status()

    def get_path_mtu_info(self, target: str = "8.8.8.8") -> Dict[str, any]:
        """获取路径MTU信息"""
        return self._discover_path_mtu(target)