# -*- coding: utf-8 -*-
"""
网络诊断工具 - Flask API服务器
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from diagnostic_engine import NetworkDiagnosticEngine, Severity
from diagnostic_tests import run_full_diagnostic
from repair_engine import RepairEngine
from logger_reporter import Logger, ReportGenerator
from config import Config

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = BASE_DIR

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app)

diagnostic_engine = None
repair_engine = None
logger = None
report_generator = None
diagnostic_results = []


def initialize_tools():
    """初始化工具"""
    global diagnostic_engine, repair_engine, logger, report_generator
    
    config = Config()
    diagnostic_engine = NetworkDiagnosticEngine(config.get_config_dict())
    repair_engine = RepairEngine()
    logger = Logger()
    report_generator = ReportGenerator()


@app.route('/')
def index():
    """首页"""
    return app.send_static_file('index.html')


@app.route('/api/diagnostic', methods=['POST'])
def run_diagnostic():
    """执行全量诊断"""
    global diagnostic_results
    
    logger.info("=" * 60)
    logger.info("🚀 收到诊断请求 - 全量检测开始")
    logger.info("=" * 60)

    run_full_diagnostic(diagnostic_engine)
    diagnostic_results = diagnostic_engine.get_all_results()

    report_generator.add_diagnostic_results(diagnostic_results)
    summary = report_generator.generate_summary()

    status_info = get_status_summary(diagnostic_results)

    logger.info(f"诊断完成 - 健康评分: {summary['health_score']}")

    return jsonify({
        'success': True,
        'results': [r.to_dict() for r in diagnostic_results],
        'summary': summary,
        'status': status_info
    })


@app.route('/api/fix', methods=['POST'])
def auto_fix():
    """执行自动修复"""
    global diagnostic_results
    
    if not diagnostic_results:
        return jsonify({
            'success': False,
            'message': '请先执行诊断'
        }), 400

    logger.info("🔧 收到修复请求 - 开始自动修复")

    success_count, fail_count, messages = repair_engine.auto_fix_all(diagnostic_results)

    report_generator.add_fix_results(success_count, fail_count, messages)

    logger.info(f"修复完成 - 成功: {success_count}, 失败: {fail_count}")

    return jsonify({
        'success': True,
        'success_count': success_count,
        'fail_count': fail_count,
        'messages': messages
    })


@app.route('/api/quick-fix', methods=['POST'])
def quick_fix():
    """快速修复"""
    data = request.get_json()
    fix_type = data.get('type', '')

    logger.info(f"⚡ 收到快速修复请求: {fix_type}")

    success = False
    message = ""

    if fix_type == "proxy":
        success, message = repair_engine.quick_fix_proxy_issue()
    elif fix_type == "github":
        success, message = repair_engine.quick_fix_github_443()
    elif fix_type == "dns":
        success, message = repair_engine.flush_dns_cache()
    elif fix_type == "git_reset":
        success, message = repair_engine.reset_git_network_config()
    else:
        return jsonify({
            'success': False,
            'message': f'未知修复类型: {fix_type}'
        }), 400

    return jsonify({
        'success': success,
        'message': message
    })


@app.route('/api/report', methods=['POST'])
def export_report():
    """导出报告"""
    data = request.get_json()
    format_type = data.get('format', 'all')

    logger.info(f"📄 收到导出报告请求: {format_type}")

    if format_type == 'all':
        results = report_generator.export_reports()
        return jsonify({
            'success': True,
            'formats': {fmt: {'success': success, 'path': path} 
                       for fmt, (success, path) in results.items()}
        })
    elif format_type == 'txt':
        success, path = report_generator.generate_text_report(
            f"网络诊断报告_{get_timestamp()}.txt")
        return jsonify({'success': success, 'path': path})
    elif format_type == 'html':
        success, path = report_generator.generate_html_report(
            f"网络诊断报告_{get_timestamp()}.html")
        return jsonify({'success': success, 'path': path})
    else:
        return jsonify({
            'success': False,
            'message': f'未知格式: {format_type}'
        }), 400


def get_status_summary(results):
    """获取状态摘要"""
    status = {
        'local_ip': '检测失败',
        'gateway': '检测失败',
        'gateway_status': False,
        'public_net': '检测失败',
        'public_net_status': False
    }

    for result in results:
        if '本机IP地址' in result.test_name and result.status in [Severity.SUCCESS, Severity.INFO]:
            match = re.search(r'\d+\.\d+\.\d+\.\d+', result.message)
            if match:
                status['local_ip'] = match.group(0)

        if '网关连通性' in result.test_name and result.status == Severity.SUCCESS:
            match = re.search(r'\d+\.\d+\.\d+\.\d+', result.message)
            if match:
                status['gateway'] = match.group(0)
            status['gateway_status'] = True

        if '公网连通性' in result.test_name and result.status == Severity.SUCCESS:
            status['public_net'] = '正常'
            status['public_net_status'] = True

    return status


def get_timestamp():
    """获取时间戳"""
    from datetime import datetime
    return datetime.now().strftime("%Y%m%d_%H%M%S")


@app.errorhandler(404)
def not_found(e):
    """404处理"""
    return app.send_static_file('index.html')


if __name__ == '__main__':
    initialize_tools()
    print("\n" + "=" * 60)
    print("🚀 网络诊断修复工具 API 服务器启动")
    print("   访问地址: http://localhost:8162")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=8162, debug=False)