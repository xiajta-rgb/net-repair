# -*- coding: utf-8 -*-
"""
网络&Git一体化诊断修复工具 - 日志和报告模块
日志系统、报告生成和导出功能
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from colorama import init, Fore, Style

init(autoreset=True)


class LogLevel:
    """日志级别"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    CRITICAL = "CRITICAL"


class Logger:
    """日志系统"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or self._generate_log_filename()
        self.logs: List[Dict] = []
        self.enable_console = True
        self.enable_file = True

    def _generate_log_filename(self) -> str:
        """生成日志文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        return os.path.join(log_dir, f"net_diag_{timestamp}.log")

    def _get_color(self, level: str) -> str:
        """获取日志级别对应的颜色"""
        color_map = {
            LogLevel.DEBUG: Fore.WHITE,
            LogLevel.INFO: Fore.CYAN,
            LogLevel.SUCCESS: Fore.GREEN,
            LogLevel.WARNING: Fore.YELLOW,
            LogLevel.ERROR: Fore.RED,
            LogLevel.CRITICAL: Fore.RED + Style.BRIGHT
        }
        return color_map.get(level, Fore.WHITE)

    def _format_log(self, level: str, message: str) -> str:
        """格式化日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{level}] {message}"

    def log(self, level: str, message: str, print_to_console: bool = True):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": level,
            "message": message
        }
        self.logs.append(log_entry)

        if self.enable_file:
            formatted_log = self._format_log(level, message)
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(formatted_log + "\n")
            except Exception as e:
                print(f"写入日志文件失败: {e}")

        if self.enable_console and print_to_console:
            color = self._get_color(level)
            print(f"{color}{self._format_log(level, message)}{Style.RESET_ALL}")

    def debug(self, message: str):
        """记录调试日志"""
        self.log(LogLevel.DEBUG, message)

    def info(self, message: str):
        """记录信息日志"""
        self.log(LogLevel.INFO, message)

    def success(self, message: str):
        """记录成功日志"""
        self.log(LogLevel.SUCCESS, message)

    def warning(self, message: str):
        """记录警告日志"""
        self.log(LogLevel.WARNING, message)

    def error(self, message: str):
        """记录错误日志"""
        self.log(LogLevel.ERROR, message)

    def critical(self, message: str):
        """记录严重错误日志"""
        self.log(LogLevel.CRITICAL, message)

    def get_logs(self) -> List[Dict]:
        """获取所有日志"""
        return self.logs

    def clear_logs(self):
        """清空日志"""
        self.logs = []

    def get_log_file(self) -> str:
        """获取日志文件路径"""
        return self.log_file


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.report_data: Dict = {}
        self.diagnostic_results: List[Dict] = []
        self.fix_results: List[Dict] = []

    def add_diagnostic_results(self, results: List):
        """添加诊断结果"""
        self.diagnostic_results = [r.to_dict() if hasattr(r, 'to_dict') else r for r in results]

    def add_fix_results(self, success_count: int, fail_count: int, messages: List[str]):
        """添加修复结果"""
        self.fix_results = {
            "success_count": success_count,
            "fail_count": fail_count,
            "messages": messages,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_summary(self) -> Dict:
        """生成诊断摘要"""
        total = len(self.diagnostic_results)
        critical_count = sum(1 for r in self.diagnostic_results if r.get('status') == '致命')
        error_count = sum(1 for r in self.diagnostic_results if r.get('status') == '严重')
        warning_count = sum(1 for r in self.diagnostic_results if r.get('status') == '警告')
        success_count = sum(1 for r in self.diagnostic_results if r.get('status') in ['通过', '正常'])

        health_score = 100
        if critical_count > 0:
            health_score -= critical_count * 30
        if error_count > 0:
            health_score -= error_count * 15
        if warning_count > 0:
            health_score -= warning_count * 5

        health_score = max(0, health_score)

        return {
            "total_tests": total,
            "critical": critical_count,
            "error": error_count,
            "warning": warning_count,
            "success": success_count,
            "health_score": health_score,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_text_report(self, output_file: str):
        """生成文本格式报告"""
        summary = self.generate_summary()

        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("网络&Git诊断修复工具 - 检测报告")
        report_lines.append("=" * 70)
        report_lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"健康评分: {summary['health_score']}/100")

        report_lines.append("\n" + "-" * 70)
        report_lines.append("📊 诊断摘要")
        report_lines.append("-" * 70)
        report_lines.append(f"  总测试项: {summary['total_tests']}")
        report_lines.append(f"  ✅ 通过: {summary['success']}")
        report_lines.append(f"  ⚠️ 警告: {summary['warning']}")
        report_lines.append(f"  ❌ 错误: {summary['error']}")
        report_lines.append(f"  💀 致命: {summary['critical']}")

        report_lines.append("\n" + "-" * 70)
        report_lines.append("🔍 详细检测结果")
        report_lines.append("-" * 70)

        severity_order = ['致命', '严重', '警告', '正常', '通过', '信息']

        grouped_results = {}
        for result in self.diagnostic_results:
            status = result.get('status', '未知')
            if status not in grouped_results:
                grouped_results[status] = []
            grouped_results[status].append(result)

        for severity in severity_order:
            if severity in grouped_results:
                report_lines.append(f"\n[{severity}]")
                for result in grouped_results[severity]:
                    component = result.get('component', '')
                    test_name = result.get('test_name', '')
                    message = result.get('message', '')
                    suggestion = result.get('suggestion', '')

                    report_lines.append(f"  • {component} - {test_name}")
                    report_lines.append(f"    {message}")
                    if suggestion:
                        report_lines.append(f"    💡 建议: {suggestion}")

        if self.fix_results:
            report_lines.append("\n" + "-" * 70)
            report_lines.append("🔧 修复操作记录")
            report_lines.append("-" * 70)
            report_lines.append(f"  成功: {self.fix_results.get('success_count', 0)}")
            report_lines.append(f"  失败: {self.fix_results.get('fail_count', 0)}")
            report_lines.append("\n  详细信息:")
            for msg in self.fix_results.get('messages', []):
                report_lines.append(f"    {msg}")

        report_lines.append("\n" + "=" * 70)
        report_lines.append("报告生成完成")
        report_lines.append("=" * 70)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(report_lines))
            return True, output_file
        except Exception as e:
            return False, str(e)

    def generate_json_report(self, output_file: str):
        """生成JSON格式报告"""
        report = {
            "report_info": {
                "title": "网络&Git诊断修复报告",
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "version": "1.0"
            },
            "summary": self.generate_summary(),
            "diagnostic_results": self.diagnostic_results,
            "fix_results": self.fix_results
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            return True, output_file
        except Exception as e:
            return False, str(e)

    def generate_html_report(self, output_file: str, logger: Optional[Logger] = None):
        """生成HTML格式报告"""
        summary = self.generate_summary()

        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网络&Git诊断报告</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-card.success {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-card.warning {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .stat-card.error {{ background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }}
        .stat-card .number {{ font-size: 36px; font-weight: bold; }}
        .stat-card .label {{ font-size: 14px; opacity: 0.9; }}
        .section {{ margin: 30px 0; }}
        .section h2 {{ color: #333; border-left: 4px solid #007bff; padding-left: 10px; }}
        .result-item {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
        .result-item.success {{ border-left-color: #28a745; }}
        .result-item.warning {{ border-left-color: #ffc107; }}
        .result-item.error {{ border-left-color: #dc3545; }}
        .result-item .component {{ font-weight: bold; color: #333; }}
        .result-item .message {{ color: #666; margin: 5px 0; }}
        .result-item .suggestion {{ background: #e9ecef; padding: 10px; border-radius: 5px; margin-top: 10px; color: #495057; }}
        .timestamp {{ color: #666; font-size: 12px; }}
        .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌐 网络&Git诊断修复报告</h1>
        <div class="timestamp">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>

        <div class="summary">
            <div class="stat-card">
                <div class="number">{summary['health_score']}</div>
                <div class="label">健康评分</div>
            </div>
            <div class="stat-card success">
                <div class="number">{summary['success']}</div>
                <div class="label">通过</div>
            </div>
            <div class="stat-card warning">
                <div class="number">{summary['warning']}</div>
                <div class="label">警告</div>
            </div>
            <div class="stat-card error">
                <div class="number">{summary['error'] + summary['critical']}</div>
                <div class="label">错误</div>
            </div>
        </div>

        <div class="section">
            <h2>📋 详细检测结果</h2>
"""

        severity_order = ['致命', '严重', '警告', '正常', '通过', '信息']
        severity_classes = {
            '致命': 'error',
            '严重': 'error',
            '警告': 'warning',
            '正常': 'success',
            '通过': 'success',
            '信息': ''
        }

        for severity in severity_order:
            matching_results = [r for r in self.diagnostic_results if r.get('status') == severity]
            if matching_results:
                css_class = severity_classes.get(severity, '')
                html_template += f'<div style="margin: 15px 0;"><strong>[{severity}]</strong></div>'

                for result in matching_results:
                    component = result.get('component', '')
                    test_name = result.get('test_name', '')
                    message = result.get('message', '')
                    suggestion = result.get('suggestion', '')

                    html_template += f"""
                    <div class="result-item {css_class}">
                        <div class="component">🎯 {component} - {test_name}</div>
                        <div class="message">{message}</div>
                        {'<div class="suggestion">💡 建议: ' + suggestion + '</div>' if suggestion else ''}
                    </div>
                    """

        if self.fix_results:
            html_template += f"""
        <div class="section">
            <h2>🔧 修复操作</h2>
            <div class="result-item">
                <p>成功修复: {self.fix_results.get('success_count', 0)} | 失败: {self.fix_results.get('fail_count', 0)}</p>
                <ul>
                    {"".join(f"<li>{msg}</li>" for msg in self.fix_results.get('messages', []))}
                </ul>
            </div>
        </div>
            """

        html_template += f"""
        <div class="footer">
            <p>网络&Git诊断修复工具 v1.0</p>
        </div>
    </div>
</body>
</html>"""

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_template)
            return True, output_file
        except Exception as e:
            return False, str(e)

    def export_reports(self, base_name: Optional[str] = None) -> Dict[str, Tuple[bool, str]]:
        """导出所有格式报告"""
        if not base_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = f"net_diagnostic_report_{timestamp}"

        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)

        results = {}

        txt_file = os.path.join(reports_dir, f"{base_name}.txt")
        success, msg = self.generate_text_report(txt_file)
        results['txt'] = (success, msg)

        json_file = os.path.join(reports_dir, f"{base_name}.json")
        success, msg = self.generate_json_report(json_file)
        results['json'] = (success, msg)

        html_file = os.path.join(reports_dir, f"{base_name}.html")
        success, msg = self.generate_html_report(html_file)
        results['html'] = (success, msg)

        return results


class ReportExporter:
    """报告导出器 - 便捷导出接口"""

    @staticmethod
    def quick_export(diagnostic_results: List, fix_results: Optional[Dict] = None,
                     formats: List[str] = ['txt', 'html']) -> Dict[str, Tuple[bool, str]]:
        """快速导出报告"""
        generator = ReportGenerator()
        generator.add_diagnostic_results(diagnostic_results)

        if fix_results:
            generator.add_fix_results(
                fix_results.get('success_count', 0),
                fix_results.get('fail_count', 0),
                fix_results.get('messages', [])
            )

        return generator.export_reports(formats=formats)

    @staticmethod
    def export_txt(diagnostic_results: List, output_file: str) -> Tuple[bool, str]:
        """导出文本报告"""
        generator = ReportGenerator()
        generator.add_diagnostic_results(diagnostic_results)
        return generator.generate_text_report(output_file)

    @staticmethod
    def export_html(diagnostic_results: List, output_file: str) -> Tuple[bool, str]:
        """导出HTML报告"""
        generator = ReportGenerator()
        generator.add_diagnostic_results(diagnostic_results)
        return generator.generate_html_report(output_file)