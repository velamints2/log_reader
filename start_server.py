#!/usr/bin/env python3
"""
机器人日志分析系统 - 专用前端服务器启动脚本
"""

import os
import sys
import time
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# 确保在正确的目录
os.chdir('/Users/macbookair/Documents/trae_projects/log_reader')

# 创建Flask应用
app = Flask(__name__, static_folder='frontend')
CORS(app)

@app.route('/')
def index():
    """首页"""
    try:
        return send_from_directory('frontend', 'index.html')
    except Exception as e:
        return f"<h1>机器人日志分析系统</h1><p>前端文件加载失败: {e}</p><p>当前目录: {os.getcwd()}</p>"

@app.route('/<path:path>')
def serve_static(path):
    """静态文件服务"""
    return send_from_directory('frontend', path)

@app.route('/api/status')
def api_status():
    """API状态"""
    return jsonify({
        'status': 'success',
        'message': '机器人日志分析系统运行正常',
        'version': '1.0.0',
        'features': [
            '机器人日志分析',
            'AI增强报告',
            '实时监控',
            '多格式报告生成'
        ]
    })

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time()
    })

@app.route('/api/logs')
def get_logs():
    """获取日志文件列表"""
    try:
        logs_dir = 'logs'
        if not os.path.exists(logs_dir):
            return jsonify([])
        
        log_files = []
        for filename in os.listdir(logs_dir):
            if filename.endswith(('.log', '.txt', '.ERROR', '.INFO', '.WARNING')):
                filepath = os.path.join(logs_dir, filename)
                stat = os.stat(filepath)
                log_files.append({
                    'name': filename,
                    'size': f'{stat.st_size / 1024:.1f} KB',
                    'modified': time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                })
        
        return jsonify(log_files)
    except Exception as e:
        return jsonify([])

@app.route('/api/reports')
def get_reports():
    """获取报告文件列表"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify([])
        
        reports = []
        for filename in os.listdir(reports_dir):
            if filename.endswith(('.html', '.txt', '.json')):
                filepath = os.path.join(reports_dir, filename)
                stat = os.stat(filepath)
                
                # 设置报告类型
                if 'gpt_enhanced' in filename:
                    report_type = 'GPT增强分析'
                elif 'robot_analysis' in filename:
                    report_type = '综合分析'
                elif 'health' in filename:
                    report_type = '健康分析'
                else:
                    report_type = '详细分析'
                
                reports.append({
                    'id': filename.replace('.html', '').replace('.txt', '').replace('.json', ''),
                    'title': filename.replace('_', ' ').replace('.html', '').replace('.txt', '').replace('.json', ''),
                    'filename': filename,
                    'date': time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime)),
                    'size': f'{stat.st_size / 1024:.1f} KB',
                    'type': report_type
                })
        
        return jsonify(reports)
    except Exception as e:
        return jsonify([])

@app.route('/api/test', methods=['POST'])
def test_api():
    """测试API连接"""
    try:
        data = request.get_json()
        return jsonify({
            'status': 'success',
            'message': 'API连接测试成功 (模拟响应)',
            'provider': data.get('api_provider', 'unknown')
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'API测试失败: ' + str(e)
        })

if __name__ == '__main__':
    print("=" * 50)
    print("🤖 机器人日志分析系统")
    print("=" * 50)
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📂 前端目录: frontend")
    
    # 检查前端文件是否存在
    frontend_files = ['frontend/index.html', 'frontend/script.js', 'frontend/styles.css']
    for file_path in frontend_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
    
    print("\n🚀 启动服务器...")
    print("📱 访问地址: http://localhost:8080")
    print("🔗 API文档: http://localhost:8080/api/status")
    print("\n⏹️  按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动服务器
    try:
        app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")