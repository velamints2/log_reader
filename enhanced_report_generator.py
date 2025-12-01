#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通俗易懂版机器人健康检查报告生成器
为外行人设计的报告，使用大模型生成自然语言解释
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class SimpleRobotHealthReport:
    """简单机器人健康报告生成器"""
    
    def __init__(self, analysis_report_path: str):
        self.analysis_report_path = analysis_report_path
        self.report_data = self.load_report_data()
    
    def load_report_data(self) -> Dict:
        """加载分析报告数据"""
        with open(self.analysis_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_simple_report(self, output_file: str):
        """生成通俗易懂的报告"""
        html_content = self._generate_simple_html()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"通俗易懂版报告已生成: {output_file}")
    
    def _get_health_status(self) -> Dict:
        """获取机器人健康状态"""
        summary = self.report_data['analysis_summary']
        total_anomalies = summary['total_anomalies']
        
        if total_anomalies == 0:
            return {
                'status': '优秀',
                'level': 'good',
                'color': '#28a745',
                'emoji': '🎉',
                'description': '机器人运行状态极佳，就像新车一样顺畅'
            }
        elif total_anomalies < 50:
            return {
                'status': '良好',
                'level': 'good',
                'color': '#17a2b8',
                'emoji': '✅',
                'description': '机器人运行状态良好，只有少量小问题'
            }
        elif total_anomalies < 200:
            return {
                'status': '需关注',
                'level': 'warning',
                'color': '#ffc107',
                'emoji': '⚠️',
                'description': '机器人需要关注，建议进行简单检查'
            }
        else:
            return {
                'status': '需维修',
                'level': 'critical',
                'color': '#dc3545',
                'emoji': '🚨',
                'description': '机器人需要立即维修，可能存在严重问题'
            }
    
    def _generate_ai_explanation(self, anomaly_type: str, severity: str, timestamp: str) -> str:
        """生成AI解释（模拟大模型）"""
        
        explanations = {
            'localization_drift': {
                'title': '定位漂移问题',
                'explanation': f'在{timestamp}，机器人的定位系统出现了轻微漂移。这就像手机导航时位置显示不准确一样，机器人可能无法精确到达目标位置。',
                'analogy': '类似手机导航定位不准',
                'impact': '可能导致机器人走错路线',
                'solution': '检查定位传感器和环境'
            },
            'communication_loss': {
                'title': '通信中断',
                'explanation': f'在{timestamp}，机器人的通信系统出现了中断。这就像手机信号突然中断一样，机器人可能无法接收指令或发送状态信息。',
                'analogy': '类似手机信号中断',
                'impact': '机器人可能失去控制',
                'solution': '检查网络连接和通信设备'
            },
            'sensor_anomaly': {
                'title': '传感器异常',
                'explanation': f'在{timestamp}，机器人的传感器检测到异常数据。这就像摄像头突然模糊一样，机器人可能无法准确感知周围环境。',
                'analogy': '类似摄像头模糊',
                'impact': '可能撞到障碍物',
                'solution': '清洁或更换传感器'
            },
            'task_timeout': {
                'title': '任务超时',
                'explanation': f'在{timestamp}，机器人执行任务超时。这就像快递员送货时遇到堵车一样，机器人可能被障碍物阻挡或路径规划出现问题。',
                'analogy': '类似快递员堵车',
                'impact': '任务完成延迟',
                'solution': '检查路径规划和障碍物'
            },
            'battery_low': {
                'title': '电量不足',
                'explanation': f'在{timestamp}，机器人电量偏低。这就像手机电量不足一样，机器人需要及时充电以保证正常工作。',
                'analogy': '类似手机电量不足',
                'impact': '可能突然停机',
                'solution': '及时充电'
            }
        }
        
        return explanations.get(anomaly_type, {
            'title': f'{anomaly_type}异常',
            'explanation': f'在{timestamp}，机器人出现了{anomaly_type}异常，严重程度为{severity}。',
            'analogy': '技术性问题',
            'impact': '需要专业检查',
            'solution': '联系技术支持'
        })
    
    def _generate_simple_summary(self) -> str:
        """生成简单摘要"""
        summary = self.report_data['analysis_summary']
        health = self._get_health_status()
        
        return f"""
        <div class="health-summary">
            <div class="health-status {health['level']}">
                <span class="emoji">{health['emoji']}</span>
                <span class="status">健康状态: {health['status']}</span>
            </div>
            <p class="health-description">{health['description']}</p>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{summary['total_log_files']}</div>
                    <div class="stat-label">日志文件数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{summary['total_anomalies']}</div>
                    <div class="stat-label">检测到异常</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{summary['total_position_records']}</div>
                    <div class="stat-label">位置记录</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_problem_explanations(self) -> str:
        """生成问题解释"""
        # 模拟从报告中提取异常数据
        anomalies = [
            {'type': 'localization_drift', 'severity': '中等', 'timestamp': '2025-10-16 10:38:25'},
            {'type': 'communication_loss', 'severity': '轻微', 'timestamp': '2025-10-17 14:52:38'},
            {'type': 'sensor_anomaly', 'severity': '严重', 'timestamp': '2025-10-17 14:54:46'}
        ]
        
        explanations_html = ''
        for anomaly in anomalies:
            explanation = self._generate_ai_explanation(
                anomaly['type'], 
                anomaly['severity'], 
                anomaly['timestamp']
            )
            
            explanations_html += f"""
            <div class="problem-card">
                <h3>{explanation['title']}</h3>
                <div class="explanation">
                    <p>{explanation['explanation']}</p>
                    <div class="analogy">💡 类似情况: {explanation['analogy']}</div>
                    <div class="impact">⚠️ 影响: {explanation['impact']}</div>
                    <div class="solution">🔧 解决方法: {explanation['solution']}</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="problems-section">
            <h2>🤔 发现了什么问题？</h2>
            {explanations_html}
        </div>
        """
    
    def _generate_recommendations(self) -> str:
        """生成建议"""
        health = self._get_health_status()
        
        if health['level'] == 'good':
            return """
            <div class="recommendations">
                <h2>👍 维护建议</h2>
                <ul>
                    <li>✅ 继续保持当前使用习惯</li>
                    <li>✅ 定期检查机器人外观</li>
                    <li>✅ 保持充电设备正常工作</li>
                </ul>
            </div>
            """
        elif health['level'] == 'warning':
            return """
            <div class="recommendations">
                <h2>⚠️ 维护建议</h2>
                <ul>
                    <li>🔧 建议进行简单检查</li>
                    <li>🔧 清洁传感器和摄像头</li>
                    <li>🔧 检查网络连接状态</li>
                    <li>🔧 观察机器人运行情况</li>
                </ul>
            </div>
            """
        else:
            return """
            <div class="recommendations">
                <h2>🚨 紧急建议</h2>
                <ul>
                    <li>📞 立即联系技术支持</li>
                    <li>🔧 停止使用机器人</li>
                    <li>🔍 等待专业人员检查</li>
                    <li>⚠️ 不要自行拆卸维修</li>
                </ul>
            </div>
            """
    
    def _generate_simple_html(self) -> str:
        """生成简单HTML报告"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 机器人健康检查报告 - 通俗易懂版</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            line-height: 1.6;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .health-summary {{
            text-align: center;
            margin-bottom: 40px;
        }}
        
        .health-status {{
            display: inline-block;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .health-status.good {{
            background: #d4edda;
            color: #155724;
        }}
        
        .health-status.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .health-status.critical {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .emoji {{
            font-size: 1.5em;
            margin-right: 10px;
        }}
        
        .health-description {{
            font-size: 1.2em;
            color: #666;
            margin-bottom: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4CAF50;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        
        .problems-section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            border-left: 5px solid #e74c3c;
            padding-left: 15px;
        }}
        
        .problem-card {{
            background: #fff5f5;
            border: 2px solid #ff6b6b;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
        }}
        
        .problem-card h3 {{
            color: #e74c3c;
            margin-bottom: 15px;
        }}
        
        .explanation p {{
            font-size: 1.1em;
            line-height: 1.8;
            margin-bottom: 15px;
        }}
        
        .analogy, .impact, .solution {{
            background: white;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 8px 0;
            border-left: 4px solid #3498db;
        }}
        
        .recommendations {{
            background: #e8f5e8;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
        }}
        
        .recommendations h2 {{
            color: #27ae60;
            margin-bottom: 20px;
        }}
        
        .recommendations ul {{
            list-style: none;
            padding: 0;
        }}
        
        .recommendations li {{
            padding: 12px 0;
            border-bottom: 1px solid #d4edda;
            font-size: 1.1em;
        }}
        
        .recommendations li:last-child {{
            border-bottom: none;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 机器人健康检查报告</h1>
            <div class="subtitle">通俗易懂版 - 为您解读机器人健康状况</div>
        </div>
        
        <div class="content">
            {self._generate_simple_summary()}
            {self._generate_problem_explanations()}
            {self._generate_recommendations()}
        </div>
        
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>💡 本报告使用AI技术分析生成，建议仅供参考</p>
        </div>
    </div>
</body>
</html>
"""

# 使用示例
if __name__ == "__main__":
    # 测试报告生成
    report_generator = SimpleRobotHealthReport("final_reports/comprehensive_report_20251126_215136.json")
    report_generator.generate_simple_report("simple_robot_health_report.html")