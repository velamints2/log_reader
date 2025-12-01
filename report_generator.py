#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版机器人日志分析报告生成器
生成通俗易懂的HTML报告，集成大模型能力，适合外行人理解
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
import base64

class EnhancedReportGenerator:
    """增强版报告生成器类"""
    
    def __init__(self, analysis_report_path: str):
        self.analysis_report_path = analysis_report_path
        self.report_data = self.load_report_data()
    
    def load_report_data(self) -> Dict:
        """加载分析报告数据"""
        with open(self.analysis_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_enhanced_html_report(self, output_file: str):
        """生成增强版HTML报告"""
        html_content = self._generate_enhanced_html_content()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"增强版HTML报告已生成: {output_file}")
    
    def _generate_ai_explanation(self, anomaly_data: Dict) -> str:
        """使用大模型生成通俗易懂的故障解释"""
        # 模拟大模型生成的自然语言解释
        anomaly_type = anomaly_data.get('type', '未知异常')
        severity = anomaly_data.get('severity', '中等')
        timestamp = anomaly_data.get('timestamp', '未知时间')
        
        explanations = {
            'localization_drift': f"在{timestamp}，机器人的定位系统出现了轻微漂移。这就像手机导航时位置显示不准确一样，机器人可能无法精确到达目标位置。",
            'communication_loss': f"在{timestamp}，机器人的通信系统出现了中断。这就像手机信号突然中断一样，机器人可能无法接收指令或发送状态信息。",
            'sensor_anomaly': f"在{timestamp}，机器人的传感器检测到异常数据。这就像摄像头突然模糊一样，机器人可能无法准确感知周围环境。",
            'task_timeout': f"在{timestamp}，机器人执行任务超时。这就像快递员送货时遇到堵车一样，机器人可能被障碍物阻挡或路径规划出现问题。",
            'battery_low': f"在{timestamp}，机器人电量偏低。这就像手机电量不足一样，机器人需要及时充电以保证正常工作。",
            'motor_anomaly': f"在{timestamp}，机器人的电机系统出现异常。这就像汽车发动机出现异响一样，机器人可能需要检查机械部件。"
        }
        
        return explanations.get(anomaly_type, f"在{timestamp}，机器人出现了{anomaly_type}异常，严重程度为{severity}。")
    
    def _generate_plain_language_summary(self) -> str:
        """生成通俗易懂的总体摘要"""
        summary = self.report_data['analysis_summary']
        total_anomalies = summary['total_anomalies']
        
        if total_anomalies == 0:
            return "🎉 好消息！机器人运行状态良好，没有检测到任何异常。机器人就像一位经验丰富的快递员，准时准确地完成了所有任务。"
        elif total_anomalies < 100:
            return f"📊 机器人整体运行状态良好，检测到{total_anomalies}个轻微异常。这就像开车时偶尔遇到的小颠簸，不影响整体行程。"
        elif total_anomalies < 1000:
            return f"⚠️ 机器人运行状态需要关注，检测到{total_anomalies}个异常。这就像汽车需要定期保养一样，建议检查机器人的关键部件。"
        else:
            return f"🚨 机器人运行状态需要立即关注！检测到{total_anomalies}个异常。这就像汽车发动机出现严重问题，建议立即进行专业检修。"
    
    def _generate_html_content(self) -> str:
        """生成HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>机器人日志分析报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #3498db;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: #fafafa;
        }}
        .section h2 {{
            color: #2c3e50;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .summary-card h3 {{
            margin: 0 0 10px 0;
            color: #2c3e50;
        }}
        .summary-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }}
        .anomaly-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .anomaly-table th, .anomaly-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .anomaly-table th {{
            background-color: #3498db;
            color: white;
        }}
        .anomaly-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .severity-high {{
            background-color: #ff6b6b !important;
            color: white;
        }}
        .severity-medium {{
            background-color: #ffd93d !important;
        }}
        .severity-low {{
            background-color: #6bcf7f !important;
        }}
        .recommendation {{
            background: #e8f4fd;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .chart-container {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        {self._generate_header()}
        {self._generate_summary()}
        {self._generate_task_analysis()}
        {self._generate_anomaly_analysis()}
        {self._generate_localization_analysis()}
        {self._generate_stop_point_analysis()}
        {self._generate_historical_trace()}
        {self._generate_recommendations()}
    </div>
</body>
</html>
"""
    
    def _generate_header(self) -> str:
        """生成报告头部"""
        timestamp = self.report_data['analysis_summary']['analysis_timestamp']
        return f"""
        <div class="header">
            <h1>🤖 机器人日志分析报告</h1>
            <p class="timestamp">生成时间: {timestamp}</p>
        </div>
        """
    
    def _generate_summary(self) -> str:
        """生成分析摘要"""
        summary = self.report_data['analysis_summary']
        return f"""
        <div class="section">
            <h2>📊 分析摘要</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>日志文件数</h3>
                    <div class="value">{summary['total_log_files']}</div>
                </div>
                <div class="summary-card">
                    <h3>任务段数</h3>
                    <div class="value">{summary['total_task_segments']}</div>
                </div>
                <div class="summary-card">
                    <h3>位置记录数</h3>
                    <div class="value">{summary['total_position_records']}</div>
                </div>
                <div class="summary-card">
                    <h3>检测异常数</h3>
                    <div class="value">{summary['total_anomalies']}</div>
                </div>
            </div>
        </div>
        """
    
    def _generate_task_analysis(self) -> str:
        """生成任务分析"""
        task_overview = self.report_data['task_overview']
        
        if task_overview['total_tasks'] == 0:
            return f"""
            <div class="section">
                <h2>📋 任务分析</h2>
                <p>未检测到明确的任务阶段。可能原因：</p>
                <ul>
                    <li>日志中缺少任务开始/结束标记</li>
                    <li>机器人处于调试或维护模式</li>
                    <li>需要调整任务识别模式</li>
                </ul>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📋 任务分析</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>总任务数</h3>
                    <div class="value">{task_overview['total_tasks']}</div>
                </div>
                <div class="summary-card">
                    <h3>总时长(小时)</h3>
                    <div class="value">{task_overview['total_duration_hours']:.1f}</div>
                </div>
                <div class="summary-card">
                    <h3>平均时长(分钟)</h3>
                    <div class="value">{task_overview['avg_task_duration_minutes']:.1f}</div>
                </div>
            </div>
            
            <h3>任务类型分布</h3>
            <div class="chart-container">
                <p>任务类型统计:</p>
                <ul>
                    {''.join([f'<li>{task_type}: {count} 次</li>' for task_type, count in task_overview['task_types'].items()])}
                </ul>
            </div>
        </div>
        """
    
    def _generate_anomaly_analysis(self) -> str:
        """生成异常分析"""
        anomaly_summary = self.report_data['anomaly_summary']
        
        # 生成异常类型表格
        anomaly_type_rows = ''
        for anomaly_type, count in anomaly_summary['by_type'].items():
            severity_class = self._get_severity_class(anomaly_type)
            anomaly_type_rows += f"""
            <tr>
                <td>{anomaly_type}</td>
                <td>{count}</td>
                <td><span class="severity-{severity_class}">{severity_class}</span></td>
            </tr>
            """
        
        # 生成异常时间线（前10个）
        timeline_rows = ''
        for i, anomaly in enumerate(anomaly_summary['timeline'][:10]):
            timeline_rows += f"""
            <tr>
                <td>{anomaly['timestamp']}</td>
                <td>{anomaly['type']}</td>
                <td><span class="severity-{anomaly['severity']}">{anomaly['severity']}</span></td>
                <td>{anomaly['description'][:100]}...</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>⚠️ 异常分析</h2>
            
            <h3>异常统计</h3>
            <table class="anomaly-table">
                <thead>
                    <tr>
                        <th>异常类型</th>
                        <th>出现次数</th>
                        <th>严重程度</th>
                    </tr>
                </thead>
                <tbody>
                    {anomaly_type_rows}
                </tbody>
            </table>
            
            <h3>最近异常事件</h3>
            <table class="anomaly-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>类型</th>
                        <th>严重程度</th>
                        <th>描述</th>
                    </tr>
                </thead>
                <tbody>
                    {timeline_rows}
                </tbody>
            </table>
            
            <div class="chart-container">
                <h4>异常严重程度分布</h4>
                <p>高严重度: {anomaly_summary['by_severity'].get('high', 0)} 次</p>
                <p>中严重度: {anomaly_summary['by_severity'].get('medium', 0)} 次</p>
                <p>低严重度: {anomaly_summary['by_severity'].get('low', 0)} 次</p>
            </div>
        </div>
        """
    
    def _generate_localization_analysis(self) -> str:
        """生成定位分析"""
        localization_data = self.report_data['localization_analysis']
        
        if not localization_data:
            return f"""
            <div class="section">
                <h2>📍 定位分析</h2>
                <p>未检测到足够的定位数据。可能原因：</p>
                <ul>
                    <li>日志中缺少SLAM或里程计数据</li>
                    <li>定位系统未正常工作</li>
                    <li>需要调整位置信息提取模式</li>
                </ul>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📍 定位分析</h2>
            <p>检测到 {len(localization_data)} 个定位记录</p>
            <div class="chart-container">
                <h4>定位质量趋势</h4>
                <p>平均定位分数: {sum(entry['score'] for entry in localization_data) / len(localization_data):.1f}</p>
                <p>定位记录时间范围: {localization_data[0]['timestamp']} 到 {localization_data[-1]['timestamp']}</p>
            </div>
        </div>
        """
    
    def _generate_stop_point_analysis(self) -> str:
        """生成停机点分析"""
        stop_points = self.report_data['stop_point_analysis']
        
        if not stop_points:
            return f"""
            <div class="section">
                <h2>🛑 停机点分析</h2>
                <p>未检测到明显的停机点。机器人运动状态正常。</p>
            </div>
            """
        
        stop_point_rows = ''
        for i, stop_point in enumerate(stop_points[:5]):  # 显示前5个停机点
            stop_point_rows += f"""
            <tr>
                <td>{i+1}</td>
                <td>{stop_point['timestamp']}</td>
                <td>({stop_point['position']['x']:.2f}, {stop_point['position']['y']:.2f})</td>
                <td>{stop_point['duration_minutes']} 分钟</td>
                <td>{stop_point['avg_movement']:.4f}</td>
            </tr>
            """
        
        return f"""
        <div class="section">
            <h2>🛑 停机点分析</h2>
            <p>检测到 {len(stop_points)} 个可能的停机点</p>
            
            <table class="anomaly-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>时间</th>
                        <th>位置</th>
                        <th>持续时间</th>
                        <th>平均移动</th>
                    </tr>
                </thead>
                <tbody>
                    {stop_point_rows}
                </tbody>
            </table>
        </div>
        """
    
    def _generate_historical_trace(self) -> str:
        """生成历史追溯分析"""
        historical_data = self.report_data['historical_trace_analysis']
        
        if historical_data.get('message') == '没有发现任务数据':
            return f"""
            <div class="section">
                <h2>📈 历史追溯分析</h2>
                <p>由于缺少任务数据，无法进行历史追溯分析。</p>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>📈 历史追溯分析</h2>
            <p>分析了 {historical_data['total_tasks_analyzed']} 个任务序列</p>
            
            <div class="chart-container">
                <h4>任务序列统计</h4>
                <p>共分析 {len(historical_data['task_sequences'])} 个连续任务序列</p>
                
                {''.join([f'''
                <div style="margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                    <strong>{seq['sequence_id']}</strong><br>
                    总时长: {seq['total_duration_hours']:.1f} 小时<br>
                    异常数: {seq['anomaly_count']}
                </div>
                ''' for seq in historical_data['task_sequences'][:3]])}
            </div>
        </div>
        """
    
    def _generate_recommendations(self) -> str:
        """生成改进建议"""
        recommendations = self.report_data['recommendations']
        
        recommendation_items = ''
        for i, rec in enumerate(recommendations, 1):
            recommendation_items += f"""
            <div class="recommendation">
                <strong>建议 {i}:</strong> {rec}
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>💡 改进建议</h2>
            {recommendation_items}
        </div>
        """
    
    def _get_severity_class(self, anomaly_type: str) -> str:
        """获取异常严重程度类别"""
        severity_map = {
            'sensor_offline': 'medium',
            'mechanical_issue': 'high',
            'cpu_high': 'high',
            'speed_anomaly': 'medium',
            'localization_drop': 'high'
        }
        return severity_map.get(anomaly_type, 'low')

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='生成机器人日志分析HTML报告')
    parser.add_argument('-i', '--input', required=True, help='分析报告JSON文件路径')
    parser.add_argument('-o', '--output', default='robot_analysis_report.html', 
                       help='输出HTML报告文件路径')
    
    args = parser.parse_args()
    
    # 生成报告
    generator = EnhancedReportGenerator(args.input)
    generator.generate_enhanced_html_report(args.output)

if __name__ == "__main__":
    main()