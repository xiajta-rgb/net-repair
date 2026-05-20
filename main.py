# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 主程序
Network & Git Diagnostic Tool - Main Entry
"""

import sys
import os
from colorama import init, Fore, Style

from diagnostic_engine import NetworkDiagnosticEngine, Severity
from diagnostic_tests import run_full_diagnostic, NetworkCardTester, DNSTester, PortTester, GitTester, RouteTester, SystemProxyTester
from repair_engine import RepairEngine
from logger_reporter import Logger, ReportGenerator, ReportExporter
from config import Config, SystemInfo

init(autoreset=True)


class NetworkRepairTool:
    """网络修复工具主类"""

    def __init__(self):
        self.config = Config()
        self.engine = NetworkDiagnosticEngine(self.config.get_config_dict())
        self.repair_engine = RepairEngine()
        self.logger = Logger()
        self.report_generator = ReportGenerator()
        self.diagnostic_results = []

    def print_banner(self):
        """打印工具横幅"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║       🌐 网络&Git一体化诊断修复工具 v1.0                  ║
║       Network & Git Diagnostic & Repair Tool             ║
║                                                          ║
║       适用场景：网络受限 | Git连接失败 | 代理失效         ║
║                 443端口不通 | DNS解析异常                 ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(banner)

    def print_system_info(self):
        """打印系统信息"""
        sys_info = SystemInfo.get_system_info()
        print(f"\n{Fore.YELLOW}📋 系统信息:")
        print(f"   平台: {sys_info['platform_name']}")
        print(f"   Python: {sys_info['python_version']}")
        print(f"   Git: {sys_info['git_version']}{Style.RESET_ALL}")

    def run_full_diagnostic(self):
        """执行全量诊断"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"🚀 开始全量网络诊断...")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        self.logger.info("=" * 60)
        self.logger.info("🚀 网络&Git诊断修复工具 - 全量检测开始")
        self.logger.info("=" * 60)

        run_full_diagnostic(self.engine)
        self.diagnostic_results = self.engine.get_all_results()

        self._display_results()

        self.report_generator.add_diagnostic_results(self.diagnostic_results)

        return self.diagnostic_results

    def _display_results(self):
        """显示诊断结果"""
        severity_colors = {
            '致命': Fore.RED + Style.BRIGHT,
            '严重': Fore.RED,
            '警告': Fore.YELLOW,
            '正常': Fore.GREEN,
            '通过': Fore.GREEN,
            '信息': Fore.CYAN
        }

        severity_order = ['致命', '严重', '警告', '正常', '通过', '信息']

        grouped_results = {}
        for result in self.diagnostic_results:
            status = result.status.value
            if status not in grouped_results:
                grouped_results[status] = []
            grouped_results[status].append(result)

        for severity in severity_order:
            if severity in grouped_results:
                color = severity_colors.get(severity, Fore.WHITE)
                print(f"\n{color}═══ [{severity}] ═══{Style.RESET_ALL}")

                for result in grouped_results[severity]:
                    icon = "💀" if severity == '致命' else "❌" if severity == '严重' else "⚠️" if severity == '警告' else "✅"
                    print(f"  {icon} {result.component} - {result.test_name}")
                    print(f"     {result.message}")

                    if result.suggestion:
                        print(f"     💡 建议: {result.suggestion}")

                    self.logger.info(f"[{severity}] {result.message}")

        summary = self.report_generator.generate_summary()
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"📊 诊断摘要: 通过({summary['success']}) | 警告({summary['warning']}) | 错误({summary['error']+summary['critical']})")
        print(f"   健康评分: {summary['health_score']}/100")
        print(f"{'='*60}{Style.RESET_ALL}\n")

    def run_auto_fix(self):
        """执行自动修复"""
        if not self.diagnostic_results:
            print(f"\n{Fore.YELLOW}⚠️ 请先执行诊断后再进行修复{Style.RESET_ALL}")
            return

        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"🔧 开始智能修复...")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        critical_issues = self.engine.get_critical_issues()

        if not critical_issues:
            print(f"{Fore.GREEN}✅ 未检测到需要修复的问题{Style.RESET_ALL}")
            return

        recommendations = self.repair_engine.get_recommended_fixes(self.diagnostic_results)

        if recommendations:
            print(f"{Fore.CYAN}📋 检测到 {len(recommendations)} 个可修复问题:{Style.RESET_ALL}\n")

            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. [{rec['severity']}] {rec['component']} - {rec['test_name']}")
                print(f"     问题: {rec['problem']}")
                print(f"     建议: {rec['suggestion']}\n")

        print(f"\n{Fore.YELLOW}正在执行修复操作...{Style.RESET_ALL}\n")

        success_count, fail_count, messages = self.repair_engine.auto_fix_all(self.diagnostic_results)

        for msg in messages:
            if "成功" in msg:
                print(f"{Fore.GREEN}{msg}{Style.RESET_ALL}")
            elif "失败" in msg or "错误" in msg:
                print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}{msg}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"🔧 修复完成!")
        print(f"   成功: {success_count} | 失败: {fail_count}")
        print(f"{'='*60}{Style.RESET_ALL}\n")

        fix_results = {
            "success_count": success_count,
            "fail_count": fail_count,
            "messages": messages
        }
        self.report_generator.add_fix_results(success_count, fail_count, messages)

        print(f"{Fore.CYAN}💡 提示: 建议重新执行诊断验证修复效果{Style.RESET_ALL}\n")

    def run_quick_fix(self, fix_type: str):
        """执行快速修复"""
        print(f"\n{Fore.CYAN}⚡ 执行快速修复: {fix_type}{Style.RESET_ALL}\n")

        success = False
        message = ""

        if fix_type == "proxy":
            success, message = self.repair_engine.quick_fix_proxy_issue()
        elif fix_type == "github_443":
            success, message = self.repair_engine.quick_fix_github_443()
        elif fix_type == "dns":
            success, message = self.repair_engine.flush_dns_cache()
        elif fix_type == "git_reset":
            success, message = self.repair_engine.reset_git_network_config()

        print(message)
        print()

        return success, message

    def export_report(self, format_type: str = 'all'):
        """导出报告"""
        print(f"\n{Fore.CYAN}📄 正在导出报告...{Style.RESET_ALL}\n")

        if format_type == 'all':
            results = self.report_generator.export_reports()
            for fmt, (success, msg) in results.items():
                if success:
                    print(f"{Fore.GREEN}✅ {fmt.upper()} 报告已生成: {msg}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ {fmt.upper()} 报告生成失败: {msg}{Style.RESET_ALL}")
        elif format_type == 'txt':
            success, msg = ReportExporter.export_txt(
                self.diagnostic_results,
                f"网络诊断报告_{self._get_timestamp()}.txt"
            )
            status_color = Fore.GREEN if success else Fore.RED
            print(f"{status_color}{'✅' if success else '❌'} TXT报告: {msg}{Style.RESET_ALL}")
        elif format_type == 'html':
            success, msg = ReportExporter.export_html(
                self.diagnostic_results,
                f"网络诊断报告_{self._get_timestamp()}.html"
            )
            status_color = Fore.GREEN if success else Fore.RED
            print(f"{status_color}{'✅' if success else '❌'} HTML报告: {msg}{Style.RESET_ALL}")

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def print_menu(self):
        """打印菜单"""
        menu = f"""
{Fore.YELLOW}╔════════════════════════════════════════╗
║         操作菜单                      ║
╠════════════════════════════════════════╣
║  1. 🚀 执行全量诊断                   ║
║  2. 🔧 自动修复检测到的问题           ║
║  3. ⚡ 快速修复Git代理问题             ║
║  4. ⚡ 快速修复GitHub 443端口          ║
║  5. ⚡ 刷新DNS缓存                     ║
║  6. ⚡ 重置Git网络配置                 ║
║  7. 📄 导出诊断报告(TXT)               ║
║  8. 📄 导出诊断报告(HTML)              ║
║  9. 📄 导出所有格式报告                ║
║  0. ❌ 退出工具                       ║
╚════════════════════════════════════════╝{Style.RESET_ALL}
"""
        print(menu)

    def run(self):
        """运行工具"""
        self.print_banner()
        self.print_system_info()

        while True:
            self.print_menu()

            try:
                choice = input(f"{Fore.CYAN}请输入操作序号 [0-9]: {Style.RESET_ALL}").strip()

                if choice == '1':
                    self.run_full_diagnostic()
                elif choice == '2':
                    self.run_auto_fix()
                elif choice == '3':
                    self.run_quick_fix("proxy")
                elif choice == '4':
                    self.run_quick_fix("github_443")
                elif choice == '5':
                    self.run_quick_fix("dns")
                elif choice == '6':
                    self.run_quick_fix("git_reset")
                elif choice == '7':
                    self.export_report('txt')
                elif choice == '8':
                    self.export_report('html')
                elif choice == '9':
                    self.export_report('all')
                elif choice == '0':
                    print(f"\n{Fore.GREEN}👋 感谢使用网络&Git诊断修复工具，再见！{Style.RESET_ALL}\n")
                    break
                else:
                    print(f"\n{Fore.RED}⚠️ 输入无效，请输入 0-9 之间的数字{Style.RESET_ALL}\n")

            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}⚠️ 操作已取消{Style.RESET_ALL}\n")
            except Exception as e:
                print(f"\n{Fore.RED}❌ 发生错误: {str(e)}{Style.RESET_ALL}\n")


def main():
    """主函数"""
    try:
        tool = NetworkRepairTool()
        tool.run()
    except Exception as e:
        print(f"\n{Fore.RED}❌ 工具启动失败: {str(e)}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 请确保已安装必要依赖: pip install colorama{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()