# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 智能修复引擎
智能修复策略引擎 - 针对检测到的故障自动修复
"""

import subprocess
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass


class RepairAction:
    """修复操作"""

    def __init__(self, name: str, description: str, command: Optional[List[str]] = None,
                 auto_execute: bool = True, risk_level: str = "低"):
        self.name = name
        self.description = description
        self.command = command
        self.auto_execute = auto_execute
        self.risk_level = risk_level
        self.executed = False
        self.success = False
        self.message = ""

    def execute(self) -> Tuple[bool, str]:
        """执行修复操作"""
        if not self.command:
            return False, "无执行命令"

        try:
            result = subprocess.run(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.executed = True
                self.success = True
                self.message = f"✅ {self.name} - 执行成功"
                return True, self.message
            else:
                self.executed = True
                self.success = False
                self.message = f"❌ {self.name} - 执行失败: {result.stderr or result.stdout}"
                return False, self.message

        except subprocess.TimeoutExpired:
            self.executed = True
            self.success = False
            self.message = f"❌ {self.name} - 执行超时"
            return False, self.message
        except Exception as e:
            self.executed = True
            self.success = False
            self.message = f"❌ {self.name} - 异常: {str(e)}"
            return False, self.message


class RepairEngine:
    """智能修复引擎"""

    def __init__(self):
        self.platform = sys.platform
        self.actions: List[RepairAction] = []
        self.fix_history: List[dict] = []

    def add_action(self, action: RepairAction):
        """添加修复操作"""
        self.actions.append(action)

    def clear_actions(self):
        """清空修复操作队列"""
        self.actions = []

    def _git_config_unset(self, key: str) -> RepairAction:
        """创建Git配置清除操作"""
        if self.platform == "win32":
            cmd = ["git", "config", "--global", "--unset", key]
        else:
            cmd = ["git", "config", "--global", "--unset", key]

        return RepairAction(
            name=f"清除Git配置-{key}",
            description=f"清除Git {key} 配置",
            command=cmd,
            risk_level="低"
        )

    def _create_dns_flush_action(self) -> RepairAction:
        """创建DNS刷新操作"""
        if self.platform == "win32":
            cmd = ["ipconfig", "/flushdns"]
        elif self.platform == "darwin":
            cmd = ["sudo", "dscacheutil", "-flushcache"]
        else:
            cmd = ["sudo", "systemd-resolve", "--flush-caches"]

        return RepairAction(
            name="刷新DNS缓存",
            description="清除本地DNS缓存",
            command=cmd,
            risk_level="低"
        )

    def _create_git_ssl_disable_action(self) -> RepairAction:
        """创建Git SSL禁用操作"""
        cmd = ["git", "config", "--global", "http.sslVerify", "false"]

        return RepairAction(
            name="禁用Git SSL验证",
            description="临时禁用Git SSL验证(测试用)",
            command=cmd,
            risk_level="中"
        )

    def _create_git_ssl_enable_action(self) -> RepairAction:
        """创建Git SSL启用操作"""
        cmd = ["git", "config", "--global", "http.sslVerify", "true"]

        return RepairAction(
            name="启用Git SSL验证",
            description="重新启用Git SSL验证",
            command=cmd,
            risk_level="低"
        )

    def _create_git_mirror_config_action(self) -> RepairAction:
        """创建Git镜像配置操作"""
        mirror_url = "https://gitee.com/mirrors/github-mirror.git"

        return RepairAction(
            name="配置Git国内镜像",
            description="尝试配置Git镜像源作为替代方案",
            command=None,
            risk_level="低"
        )

    def _create_system_proxy_clear_action(self) -> RepairAction:
        """创建清除系统代理操作"""
        if self.platform == "win32":
            cmd = [
                "powershell",
                "-Command",
                r"Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0"
            ]
        else:
            cmd = [" networksetup", "-setwebproxy", "Wi-Fi", "off"]

        return RepairAction(
            name="清除系统代理",
            description="关闭Windows系统代理设置",
            command=cmd,
            risk_level="中"
        )

    def _create_git_reset_network_action(self) -> RepairAction:
        """创建Git网络配置重置操作"""
        actions = []

        for key in ["http.proxy", "https.proxy"]:
            actions.append(RepairAction(
                name=f"重置Git网络配置-{key}",
                description=f"清除Git {key} 配置",
                command=["git", "config", "--global", "--unset", key] if self.platform == "win32" else ["git", "config", "--global", "--unset", key],
                risk_level="低"
            ))

        actions.append(RepairAction(
            name="重置Git SSL配置",
            description="恢复Git SSL验证默认设置",
            command=["git", "config", "--global", "--unset", "http.sslVerify"],
            risk_level="低"
        ))

        return actions

    def detect_and_prepare_fixes(self, diagnostic_results: List) -> List[RepairAction]:
        """根据诊断结果检测并准备修复操作"""
        self.clear_actions()

        for result in diagnostic_results:
            if result.status.value in ["严重", "警告"]:
                if "代理端口未监听" in result.message or "无效代理" in result.message:
                    self.add_action(self._git_config_unset("http.proxy"))
                    self.add_action(self._git_config_unset("https.proxy"))

                if "Git SSL验证" in result.test_name and result.status.value == "警告":
                    self.add_action(self._create_git_ssl_disable_action())

                if "端口连接失败" in result.message and "github.com" in result.message:
                    self.add_action(self._create_git_ssl_disable_action())

                if "DNS" in result.component and result.status.value == "错误":
                    self.add_action(self._create_dns_flush_action())

                if "系统代理" in result.test_name and result.status.value == "警告":
                    self.add_action(self._create_system_proxy_clear_action())

        if not self.actions:
            self.add_action(RepairAction(
                name="无操作",
                description="未检测到需要修复的问题",
                command=None,
                risk_level="无"
            ))

        return self.actions

    def execute_all_fixes(self) -> Tuple[int, int, List[str]]:
        """执行所有修复操作"""
        success_count = 0
        fail_count = 0
        messages = []

        for action in self.actions:
            if action.command:
                success, message = action.execute()
                messages.append(message)

                if success:
                    success_count += 1
                else:
                    fail_count += 1

                self.fix_history.append({
                    "action": action.name,
                    "success": success,
                    "message": message
                })
            else:
                messages.append(f"ℹ️ {action.description}")

        return success_count, fail_count, messages

    def get_fix_summary(self) -> dict:
        """获取修复摘要"""
        total = len(self.actions)
        executed = sum(1 for a in self.actions if a.executed)
        success = sum(1 for a in self.actions if a.success)
        failed = sum(1 for a in self.actions if a.executed and not a.success)

        return {
            "total_actions": total,
            "executed": executed,
            "success": success,
            "failed": failed,
            "success_rate": f"{(success/executed*100):.1f}%" if executed > 0 else "0%"
        }

    def get_recommended_fixes(self, diagnostic_results: List) -> List[dict]:
        """获取推荐的修复方案（基于诊断结果）"""
        recommendations = []

        for result in diagnostic_results:
            if result.suggestion and result.status.value in ["严重", "警告", "致命"]:
                recommendations.append({
                    "component": result.component,
                    "test_name": result.test_name,
                    "problem": result.message,
                    "suggestion": result.suggestion,
                    "severity": result.status.value
                })

        return recommendations

    def reset_git_network_config(self) -> Tuple[bool, str]:
        """重置Git网络配置（综合修复）"""
        messages = []
        all_success = True

        proxy_keys = ["http.proxy", "https.proxy"]
        for key in proxy_keys:
            action = self._git_config_unset(key)
            success, msg = action.execute()
            messages.append(msg)
            if not success:
                all_success = False

        action = self._create_git_ssl_enable_action()
        success, msg = action.execute()
        messages.append(msg)
        if not success:
            all_success = False

        final_msg = "\n".join(messages)
        return all_success, final_msg

    def quick_fix_proxy_issue(self) -> Tuple[bool, str]:
        """快速修复代理问题"""
        messages = []

        action1 = self._git_config_unset("http.proxy")
        success1, msg1 = action1.execute()
        messages.append(msg1)

        action2 = self._git_config_unset("https.proxy")
        success2, msg2 = action2.execute()
        messages.append(msg2)

        all_success = success1 and success2
        final_msg = "\n".join(messages)

        return all_success, final_msg

    def quick_fix_github_443(self) -> Tuple[bool, str]:
        """快速修复GitHub 443端口问题"""
        messages = []

        action = self._create_git_ssl_disable_action()
        success, msg = action.execute()
        messages.append(msg)

        return success, "\n".join(messages)

    def flush_dns_cache(self) -> Tuple[bool, str]:
        """刷新DNS缓存"""
        action = self._create_dns_flush_action()
        success, msg = action.execute()

        return success, msg

    def auto_fix_all(self, diagnostic_results: List) -> Tuple[int, int, List[str]]:
        """一键自动修复所有问题"""
        self.detect_and_prepare_fixes(diagnostic_results)
        return self.execute_all_fixes()

    def get_fix_history(self) -> List[dict]:
        """获取修复历史"""
        return self.fix_history

    def clear_history(self):
        """清空修复历史"""
        self.fix_history = []