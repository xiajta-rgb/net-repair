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
                text=True
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

    def _port_test(self, host: str, port: int, timeout: int = 3) -> Tuple[bool, str]:
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