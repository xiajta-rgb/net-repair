# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 配置文件
"""

import os
from typing import List, Dict


class Config:
    """工具配置类"""

    def __init__(self):
        self.test_domains: List[str] = [
            "github.com",
            "www.baidu.com",
            "www.google.com"
        ]

        self.test_dns: List[str] = [
            "223.5.5.5",
            "8.8.8.8",
            "119.29.29.29",
            "1.1.1.1"
        ]

        self.proxy_ports: List[int] = [
            10808,
            7890,
            1080,
            1086,
            7891
        ]

        self.timeout: int = 3
        self.retry_count: int = 2
        self.max_hops: int = 30

        self.git_domains: List[str] = [
            "github.com",
            "gitlab.com",
            "gitee.com"
        ]

        self.important_ports: Dict[str, int] = {
            "HTTPS": 443,
            "SSH": 22,
            "HTTP": 80
        }

        self.dns_timeout: int = 5
        self.port_timeout: int = 3
        self.ping_count: int = 2

    def get_config_dict(self) -> Dict:
        """获取配置字典"""
        return {
            "test_domains": self.test_domains,
            "test_dns": self.test_dns,
            "proxy_ports": self.proxy_ports,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_hops": self.max_hops,
            "git_domains": self.git_domains,
            "important_ports": self.important_ports,
            "dns_timeout": self.dns_timeout,
            "port_timeout": self.port_timeout,
            "ping_count": self.ping_count
        }

    def update_config(self, key: str, value):
        """更新配置项"""
        if hasattr(self, key):
            setattr(self, key, value)
            return True
        return False

    @staticmethod
    def load_from_file(file_path: str) -> 'Config':
        """从文件加载配置"""
        config = Config()

        if os.path.exists(file_path):
            try:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for key, value in data.items():
                    if hasattr(config, key):
                        setattr(config, key, value)

            except Exception as e:
                print(f"加载配置文件失败: {e}")

        return config

    def save_to_file(self, file_path: str):
        """保存配置到文件"""
        try:
            import json
            config_dict = self.get_config_dict()

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)

            return True, f"配置已保存到: {file_path}"
        except Exception as e:
            return False, f"保存配置失败: {e}"


class SystemInfo:
    """系统信息类"""

    @staticmethod
    def get_platform() -> str:
        """获取操作系统平台"""
        import sys
        return sys.platform

    @staticmethod
    def get_platform_name() -> str:
        """获取操作系统名称"""
        import platform
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Darwin":
            return "macOS"
        elif system == "Linux":
            return "Linux"
        else:
            return system

    @staticmethod
    def get_python_version() -> str:
        """获取Python版本"""
        import sys
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    @staticmethod
    def check_git_installed() -> bool:
        """检查Git是否安装"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    @staticmethod
    def get_git_version() -> str:
        """获取Git版本"""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
                text=True
            )
            return result.stdout.strip()
        except:
            return "未安装"

    @staticmethod
    def get_system_info() -> Dict:
        """获取系统信息"""
        return {
            "platform": SystemInfo.get_platform(),
            "platform_name": SystemInfo.get_platform_name(),
            "python_version": SystemInfo.get_python_version(),
            "git_installed": SystemInfo.check_git_installed(),
            "git_version": SystemInfo.get_git_version()
        }


DEFAULT_CONFIG = Config()