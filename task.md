Phase 0：项目骨架 & 环境准备

任务 0-1：创建基础目录结构

目标：有一个符合架构文档的最小目录树（还不需要有完整代码）。
步骤：
创建根目录 log_reader/
在其中创建子目录：
backend/
frontend/
logs/
reports/
temp_reports/
在 logs/ 里放一个小的测试日志文件 sample.log（几行文本即可）。
完成标准：
上述目录和文件存在。
测试方法：
ls / 文件管理器中可看到这些目录结构。
任务 0-2：创建 requirements.txt

目标：列出 MVP 后端必需依赖。
步骤：
在根目录创建 requirements.txt，暂时只包含：
Flask
Flask-CORS
requests
完成标准：
requirements.txt 存在且可被 pip install -r requirements.txt 正常执行。
测试方法：
在虚拟环境里运行 pip install -r requirements.txt 没报错。
任务 0-3：创建最小的 config.py

目标：提供统一配置入口（API key、路径等），即便先只用默认值。
步骤：
在根目录创建 config.py，内容类似：
import os

LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "./logs")
REPORTS_DIRECTORY = os.getenv("REPORTS_DIRECTORY", "./reports")
TEMP_REPORTS_DIRECTORY = os.getenv("TEMP_REPORTS_DIRECTORY", "./temp_reports")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_DEEPSEEK = os.getenv("USE_DEEPSEEK", "false").lower() == "true"
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")
完成标准：
文件可以被 import config 正常导入。
测试方法：
在 Python REPL 里 import config; print(config.LOG_DIRECTORY)。
Phase 1：后端 Flask 最小可用 API

任务 1-1：创建 backend/server.py 并初始化 Flask app

目标：有一个最简 Flask 应用能启动。
步骤：
在 backend/server.py 中：
from flask import Flask

app = Flask(__name__)

if __name__ == "__main__":
    app.run(port=8080, debug=True)
完成标准：
python backend/server.py 可以启动一个空服务。
测试方法：
访问 http://localhost:8080/ 返回 404（这是正常的）。
任务 1-2：添加 CORS 支持和 JSON 响应基础

目标：支持跨域 & 返回 JSON。
步骤：
在 server.py 中：
from flask_cors import CORS
from flask import jsonify

app = Flask(__name__)
CORS(app)
完成标准：
服务仍能正常启动。
测试方法：
访问任意存在的端点时，response header 有 Access-Control-Allow-Origin: *（后面再测）。
任务 1-3：实现 GET /api/status 健康检查接口

目标：暴露一个可用的状态检查 API。
步骤：
在 server.py 中添加：
@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "success",
        "message": "Backend is running"
    })
完成标准：
GET /api/status 返回 JSON。
测试方法：
curl http://localhost:8080/api/status，看到 {"status":"success"...}。
Phase 2：后端设置管理接口（/api/settings）

任务 2-1：在 server.py 中添加 settings_storage 内存对象

目标：有一个全局可读写的设置字典。
步骤：
在 server.py 顶部添加：
settings_storage = {}
完成标准：
该变量可在路由中访问。
测试方法：
临时在某个路由中 print(settings_storage)，不报错。
任务 2-2：实现 GET /api/settings 返回当前设置 + 配置状态

目标：前端能看到当前 API 设置情况。
步骤：
在 server.py 中添加：
from config import OPENAI_API_KEY, BASE_URL

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
完成标准：
请求成功返回 JSON，包含 settings 对象。
测试方法：
curl http://localhost:8080/api/settings 并检查字段。
任务 2-3：实现 POST /api/settings 更新内存设置

目标：前端可以修改 API provider / key / base_url。
步骤：
在 server.py 中添加：
from flask import request

@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.get_json() or {}
    for key in ["api_provider", "api_key", "base_url", "model"]:
        if key in data:
            settings_storage[key] = data[key]
    return jsonify({"status": "success", "settings": settings_storage})
完成标准：
POST 后 settings_storage 发生变化。
测试方法：
curl -X POST http://localhost:8080/api/settings -H "Content-Type: application/json" -d '{"api_provider":"openai","api_key":"test","base_url":"https://api.openai.com/v1"}'
再调用 GET /api/settings，看到 api_key_configured 为 true。
Phase 3：核心日志分析调用链（先用简单假实现）

任务 3-1：创建 complete_robot_log_analyzer.py 的最小壳

目标：有一个类可以被 server.py 导入 & 调用（先不实现真实分析逻辑）。
步骤：
在根目录创建 complete_robot_log_analyzer.py：
import os
import json
from config import LOG_DIRECTORY, TEMP_REPORTS_DIRECTORY, REPORTS_DIRECTORY

class CompleteRobotLogAnalyzer:
    def __init__(self, log_directory=None):
        self.log_directory = log_directory or LOG_DIRECTORY

    def generate_integrated_report(self):
        # 简单假数据，后续再替换为真分析
        return {
            "summary": "Mock analysis summary",
            "log_directory": self.log_directory,
            "task_count": 0,
            "error_count": 0
        }

    def save_reports(self, temp_output_dir=None):
        temp_output_dir = temp_output_dir or TEMP_REPORTS_DIRECTORY
        os.makedirs(temp_output_dir, exist_ok=True)
        os.makedirs(REPORTS_DIRECTORY, exist_ok=True)

        report_data = self.generate_integrated_report()
        report_id = "report_mock_1"
        json_path = os.path.join(temp_output_dir, f"{report_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        # 同时在 reports/ 写入一个简单 txt
        txt_path = os.path.join(REPORTS_DIRECTORY, f"{report_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("Mock report\n")
        return {
            "report_id": report_id,
            "json_path": json_path,
            "txt_path": txt_path
        }
展开
完成标准：
from complete_robot_log_analyzer import CompleteRobotLogAnalyzer 不报错。
测试方法：
在 REPL 中实例化并调用 save_reports()，检查 temp_reports/ 和 reports/ 中生成了文件。
任务 3-2：实现 POST /api/analyze 调用分析器并返回结果

目标：形成「前端 → /api/analyze → 分析器 → 生成报告 → 返回」的最小闭环。
步骤：
在 backend/server.py 中：
from complete_robot_log_analyzer import CompleteRobotLogAnalyzer
from config import LOG_DIRECTORY, TEMP_REPORTS_DIRECTORY

@app.route("/api/analyze", methods=["POST"])
def analyze_logs():
    data = request.get_json() or {}
    log_directory = data.get("log_directory", LOG_DIRECTORY)
    enable_ai = bool(data.get("enable_ai", False))
    report_type = data.get("report_type", "basic")

    analyzer = CompleteRobotLogAnalyzer(log_directory)
    result = analyzer.save_reports(TEMP_REPORTS_DIRECTORY)

    # MVP 先忽略 enable_ai & report_type，只返回基本信息
    return jsonify({
        "status": "success",
        "report_id": result["report_id"],
        "paths": {
            "json": result["json_path"],
            "txt": result["txt_path"]
        }
    })
完成标准：
请求分析后会在 temp_reports/ 与 reports/ 生成文件。
测试方法：
curl -X POST http://localhost:8080/api/analyze -H "Content-Type: application/json" -d '{"log_directory":"./logs","enable_ai":false,"report_type":"basic"}'
检查返回 JSON 中的 report_id 和对应文件是否存在。
Phase 4：报告列表接口

任务 4-1：实现 GET /api/reports 列出 reports/ 中的文件

目标：前端可以获取当前已有报告列表。
步骤：
在 server.py 中：
import os
from config import REPORTS_DIRECTORY

@app.route("/api/reports", methods=["GET"])
def list_reports():
    os.makedirs(REPORTS_DIRECTORY, exist_ok=True)
    items = []
    for name in os.listdir(REPORTS_DIRECTORY):
        path = os.path.join(REPORTS_DIRECTORY, name)
        if os.path.isfile(path):
            size = os.path.getsize(path)
            items.append({
                "id": os.path.splitext(name)[0],
                "name": name,
                "type": "text",
                "size": f"{size} B"
            })
    return jsonify(items)
完成标准：
API 返回报告列表数组。
测试方法：
先调用一次 /api/analyze 生成报告，再访问 GET /api/reports，应至少有1条记录。
Phase 5：前端静态页面骨架

任务 5-1：创建 frontend/index.html 基本结构

目标：有一个简单 HTML 页面，包含主区域和一个按钮。
步骤：
内容示例：
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>机器人日志分析系统</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <h1>机器人日志分析系统 MVP</h1>
  <button id="test-status-btn">测试后端状态</button>
  <pre id="status-output"></pre>

  <script src="script.js"></script>
</body>
</html>
完成标准：
打开 HTML 时可以看到标题和按钮。
测试方法：
通过 Flask（下一步）或直接本地打开检查。
任务 5-2：创建 frontend/styles.css 基本样式

目标：让页面不至于太难看（简单即可）。
步骤：
内容示例：
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 16px;
}
pre {
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
}
完成标准：
页面样式生效。
测试方法：
浏览器查看是否字体和背景生效。
任务 5-3：创建 frontend/script.js 并实现 /api/status 调用

目标：前端可以点击按钮测试后端状态。
步骤：
在 script.js：
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('test-status-btn');
  const output = document.getElementById('status-output');

  btn.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      output.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      output.textContent = 'Error: ' + err.message;
    }
  });
});
完成标准：
点击按钮，可以看到后端返回的信息。
测试方法：
启动 Flask（支持静态文件，下一任务），在浏览器测试按钮。
任务 5-4：在 Flask 中提供前端静态文件服务

目标：通过 http://localhost:8080/ 直接访问前端页面。
步骤：
在 server.py 中：
from flask import send_from_directory
import os

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.route("/", methods=["GET"])
def serve_index():
  return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>", methods=["GET"])
def serve_static(path):
  return send_from_directory(FRONTEND_DIR, path)
完成标准：
访问 http://localhost:8080/ 能看到页面，且脚本加载正常。
测试方法：
手动访问和点击 “测试后端状态”。
Phase 6：前端日志分析触发 & 结果展示

任务 6-1：在前端添加「开始分析」表单

目标：用户能在页面输入参数并提交 /api/analyze。
步骤：
修改 index.html：
<section>
  <h2>启动日志分析</h2>
  <label>日志目录：<input id="log-dir-input" value="./logs"></label>
  <label>
    <input type="checkbox" id="enable-ai-checkbox"> 启用AI增强
  </label>
  <button id="start-analysis-btn">开始分析</button>
  <pre id="analysis-output"></pre>
</section>
完成标准：
页面上有输入框和按钮。
测试方法：
浏览器检查 UI。
任务 6-2：在 script.js 中实现 /api/analyze 调用

目标：点击“开始分析”，调用后端并显示结果。
步骤：
在 DOMContentLoaded 回调中添加逻辑：
const logDirInput = document.getElementById('log-dir-input');
const enableAiCheckbox = document.getElementById('enable-ai-checkbox');
const startBtn = document.getElementById('start-analysis-btn');
const analysisOutput = document.getElementById('analysis-output');

startBtn.addEventListener('click', async () => {
  analysisOutput.textContent = '分析中...';
  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        log_directory: logDirInput.value,
        enable_ai: enableAiCheckbox.checked,
        report_type: 'basic'
      })
    });
    const data = await res.json();
    analysisOutput.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    analysisOutput.textContent = 'Error: ' + err.message;
  }
});
完成标准：
点击按钮后，能看到后端返回的 report_id。
测试方法：
完整跑一遍：打开页面 → 填/不填参数 → 开始分析 → 检查 temp_reports/、reports/ 是否有文件。
任务 6-3：增加「报告列表」展示区

目标：前端能调用 /api/reports，展示已有报告。
步骤：
修改 index.html：
<section>
  <h2>已有报告列表</h2>
  <button id="refresh-reports-btn">刷新列表</button>
  <ul id="reports-list"></ul>
</section>
在 script.js 中：
const refreshReportsBtn = document.getElementById('refresh-reports-btn');
const reportsList = document.getElementById('reports-list');

refreshReportsBtn.addEventListener('click', async () => {
  reportsList.innerHTML = '<li>加载中...</li>';
  try {
    const res = await fetch('/api/reports');
    const data = await res.json();
    reportsList.innerHTML = '';
    data.forEach(item => {
      const li = document.createElement('li');
      li.textContent = `${item.name} (${item.size})`;
      reportsList.appendChild(li);
    });
  } catch (err) {
    reportsList.innerHTML = `<li>Error: ${err.message}</li>`;
  }
});
完成标准：
点击“刷新列表”可以看到报告名称列表。
测试方法：
先触发一次分析生成报告，再刷新列表，确认能看到新报告。
Phase 7：设置管理前端（localStorage）

任务 7-1：在前端添加 API 设置表单

目标：用户可以输入 API Provider、Key、Base URL。
步骤：
在 index.html 添加：
<section>
  <h2>API 设置</h2>
  <label>Provider:
    <select id="api-provider">
      <option value="openai">OpenAI</option>
      <option value="deepseek">DeepSeek</option>
    </select>
  </label>
  <label>API Key:
    <input id="api-key" type="password">
  </label>
  <label>Base URL:
    <input id="base-url" value="https://api.openai.com/v1">
  </label>
  <button id="save-settings-btn">保存设置</button>
  <pre id="settings-output"></pre>
</section>
完成标准：
表单元素和按钮显示正常。
测试方法：
浏览器查看 UI。
任务 7-2：在 script.js 中实现设置保存到 localStorage

目标：前端保存用户的设置。
步骤：
在 DOMContentLoaded 中添加：
const apiProvider = document.getElementById('api-provider');
const apiKey = document.getElementById('api-key');
const baseUrl = document.getElementById('base-url');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const settingsOutput = document.getElementById('settings-output');

// 初始化时从 localStorage 读取
const savedProvider = localStorage.getItem('api_provider');
const savedKey = localStorage.getItem('api_key');
const savedBaseUrl = localStorage.getItem('base_url');

if (savedProvider) apiProvider.value = savedProvider;
if (savedKey) apiKey.value = savedKey;
if (savedBaseUrl) baseUrl.value = savedBaseUrl;

saveSettingsBtn.addEventListener('click', async () => {
  const payload = {
    api_provider: apiProvider.value,
    api_key: apiKey.value,
    base_url: baseUrl.value
  };
  // 先存 localStorage
  localStorage.setItem('api_provider', payload.api_provider);
  localStorage.setItem('api_key', payload.api_key);
  localStorage.setItem('base_url', payload.base_url);

  // 再同步到后端
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    settingsOutput.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    settingsOutput.textContent = 'Error: ' + err.message;
  }
});
展开
完成标准：
刷新页面后，表单仍能显示之前保存的值。
测试方法：
输入数据 → 保存 → 刷新页面 → 检查表单是否保留 → 查看 network 中 /api/settings 请求是否成功。
