from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
from flask import send_from_directory, send_file
import sys
import os
import json
from datetime import datetime, timedelta

# 添加根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置文件
from config import OPENAI_API_KEY, BASE_URL, LOG_DIRECTORY, TEMP_REPORTS_DIRECTORY
from config import API_KEY, API_BASE_URL, API_MODEL, MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT
import requests
import time
import re

# 导入分析器
from complete_robot_log_analyzer import CompleteRobotLogAnalyzer
from config import REPORTS_DIRECTORY

# 导入智能日志诊断Agent
from log_agent import LogDiagnosticAgent

# 全局设置存储对象
settings_storage = {}

# 前端静态文件目录
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app = Flask(__name__)
CORS(app)

@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "success",
        "message": "Backend is running"
    })

@app.route("/api/test", methods=["GET"])
def test_api():
    """测试API连接"""
    return jsonify({
        "status": "success",
        "message": "API连接正常",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/api/logs", methods=["GET"])
def get_logs():
    """获取日志文件列表"""
    log_directory = LOG_DIRECTORY
    if not os.path.exists(log_directory):
        return jsonify({"error": "日志目录不存在"}), 404
    
    log_files = []
    for filename in os.listdir(log_directory):
        file_path = os.path.join(log_directory, filename)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            log_files.append({
                "name": filename,
                "size": size,
                "type": "log"
            })
    
    return jsonify({
        "status": "success",
        "log_files": log_files,
        "total_count": len(log_files)
    })

@app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify({
        "status": "success",
        "settings": {
            "api_provider": settings_storage.get("api_provider", "openai"),
            "api_key_configured": bool(settings_storage.get("api_key") or OPENAI_API_KEY),
            "base_url": settings_storage.get("base_url", BASE_URL)
        }
    })

@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.get_json() or {}
    for key in ["api_provider", "api_key", "base_url", "model"]:
        if key in data:
            settings_storage[key] = data[key]
    return jsonify({"status": "success", "settings": settings_storage})

@app.route("/api/analyze", methods=["POST"])
def analyze_logs():
    data = request.get_json() or {}
    log_directory = data.get("log_directory", LOG_DIRECTORY)
    enable_ai = bool(data.get("enable_ai", True))  # 默认启用AI
    report_type = data.get("report_type", "enhanced")  # 默认为增强分析
    
    # 确保日志目录存在
    if not os.path.exists(log_directory):
        return jsonify({
            "status": "error",
            "message": f"日志目录不存在: {log_directory}"
        }), 400
    
    # 根据报告类型选择分析器
    if report_type == "basic":
        # 使用简单分析器
        return analyze_with_basic_analyzer(data)
    else:
        # 使用综合分析器进行深度分析
        return analyze_with_comprehensive_analyzer(data)

def analyze_with_basic_analyzer(data):
    """基础分析"""
    log_directory = data.get("log_directory", LOG_DIRECTORY)
    analyzer = CompleteRobotLogAnalyzer(log_directory)
    result = analyzer.save_reports(TEMP_REPORTS_DIRECTORY)
    
    return jsonify({
        "status": "success",
        "report_id": result["report_id"],
        "paths": {
            "json": result["json_path"],
            "txt": result["txt_path"]
        },
        "analysis_type": "basic",
        "message": "基础分析完成"
    })

def analyze_with_comprehensive_analyzer(data):
    """综合分析"""
    from comprehensive_robot_analyzer import ComprehensiveRobotAnalyzer
    from complaint_analyzer import ComplaintAnalyzer
    from historical_trace_analyzer import HistoricalTraceAnalyzer
    from enhanced_detailed_report_generator import EnhancedDetailedReportGenerator
    from deepseek_enhanced_report_generator import DeepSeekEnhancedReportGenerator
    
    log_directory = data.get("log_directory", LOG_DIRECTORY)
    complaint_time_str = data.get("complaint_time")
    output_dir = TEMP_REPORTS_DIRECTORY
    
    try:
        # 生成唯一的报告ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_prefix = f"comprehensive_report_{timestamp}"
        
        # 1. 综合日志分析
        print("🔍 开始综合日志分析...")
        comprehensive_analyzer = ComprehensiveRobotAnalyzer(log_directory)
        comprehensive_analyzer.analyze_all_logs()
        
        # 生成综合报告
        comprehensive_report = comprehensive_analyzer.generate_comprehensive_report()
        comprehensive_report_path = os.path.join(output_dir, f"{report_prefix}.json")
        comprehensive_analyzer.save_report(comprehensive_report, comprehensive_report_path)
        
        # 2. 投诉分析（如果有投诉时间）
        complaint_result = None
        if complaint_time_str:
            try:
                complaint_time = datetime.strptime(complaint_time_str, "%Y-%m-%d %H:%M:%S")
                print("🔍 开始投诉分析...")
                complaint_analyzer = ComplaintAnalyzer(log_directory)
                complaint_analyzer.analyze_all_logs()
                
                complaint_report = complaint_analyzer.generate_complaint_report(
                    complaint_time, 
                    os.path.join(output_dir, f"complaint_report_{timestamp}.json")
                )
                complaint_result = complaint_report
            except Exception as e:
                print(f"⚠️ 投诉分析失败: {e}")
        
        # 3. 历史追溯分析
        print("🔍 开始历史追溯分析...")
        historical_analyzer = HistoricalTraceAnalyzer(log_directory)
        historical_analyzer.analyze_all_logs()
        historical_report_path = os.path.join(output_dir, f"historical_trace_report_{timestamp}.json")
        historical_report = historical_analyzer.generate_trace_report(output_file=historical_report_path)
        
        # 4. 集成所有分析结果
        print("🔄 集成分析结果...")
        integrated_report = {
            "report_metadata": {
                "report_id": report_prefix,
                "generated_at": datetime.now().isoformat(),
                "log_directory": log_directory,
                "analysis_type": "comprehensive",
                "enable_ai": True
            },
            "comprehensive_analysis": comprehensive_report,
            "historical_trace": historical_report,
            "complaint_analysis": complaint_result,
            "integrated_summary": {
                "total_log_files": comprehensive_report.get("analysis_summary", {}).get("total_log_files", 0),
                "total_anomalies": comprehensive_report.get("analysis_summary", {}).get("total_anomalies", 0),
                "total_task_segments": comprehensive_report.get("analysis_summary", {}).get("total_task_segments", 0),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        # 保存集成报告
        integrated_path = os.path.join(output_dir, f"integrated_report_{timestamp}.json")
        with open(integrated_path, 'w', encoding='utf-8') as f:
            json.dump(integrated_report, f, ensure_ascii=False, indent=2, default=str)
        
        # 5. 生成增强HTML报告
        print("📊 生成可视化报告...")
        html_report_path = None
        deepseek_html_report_path = None
        
        try:
            # 获取报告类型
            report_type = data.get('report_type', 'enhanced')
            
            # 生成标准增强报告
            if report_type in ['enhanced', 'comprehensive']:
                html_generator = EnhancedDetailedReportGenerator(integrated_path)
                html_report_path = os.path.join(output_dir, f"enhanced_detailed_report_{timestamp}.html")
                html_generator.generate_detailed_report(html_report_path)
                
                # 同时保存到reports目录供下载
                reports_html_path = os.path.join(REPORTS_DIRECTORY, f"enhanced_detailed_report_{timestamp}.html")
                html_generator.generate_detailed_report(reports_html_path)
            
            # 生成DeepSeek增强版报告
            if report_type in ['deepseek_enhanced', 'comprehensive']:
                print("🤖 生成DeepSeek AI增强报告...")
                deepseek_generator = DeepSeekEnhancedReportGenerator(integrated_path)
                deepseek_html_report_path = os.path.join(output_dir, f"deepseek_enhanced_report_{timestamp}.html")
                deepseek_generator.generate_detailed_report(deepseek_html_report_path)
                
                # 同时保存到reports目录供下载
                deepseek_reports_path = os.path.join(REPORTS_DIRECTORY, f"deepseek_enhanced_report_{timestamp}.html")
                deepseek_generator.generate_detailed_report(deepseek_reports_path)
            
        except Exception as e:
            print(f"⚠️ HTML报告生成失败: {e}")
        
        # 构建结果响应
        result_paths = {
            "json": integrated_path,
            "html": html_report_path,
            "deepseek_html": deepseek_html_report_path,
            "comprehensive_json": comprehensive_report_path,
            "historical_json": historical_report_path
        }
        
        if complaint_result:
            result_paths["complaint_json"] = os.path.join(output_dir, f"complaint_report_{timestamp}.json")
        
        return jsonify({
            "status": "success",
            "report_id": report_prefix,
            "analysis_type": "comprehensive",
            "message": "综合分析完成",
            "summary": integrated_report["integrated_summary"],
            "paths": result_paths,
            "analysis_details": {
                "log_files_analyzed": comprehensive_report.get("analysis_summary", {}).get("total_log_files", 0),
                "anomalies_detected": comprehensive_report.get("analysis_summary", {}).get("total_anomalies", 0),
                "task_segments_found": comprehensive_report.get("analysis_summary", {}).get("total_task_segments", 0),
                "ai_enhanced": True
            }
        })
        
    except Exception as e:
        print(f"❌ 综合分析失败: {e}")
        return jsonify({
            "status": "error",
            "message": f"分析失败: {str(e)}"
        }), 500

@app.route("/api/reports", methods=["GET"])
def list_reports():
    """列出所有报告文件，包括reports和temp_reports目录"""
    os.makedirs(REPORTS_DIRECTORY, exist_ok=True)
    os.makedirs(TEMP_REPORTS_DIRECTORY, exist_ok=True)
    
    items = []
    
    # 扫描reports目录
    for name in os.listdir(REPORTS_DIRECTORY):
        path = os.path.join(REPORTS_DIRECTORY, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            file_ext = os.path.splitext(name)[1].lower()
            
            # 根据文件扩展名确定类型
            if file_ext == '.html':
                file_type = "html"
            elif file_ext == '.json':
                file_type = "json"
            elif file_ext == '.txt':
                file_type = "text"
            else:
                file_type = "other"
            
            items.append({
                "id": os.path.splitext(name)[0],
                "name": name,
                "type": file_type,
                "size": f"{size} B",
                "path": f"./reports/{name}"
            })
    
    # 扫描temp_reports目录
    for name in os.listdir(TEMP_REPORTS_DIRECTORY):
        path = os.path.join(TEMP_REPORTS_DIRECTORY, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            file_ext = os.path.splitext(name)[1].lower()
            
            # 根据文件扩展名确定类型
            if file_ext == '.html':
                file_type = "html"
            elif file_ext == '.json':
                file_type = "json"
            elif file_ext == '.txt':
                file_type = "text"
            else:
                file_type = "other"
            
            items.append({
                "id": os.path.splitext(name)[0],
                "name": name,
                "type": file_type,
                "size": f"{size} B",
                "path": f"./temp_reports/{name}"
            })
    
    # 按文件名排序，最新的在前面
    items.sort(key=lambda x: x["name"], reverse=True)
    
    return jsonify(items)

@app.route("/api/report", methods=["GET"])
def serve_report():
    """提供报告文件服务"""
    path = request.args.get("path")
    if not path:
        return jsonify({"error": "缺少路径参数"}), 400
    
    # 解码路径
    import urllib.parse
    decoded_path = urllib.parse.unquote(path)
    
    # 处理相对路径，转换为绝对路径
    if decoded_path.startswith('./'):
        # 相对于项目根目录的路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        decoded_path = os.path.join(project_root, decoded_path[2:])
    elif not os.path.isabs(decoded_path):
        # 其他相对路径，也相对于项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        decoded_path = os.path.join(project_root, decoded_path)
    
    # 安全检查：确保路径在允许的目录内
    allowed_dirs = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp_reports")
    ]
    
    if not any(decoded_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
        return jsonify({"error": "访问路径不被允许"}), 403
    
    # 检查文件是否存在
    if not os.path.exists(decoded_path):
        return jsonify({"error": f"报告文件不存在: {decoded_path}"}), 404
    
    # 根据文件扩展名返回不同的内容类型
    file_extension = os.path.splitext(decoded_path)[1].lower()
    
    if file_extension == '.html':
        # 返回HTML文件
        return send_file(decoded_path)
    elif file_extension == '.json':
        # 返回JSON文件内容
        try:
            with open(decoded_path, 'r', encoding='utf-8') as f:
                json_content = json.load(f)
            return jsonify(json_content)
        except Exception as e:
            return jsonify({"error": f"读取JSON文件失败: {str(e)}"}), 500
    else:
        # 其他文件类型，尝试作为普通文件发送
        return send_file(decoded_path)


def _parse_timestamp_from_line(line: str):
    """尝试从一行日志中解析常见的时间戳格式，返回 datetime 或 None。"""
    # 常见格式：
    # 1. 2025-10-12 00:00:00:004 (毫秒用冒号分隔，系统日志常见格式)
    # 2. 2025-11-30 14:30:00 或 2025-11-30T14:30:00
    # 3. 2025/11/30 14:30:00
    # 4. [2025-11-30 14:30:00]
    patterns = [
        # 毫秒用冒号分隔: 2025-10-12 00:00:00:004
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):\d+", '%Y-%m-%d %H:%M:%S'),
        # 标准格式: 2025-11-30 14:30:00.123 或 2025-11-30 14:30:00
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", '%Y-%m-%d %H:%M:%S'),
        # ISO格式: 2025-11-30T14:30:00
        (r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", None),  # 使用 fromisoformat
        # 带方括号: [2025-11-30 14:30:00]
        (r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", '%Y-%m-%d %H:%M:%S'),
        # 斜杠格式: 2025/11/30 14:30:00
        (r"(\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})", '%Y/%m/%d %H:%M:%S'),
    ]
    for pattern, fmt in patterns:
        m = re.search(pattern, line)
        if m:
            s = m.group(1)
            try:
                if fmt is None:
                    return datetime.fromisoformat(s)
                return datetime.strptime(s, fmt)
            except Exception:
                continue
    return None


def extract_logs_around_time(issue_time_str: str, window_min: int = 10, max_lines: int = 1000):
    """从 `LOG_DIRECTORY` 中提取以 issue_time 为中心、前后 window_min 分钟的日志行。
    返回 (joined_lines, error_message_or_None)
    """
    try:
        issue_time = datetime.strptime(issue_time_str, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return "", f"错误的时间格式，需为 YYYY-MM-DD HH:MM:SS -> {e}"

    start_time = issue_time - timedelta(minutes=window_min)
    end_time = issue_time + timedelta(minutes=window_min)

    matched = []
    if not os.path.exists(LOG_DIRECTORY):
        return "", f"日志目录不存在: {LOG_DIRECTORY}"

    # 遍历日志目录，尝试解析每一行的时间戳
    for root, _, files in os.walk(LOG_DIRECTORY):
        for name in files:
            path = os.path.join(root, name)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                    for line in fh:
                        ts = _parse_timestamp_from_line(line)
                        if ts and start_time <= ts <= end_time:
                            matched.append(f"{name} {ts.isoformat()} {line.strip()}")
                            if len(matched) >= max_lines:
                                break
            except Exception as e:
                # 忽略单个文件读取错误
                print(f"⚠️ 读取日志文件失败: {path} -> {e}")
        if len(matched) >= max_lines:
            break

    # 回退策略：如果没有解析到时间戳，按日期匹配行文本
    if not matched:
        date_only = issue_time_str.split(' ')[0]
        for root, _, files in os.walk(LOG_DIRECTORY):
            for name in files:
                path = os.path.join(root, name)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                        for line in fh:
                            if date_only in line:
                                matched.append(f"{name} {line.strip()}")
                                if len(matched) >= max_lines:
                                    break
                except Exception:
                    continue
            if len(matched) >= max_lines:
                break

    return ("\n".join(matched), None)


def _build_prompt(description: str, issue_time: str, logs: str):
    return (
        "你是系统日志分析专家。\n"
        f"问题时间: {issue_time}\n"
        f"用户描述: {description}\n"
        "请阅读下面的日志片段，分析可能的根因（root cause），标注关键日志行，并给出可执行的排查和修复建议。\n"
        "请用中文结构化输出，包含：summary（简要结论）、root_cause_hypothesis（根因假设）、key_log_lines（关键日志行与解释）、suggested_actions（建议操作）。\n\n"
        "相关日志开始:\n" + (logs or "（无找到相关日志）") + "\n\n请开始分析："
    )


def call_ai_model(prompt: str, retries: int = 3, backoff: float = 2.0):
    """调用外部大模型 API（OpenAI/兼容 API）。
    支持重试与指数退避，返回 dict（包含 raw 文本或 error）。
    """
    if not API_KEY:
        return {"error": "未配置 API_KEY（请在环境变量或 config.py 中设置）"}

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": API_MODEL or "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS or 1000,
        "temperature": TEMPERATURE or 0.7
    }

    url = API_BASE_URL.rstrip('/') + '/chat/completions'
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=REQUEST_TIMEOUT or 30)
            resp.raise_for_status()
            data = resp.json()
            # 尝试解析结果
            choice = (data.get('choices') or [None])[0]
            if not choice:
                return {"error": "模型返回格式异常", "raw": data}
            message = choice.get('message') or {}
            content = message.get('content') or choice.get('text') or ''
            return {"raw": content, "meta": data, "attempt": attempt}
        except requests.exceptions.RequestException as e:
            last_err = str(e)
            print(f"⚠️ 调用AI失败 (attempt {attempt}/{retries}): {last_err}")
            if attempt < retries:
                sleep_time = backoff * (2 ** (attempt - 1))
                print(f"   -> 重试等待 {sleep_time} 秒...")
                time.sleep(sleep_time)
                continue
            else:
                return {"error": last_err}
        except Exception as e:
            return {"error": str(e)}


@app.route('/api/diagnose', methods=['POST'])
def diagnose_issue():
    """根据用户给定的时间/描述，定位日志片段并调用大模型返回诊断建议。"""
    data = request.get_json() or {}
    issue_time = data.get('issue_time')
    description = data.get('description', '')
    window = int(data.get('window', 10))

    if not issue_time:
        return jsonify({"status": "error", "message": "缺少参数 issue_time，格式: YYYY-MM-DD HH:MM:SS"}), 400

    logs, err = extract_logs_around_time(issue_time, window)
    if err:
        return jsonify({"status": "error", "message": err}), 400

    prompt = _build_prompt(description, issue_time, logs)
    ai_result = call_ai_model(prompt)

    return jsonify({
        "status": "success",
        "issue_time": issue_time,
        "window_minutes": window,
        "logs_found": bool(logs),
        "logs_preview": logs[:4000],
        "ai_analysis": ai_result
    })


# ==================== 智能Agent诊断 ====================

# 全局Agent实例（懒加载）
_log_agent = None

def get_log_agent():
    """获取或创建LogDiagnosticAgent实例"""
    global _log_agent
    if _log_agent is None:
        _log_agent = LogDiagnosticAgent(LOG_DIRECTORY)
    return _log_agent


@app.route('/api/agent/diagnose', methods=['POST'])
def agent_diagnose():
    """
    智能Agent诊断API
    
    Agent会根据问题描述智能选择相关日志文件进行分析，
    而不是盲目读取所有日志。
    
    请求参数:
    - description: 问题描述（必需）
    - issue_time: 问题发生时间（可选，格式: YYYY-MM-DD HH:MM:SS）
    - window: 时间窗口（分钟，默认10）
    - max_lines_per_file: 每个日志文件最大读取行数（默认500）
    
    返回:
    - reasoning: Agent的思考过程
    - selected_logs: 选择的日志文件及原因
    - log_contents: 提取的日志内容摘要
    - ai_analysis: AI分析结果
    """
    data = request.get_json() or {}
    description = data.get('description', '').strip()
    issue_time = data.get('issue_time', '')
    window = int(data.get('window', 10))
    max_lines = int(data.get('max_lines_per_file', 500))
    
    if not description:
        return jsonify({
            "status": "error",
            "message": "缺少参数 description（问题描述）"
        }), 400
    
    try:
        agent = get_log_agent()
        result = agent.diagnose(
            problem_description=description,
            issue_time=issue_time if issue_time else None,
            window_minutes=window
        )
        
        return jsonify({
            "status": "success",
            **result
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Agent诊断失败: {str(e)}"
        }), 500


@app.route('/api/agent/logs-info', methods=['GET'])
def agent_logs_info():
    """
    获取Agent的日志知识库信息
    
    返回Agent了解的所有日志文件类型及其用途说明
    """
    try:
        agent = get_log_agent()
        knowledge = agent.get_log_knowledge()
        
        return jsonify({
            "status": "success",
            "log_types_count": len(knowledge),
            "knowledge_base": knowledge
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取日志知识库失败: {str(e)}"
        }), 500


@app.route('/api/agent/available-logs', methods=['GET'])
def agent_available_logs():
    """
    获取当前日志目录中实际存在的日志文件
    
    返回每个日志文件的名称、大小、类型说明
    """
    try:
        agent = get_log_agent()
        available = agent.list_available_logs()
        
        return jsonify({
            "status": "success",
            "logs_count": len(available),
            "logs": available
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"获取可用日志列表失败: {str(e)}"
        }), 500


# 前端静态文件服务路由
@app.route("/", methods=["GET"])
def serve_index():
    """服务前端主页"""
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>", methods=["GET"])
def serve_static_files(filename):
    """服务静态文件（CSS、JS等）"""
    return send_from_directory(FRONTEND_DIR, filename)

if __name__ == "__main__":
    app.run(port=8080, debug=False, threaded=False)