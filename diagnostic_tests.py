# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 诊断测试模块
诊断测试套件 - 包含所有诊断检测项
"""

from diagnostic_engine import (
    NetworkDiagnosticEngine, DiagnosticResult, Severity,
    NetworkComponent
)


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
    def test_git_proxy_config(engine: NetworkDiagnosticEngine):
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

            listening_ports = PortTester.test_proxy_ports(engine)

            if listening_ports:
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

        PortTester.test_target_port_connectivity(
            engine,
            "github.com",
            22,
            "Git远程仓库(SSH)"
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


def run_full_diagnostic(engine: NetworkDiagnosticEngine):
    """执行全量诊断"""
    engine.clear_results()

    engine.add_result(
        component="系统",
        test_name="系统信息",
        status=Severity.INFO,
        message=f"🚀 开始网络&Git全量诊断 ({engine.platform})",
        details=f"时间: {engine.results[0].timestamp if engine.results else ''}"
    )

    NetworkCardTester.test_local_ip(engine)
    NetworkCardTester.test_gateway_connectivity(engine)
    PublicNetworkTester.test_public_dns_connectivity(engine)

    for domain in engine.config["test_domains"]:
        DNSTester.test_domain_resolution(engine, [domain])

    DNSTester.test_public_dns_servers(engine)

    for domain in engine.config["test_domains"]:
        PortTester.test_target_port_connectivity(engine, domain, 443, f"{domain} HTTPS")

    PortTester.test_proxy_ports(engine)
    GitTester.test_git_proxy_config(engine)
    GitTester.test_git_ssl_verify(engine)
    GitTester.test_git_remote_connectivity(engine, "github.com")

    SystemProxyTester.test_system_proxy(engine)

    RouteTester.test_route_to_target(engine, "github.com", "GitHub")

    return engine.get_all_results()