# 机器人日志诊断 API 文档

## 概述

本文档介绍机器人日志分析系统的诊断 API，用于根据特定问题时间和描述进行智能日志分析和根因诊断。

---

## API 端点

### 1. 特定时间问题诊断

#### 请求信息

**URL:** `/api/diagnose`  
**方法:** `POST`  
**Content-Type:** `application/json`

#### 请求参数

| 参数 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `issue_time` | string | ✅ 是 | 问题发生时间，格式 `YYYY-MM-DD HH:MM:SS` | `"2025-10-12 01:01:31"` |
| `description` | string | ❌ 否 | 问题描述（可选，帮助AI更精准分析） | `"系统突然重启"` |
| `window` | integer | ❌ 否 | 时间窗口，单位分钟（默认 10） | `15` |

#### 响应格式

**成功响应 (200):**

```json
{
  "status": "success",
  "issue_time": "2025-10-12 01:01:31",
  "window_minutes": 10,
  "logs_found": true,
  "logs_preview": "...(日志片段预览，前4000字符)...",
  "ai_analysis": {
    "raw": "### **分析报告**\n...(结构化诊断报告)...",
    "meta": {
      "model": "deepseek-chat",
      "usage": {
        "total_tokens": 33700,
        "completion_tokens": 1282
      }
    },
    "attempt": 1
  }
}
```

**错误响应:**

```json
{
  "status": "error",
  "message": "错误说明"
}
```

#### 错误代码

| HTTP 状态 | 说明 |
|----------|------|
| 200 | 诊断成功 |
| 400 | 参数错误（缺少 issue_time 或格式不正确） |
| 500 | 服务器错误（日志提取或AI调用失败） |

---

## 使用示例

### 示例 1：基础诊断（最小参数）

```bash
curl -X POST http://127.0.0.1:8080/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "issue_time": "2025-10-12 01:01:31"
  }'
```

### 示例 2：详细诊断（带问题描述和时间窗口）

```bash
curl -X POST http://127.0.0.1:8080/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "issue_time": "2025-10-12 01:01:31",
    "description": "系统在整点时间突然重启，请分析原因",
    "window": 15
  }'
```

### 示例 3：Python 调用

```python
import requests
import json

url = "http://127.0.0.1:8080/api/diagnose"
payload = {
    "issue_time": "2025-10-12 01:01:31",
    "description": "系统定位模块工作异常",
    "window": 20
}

response = requests.post(url, json=payload)
result = response.json()

if result["status"] == "success":
    print("诊断结果:")
    print(result["ai_analysis"]["raw"])
else:
    print(f"诊断失败: {result['message']}")
```

### 示例 4：JavaScript 调用（前端）

```javascript
async function diagnoseIssue(issueTime, description) {
  const response = await fetch("/api/diagnose", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      issue_time: issueTime,
      description: description,
      window: 10
    })
  });

  const result = await response.json();
  
  if (result.status === "success") {
    console.log("诊断报告:");
    console.log(result.ai_analysis.raw);
  } else {
    console.error("诊断失败:", result.message);
  }
}

// 调用
diagnoseIssue("2025-10-12 01:01:31", "系统重启问题");
```

---

## 诊断工作流程

```
用户输入时间 + 问题描述
        ↓
时间戳验证 (YYYY-MM-DD HH:MM:SS)
        ↓
提取时间窗口内日志 (默认前后各 window 分钟)
        ↓
构建诊断提示词 (Prompt)
        ↓
调用 DeepSeek / OpenAI API
        ↓
返回结构化诊断报告
```

### 诊断报告包含内容

1. **Summary (简要结论)** - 问题的快速定性和初步判断
2. **Root Cause Hypothesis (根因假设)** - 基于日志的深层原因分析
3. **Key Log Lines (关键日志行)** - 标注重要日志并解释其含义
4. **Suggested Actions (建议操作)** - 后续排查和修复建议

---

## 配置说明

### 后端配置文件 (`config.py`)

```python
# API 超时时间（秒）
REQUEST_TIMEOUT = 120

# AI 最大生成 token 数
MAX_TOKENS = 2000

# 使用的 AI 服务
USE_DEEPSEEK = True  # True: DeepSeek, False: OpenAI
DEEPSEEK_API_KEY = "your-deepseek-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
```

### 重试机制

当 AI 调用超时或失败时，系统会自动重试：
- **最大重试次数**: 3 次
- **退避策略**: 指数退避 (2s → 4s → 8s)
- **总超时上限**: 120 秒

---

## 支持的日志时间格式

系统自动识别以下时间戳格式：

| 格式 | 示例 |
|------|------|
| 毫秒冒号分隔 | `2025-10-12 01:01:31:726` |
| 标准格式 | `2025-10-12 01:01:31` |
| ISO 格式 | `2025-10-12T01:01:31` |
| 方括号格式 | `[2025-10-12 01:01:31]` |
| 斜杠格式 | `2025/10/12 01:01:31` |

---

## 日志目录结构

系统会扫描 `./logs/` 目录下的所有日志文件：

```
logs/
├── ikitbot_driver.log
├── navigation_move_base.log
├── 00_00_04_mqtt.txt
├── 00_00_04_can.txt
├── 01_01_31_action.txt
├── 01_00_58_grpc.log
└── ... (其他日志文件)
```

---

## 常见问题

### Q1: 诊断结果为什么显示 "当前无法连接AI分析服务"？

**A:** 可能原因：
1. API 密钥未配置或无效
2. 网络连接问题
3. DeepSeek/OpenAI 服务暂时不可用

**解决方案：**
- 检查 `config.py` 中的 `DEEPSEEK_API_KEY` 或 `OPENAI_API_KEY`
- 查看后端日志中的错误信息
- 检查网络连接和防火墙设置

### Q2: 提取的日志为什么是空的？

**A:** 可能原因：
1. 指定的时间在日志中不存在
2. 日志文件时间格式不标准
3. 时间窗口 (window) 设置过小

**解决方案：**
- 扩大时间窗口（增加 `window` 参数）
- 检查日志目录中是否有时间段对应的日志
- 查看日志文件的时间戳格式

### Q3: 诊断分析的准确度如何？

**A:** 准确度取决于：
1. 日志的完整性和详细程度
2. 问题描述的清晰程度
3. 时间窗口的合理性

**建议：**
- 提供尽可能详细的问题描述
- 根据问题类型调整时间窗口
- 检查是否有其他相关日志文件

### Q4: 支持哪些 AI 服务？

**A:** 目前支持：
- **DeepSeek** (推荐，默认)
- **OpenAI** (GPT-3.5/GPT-4)

通过修改 `config.py` 中的 `USE_DEEPSEEK` 进行切换。

---

## 性能指标

| 指标 | 典型值 |
|------|--------|
| 日志提取时间 | < 1s |
| AI 分析时间 | 3-10s |
| 总响应时间 | 3-15s |
| 最大重试次数 | 3 次 |
| 超时上限 | 120s |

---

## 相关接口

### 获取日志列表

```
GET /api/logs
```

获取所有可用日志文件列表。

### 获取分析报告列表

```
GET /api/reports
```

获取所有已生成的分析报告。

### 获取特定报告

```
GET /api/report?path=./temp_reports/report.html
```

获取指定报告的内容。

---

## 更新日志

### v2.0 (2025-12-01)

✅ 新增特定时间诊断 API (`/api/diagnose`)
✅ 增加 AI 调用重试机制与指数退避
✅ 扩展日志时间戳识别格式
✅ 增加 REQUEST_TIMEOUT 到 120s
✅ 增加 MAX_TOKENS 到 2000

---

## 技术支持

如有问题或建议，请：
1. 查看后端日志：`server.log`
2. 检查 `config.py` 配置
3. 在 GitHub 提交 Issue

---

## 许可证

MIT License

