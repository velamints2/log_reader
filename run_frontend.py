#!/usr/bin/env python3
"""
机器人日志分析系统 - 前端界面启动脚本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    print("🔍 检查依赖包...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'openai',
        'python_dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  缺少依赖包: {', '.join(missing_packages)}")
        print("请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_api_config():
    """检查API配置"""
    print("\n🔧 检查API配置...")
    
    # 检查环境变量
    openai_key = os.environ.get('OPENAI_API_KEY')
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY')
    use_deepseek = os.environ.get('USE_DEEPSEEK', 'false').lower() == 'true'
    
    if use_deepseek:
        print("   • API提供商: DeepSeek")
        if deepseek_key:
            print("   • DeepSeek API密钥: 已配置")
        else:
            print("   • DeepSeek API密钥: ❌ 未配置")
    else:
        print("   • API提供商: OpenAI")
        if openai_key:
            print("   • OpenAI API密钥: 已配置")
        else:
            print("   • OpenAI API密钥: ❌ 未配置")
    
    # 检查配置文件
    config_file = Path('config.py')
    if config_file.exists():
        print("   • 配置文件: 存在")
    else:
        print("   • 配置文件: ❌ 不存在")
    
    return True

def start_backend_server():
    """启动后端服务器"""
    print("\n🚀 启动后端服务器...")
    
    # 检查后端文件是否存在
    backend_file = Path('backend/server.py')
    if not backend_file.exists():
        print("❌ 后端服务器文件不存在")
        return None
    
    try:
        # 启动Flask服务器
        process = subprocess.Popen([
            sys.executable, 'backend/server.py'
        ], cwd=os.getcwd())
        
        print("✅ 后端服务器已启动")
        print("   • 地址: http://localhost:5000")
        print("   • API地址: http://localhost:5000/api")
        
        return process
    except Exception as e:
        print(f"❌ 启动后端服务器失败: {e}")
        return None

def open_browser():
    """打开浏览器"""
    print("\n🌐 正在打开浏览器...")
    
    # 等待服务器启动
    time.sleep(2)
    
    try:
        webbrowser.open('http://localhost:5000')
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"⚠️  无法自动打开浏览器: {e}")
        print("请手动访问: http://localhost:5000")

def main():
    """主函数"""
    print("🤖 机器人日志分析系统 - 前端界面")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = Path.cwd()
    print(f"📁 当前目录: {current_dir}")
    
    # 检查是否在项目根目录
    required_files = ['requirements.txt', 'config.py', 'complete_gpt_integration.py']
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        print("请确保在项目根目录运行此脚本")
        return
    
    print("✅ 项目目录检查通过")
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查API配置
    check_api_config()
    
    # 启动后端服务器
    server_process = start_backend_server()
    
    if server_process is None:
        return
    
    # 打开浏览器
    open_browser()
    
    print("\n📋 使用说明:")
    print("   • 前端界面: http://localhost:5000")
    print("   • 系统状态: 查看仪表板区域")
    print("   • 日志分析: 在分析页面选择日志目录")
    print("   • 报告查看: 在报告页面查看历史报告")
    print("   • 系统设置: 在设置页面配置API参数")
    
    print("\n⏹️  按 Ctrl+C 停止服务器")
    
    try:
        # 等待服务器进程
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止服务器...")
        server_process.terminate()
        server_process.wait()
        print("✅ 服务器已停止")

if __name__ == '__main__':
    main()