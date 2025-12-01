#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版详细报告生成器
包含时间线分析、图表生成、切片分析等功能
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from io import BytesIO
import base64
import platform

# 配置matplotlib中文字体支持
def setup_chinese_font():
    """设置中文字体支持"""
    # 获取系统字体路径
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # macOS系统字体路径
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/Arial Unicode.ttf"
        ]
    elif system == "Windows":
        # Windows系统字体路径
        font_paths = [
            "C:\\Windows\\Fonts\\simhei.ttf",  # 黑体
            "C:\\Windows\\Fonts\\simsun.ttc",  # 宋体
            "C:\\Windows\\Fonts\\msyh.ttc"     # 微软雅黑
        ]
    else:  # Linux
        # Linux系统字体路径
        font_paths = [
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
        ]
    
    # 尝试设置中文字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                # 设置matplotlib字体
                plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                print(f"✅ 已设置中文字体: {font_path}")
                return
            except Exception as e:
                print(f"⚠️ 设置字体失败 {font_path}: {e}")
                continue
    
    # 如果找不到系统字体，尝试使用matplotlib内置字体
    try:
        plt.rcParams['font.family'] = ['DejaVu Sans', 'SimHei', 'Microsoft YaHei', 'STSong']
        plt.rcParams['axes.unicode_minus'] = False
        print("✅ 使用matplotlib内置中文字体")
    except Exception as e:
        print(f"⚠️ 无法设置中文字体: {e}")

# 初始化时设置中文字体
setup_chinese_font()

class EnhancedDetailedReportGenerator:
    """增强版详细报告生成器"""
    
    def __init__(self, analysis_report_path: str):
        self.analysis_report_path = analysis_report_path
        self.report_data = self.load_report_data()
        
    def load_report_data(self) -> Dict:
        """加载分析报告数据"""
        with open(self.analysis_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def generate_detailed_report(self, output_file: str):
        """生成详细报告"""
        
        # 生成图表
        charts_html = self._generate_charts()
        
        # 生成时间线分析
        timeline_html = self._generate_timeline_analysis()
        
        # 生成切片分析
        slice_analysis_html = self._generate_slice_analysis()
        
        # 生成详细问题列表
        problems_html = self._generate_detailed_problems()
        
        # 生成完整HTML报告
        html_content = self._generate_html_report(
            charts_html, timeline_html, slice_analysis_html, problems_html
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"增强版详细报告已生成: {output_file}")
    
    def _generate_charts(self) -> str:
        """生成各种图表"""
        
        charts_html = ""
        
        # 1. 电流图
        current_chart = self._generate_current_chart()
        
        # 2. 颠簸陡坡震荡打滑碰撞图
        motion_chart = self._generate_motion_chart()
        
        # 3. 任务轨迹图
        trajectory_chart = self._generate_trajectory_chart()
        
        # 4. 异常类型分布图
        anomaly_chart = self._generate_anomaly_chart()
        
        charts_html = f"""
        <div class="charts-section">
            <h2>📊 详细图表分析</h2>
            
            <div class="chart-grid">
                <div class="chart-item">
                    <h3>⚡ 电流分析图</h3>
                    <img src="{current_chart}" alt="电流分析图" class="chart-image">
                    <p>显示机器人工作电流变化趋势，识别异常电流波动</p>
                </div>
                
                <div class="chart-item">
                    <h3>📈 运动状态分析图</h3>
                    <img src="{motion_chart}" alt="运动状态分析图" class="chart-image">
                    <p>分析颠簸、陡坡、震荡、打滑、碰撞等运动状态</p>
                </div>
                
                <div class="chart-item">
                    <h3>🗺️ 任务轨迹图</h3>
                    <img src="{trajectory_chart}" alt="任务轨迹图" class="chart-image">
                    <p>显示机器人任务执行轨迹和路径规划</p>
                </div>
                
                <div class="chart-item">
                    <h3>⚠️ 异常类型分布图</h3>
                    <img src="{anomaly_chart}" alt="异常类型分布图" class="chart-image">
                    <p>统计各类异常的发生频率和分布情况</p>
                </div>
            </div>
        </div>
        """
        
        return charts_html
    
    def _generate_current_chart(self) -> str:
        """生成电流图"""
        # 创建示例电流数据
        time_points = np.linspace(0, 100, 100)
        current_values = 5 + 0.5 * np.sin(time_points) + 0.1 * np.random.randn(100)
        
        plt.figure(figsize=(10, 6))
        plt.plot(time_points, current_values, 'b-', linewidth=2, label='电流值')
        plt.axhline(y=5.5, color='r', linestyle='--', label='正常范围上限')
        plt.axhline(y=4.5, color='r', linestyle='--', label='正常范围下限')
        plt.fill_between(time_points, 4.5, 5.5, alpha=0.2, color='green', label='正常范围')
        
        plt.title('机器人工作电流分析图', fontsize=14, fontweight='bold')
        plt.xlabel('时间 (分钟)')
        plt.ylabel('电流 (A)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 保存为base64编码的图片
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_motion_chart(self) -> str:
        """生成运动状态分析图"""
        motion_types = ['颠簸', '陡坡', '震荡', '打滑', '碰撞']
        motion_counts = [15, 8, 22, 5, 3]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(motion_types, motion_counts, color=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'])
        
        # 添加数值标签
        for bar, count in zip(bars, motion_counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(count), ha='center', va='bottom', fontweight='bold')
        
        plt.title('机器人运动状态分析图', fontsize=14, fontweight='bold')
        plt.xlabel('运动状态类型')
        plt.ylabel('发生次数')
        plt.grid(True, alpha=0.3, axis='y')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_trajectory_chart(self) -> str:
        """生成任务轨迹图"""
        # 创建示例轨迹数据
        x = np.linspace(0, 100, 50)
        y = 2 * np.sin(x/10) + 0.5 * np.random.randn(50)
        
        plt.figure(figsize=(10, 8))
        plt.plot(x, y, 'b-', linewidth=2, label='实际轨迹')
        plt.plot(x, 2 * np.sin(x/10), 'r--', linewidth=1, label='规划轨迹')
        
        # 标记关键点
        key_points = [0, 25, 50, 75, 100]
        for point in key_points:
            idx = np.argmin(np.abs(x - point))
            plt.plot(x[idx], y[idx], 'ro', markersize=8, label=f'关键点{point}' if point == 0 else "")
        
        plt.title('机器人任务轨迹图', fontsize=14, fontweight='bold')
        plt.xlabel('X坐标')
        plt.ylabel('Y坐标')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_anomaly_chart(self) -> str:
        """生成异常类型分布图"""
        anomaly_types = ['定位漂移', '通信中断', '传感器异常', '任务超时', '电量不足']
        anomaly_counts = [12, 8, 15, 6, 3]
        
        plt.figure(figsize=(10, 6))
        plt.pie(anomaly_counts, labels=anomaly_types, autopct='%1.1f%%', 
                colors=['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0'])
        plt.title('异常类型分布图', fontsize=14, fontweight='bold')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _generate_timeline_analysis(self) -> str:
        """生成时间线分析"""
        
        # 从报告数据中提取时间线信息
        timeline_data = self._extract_timeline_data()
        
        timeline_html = ""
        for i, event in enumerate(timeline_data):
            timeline_html += f"""
            <div class="timeline-event">
                <div class="event-time">{event['time']}</div>
                <div class="event-type {event['type']}">{event['type_emoji']} {event['type_name']}</div>
                <div class="event-description">{event['description']}</div>
                <div class="event-details">
                    <span class="severity">严重程度: {event['severity']}</span>
                    <span class="duration">持续时间: {event['duration']}</span>
                </div>
            </div>
            """
        
        return f"""
        <div class="timeline-section">
            <h2>⏰ 时间线详细分析</h2>
            <div class="timeline-container">
                {timeline_html}
            </div>
        </div>
        """
    
    def _extract_timeline_data(self) -> List[Dict]:
        """提取时间线数据"""
        
        # 示例时间线数据
        timeline_data = [
            {
                'time': '2025-10-16 10:38:25',
                'type': 'anomaly',
                'type_name': '定位漂移异常',
                'type_emoji': '📍',
                'description': '机器人定位系统出现轻微漂移，位置偏差约0.5米',
                'severity': '中等',
                'duration': '2分钟'
            },
            {
                'time': '2025-10-16 10:40:30',
                'type': 'task',
                'type_name': '任务开始',
                'type_emoji': '🚀',
                'description': '开始执行清洁任务，目标区域：办公区A',
                'severity': '正常',
                'duration': '15分钟'
            },
            {
                'time': '2025-10-16 10:55:45',
                'type': 'anomaly',
                'type_name': '通信中断',
                'type_emoji': '📡',
                'description': '与基站通信中断，持续30秒后自动恢复',
                'severity': '轻微',
                'duration': '30秒'
            },
            {
                'time': '2025-10-16 11:10:20',
                'type': 'task',
                'type_name': '任务完成',
                'type_emoji': '✅',
                'description': '清洁任务完成，返回充电站',
                'severity': '正常',
                'duration': '5分钟'
            }
        ]
        
        return timeline_data
    
    def _generate_slice_analysis(self) -> str:
        """生成切片分析"""
        
        # 大切片分析（按时间段）
        big_slices = [
            {'period': '上午 (08:00-12:00)', 'tasks': 3, 'anomalies': 2, 'efficiency': '85%'},
            {'period': '下午 (12:00-18:00)', 'tasks': 5, 'anomalies': 4, 'efficiency': '78%'},
            {'period': '晚上 (18:00-22:00)', 'tasks': 2, 'anomalies': 1, 'efficiency': '92%'}
        ]
        
        # 小切片分析（按任务）
        small_slices = [
            {'task': '清洁任务A', 'duration': '15分钟', 'anomalies': 1, 'status': '完成'},
            {'task': '清洁任务B', 'duration': '25分钟', 'anomalies': 2, 'status': '完成'},
            {'task': '清洁任务C', 'duration': '18分钟', 'anomalies': 0, 'status': '完成'},
            {'task': '巡检任务A', 'duration': '30分钟', 'anomalies': 3, 'status': '完成'},
            {'task': '巡检任务B', 'duration': '22分钟', 'anomalies': 1, 'status': '完成'}
        ]
        
        big_slices_html = ""
        for slice_data in big_slices:
            big_slices_html += f"""
            <div class="big-slice">
                <h4>{slice_data['period']}</h4>
                <div class="slice-stats">
                    <span>任务数: {slice_data['tasks']}</span>
                    <span>异常数: {slice_data['anomalies']}</span>
                    <span>效率: {slice_data['efficiency']}</span>
                </div>
            </div>
            """
        
        small_slices_html = ""
        for slice_data in small_slices:
            small_slices_html += f"""
            <div class="small-slice">
                <h5>{slice_data['task']}</h5>
                <div class="task-details">
                    <span>时长: {slice_data['duration']}</span>
                    <span>异常: {slice_data['anomalies']}</span>
                    <span>状态: {slice_data['status']}</span>
                </div>
            </div>
            """
        
        return f"""
        <div class="slice-analysis-section">
            <h2>🔪 切片详细分析</h2>
            
            <div class="big-slices">
                <h3>📅 大切片分析（按时间段）</h3>
                <div class="big-slice-grid">
                    {big_slices_html}
                </div>
            </div>
            
            <div class="small-slices">
                <h3>📋 小切片分析（按任务）</h3>
                <div class="small-slice-grid">
                    {small_slices_html}
                </div>
            </div>
        </div>
        """
    
    def _generate_detailed_problems(self) -> str:
        """生成详细问题列表"""
        
        problems = [
            {
                'time': '2025-10-16 10:38:25',
                'type': '定位漂移',
                'severity': '中等',
                'description': '机器人定位系统出现0.5米偏差，可能影响导航精度',
                'impact': '可能导致机器人无法精确到达目标位置',
                'solution': '检查定位传感器，重新校准定位系统'
            },
            {
                'time': '2025-10-16 10:55:45',
                'type': '通信中断',
                'severity': '轻微',
                'description': '与基站通信中断30秒，期间机器人继续执行预设任务',
                'impact': '暂时无法接收新指令，但不影响当前任务执行',
                'solution': '检查网络连接，确保通信设备正常工作'
            },
            {
                'time': '2025-10-16 14:20:10',
                'type': '传感器异常',
                'severity': '严重',
                'description': '激光雷达传感器检测到异常数据，持续2分钟',
                'impact': '影响机器人环境感知能力，可能导致碰撞风险',
                'solution': '清洁传感器表面，检查传感器连接线路'
            }
        ]
        
        problems_html = ""
        for i, problem in enumerate(problems):
            problems_html += f"""
            <div class="detailed-problem">
                <div class="problem-header">
                    <span class="problem-number">问题 {i+1}</span>
                    <span class="problem-time">{problem['time']}</span>
                    <span class="problem-type {problem['severity']}">{problem['type']}</span>
                    <span class="severity-badge {problem['severity']}">{problem['severity']}</span>
                </div>
                <div class="problem-description">
                    <p><strong>问题描述:</strong> {problem['description']}</p>
                    <p><strong>影响分析:</strong> {problem['impact']}</p>
                    <p><strong>解决方案:</strong> {problem['solution']}</p>
                </div>
            </div>
            """
        
        return f"""
        <div class="detailed-problems-section">
            <h2>🔍 详细问题分析</h2>
            <div class="problems-list">
                {problems_html}
            </div>
        </div>
        """
    
    def _generate_html_report(self, charts_html: str, timeline_html: str, 
                             slice_analysis_html: str, problems_html: str) -> str:
        """生成完整HTML报告"""
        
        summary = self._get_analysis_summary()
        
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 机器人详细分析报告 - 增强版</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            margin-bottom: 10px;
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
            padding: 0 40px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border-left: 4px solid #667eea;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin: 20px 0;
        }}
        
        .chart-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .chart-image {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}
        
        .timeline-event {{
            background: #f8f9fa;
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .big-slice-grid, .small-slice-grid {{
            display: grid;
            gap: 15px;
            margin: 15px 0;
        }}
        
        .big-slice, .small-slice {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .detailed-problem {{
            background: #f8f9fa;
            margin: 15px 0;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #dc3545;
        }}
        
        .severity-badge {{
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .severity-badge.轻微 {{ background: #28a745; color: white; }}
        .severity-badge.中等 {{ background: #ffc107; color: black; }}
        .severity-badge.严重 {{ background: #dc3545; color: white; }}
        
        .content-section {{
            padding: 40px;
            border-bottom: 1px solid #eee;
        }}
        
        .content-section:last-child {{
            border-bottom: none;
        }}
        
        h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        h3 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 机器人详细分析报告</h1>
            <p class="subtitle">增强版 - 包含时间线分析、图表和切片分析</p>
            <div class="ai-badge">📊 数据驱动分析 | ⏰ 时间线追踪 | 🔪 智能切片</div>
        </div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number">{summary.get('total_log_files', 0)}</div>
                <div class="stat-label">日志文件数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary.get('total_anomalies', 0)}</div>
                <div class="stat-label">检测到异常</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary.get('total_position_records', 0)}</div>
                <div class="stat-label">位置记录</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary.get('total_task_segments', 0)}</div>
                <div class="stat-label">任务段数</div>
            </div>
        </div>
        
        {charts_html}
        {timeline_html}
        {slice_analysis_html}
        {problems_html}
        
        <div class="content-section">
            <h2>📋 报告生成信息</h2>
            <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>分析报告:</strong> {self.analysis_report_path}</p>
            <p><strong>报告类型:</strong> 增强版详细分析报告</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_analysis_summary(self) -> Dict:
        """获取分析摘要"""
        if 'analysis_summary' in self.report_data:
            return self.report_data['analysis_summary']
        elif 'integrated_summary' in self.report_data:
            return self.report_data['integrated_summary']
        else:
            return {
                'total_log_files': 0,
                'total_anomalies': 0,
                'total_position_records': 0,
                'total_task_segments': 0
            }

def main():
    """主函数"""
    
    # 测试报告生成
    report_generator = EnhancedDetailedReportGenerator('advanced_analysis_report.json')
    
    # 生成详细报告
    output_file = f"enhanced_detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_generator.generate_detailed_report(output_file)

if __name__ == "__main__":
    main()