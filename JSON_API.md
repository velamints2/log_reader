# JSON API 接口文档

适用于大模型集成的精简 JSON 数据接口。所有接口返回结构化数据，便于大模型直接处理，无需前端可视化。

---

## API 概览

| 端点 | 方法 | 说明 | 返回格式 |
|------|------|------|---------|
| `/api/json/analyze` | GET | 综合日志分析 | JSON |
| `/api/json/historical-trace` | GET | 历史追溯分析 | JSON |
| `/api/json/complaint` | POST | 投诉分析 | JSON |
| `/api/json/anomaly-summary` | GET | 异常汇总 | JSON |
| `/api/json/log-files` | GET | 日志文件信息 | JSON |
| `/api/json/system-health` | GET | 系统健康评估 | JSON |

---

## 1. 综合日志分析

### 请求

```
GET /api/json/analyze?log_dir=./logs
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "analysis_summary": {
    "total_log_files": 28,
    "total_anomalies": 45,
    "total_task_segments": 120,
    "analysis_start_time": "2025-10-12 01:00:00",
    "analysis_end_time": "2025-10-12 01:01:31"
  },
  "anomaly_summary": {
    "by_severity": {
      "critical": 2,
      "high": 8,
      "medium": 15,
      "low": 20
    },
    "by_type": {
      "mechanical_issue": 5,
      "sensor_offline": 3,
      "speed_anomaly": 12,
      ...
    }
  },
  "key_findings": {
    "total_log_files": 28,
    "total_anomalies": 45,
    "total_task_segments": 120,
    "critical_anomalies": [
      {
        "type": "motor_error",
        "severity": "critical",
        "file": "ikitbot_driver.log",
        "time": "2025-10-12 01:00:15",
        "message": "电机1驱动故障"
      },
      ...
    ]
  }
}
```

### 使用示例

```bash
# 分析默认日志目录
curl http://127.0.0.1:8080/api/json/analyze | jq .

# 分析自定义日志目录
curl "http://127.0.0.1:8080/api/json/analyze?log_dir=/path/to/logs" | jq .
```

---

## 2. 历史追溯分析

### 请求

```
GET /api/json/historical-trace?log_dir=./logs
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "trace_summary": {
    "total_task_segments": 120,
    "time_span": "00:01:31",
    "earliest_time": "2025-10-12 01:00:00",
    "latest_time": "2025-10-12 01:01:31"
  },
  "task_timeline": [
    {
      "segment_id": 1,
      "start_time": "2025-10-12 01:00:00",
      "end_time": "2025-10-12 01:00:15",
      "duration_seconds": 15,
      "type": "navigation",
      "status": "success"
    },
    {
      "segment_id": 2,
      "start_time": "2025-10-12 01:00:15",
      "end_time": "2025-10-12 01:00:58",
      "duration_seconds": 43,
      "type": "restart",
      "status": "in_progress"
    },
    ...
  ],
  "system_state_transitions": [
    {
      "time": "2025-10-12 01:00:00",
      "from_state": "normal",
      "to_state": "restarting",
      "trigger": "scheduled_restart",
      "duration_until_next": "58s"
    },
    ...
  ],
  "anomaly_timeline": [
    {
      "time": "2025-10-12 01:00:00",
      "type": "system_restart",
      "severity": "medium",
      "source": "RestartController"
    },
    ...
  ]
}
```

### 使用示例

```bash
curl http://127.0.0.1:8080/api/json/historical-trace | jq .
```

---

## 3. 投诉分析

### 请求

```
POST /api/json/complaint
Content-Type: application/json

{
  "complaint_time": "2025-10-12 01:00:30",
  "log_dir": "./logs"
}
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `complaint_time` | string | ✅ | 投诉时间（格式：`YYYY-MM-DD HH:MM:SS`） |
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "complaint_time": "2025-10-12 01:00:30",
  "analysis_window": {
    "start": "2025-10-12 01:00:20",
    "end": "2025-10-12 01:00:40"
  },
  "complaint_summary": {
    "primary_issue": "系统意外重启",
    "affected_systems": ["ROS连接", "GRPC服务"],
    "estimated_impact": "服务中断58秒"
  },
  "pre_complaint_events": [
    {
      "time": "2025-10-12 01:00:00",
      "type": "restart_triggered",
      "severity": "medium",
      "description": "定时重启命令触发"
    },
    ...
  ],
  "complaint_time_events": [
    {
      "time": "2025-10-12 01:00:30",
      "type": "ros_disconnect",
      "severity": "high",
      "description": "ROS连接断开"
    },
    ...
  ],
  "post_complaint_events": [
    {
      "time": "2025-10-12 01:00:58",
      "type": "grpc_restart",
      "severity": "low",
      "description": "GRPC服务重新启动"
    },
    ...
  ],
  "root_cause_analysis": {
    "primary_cause": "定时重启任务",
    "trigger": "RestartController@01:00:00",
    "confidence": 0.95,
    "explanation": "系统在整点执行计划内重启，导致ROS连接断开和GRPC服务中断"
  },
  "key_findings": [
    "这是一次计划内重启，而非故障",
    "重启过程正常，服务自动恢复",
    "无数据丢失或异常错误"
  ]
}
```

### 使用示例

```bash
curl -X POST http://127.0.0.1:8080/api/json/complaint \
  -H "Content-Type: application/json" \
  -d '{
    "complaint_time": "2025-10-12 01:00:30",
    "log_dir": "./logs"
  }' | jq .
```

---

## 4. 异常汇总

### 请求

```
GET /api/json/anomaly-summary?log_dir=./logs
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "total_anomalies": 45,
  "severity_distribution": {
    "critical": 2,
    "high": 8,
    "medium": 15,
    "low": 20
  },
  "type_distribution": {
    "mechanical_issue": 5,
    "sensor_offline": 3,
    "speed_anomaly": 12,
    "cpu_high": 8,
    "motor_error": 4,
    "collision": 13
  },
  "file_distribution": {
    "ikitbot_driver.log": 8,
    "navigation_move_base.log": 12,
    "01_00_58_grpc.log": 5,
    ...
  },
  "top_anomalies": [
    {
      "type": "collision",
      "severity": "high",
      "file": "virtual_bumper.log",
      "time": "2025-10-12 01:00:45",
      "message": "前碰撞传感器触发"
    },
    ...
  ]
}
```

### 使用示例

```bash
curl http://127.0.0.1:8080/api/json/anomaly-summary | jq .
```

---

## 5. 日志文件信息

### 请求

```
GET /api/json/log-files?log_dir=./logs
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "log_directory": "./logs",
  "total_files": 28,
  "total_size_bytes": 5242880,
  "total_size_mb": 5.0,
  "log_files": [
    {
      "name": "01_00_58_grpc.log",
      "size_bytes": 1048576,
      "size_kb": 1024.0,
      "modified_time": "2025-10-12T01:00:58.000000"
    },
    {
      "name": "navigation_move_base.log",
      "size_bytes": 819200,
      "size_kb": 800.0,
      "modified_time": "2025-10-12T01:01:31.000000"
    },
    ...
  ]
}
```

### 使用示例

```bash
curl http://127.0.0.1:8080/api/json/log-files | jq .
```

---

## 6. 系统健康评估

### 请求

```
GET /api/json/system-health?log_dir=./logs
```

### 参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `log_dir` | string | ❌ | 日志目录（默认 `./logs`） |

### 响应示例

```json
{
  "status": "success",
  "timestamp": "2025-12-02T10:30:45.123456",
  "health_score": 78,
  "health_status": "good",
  "health_status_cn": "良好",
  "anomaly_breakdown": {
    "critical": 2,
    "high": 8,
    "medium": 15,
    "low": 20,
    "total": 45
  },
  "key_issues": [
    {
      "severity": "critical",
      "type": "motor_error",
      "count": 1,
      "message": "电机1驱动故障"
    },
    {
      "severity": "high",
      "type": "collision",
      "count": 2,
      "message": "多次碰撞检测"
    },
    ...
  ],
  "recommendations": [
    "⚠️ 发现 8 个高优先级问题，建议尽快修复",
    "📊 系统有改进空间，建议关注高优先级问题",
    "🔧 重点检查电机和碰撞传感器"
  ]
}
```

### 健康评分标准

| 评分 | 状态 | 说明 |
|------|------|------|
| 90+ | excellent (优秀) | 系统运行完美 |
| 70-89 | good (良好) | 系统运行正常 |
| 50-69 | fair (一般) | 系统有问题需要关注 |
| 30-49 | poor (较差) | 系统问题较多 |
| <30 | critical (严重) | 系统需要紧急处理 |

### 使用示例

```bash
curl http://127.0.0.1:8080/api/json/system-health | jq .
```

---

## Python 集成示例

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def get_analysis():
    """获取综合分析结果"""
    response = requests.get(f"{BASE_URL}/api/json/analyze")
    return response.json()

def get_health():
    """获取系统健康状态"""
    response = requests.get(f"{BASE_URL}/api/json/system-health")
    return response.json()

def analyze_complaint(complaint_time):
    """分析投诉问题"""
    response = requests.post(
        f"{BASE_URL}/api/json/complaint",
        json={"complaint_time": complaint_time}
    )
    return response.json()

def get_anomalies():
    """获取异常汇总"""
    response = requests.get(f"{BASE_URL}/api/json/anomaly-summary")
    return response.json()

# 使用示例
if __name__ == "__main__":
    print("=== 系统分析 ===")
    
    # 1. 获取系统健康状态
    health = get_health()
    print(f"健康评分: {health['health_score']}")
    print(f"状态: {health['health_status_cn']}")
    
    # 2. 获取异常信息
    anomalies = get_anomalies()
    print(f"严重异常: {anomalies['severity_distribution']['critical']}")
    print(f"高优先级异常: {anomalies['severity_distribution']['high']}")
    
    # 3. 分析投诉
    complaint = analyze_complaint("2025-10-12 01:00:30")
    print(f"投诉时间: {complaint['complaint_time']}")
    print(f"根因: {complaint['root_cause_analysis']['primary_cause']}")
```

---

## cURL 集成示例

```bash
#!/bin/bash

BASE_URL="http://127.0.0.1:8080"

# 1. 获取系统健康评分
echo "=== 系统健康评估 ==="
curl -s "$BASE_URL/api/json/system-health" | jq '.health_score,.health_status_cn'

# 2. 获取异常统计
echo "=== 异常统计 ==="
curl -s "$BASE_URL/api/json/anomaly-summary" | jq '.total_anomalies,.severity_distribution'

# 3. 获取日志文件信息
echo "=== 日志文件信息 ==="
curl -s "$BASE_URL/api/json/log-files" | jq '.total_files,.total_size_mb'

# 4. 分析特定投诉
echo "=== 投诉分析 ==="
curl -s -X POST "$BASE_URL/api/json/complaint" \
  -H "Content-Type: application/json" \
  -d '{"complaint_time":"2025-10-12 01:00:30"}' | \
  jq '.complaint_summary,.root_cause_analysis'

# 5. 历史追溯
echo "=== 历史追溯 ==="
curl -s "$BASE_URL/api/json/historical-trace" | jq '.trace_summary,.task_timeline[0:3]'
```

---

## 数据精简策略

所有 JSON API 采用数据精简策略，确保返回数据量合理且易于大模型处理：

- ✅ 关键异常仅返回前 10-30 条
- ✅ 任务段/状态转换仅返回前 20 条
- ✅ 日志文件按大小排序，便于识别问题来源
- ✅ 异常消息截断为 80-100 字符
- ✅ 所有时间戳使用 ISO 8601 格式
- ✅ 数值信息精确到合理小数位

---

## 错误处理

所有端点统一错误响应格式：

```json
{
  "status": "error",
  "message": "具体错误说明"
}
```

常见错误：

| 错误 | 说明 | 解决方案 |
|------|------|---------|
| "日志目录不存在" | log_dir 路径无效 | 检查 log_dir 参数是否正确 |
| "缺少参数: complaint_time" | POST 投诉分析时未提供时间 | 添加 complaint_time 参数 |
| "时间格式错误" | 时间不符合 YYYY-MM-DD HH:MM:SS | 检查时间格式 |

---

## 性能指标

| 操作 | 典型响应时间 |
|------|------------|
| 综合分析 | 2-5s |
| 历史追溯 | 1-3s |
| 投诉分析 | 1-2s |
| 异常汇总 | 1s |
| 日志文件信息 | <500ms |
| 系统健康评估 | 2-5s |

---

## 集成建议

1. **大模型分析**：先调用 `/api/json/analyze` 和 `/api/json/system-health` 获取概览
2. **问题诊断**：使用 `/api/json/complaint` 分析特定投诉时间
3. **历史追溯**：使用 `/api/json/historical-trace` 理解问题发生过程
4. **实时监控**：定期调用 `/api/json/system-health` 监控系统状态

---

## 更新日志

### v1.0 (2025-12-02)

✅ 新增 6 个 JSON API 端点
✅ 精简数据格式，优化大模型处理
✅ 完整文档和集成示例
✅ 统一错误处理和响应格式

