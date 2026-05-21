# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 诊断测试模块
诊断测试套件 - 包含所有诊断检测项
"""

from diagnostic_engine import (
    NetworkDiagnosticEngine, DiagnosticResult, Severity,
    NetworkComponent
)
from typing import Optional, List


class NetworkCardTester:
    """网卡状态测试"""

    @staticmethod
    def test_local_ip(engine: NetworkDiagnosticEngine):
        """测试本机IP地址获取"""
        local_ip = engine._get_local_ip()

        if local_ip:
            if local_ip.startswith("127."):
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name="本机IP地址",
                    status=Severity.WARNING,
                    message=f"⚠️ 本机IP: {local_ip} (Loopback地址)",
                    details="检测到Loopback地址，可能网卡未正确配置",
                    suggestion="检查网络连接和DHCP配置"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name="本机IP地址",
                    status=Severity.SUCCESS,
                    message=f"✅ 本机IP: {local_ip}",
                    details="IP地址获取正常"
                )
        else:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="本机IP地址",
                status=Severity.ERROR,
                message="❌ 无法获取本机IP地址",
                details="网络接口可能未启用或未正确配置",
                suggestion="检查网卡驱动和网络连接"
            )

    @staticmethod
    def test_gateway_connectivity(engine: NetworkDiagnosticEngine):
        """测试网关连通性"""
        gateway = engine._get_default_gateway()

        if gateway:
            success, latency, error = engine._ping(gateway, count=2)

            if success:
                latency_msg = f" (延迟: {latency}ms)" if latency else ""
                engine.add_result(
                    component=NetworkComponent.GATEWAY.value,
                    test_name="网关连通性",
                    status=Severity.SUCCESS,
                    message=f"✅ 网关 {gateway} 连通正常{latency_msg}",
                    details=f"内网连接正常，可达默认网关"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.GATEWAY.value,
                    test_name="网关连通性",
                    status=Severity.ERROR,
                    message=f"❌ 网关 {gateway} 连接失败",
                    details=error,
                    suggestion="检查路由器/网关配置或更换网关"
                )
        else:
            engine.add_result(
                component=NetworkComponent.GATEWAY.value,
                test_name="网关连通性",
                status=Severity.CRITICAL,
                message="❌ 无法获取默认网关",
                details="可能未连接网络或网络配置异常",
                suggestion="检查物理网络连接和网络配置"
            )

    @staticmethod
    def test_network_adapters(engine: NetworkDiagnosticEngine):
        """测试网卡状态"""
        result = engine._check_network_adapters_status()
        
        if result.get("success"):
            adapters = result.get("adapters", [])
            enabled_count = sum(1 for a in adapters if a.get("Status") == "Up")
            disabled_count = len(adapters) - enabled_count
            
            if disabled_count > 0:
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name="网卡状态",
                    status=Severity.WARNING,
                    message=f"⚠️ 网卡状态: {enabled_count}个启用, {disabled_count}个禁用",
                    details=f"检测到 {len(adapters)} 个网卡",
                    suggestion="如需使用禁用网卡，请启用对应的网络适配器"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name="网卡状态",
                    status=Severity.SUCCESS,
                    message=f"✅ 网卡状态正常: {enabled_count}个已启用",
                    details=f"所有 {len(adapters)} 个网卡均正常工作"
                )
        else:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="网卡状态",
                status=Severity.WARNING,
                message=f"⚠️ 无法获取网卡状态详情",
                details=result.get("error", "未知错误"),
                suggestion="请以管理员权限运行或检查网络适配器"
            )

    @staticmethod
    def test_cable_connection(engine: NetworkDiagnosticEngine):
        """测试网线连接状态"""
        connected, info = engine._check_cable_connection()
        
        if connected:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="网线连接",
                status=Severity.SUCCESS,
                message=f"✅ {info}",
                details="网络物理连接正常"
            )
        else:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="网线连接",
                status=Severity.ERROR,
                message=f"❌ {info}",
                details="请检查网线是否插好，或是否使用了正确的网络适配器",
                suggestion="1. 检查网线连接 2. 尝试更换网线 3. 确认网卡已启用"
            )

    @staticmethod
    def test_dhcp_status(engine: NetworkDiagnosticEngine):
        """测试DHCP状态"""
        enabled, ip_type, info = engine._check_dhcp_status()
        
        if enabled:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="DHCP服务",
                status=Severity.SUCCESS,
                message=f"✅ DHCP状态: {ip_type}",
                details=info
            )
        else:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="DHCP服务",
                status=Severity.ERROR,
                message=f"❌ DHCP异常: {info}",
                details="DHCP配置可能存在问题",
                suggestion="1. 尝试手动刷新IP: ipconfig /release && ipconfig /renew 2. 检查网络适配器DHCP设置"
            )

    @staticmethod
    def test_ip_conflict(engine: NetworkDiagnosticEngine):
        """测试IP地址冲突"""
        has_conflict, conflict_info = engine._check_ip_conflict()
        
        if has_conflict:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="IP地址冲突",
                status=Severity.ERROR,
                message=f"❌ {conflict_info}",
                details="网络上可能存在IP地址冲突",
                suggestion="1. 释放并重新获取IP: ipconfig /release && ipconfig /renew 2. 手动设置一个不同的静态IP"
            )
        else:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="IP地址冲突",
                status=Severity.SUCCESS,
                message="✅ 未检测到IP地址冲突",
                details="IP配置正常"
            )

    @staticmethod
    def test_hosts_file(engine: NetworkDiagnosticEngine):
        """测试hosts文件"""
        success, entries, info = engine._check_hosts_file()
        
        if success:
            if entries:
                entry_list = ", ".join(entries[:3])
                more = f" 等{len(entries)}条" if len(entries) > 3 else ""
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name="hosts文件",
                    status=Severity.WARNING,
                    message=f"⚠️ hosts文件有自定义配置{more}",
                    details=f"发现 {len(entries)} 条自定义规则: {entry_list}",
                    suggestion="如遇奇怪的DNS问题，可考虑清空hosts文件自定义部分"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name="hosts文件",
                    status=Severity.SUCCESS,
                    message="✅ hosts文件正常",
                    details="无自定义配置"
                )
        else:
            engine.add_result(
                component=NetworkComponent.DNS.value,
                test_name="hosts文件",
                status=Severity.WARNING,
                message=f"⚠️ {info}",
                details="可能无法读取hosts文件",
                suggestion="检查文件权限或以管理员身份运行"
            )


class PublicNetworkTester:
    """公网连通性测试"""

    @staticmethod
    def test_public_dns_connectivity(engine: NetworkDiagnosticEngine):
        """测试公网DNS连通性（223.5.5.5 / 8.8.8.8）"""
        public_hosts = [
            ("223.5.5.5", "阿里DNS"),
            ("8.8.8.8", "Google DNS"),
            ("119.29.29.29", "腾讯DNS")
        ]

        success_count = 0
        fail_count = 0

        for host, name in public_hosts:
            success, latency, error = engine._ping(host, count=2)

            if success:
                success_count += 1
                latency_msg = f" (延迟: {latency}ms)" if latency else ""
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name=f"公网连通性-{name}",
                    status=Severity.SUCCESS,
                    message=f"✅ {name}({host}) 连通{latency_msg}",
                    details=f"Ping测试成功"
                )
            else:
                fail_count += 1
                engine.add_result(
                    component=NetworkComponent.NETWORK_CARD.value,
                    test_name=f"公网连通性-{name}",
                    status=Severity.ERROR,
                    message=f"❌ {name}({host}) 连接失败",
                    details=error,
                    suggestion="检查网络连接或防火墙配置"
                )

        if fail_count > 0 and success_count == 0:
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name="公网连通性汇总",
                status=Severity.CRITICAL,
                message="❌ 所有公网DNS均无法访问",
                details="网络可能完全断开或被限制",
                suggestion="检查网络连接、路由器配置或联系网络管理员"
            )


class DNSTester:
    """DNS测试套件"""

    @staticmethod
    def test_domain_resolution(engine: NetworkDiagnosticEngine, domains: list):
        """测试域名解析"""
        for domain in domains:
            success, ip, elapsed = engine._dns_resolve(domain)

            if success and ip:
                elapsed_msg = f" (耗时: {elapsed:.0f}ms)" if elapsed else ""
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name=f"域名解析-{domain}",
                    status=Severity.SUCCESS,
                    message=f"✅ {domain} → {ip}{elapsed_msg}",
                    details=f"DNS解析正常，响应时间: {elapsed:.0f}ms" if elapsed else "DNS解析正常"
                )

                if elapsed and elapsed > 500:
                    engine.add_result(
                        component=NetworkComponent.DNS.value,
                        test_name=f"DNS解析速度-{domain}",
                        status=Severity.WARNING,
                        message=f"⚠️ {domain} 解析较慢 ({elapsed:.0f}ms)",
                        details="DNS响应时间超过500ms，可能影响访问速度",
                        suggestion="考虑更换为更快的DNS服务器"
                    )
            else:
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name=f"域名解析-{domain}",
                    status=Severity.ERROR,
                    message=f"❌ {domain} 解析失败",
                    details="域名无法解析，可能是DNS配置问题或网络限制",
                    suggestion="检查DNS配置或尝试更换DNS服务器"
                )

    @staticmethod
    def test_public_dns_servers(engine: NetworkDiagnosticEngine):
        """测试公共DNS服务器可用性"""
        dns_servers = [
            ("223.5.5.5", "阿里DNS"),
            ("8.8.8.8", "Google DNS"),
            ("119.29.29.29", "腾讯DNS"),
            ("1.1.1.1", "Cloudflare DNS")
        ]

        for host, name in dns_servers:
            success, _, _ = engine._dns_resolve(host)

            if success:
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name=f"DNS服务器-{name}",
                    status=Severity.SUCCESS,
                    message=f"✅ {name}({host}) 可用",
                    details="DNS服务器响应正常"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.DNS.value,
                    test_name=f"DNS服务器-{name}",
                    status=Severity.WARNING,
                    message=f"⚠️ {name}({host}) 无响应",
                    details="DNS服务器可能不可达",
                    suggestion="该DNS服务器可能被防火墙拦截"
                )


class PortTester:
    """端口测试套件"""

    @staticmethod
    def test_target_port_connectivity(engine: NetworkDiagnosticEngine, domain: str, port: int, service_name: str):
        """测试目标端口连通性"""
        success, error = engine._port_test(domain, port, timeout=engine.config["timeout"])

        if success:
            engine.add_result(
                component=NetworkComponent.PORT.value,
                test_name=f"{service_name}端口({domain}:{port})",
                status=Severity.SUCCESS,
                message=f"✅ {service_name}({domain}:{port}) 连通",
                details="端口连接正常，服务可达"
            )
        else:
            severity = Severity.ERROR if port == 443 else Severity.WARNING
            engine.add_result(
                component=NetworkComponent.PORT.value,
                test_name=f"{service_name}端口({domain}:{port})",
                status=severity,
                message=f"❌ {service_name}({domain}:{port}) 连接失败",
                details=error,
                suggestion="可能原因: 防火墙拦截、服务未启动、网络限制、代理配置错误"
                    if port == 443 else
                    "检查目标服务是否启动或网络是否允许访问"
            )

    @staticmethod
    def test_proxy_ports(engine: NetworkDiagnosticEngine):
        """测试代理端口监听状态"""
        proxy_ports = engine.config["proxy_ports"]

        listening_ports = []
        not_listening_ports = []

        for port in proxy_ports:
            success, error = engine._port_test("127.0.0.1", port, timeout=2)

            if success:
                listening_ports.append(port)
            else:
                not_listening_ports.append(port)

        if listening_ports:
            ports_str = ", ".join(map(str, listening_ports))
            engine.add_result(
                component=NetworkComponent.PROXY.value,
                test_name="代理端口监听",
                status=Severity.SUCCESS,
                message=f"✅ 代理端口监听正常: {ports_str}",
                details=f"检测到 {len(listening_ports)} 个代理端口正在监听"
            )
        else:
            engine.add_result(
                component=NetworkComponent.PROXY.value,
                test_name="代理端口监听",
                status=Severity.WARNING,
                message=f"⚠️ 未检测到常用代理端口监听: {', '.join(map(str, not_listening_ports))}",
                details="代理软件可能未启动或未配置代理",
                suggestion="启动代理软件(Clash/V2Ray/Shadowrocket)或检查代理端口配置"
            )

        return listening_ports


class GitTester:
    """Git配置测试套件"""

    @staticmethod
    def test_git_proxy_config(engine: NetworkDiagnosticEngine, listening_ports: Optional[List] = None):
        """测试Git代理配置"""
        git_config = engine._check_git_config()

        proxy_configured = any(key in git_config for key in ["http.proxy", "https.proxy"])

        if proxy_configured:
            proxy_list = []
            if "http.proxy" in git_config:
                proxy_list.append(f"HTTP: {git_config['http.proxy']}")
            if "https.proxy" in git_config:
                proxy_list.append(f"HTTPS: {git_config['https.proxy']}")

            proxy_str = "\n".join(proxy_list)

            if listening_ports and len(listening_ports) > 0:
                port_str = ", ".join(map(str, listening_ports))
                engine.add_result(
                    component=NetworkComponent.GIT.value,
                    test_name="Git代理配置",
                    status=Severity.SUCCESS,
                    message=f"✅ 检测到Git代理配置，代理端口可用({port_str})\n{proxy_str}",
                    details="Git代理配置存在且代理软件正在运行"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.GIT.value,
                    test_name="Git代理配置",
                    status=Severity.ERROR,
                    message=f"⚠️ Git配置了代理但代理端口未监听\n{proxy_str}",
                    details="Git代理指向的端口无服务监听，可能是无效代理配置",
                    suggestion="1. 启动代理软件 2. 更新Git代理配置指向正确端口 3. 如不使用代理，执行 'git config --global --unset http.proxy'"
                )
        else:
            engine.add_result(
                component=NetworkComponent.GIT.value,
                test_name="Git代理配置",
                status=Severity.INFO,
                message="✅ Git无代理配置",
                details="Git未配置全局代理"
            )

    @staticmethod
    def test_git_ssl_verify(engine: NetworkDiagnosticEngine):
        """测试Git SSL验证设置"""
        ssl_verify = engine._get_git_ssl_verify()

        if ssl_verify == "false":
            engine.add_result(
                component=NetworkComponent.SSL.value,
                test_name="Git SSL验证",
                status=Severity.WARNING,
                message="⚠️ Git SSL验证已禁用",
                details="http.sslVerify 设置为 false，存在安全风险",
                suggestion="如连接正常，建议重新启用SSL验证: git config --global http.sslVerify true"
            )
        elif ssl_verify == "true":
            engine.add_result(
                component=NetworkComponent.SSL.value,
                test_name="Git SSL验证",
                status=Severity.SUCCESS,
                message="✅ Git SSL验证已启用",
                details="SSL验证正常启用，保障连接安全"
            )
        else:
            engine.add_result(
                component=NetworkComponent.SSL.value,
                test_name="Git SSL验证",
                status=Severity.INFO,
                message=f"ℹ️ Git SSL验证未设置 (默认: true)",
                details="使用Git默认配置"
            )

    @staticmethod
    def test_git_remote_connectivity(engine: NetworkDiagnosticEngine, domain: str = "github.com"):
        """测试Git远程仓库连通性"""
        PortTester.test_target_port_connectivity(
            engine,
            domain,
            443,
            "Git远程仓库(HTTPS)"
        )


class RouteTester:
    """路由测试套件"""

    @staticmethod
    def test_route_to_target(engine: NetworkDiagnosticEngine, host: str, service_name: str):
        """测试到目标地址的路由"""
        trace_results = engine._traceroute(host)

        if trace_results:
            timeout_count = sum(1 for line in trace_results if '*' in line and 'ms' not in line)

            if timeout_count > 10:
                engine.add_result(
                    component=NetworkComponent.ROUTE.value,
                    test_name=f"路由追踪-{service_name}",
                    status=Severity.WARNING,
                    message=f"⚠️ 路由追踪到 {host} 存在丢包",
                    details=f"检测到 {timeout_count} 个路由节点超时",
                    suggestion="可能存在网络拥堵或路由问题"
                )
            elif timeout_count > 0:
                engine.add_result(
                    component=NetworkComponent.ROUTE.value,
                    test_name=f"路由追踪-{service_name}",
                    status=Severity.INFO,
                    message=f"ℹ️ 路由追踪到 {host} 有少量丢包",
                    details=f"检测到 {timeout_count} 个路由节点超时",
                    suggestion="可能存在短暂网络波动"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.ROUTE.value,
                    test_name=f"路由追踪-{service_name}",
                    status=Severity.SUCCESS,
                    message=f"✅ 路由到 {host} 正常",
                    details="所有路由节点正常响应"
                )
        else:
            engine.add_result(
                component=NetworkComponent.ROUTE.value,
                test_name=f"路由追踪-{service_name}",
                status=Severity.WARNING,
                message=f"⚠️ 无法获取到 {host} 的路由信息",
                details="traceroute执行失败",
                suggestion="可能网络限制或工具不可用"
            )


class SystemProxyTester:
    """系统代理测试套件"""

    @staticmethod
    def test_system_proxy(engine: NetworkDiagnosticEngine):
        """测试系统代理设置"""
        system_proxy = engine._get_system_proxy()

        if system_proxy:
            engine.add_result(
                component=NetworkComponent.PROXY.value,
                test_name="系统代理",
                status=Severity.INFO,
                message=f"ℹ️ 检测到系统代理: {system_proxy}",
                details="Windows系统代理已启用",
                suggestion="如Git无法连接，检查系统代理是否与Git代理冲突"
            )
        else:
            engine.add_result(
                component=NetworkComponent.PROXY.value,
                test_name="系统代理",
                status=Severity.INFO,
                message="✅ 系统未启用代理",
                details="Windows系统代理未启用"
            )


class WiFiTester:
    """WiFi检测套件"""

    @staticmethod
    def test_wifi_signal(engine: NetworkDiagnosticEngine):
        """测试WiFi信号强度"""
        result = engine._check_wifi_signal()

        if not result.get("connected"):
            if result.get("reason") == "no_wifi":
                engine.add_result(
                    component=NetworkComponent.WIFI.value,
                    test_name="WiFi信号",
                    status=Severity.INFO,
                    message="ℹ️ 未使用WiFi连接（可能使用有线网络）",
                    details="当前未检测到活跃的WiFi适配器"
                )
            return

        ssid = result.get("ssid", "未知")
        signal = result.get("signal")
        channel = result.get("channel")
        rate = result.get("rate")

        if signal is not None:
            if signal >= 80:
                engine.add_result(
                    component=NetworkComponent.WIFI.value,
                    test_name="WiFi信号",
                    status=Severity.SUCCESS,
                    message=f"✅ WiFi信号优秀: {ssid} ({signal}%)",
                    details=f"信道: {channel or '未知'}, 速率: {rate or '未知'}Mbps"
                )
            elif signal >= 50:
                engine.add_result(
                    component=NetworkComponent.WIFI.value,
                    test_name="WiFi信号",
                    status=Severity.WARNING,
                    message=f"⚠️ WiFi信号一般: {ssid} ({signal}%)",
                    details=f"信道: {channel or '未知'}, 速率: {rate or '未知'}Mbps",
                    suggestion="1. 靠近路由器 2. 避免障碍物 3. 更换5GHz频段"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.WIFI.value,
                    test_name="WiFi信号",
                    status=Severity.ERROR,
                    message=f"❌ WiFi信号弱: {ssid} ({signal}%)",
                    details=f"信号过弱可能导致频繁断连和速度下降",
                    suggestion="1. 靠近路由器 2. 检查干扰源 3. 考虑使用有线连接"
                )
        else:
            engine.add_result(
                component=NetworkComponent.WIFI.value,
                test_name="WiFi信号",
                status=Severity.INFO,
                message=f"ℹ️ 已连接WiFi: {ssid}",
                details="无法获取信号强度信息"
            )


class MTUTester:
    """MTU检测套件"""

    @staticmethod
    def test_mtu(engine: NetworkDiagnosticEngine):
        """测试MTU设置"""
        result = engine._check_mtu()

        if not result.get("success"):
            return

        mtu_list = result.get("mtu_list", [])
        if not mtu_list:
            return

        for item in mtu_list:
            iface = item.get("interface", "未知")
            mtu = item.get("mtu", 0)

            if mtu < 1400:
                engine.add_result(
                    component=NetworkComponent.MTU.value,
                    test_name=f"MTU设置-{iface}",
                    status=Severity.WARNING,
                    message=f"⚠️ {iface} MTU值偏小: {mtu}",
                    details="MTU过小可能导致数据包分片，影响传输效率",
                    suggestion=f"建议设置为1500: netsh interface ipv4 set subinterface \"{iface}\" mtu=1500 store=persistent"
                )
            elif mtu > 1500:
                engine.add_result(
                    component=NetworkComponent.MTU.value,
                    test_name=f"MTU设置-{iface}",
                    status=Severity.INFO,
                    message=f"ℹ️ {iface} MTU: {mtu} (巨帧)",
                    details="启用了巨帧(Jumbo Frame)，适用于高性能网络"
                )
            else:
                engine.add_result(
                    component=NetworkComponent.MTU.value,
                    test_name=f"MTU设置-{iface}",
                    status=Severity.SUCCESS,
                    message=f"✅ {iface} MTU: {mtu} (正常)",
                    details="MTU设置在标准范围内"
                )


class FirewallTester:
    """防火墙检测套件"""

    @staticmethod
    def test_firewall(engine: NetworkDiagnosticEngine):
        """测试防火墙状态"""
        result = engine._check_firewall_status()

        if not result.get("success"):
            return

        profiles = result.get("profiles", {})
        if not profiles:
            return

        all_enabled = all(profiles.values())
        all_disabled = not any(profiles.values())

        profile_names = {
            "domain": "域网络",
            "private": "专用网络",
            "public": "公用网络"
        }

        details_parts = []
        for key, enabled in profiles.items():
            name = profile_names.get(key, key)
            status_text = "启用" if enabled else "关闭"
            details_parts.append(f"{name}: {status_text}")

        details = ", ".join(details_parts)

        if all_disabled:
            engine.add_result(
                component=NetworkComponent.FIREWALL.value,
                test_name="防火墙状态",
                status=Severity.ERROR,
                message="❌ 防火墙已全部关闭",
                details=details,
                suggestion="强烈建议启用防火墙: netsh advfirewall set allprofiles state on"
            )
        elif not all_enabled:
            engine.add_result(
                component=NetworkComponent.FIREWALL.value,
                test_name="防火墙状态",
                status=Severity.WARNING,
                message="⚠️ 部分防火墙配置已关闭",
                details=details,
                suggestion="建议启用所有配置文件的防火墙"
            )
        else:
            engine.add_result(
                component=NetworkComponent.FIREWALL.value,
                test_name="防火墙状态",
                status=Severity.SUCCESS,
                message="✅ 防火墙已全部启用",
                details=details
            )


class ConnectionTester:
    """网络连接检测套件"""

    @staticmethod
    def test_connections(engine: NetworkDiagnosticEngine):
        """测试网络连接数统计"""
        result = engine._check_network_connections()

        if not result.get("success"):
            return

        stats = result.get("stats", {})
        established = stats.get("ESTABLISHED", 0)
        time_wait = stats.get("TIME_WAIT", 0)
        close_wait = stats.get("CLOSE_WAIT", 0)
        listening = stats.get("LISTENING", 0)
        syn_sent = stats.get("SYN_SENT", 0)

        total = sum(stats.values())

        if close_wait > 50:
            engine.add_result(
                component=NetworkComponent.CONNECTION.value,
                test_name="连接状态",
                status=Severity.WARNING,
                message=f"⚠️ CLOSE_WAIT连接数过多: {close_wait}",
                details=f"ESTABLISHED: {established}, TIME_WAIT: {time_wait}, CLOSE_WAIT: {close_wait}, LISTENING: {listening}",
                suggestion="CLOSE_WAIT过多可能表示应用程序未正确关闭连接，建议检查相关应用"
            )
        elif time_wait > 200:
            engine.add_result(
                component=NetworkComponent.CONNECTION.value,
                test_name="连接状态",
                status=Severity.INFO,
                message=f"ℹ️ TIME_WAIT连接数较多: {time_wait}",
                details=f"ESTABLISHED: {established}, TIME_WAIT: {time_wait}, LISTENING: {listening}",
                suggestion="TIME_WAIT较多通常是正常的短连接行为"
            )
        else:
            engine.add_result(
                component=NetworkComponent.CONNECTION.value,
                test_name="连接状态",
                status=Severity.SUCCESS,
                message=f"✅ 网络连接状态正常 (活跃: {established}, 监听: {listening})",
                details=f"ESTABLISHED: {established}, TIME_WAIT: {time_wait}, CLOSE_WAIT: {close_wait}, LISTENING: {listening}"
            )

        if syn_sent > 20:
            engine.add_result(
                component=NetworkComponent.CONNECTION.value,
                test_name="SYN连接",
                status=Severity.WARNING,
                message=f"⚠️ SYN_SENT连接数异常: {syn_sent}",
                details="大量SYN_SENT可能表示网络连接困难或遭受扫描",
                suggestion="检查防火墙设置和网络连通性"
            )


class NetworkSpeedTester:
    """网络速率检测套件"""

    @staticmethod
    def test_link_speed(engine: NetworkDiagnosticEngine):
        """测试网卡连接速率"""
        result = engine._check_network_speed()

        if not result.get("success"):
            return

        adapters = result.get("adapters", [])
        for adapter in adapters:
            name = adapter.get("name", "未知")
            speed = adapter.get("speed", "未知")
            engine.add_result(
                component=NetworkComponent.NETWORK_CARD.value,
                test_name=f"网卡速率-{name}",
                status=Severity.SUCCESS,
                message=f"✅ {name}: {speed}",
                details="网卡连接速率正常"
            )


def run_full_diagnostic(engine: NetworkDiagnosticEngine):
    """执行全量诊断"""
    engine.clear_results()

    engine.add_result(
        component="系统",
        test_name="系统信息",
        status=Severity.INFO,
        message=f"🚀 开始网络全量诊断 ({engine.platform})",
        details=f"时间: {engine.results[0].timestamp if engine.results else ''}"
    )

    NetworkCardTester.test_local_ip(engine)
    NetworkCardTester.test_gateway_connectivity(engine)
    NetworkCardTester.test_network_adapters(engine)
    NetworkCardTester.test_cable_connection(engine)
    NetworkCardTester.test_dhcp_status(engine)
    NetworkCardTester.test_ip_conflict(engine)
    NetworkCardTester.test_hosts_file(engine)
    NetworkSpeedTester.test_link_speed(engine)

    PublicNetworkTester.test_public_dns_connectivity(engine)

    for domain in engine.config["test_domains"]:
        DNSTester.test_domain_resolution(engine, [domain])

    DNSTester.test_public_dns_servers(engine)

    for domain in engine.config["test_domains"]:
        PortTester.test_target_port_connectivity(engine, domain, 443, f"{domain} HTTPS")

    proxy_test_result = PortTester.test_proxy_ports(engine)
    GitTester.test_git_proxy_config(engine, proxy_test_result)
    GitTester.test_git_ssl_verify(engine)
    GitTester.test_git_remote_connectivity(engine, "github.com")

    SystemProxyTester.test_system_proxy(engine)

    RouteTester.test_route_to_target(engine, "github.com", "GitHub")

    WiFiTester.test_wifi_signal(engine)
    MTUTester.test_mtu(engine)
    FirewallTester.test_firewall(engine)
    ConnectionTester.test_connections(engine)

    return engine.get_all_results()