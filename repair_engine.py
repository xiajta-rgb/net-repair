# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 智能修复引擎
智能修复策略引擎 - 针对检测到的故障自动修复
"""

import subprocess
import sys
import re
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

    def _create_winsock_reset_action(self) -> RepairAction:
        """创建Winsock重置操作"""
        return RepairAction(
            name="重置Winsock目录",
            description="重置网络套接字目录，修复网络协议栈异常",
            command=["netsh", "winsock", "reset"],
            risk_level="中"
        )

    def _create_tcpip_reset_action(self) -> RepairAction:
        """创建TCP/IP协议栈重置操作"""
        return RepairAction(
            name="重置TCP/IP协议栈",
            description="重置IP配置，修复网络层问题",
            command=["netsh", "int", "ip", "reset"],
            risk_level="中"
        )

    def _create_ip_release_action(self) -> RepairAction:
        """创建IP释放操作"""
        return RepairAction(
            name="释放IP地址",
            description="释放当前DHCP分配的IP地址",
            command=["ipconfig", "/release"],
            risk_level="低"
        )

    def _create_ip_renew_action(self) -> RepairAction:
        """创建IP续租操作"""
        return RepairAction(
            name="重新获取IP地址",
            description="通过DHCP重新获取IP配置",
            command=["ipconfig", "/renew"],
            risk_level="低"
        )

    def _create_firewall_enable_action(self) -> RepairAction:
        """创建启用防火墙操作"""
        return RepairAction(
            name="启用防火墙",
            description="启用所有网络配置文件的Windows防火墙",
            command=["netsh", "advfirewall", "set", "allprofiles", "state", "on"],
            risk_level="低"
        )

    def _create_mtu_fix_action(self, interface: str = "") -> RepairAction:
        """创建MTU修复操作"""
        if interface:
            cmd = ["netsh", "interface", "ipv4", "set", "subinterface", interface, "mtu=1500", "store=persistent"]
        else:
            cmd = ["netsh", "interface", "ipv4", "set", "subinterface", "\"以太网\"", "mtu=1500", "store=persistent"]
        return RepairAction(
            name="修复MTU设置",
            description="将MTU设置为标准值1500",
            command=cmd,
            risk_level="低"
        )

    def _create_dns_set_action(self, dns_server: str = "223.5.5.5") -> RepairAction:
        """创建DNS设置操作"""
        return RepairAction(
            name=f"设置DNS为{dns_server}",
            description=f"将首选DNS设置为{dns_server}",
            command=["netsh", "interface", "ipv4", "set", "dns", "\"以太网\"", "static", dns_server],
            risk_level="低"
        )

    def _create_network_adapter_reset_action(self) -> RepairAction:
        """创建网络适配器重置操作"""
        if self.platform == "win32":
            cmd = [
                "powershell", "-Command",
                "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Disable-NetAdapter -Confirm:$false; Start-Sleep -Seconds 2; Get-NetAdapter | Enable-NetAdapter -Confirm:$false"
            ]
        else:
            cmd = None
        return RepairAction(
            name="重置网络适配器",
            description="禁用再启用网络适配器",
            command=cmd,
            risk_level="中"
        )

    def _create_arp_cache_clear_action(self) -> RepairAction:
        """创建ARP缓存清除操作"""
        return RepairAction(
            name="清除ARP缓存",
            description="清除ARP表，解决IP-MAC映射异常",
            command=["netsh", "interface", "ip", "delete", "arpcache"],
            risk_level="低"
        )

    def _create_network_reset_all_action(self) -> List[RepairAction]:
        """创建网络全面重置操作序列"""
        actions = [
            self._create_winsock_reset_action(),
            self._create_tcpip_reset_action(),
            self._create_ip_release_action(),
            self._create_ip_renew_action(),
            self._create_dns_flush_action(),
            self._create_arp_cache_clear_action(),
        ]
        return actions

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

        has_critical = False
        has_gateway_issue = False
        has_dns_issue = False
        has_proxy_issue = False
        has_firewall_issue = False
        has_mtu_issue = False
        has_dhcp_issue = False
        has_ip_conflict = False
        has_connection_issue = False

        for result in diagnostic_results:
            if result.status.value not in ["致命", "严重", "警告"]:
                continue

            if result.status.value in ["致命", "严重"]:
                has_critical = True

            if "代理端口未监听" in result.message or "无效代理" in result.message or "代理端口未监听" in result.details:
                has_proxy_issue = True

            if "Git SSL验证" in result.test_name and result.status.value == "警告":
                self.add_action(self._create_git_ssl_enable_action())

            if "端口连接失败" in result.message and "github.com" in result.message:
                self.add_action(self._create_git_ssl_enable_action())

            if "DNS" in result.component and result.status.value in ["严重", "致命"]:
                has_dns_issue = True

            if "系统代理" in result.test_name and result.status.value in ["警告", "严重"]:
                has_proxy_issue = True

            if "网关" in result.test_name and result.status.value in ["致命", "严重"]:
                has_gateway_issue = True

            if "IP地址冲突" in result.test_name and result.status.value in ["严重", "致命"]:
                has_ip_conflict = True

            if "DHCP" in result.test_name and result.status.value in ["严重", "致命"]:
                has_dhcp_issue = True

            if "域名解析" in result.test_name and result.status.value in ["严重", "致命"]:
                has_dns_issue = True

            if "Git代理配置" in result.test_name and "代理端口未监听" in result.message:
                has_proxy_issue = True

            if "防火墙" in result.test_name and result.status.value in ["严重", "致命"]:
                has_firewall_issue = True

            if "MTU" in result.test_name and result.status.value in ["警告", "严重"]:
                has_mtu_issue = True

            if "CLOSE_WAIT" in result.message or "SYN_SENT" in result.message:
                has_connection_issue = True

            if "WiFi信号弱" in result.message:
                self.add_action(RepairAction(
                    name="重置WiFi适配器",
                    description="禁用再启用WiFi适配器以改善连接",
                    command=["powershell", "-Command",
                             "Get-NetAdapter | Where-Object {$_.PhysicalMediaType -match 'Wireless|802.11'} | Restart-NetAdapter -Confirm:$false"],
                    risk_level="中"
                ))

            if "WiFi信号一般" in result.message:
                self.add_action(RepairAction(
                    name="改善WiFi连接",
                    description="靠近路由器或切换到5GHz频段",
                    command=["powershell", "-Command",
                             "Get-NetAdapter | Where-Object {$_.PhysicalMediaType -match 'Wireless|802.11'} | Restart-NetAdapter -Confirm:$false"],
                    risk_level="低"
                ))

            if "网卡" in result.test_name and ("禁用" in result.message or "Down" in result.message):
                self.add_action(RepairAction(
                    name="启用网络适配器",
                    description="启用被禁用的网络适配器",
                    command=["powershell", "-Command",
                             "Get-NetAdapter | Where-Object {$_.Status -eq 'Disabled'} | Enable-NetAdapter -Confirm:$false"],
                    risk_level="低"
                ))

            if "网线" in result.test_name and "未连接" in result.message:
                pass

            if "公网" in result.test_name and result.status.value in ["致命", "严重"]:
                self.add_action(self._create_winsock_reset_action())
                self.add_action(self._create_dns_flush_action())

            if "路由" in result.test_name and "警告" in result.status.value:
                self.add_action(self._create_winsock_reset_action())
                self.add_action(self._create_dns_flush_action())

            if "TIME_WAIT" in result.message and int(re.search(r'TIME_WAIT:\s*(\d+)', result.message).group(1) if re.search(r'TIME_WAIT:\s*(\d+)', result.message) else 0) > 500:
                self.add_action(self._create_winsock_reset_action())

        if has_proxy_issue:
            self.add_action(self._git_config_unset("http.proxy"))
            self.add_action(self._git_config_unset("https.proxy"))
            self.add_action(self._create_system_proxy_clear_action())

        if has_dns_issue:
            self.add_action(self._create_dns_flush_action())
            self.add_action(self._create_dns_set_action("223.5.5.5"))

        if has_gateway_issue:
            self.add_action(self._create_winsock_reset_action())
            self.add_action(self._create_tcpip_reset_action())
            self.add_action(self._create_ip_release_action())
            self.add_action(self._create_ip_renew_action())
            self.add_action(self._create_arp_cache_clear_action())

        if has_ip_conflict:
            self.add_action(self._create_ip_release_action())
            self.add_action(self._create_ip_renew_action())
            self.add_action(self._create_arp_cache_clear_action())

        if has_dhcp_issue:
            self.add_action(self._create_ip_release_action())
            self.add_action(self._create_ip_renew_action())

        if has_firewall_issue:
            self.add_action(self._create_firewall_enable_action())

        if has_mtu_issue:
            self.add_action(self._create_mtu_fix_action())

        if has_connection_issue:
            self.add_action(self._create_winsock_reset_action())
            self.add_action(self._create_dns_flush_action())
            self.add_action(self._create_arp_cache_clear_action())

        if has_critical and not has_gateway_issue and not has_dns_issue:
            self.add_action(self._create_winsock_reset_action())
            self.add_action(self._create_dns_flush_action())
            self.add_action(self._create_ip_release_action())
            self.add_action(self._create_ip_renew_action())

        if not self.actions:
            self.add_action(RepairAction(
                name="无操作",
                description="未检测到需要修复的问题",
                command=None,
                risk_level="无"
            ))

        return self.actions

    def add_result_suggestion(self, result):
        """为无法自动修复的问题添加建议到actions列表"""
        if result.suggestion:
            self.add_action(RepairAction(
                name=f"建议: {result.test_name}",
                description=result.suggestion,
                command=None,
                risk_level="无"
            ))

    def execute_all_fixes(self) -> Tuple[int, int, List[str]]:
        """执行所有修复操作"""
        success_count = 0
        fail_count = 0
        suggestion_count = 0
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
                if "无操作" in action.name:
                    messages.append("ℹ️ 未检测到需要修复的问题")
                elif "建议:" in action.name:
                    messages.append(f"💡 {action.description}")
                    suggestion_count += 1
                else:
                    messages.append(f"ℹ️ {action.description}")

        if suggestion_count > 0:
            messages.append(f"\n📋 另有 {suggestion_count} 条手动修复建议，请查看详情")

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