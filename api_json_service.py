#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器人日志分析系统 - JSON API 服务
用于大模型集成的精简 JSON 数据接口（无可视化，仅传递信息）
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from comprehensive_robot_analyzer import ComprehensiveRobotAnalyzer
from complaint_analyzer import ComplaintAnalyzer
from historical_trace_analyzer import HistoricalTraceAnalyzer
from config import LOG_DIRECTORY, TEMP_REPORTS_DIRECTORY


def analyze_logs_json(log_directory: str = LOG_DIRECTORY) -> Dict[str, Any]:
    """
    综合日志分析 - 返回 JSON 格式结果
    
    Args:
        log_directory: 日志目录路径
        
    Returns:
        包含分析结果的字典
    """
    try:
        # 执行综合分析
        analyzer = ComprehensiveRobotAnalyzer(log_directory)
        analyzer.analyze_all_logs()
        report = analyzer.generate_comprehensive_report()
        
        # 精简关键信息
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "analysis_summary": report.get("analysis_summary", {}),
            "anomaly_summary": report.get("anomaly_summary", {}),
            "key_findings": {
                "total_log_files": report.get("analysis_summary", {}).get("total_log_files", 0),
                "total_anomalies": report.get("analysis_summary", {}).get("total_anomalies", 0),
                "total_task_segments": report.get("analysis_summary", {}).get("total_task_segments", 0),
                "critical_anomalies": [
                    a for a in report.get("anomalies", [])
                    if a.get("severity") in ["critical", "high"]
                ][:10]  # 只返回前10个关键异常
            }
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"分析失败: {str(e)}"
        }


def historical_trace_json(log_directory: str = LOG_DIRECTORY) -> Dict[str, Any]:
    """
    历史追溯分析 - 返回 JSON 格式结果
    
    Args:
        log_directory: 日志目录路径
        
    Returns:
        包含历史追溯结果的字典
    """
    try:
        analyzer = HistoricalTraceAnalyzer(log_directory)
        analyzer.analyze_all_logs()
        report = analyzer.generate_trace_report()
        
        # 精简关键信息
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "trace_summary": {
                "total_task_segments": len(report.get("task_timeline", [])),
                "time_span": report.get("analysis_metadata", {}).get("time_span"),
                "earliest_time": report.get("analysis_metadata", {}).get("earliest_time"),
                "latest_time": report.get("analysis_metadata", {}).get("latest_time"),
            },
            "task_timeline": report.get("task_timeline", [])[:20],  # 仅返回前20条
            "system_state_transitions": report.get("system_state_transitions", [])[:20],
            "anomaly_timeline": report.get("anomaly_timeline", [])[:20]
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"历史追溯失败: {str(e)}"
        }


def complaint_analysis_json(
    log_directory: str = LOG_DIRECTORY,
    complaint_time_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    投诉分析 - 返回 JSON 格式结果
    
    Args:
        log_directory: 日志目录路径
        complaint_time_str: 投诉时间，格式 "YYYY-MM-DD HH:MM:SS"
        
    Returns:
        包含投诉分析结果的字典
    """
    try:
        if not complaint_time_str:
            return {
                "status": "error",
                "message": "缺少参数: complaint_time (格式: YYYY-MM-DD HH:MM:SS)"
            }
        
        complaint_time = datetime.strptime(complaint_time_str, "%Y-%m-%d %H:%M:%S")
        
        analyzer = ComplaintAnalyzer(log_directory)
        analyzer.analyze_all_logs()
        report = analyzer.generate_complaint_report(complaint_time)
        
        # 精简关键信息
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "complaint_time": complaint_time_str,
            "analysis_window": {
                "start": (complaint_time - datetime.timedelta(minutes=10)).isoformat(),
                "end": (complaint_time + datetime.timedelta(minutes=10)).isoformat()
            },
            "complaint_summary": report.get("complaint_summary", {}),
            "pre_complaint_events": report.get("pre_complaint_events", [])[:15],
            "complaint_time_events": report.get("complaint_time_events", [])[:15],
            "post_complaint_events": report.get("post_complaint_events", [])[:15],
            "root_cause_analysis": report.get("root_cause_analysis", {}),
            "key_findings": report.get("key_findings", [])
        }
        return result
    except ValueError as e:
        return {
            "status": "error",
            "message": f"时间格式错误: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"投诉分析失败: {str(e)}"
        }


def anomaly_summary_json(log_directory: str = LOG_DIRECTORY) -> Dict[str, Any]:
    """
    异常汇总 - 返回 JSON 格式结果（无详细日志内容）
    
    Args:
        log_directory: 日志目录路径
        
    Returns:
        包含异常统计的字典
    """
    try:
        analyzer = ComprehensiveRobotAnalyzer(log_directory)
        analyzer.analyze_all_logs()
        report = analyzer.generate_comprehensive_report()
        
        # 按严重程度分类统计
        anomalies = report.get("anomalies", [])
        
        severity_count = {
            "critical": len([a for a in anomalies if a.get("severity") == "critical"]),
            "high": len([a for a in anomalies if a.get("severity") == "high"]),
            "medium": len([a for a in anomalies if a.get("severity") == "medium"]),
            "low": len([a for a in anomalies if a.get("severity") == "low"])
        }
        
        # 按类型分类
        type_count = {}
        for anomaly in anomalies:
            atype = anomaly.get("type", "unknown")
            type_count[atype] = type_count.get(atype, 0) + 1
        
        # 按文件分类
        file_count = {}
        for anomaly in anomalies:
            fname = anomaly.get("file", "unknown")
            file_count[fname] = file_count.get(fname, 0) + 1
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_anomalies": len(anomalies),
            "severity_distribution": severity_count,
            "type_distribution": type_count,
            "file_distribution": file_count,
            "top_anomalies": [
                {
                    "type": a.get("type"),
                    "severity": a.get("severity"),
                    "file": a.get("file"),
                    "time": a.get("time"),
                    "message": a.get("message", "")[:100]  # 仅返回前100字
                }
                for a in anomalies[:30]  # 仅返回前30条
            ]
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"异常汇总失败: {str(e)}"
        }


def log_files_info_json(log_directory: str = LOG_DIRECTORY) -> Dict[str, Any]:
    """
    日志文件信息 - 返回 JSON 格式结果
    
    Args:
        log_directory: 日志目录路径
        
    Returns:
        包含日志文件信息的字典
    """
    try:
        if not os.path.exists(log_directory):
            return {
                "status": "error",
                "message": f"日志目录不存在: {log_directory}"
            }
        
        log_files = []
        total_size = 0
        
        for filename in os.listdir(log_directory):
            filepath = os.path.join(log_directory, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                size = stat.st_size
                total_size += size
                
                log_files.append({
                    "name": filename,
                    "size_bytes": size,
                    "size_kb": round(size / 1024, 2),
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # 按大小排序
        log_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "log_directory": log_directory,
            "total_files": len(log_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "log_files": log_files
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"获取日志文件信息失败: {str(e)}"
        }


def system_health_json(log_directory: str = LOG_DIRECTORY) -> Dict[str, Any]:
    """
    系统健康评估 - 返回 JSON 格式结果
    
    Args:
        log_directory: 日志目录路径
        
    Returns:
        包含系统健康状态的字典
    """
    try:
        analyzer = ComprehensiveRobotAnalyzer(log_directory)
        analyzer.analyze_all_logs()
        report = analyzer.generate_comprehensive_report()
        
        # 计算健康得分 (0-100)
        anomalies = report.get("anomalies", [])
        total_anomalies = len(anomalies)
        
        # 按严重程度计算加权得分
        critical_count = len([a for a in anomalies if a.get("severity") == "critical"])
        high_count = len([a for a in anomalies if a.get("severity") == "high"])
        medium_count = len([a for a in anomalies if a.get("severity") == "medium"])
        
        health_score = max(0, 100 - critical_count * 30 - high_count * 15 - medium_count * 5)
        
        # 判断健康状态
        if health_score >= 90:
            status = "excellent"
            status_cn = "优秀"
        elif health_score >= 70:
            status = "good"
            status_cn = "良好"
        elif health_score >= 50:
            status = "fair"
            status_cn = "一般"
        elif health_score >= 30:
            status = "poor"
            status_cn = "较差"
        else:
            status = "critical"
            status_cn = "严重"
        
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "health_status": status,
            "health_status_cn": status_cn,
            "anomaly_breakdown": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": len([a for a in anomalies if a.get("severity") == "low"]),
                "total": total_anomalies
            },
            "key_issues": [
                {
                    "severity": a.get("severity"),
                    "type": a.get("type"),
                    "count": 1,
                    "message": a.get("message", "")[:80]
                }
                for a in anomalies[:10]
            ],
            "recommendations": generate_recommendations(health_score, critical_count, high_count)
        }
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"系统健康评估失败: {str(e)}"
        }


def generate_recommendations(health_score: float, critical_count: int, high_count: int) -> List[str]:
    """生成建议列表"""
    recommendations = []
    
    if critical_count > 0:
        recommendations.append(f"❌ 发现 {critical_count} 个严重问题，需要立即处理")
    
    if high_count > 0:
        recommendations.append(f"⚠️ 发现 {high_count} 个高优先级问题，建议尽快修复")
    
    if health_score < 50:
        recommendations.append("🔧 系统状态欠佳，建议进行全面诊断和维护")
    elif health_score < 70:
        recommendations.append("📊 系统有改进空间，建议关注高优先级问题")
    else:
        recommendations.append("✅ 系统运行正常，请继续监控")
    
    return recommendations


if __name__ == "__main__":
    # 测试脚本
    print("=" * 60)
    print("JSON API 服务测试")
    print("=" * 60)
    
    print("\n1. 日志分析结果:")
    result = analyze_logs_json()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")
    
    print("\n2. 历史追溯结果:")
    result = historical_trace_json()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")
    
    print("\n3. 异常汇总结果:")
    result = anomaly_summary_json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n4. 日志文件信息:")
    result = log_files_info_json()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:500] + "...")
    
    print("\n5. 系统健康评估:")
    result = system_health_json()
    print(json.dumps(result, ensure_ascii=False, indent=2))
