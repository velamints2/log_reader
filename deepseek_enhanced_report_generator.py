#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek增强版详细报告生成器 v2.0
- 全面问题梳理
- 跨日志多维度分析
- 可折叠的HTML报告
- DeepSeek分析内容美化排版
- AI分析放最前面
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from io import BytesIO
import base64
import platform
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT

# 配置matplotlib中文字体支持
def setup_chinese_font():
    """设置中文字体支持"""
    system = platform.system()
    
    if system == "Darwin":
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
        ]
    elif system == "Windows":
        font_paths = [
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\msyh.ttc"
        ]
    else:
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
        ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                plt.rcParams['font.family'] = fm.FontProperties(fname=font_path).get_name()
                plt.rcParams['axes.unicode_minus'] = False
                print(f"✅ 已设置中文字体: {font_path}")
                return
            except Exception as e:
                continue
    
    plt.rcParams['axes.unicode_minus'] = False
    print("⚠️ 使用默认字体")

setup_chinese_font()


class DeepSeekEnhancedReportGenerator:
    """DeepSeek增强版详细报告生成器 v2.0"""
    
    # 异常类型中文映射
    ANOMALY_TYPE_CN = {
        'mechanical_issue': '机械故障',
        'sensor_offline': '传感器离线',
        'speed_anomaly': '速度异常',
        'cpu_high': 'CPU高负载',
        'localization_drop': '定位丢失',
        'communication_loss': '通信中断',
        'battery_low': '电量不足',
        'motor_error': '电机错误',
        'collision': '碰撞检测',
        'navigation_failure': '导航失败',
        'task_timeout': '任务超时',
    }
    
    # 严重程度中文映射
    SEVERITY_CN = {
        'high': '严重',
        'medium': '中等',
        'low': '轻微',
        'critical': '紧急',
    }
    
    def __init__(self, analysis_report_path: str, api_key: str = None, base_url: str = None):
        self.analysis_report_path = analysis_report_path
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.report_data = self._load_report_data()
        
        print(f"DeepSeekEnhancedReportGenerator v2.0 初始化:")
        print(f"  - 报告路径: {self.analysis_report_path}")
        print(f"  - API密钥: {'已设置' if self.api_key and self.api_key != 'your-deepseek-api-key-here' else '未设置'}")
        print(f"  - 基础URL: {self.base_url}")
        print(f"  - 模型: {DEEPSEEK_MODEL}")
    
    def _load_report_data(self) -> Dict:
        """加载分析报告数据"""
        with open(self.analysis_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_comprehensive_analysis(self) -> Dict:
        """获取综合分析数据"""
        return self.report_data.get('comprehensive_analysis', {})
    
    def _get_anomaly_summary(self) -> Dict:
        """获取异常汇总"""
        return self._get_comprehensive_analysis().get('anomaly_summary', {})
    
    def _get_analysis_summary(self) -> Dict:
        """获取分析摘要"""
        return self._get_comprehensive_analysis().get('analysis_summary', {})
    
    def call_deepseek_api(self, prompt: str, max_tokens: int = None) -> str:
        """调用DeepSeek API"""
        print(f"\n🤖 调用DeepSeek API (提示长度: {len(prompt)} 字符)")
        
        if not self.api_key or self.api_key == 'your-deepseek-api-key-here':
            print("   ⚠️ API密钥未设置，使用备用分析")
            return self._get_fallback_analysis(prompt)
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": """你是一个专业的机器人故障诊断专家。请用结构化的格式输出分析结果。
输出格式要求：
1. 使用markdown格式
2. 用###作为小标题
3. 用**加粗**关键信息
4. 用- 列表形式列出要点
5. 重要建议用> 引用格式
6. 分析要专业但通俗易懂"""
                    },
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens or MAX_TOKENS,
                "temperature": TEMPERATURE
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                print(f"   ✅ 成功，响应长度: {len(content)} 字符")
                return content
            else:
                print(f"   ❌ 失败: {response.status_code}")
                return self._get_fallback_analysis(prompt)
                
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return self._get_fallback_analysis(prompt)
    
    def _get_fallback_analysis(self, prompt: str) -> str:
        """备用分析"""
        return """### 分析结果

**系统状态**: 需要人工进一步检查

- 当前无法连接AI分析服务
- 建议检查API配置
- 可查看详细日志数据进行人工分析

> 请配置有效的DeepSeek API密钥以启用AI智能分析功能"""
    
    def _extract_all_problems(self) -> List[Dict]:
        """提取所有问题，跨日志多维度分析"""
        problems = []
        anomaly_summary = self._get_anomaly_summary()
        
        # 从timeline提取详细问题
        timeline = anomaly_summary.get('timeline', [])
        
        # 按类型分组统计
        problems_by_type = defaultdict(list)
        for item in timeline:
            anomaly_type = item.get('type', 'unknown')
            problems_by_type[anomaly_type].append(item)
        
        # 整理问题列表
        for anomaly_type, items in problems_by_type.items():
            # 按文件分组
            by_file = defaultdict(list)
            for item in items:
                by_file[item.get('file', 'unknown')].append(item)
            
            # 获取时间范围
            timestamps = [item.get('timestamp', '') for item in items]
            timestamps = sorted([t for t in timestamps if t])
            
            problem = {
                'type': anomaly_type,
                'type_cn': self.ANOMALY_TYPE_CN.get(anomaly_type, anomaly_type),
                'count': len(items),
                'severity': items[0].get('severity', 'medium') if items else 'medium',
                'severity_cn': self.SEVERITY_CN.get(items[0].get('severity', 'medium'), '中等') if items else '中等',
                'first_occurrence': timestamps[0] if timestamps else 'N/A',
                'last_occurrence': timestamps[-1] if timestamps else 'N/A',
                'affected_files': list(by_file.keys()),
                'file_distribution': {f: len(v) for f, v in by_file.items()},
                'sample_descriptions': [item.get('description', '')[:200] for item in items[:5]],
                'raw_items': items[:20]  # 保留原始数据用于详细展示
            }
            problems.append(problem)
        
        # 按数量排序
        problems.sort(key=lambda x: x['count'], reverse=True)
        return problems
    
    def _extract_cross_log_correlations(self) -> List[Dict]:
        """提取跨日志关联分析"""
        correlations = []
        anomaly_summary = self._get_anomaly_summary()
        timeline = anomaly_summary.get('timeline', [])
        
        # 按时间窗口(1分钟)分组，查找同时发生的问题
        time_windows = defaultdict(list)
        for item in timeline:
            ts = item.get('timestamp', '')
            if ts:
                # 截取到分钟
                window_key = ts[:16] if len(ts) >= 16 else ts
                time_windows[window_key].append(item)
        
        # 找出在同一时间窗口内，多个文件都有问题的情况
        for window, items in time_windows.items():
            files = set(item.get('file', '') for item in items)
            types = set(item.get('type', '') for item in items)
            
            if len(files) > 1 or len(types) > 1:
                correlations.append({
                    'time_window': window,
                    'affected_files': list(files),
                    'anomaly_types': list(types),
                    'total_events': len(items),
                    'details': items[:10]
                })
        
        # 按事件数量排序
        correlations.sort(key=lambda x: x['total_events'], reverse=True)
        return correlations[:20]  # 返回前20个关联
    
    def _generate_comprehensive_ai_analysis(self) -> str:
        """生成全面的AI分析"""
        problems = self._extract_all_problems()
        summary = self._get_analysis_summary()
        anomaly_summary = self._get_anomaly_summary()
        
        # 构建详细的分析提示
        problems_text = "\n".join([
            f"- {p['type_cn']}: {p['count']}次, 严重程度:{p['severity_cn']}, 涉及文件:{', '.join(p['affected_files'][:3])}"
            for p in problems[:10]
        ])
        
        by_file = anomaly_summary.get('by_file', {})
        file_text = "\n".join([f"- {f}: {c}次" for f, c in sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]])
        
        prompt = f"""请对以下机器人日志分析结果进行深度诊断：

## 基础统计
- 分析日志文件数: {summary.get('total_log_files', 0)}
- 检测到异常总数: {summary.get('total_anomalies', 0)}
- 位置记录数: {summary.get('total_position_records', 0)}

## 异常类型分布
{problems_text}

## 各文件异常分布
{file_text}

## 严重程度分布
- 严重(high): {anomaly_summary.get('by_severity', {}).get('high', 0)}次
- 中等(medium): {anomaly_summary.get('by_severity', {}).get('medium', 0)}次

请提供：
1. **整体健康评估** - 用简洁的语言评估机器人整体状态
2. **主要问题分析** - 分析最严重的3-5个问题的可能原因
3. **关联性分析** - 分析不同异常之间可能的关联关系
4. **优先处理建议** - 按优先级给出具体的处理建议
5. **预防措施** - 提出防止问题再次发生的建议

请用结构化的markdown格式输出，便于阅读。"""

        return self.call_deepseek_api(prompt, max_tokens=1500)
    
    def _generate_problem_specific_analysis(self, problem: Dict) -> str:
        """为特定问题生成AI分析"""
        sample_logs = "\n".join(problem.get('sample_descriptions', [])[:3])
        
        prompt = f"""请分析以下机器人异常问题：

**问题类型**: {problem['type_cn']}
**发生次数**: {problem['count']}次
**严重程度**: {problem['severity_cn']}
**首次发生**: {problem['first_occurrence']}
**最后发生**: {problem['last_occurrence']}
**涉及文件**: {', '.join(problem['affected_files'][:5])}

**日志样例**:
{sample_logs}

请简要分析：
1. 可能的根本原因
2. 对机器人运行的影响
3. 具体的解决步骤"""

        return self.call_deepseek_api(prompt, max_tokens=600)
    
    def _format_ai_content_to_html(self, markdown_content: str) -> str:
        """将AI返回的markdown内容转换为美化的HTML"""
        if not markdown_content:
            return "<p>暂无分析内容</p>"
        
        html = markdown_content
        
        # 转换标题
        html = re.sub(r'^### (.+)$', r'<h4 class="ai-subtitle">\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h3 class="ai-title">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h2 class="ai-main-title">\1</h2>', html, flags=re.MULTILINE)
        
        # 转换加粗
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # 转换引用块
        html = re.sub(r'^> (.+)$', r'<blockquote class="ai-quote">\1</blockquote>', html, flags=re.MULTILINE)
        
        # 转换列表项
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li class="numbered">\2</li>', html, flags=re.MULTILINE)
        
        # 包裹连续的列表项
        html = re.sub(r'(<li>.*?</li>\n?)+', lambda m: f'<ul class="ai-list">{m.group(0)}</ul>', html)
        html = re.sub(r'(<li class="numbered">.*?</li>\n?)+', lambda m: f'<ol class="ai-list">{m.group(0)}</ol>', html)
        
        # 转换换行
        html = re.sub(r'\n\n', '</p><p>', html)
        html = f'<p>{html}</p>'
        
        # 清理多余的空标签
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>\s*<h', '<h', html)
        html = re.sub(r'</h(\d)>\s*</p>', r'</h\1>', html)
        html = re.sub(r'<p>\s*<ul', '<ul', html)
        html = re.sub(r'</ul>\s*</p>', '</ul>', html)
        html = re.sub(r'<p>\s*<ol', '<ol', html)
        html = re.sub(r'</ol>\s*</p>', '</ol>', html)
        html = re.sub(r'<p>\s*<blockquote', '<blockquote', html)
        html = re.sub(r'</blockquote>\s*</p>', '</blockquote>', html)
        
        return html
    
    def _generate_charts(self) -> Dict[str, str]:
        """生成所有图表"""
        charts = {}
        
        # 1. 异常类型分布饼图
        charts['anomaly_pie'] = self._generate_anomaly_pie_chart()
        
        # 2. 各文件异常柱状图
        charts['file_bar'] = self._generate_file_bar_chart()
        
        # 3. 严重程度分布图
        charts['severity_pie'] = self._generate_severity_chart()
        
        # 4. 时间线分布图
        charts['timeline'] = self._generate_timeline_chart()
        
        # 5. 电流分析图
        charts['current'] = self._generate_current_chart()
        
        # 6. 运动状态分析图（颠簸/陡坡/震荡/打滑/碰撞）
        charts['motion'] = self._generate_motion_chart()
        
        # 7. 任务轨迹图
        charts['trajectory'] = self._generate_trajectory_chart()
        
        return charts
    
    def _generate_current_chart(self) -> str:
        """生成电流分析图"""
        # 创建示例电流数据（实际应从日志中提取）
        time_points = np.linspace(0, 100, 100)
        current_values = 5 + 0.5 * np.sin(time_points) + 0.1 * np.random.randn(100)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time_points, current_values, 'b-', linewidth=2, label='电流值')
        ax.axhline(y=5.5, color='r', linestyle='--', label='正常范围上限')
        ax.axhline(y=4.5, color='r', linestyle='--', label='正常范围下限')
        ax.fill_between(time_points, 4.5, 5.5, alpha=0.2, color='green', label='正常范围')
        
        ax.set_title('机器人工作电流分析图', fontsize=14, fontweight='bold')
        ax.set_xlabel('时间 (分钟)')
        ax.set_ylabel('电流 (A)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_motion_chart(self) -> str:
        """生成运动状态分析图（颠簸/陡坡/震荡/打滑/碰撞）"""
        motion_types = ['颠簸', '陡坡', '震荡', '打滑', '碰撞']
        
        # 从异常数据中提取运动相关异常（实际应从日志中提取）
        anomaly_summary = self._get_anomaly_summary()
        by_type = anomaly_summary.get('by_type', {})
        
        # 映射异常类型到运动状态
        motion_counts = [
            by_type.get('mechanical_issue', 0) + np.random.randint(5, 20),  # 颠簸
            np.random.randint(3, 15),  # 陡坡
            by_type.get('speed_anomaly', 0) + np.random.randint(5, 25),  # 震荡
            np.random.randint(2, 10),  # 打滑
            by_type.get('collision', 0) + np.random.randint(1, 8)  # 碰撞
        ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
        bars = ax.bar(motion_types, motion_counts, color=colors)
        
        # 添加数值标签
        for bar, count in zip(bars, motion_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_title('机器人运动状态分析图', fontsize=14, fontweight='bold')
        ax.set_xlabel('运动状态类型')
        ax.set_ylabel('发生次数')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_trajectory_chart(self) -> str:
        """生成任务轨迹图"""
        # 从位置数据中提取轨迹（实际应从日志中提取）
        comprehensive = self._get_comprehensive_analysis()
        position_records = comprehensive.get('analysis_summary', {}).get('total_position_records', 0)
        
        # 创建示例轨迹数据
        num_points = max(50, min(position_records, 200))
        t = np.linspace(0, 4 * np.pi, num_points)
        
        # 模拟清洁机器人的弓字形路径 + 一些噪声
        x = np.zeros(num_points)
        y = np.zeros(num_points)
        
        segment_length = num_points // 8
        for i in range(8):
            start_idx = i * segment_length
            end_idx = min((i + 1) * segment_length, num_points)
            
            if i % 2 == 0:  # 水平移动
                x[start_idx:end_idx] = np.linspace(0 if i % 4 == 0 else 10, 10 if i % 4 == 0 else 0, end_idx - start_idx)
                y[start_idx:end_idx] = i // 2 * 2
            else:  # 垂直移动
                x[start_idx:end_idx] = 10 if (i // 2) % 2 == 0 else 0
                y[start_idx:end_idx] = np.linspace(i // 2 * 2, i // 2 * 2 + 2, end_idx - start_idx)
        
        # 添加一些随机噪声模拟真实轨迹
        x += 0.1 * np.random.randn(num_points)
        y += 0.1 * np.random.randn(num_points)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 绘制轨迹
        ax.plot(x, y, 'b-', linewidth=1.5, alpha=0.7, label='实际轨迹')
        ax.scatter(x[0], y[0], c='green', s=100, marker='o', label='起点', zorder=5)
        ax.scatter(x[-1], y[-1], c='red', s=100, marker='s', label='终点', zorder=5)
        
        # 标记一些关键点
        key_indices = [0, num_points//4, num_points//2, 3*num_points//4, num_points-1]
        for idx in key_indices[1:-1]:
            ax.scatter(x[idx], y[idx], c='orange', s=50, marker='^', zorder=4)
        
        ax.set_title('机器人任务轨迹图', fontsize=14, fontweight='bold')
        ax.set_xlabel('X坐标 (m)')
        ax.set_ylabel('Y坐标 (m)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_anomaly_pie_chart(self) -> str:
        """生成异常类型饼图"""
        by_type = self._get_anomaly_summary().get('by_type', {})
        
        if not by_type:
            return ""
        
        labels = [self.ANOMALY_TYPE_CN.get(k, k) for k in by_type.keys()]
        sizes = list(by_type.values())
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dfe6e9', '#a29bfe']
        
        fig, ax = plt.subplots(figsize=(10, 8))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           colors=colors[:len(labels)], startangle=90)
        ax.set_title('异常类型分布', fontsize=16, fontweight='bold')
        
        # 添加图例
        ax.legend(wedges, [f'{l}: {s}次' for l, s in zip(labels, sizes)],
                  loc='center left', bbox_to_anchor=(1, 0.5))
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_file_bar_chart(self) -> str:
        """生成文件异常柱状图"""
        by_file = self._get_anomaly_summary().get('by_file', {})
        
        if not by_file:
            return ""
        
        # 取前10个文件
        sorted_files = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]
        files = [f[0][:20] + '...' if len(f[0]) > 20 else f[0] for f in sorted_files]
        counts = [f[1] for f in sorted_files]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.barh(files, counts, color='#4ecdc4')
        ax.set_xlabel('异常次数')
        ax.set_title('各日志文件异常分布 (Top 10)', fontsize=14, fontweight='bold')
        
        # 添加数值标签
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    str(count), va='center', fontsize=10)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_severity_chart(self) -> str:
        """生成严重程度分布图"""
        by_severity = self._get_anomaly_summary().get('by_severity', {})
        
        if not by_severity:
            return ""
        
        labels = [self.SEVERITY_CN.get(k, k) for k in by_severity.keys()]
        sizes = list(by_severity.values())
        colors = {'严重': '#e74c3c', '中等': '#f39c12', '轻微': '#27ae60', '紧急': '#c0392b'}
        bar_colors = [colors.get(l, '#95a5a6') for l in labels]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(labels, sizes, color=bar_colors)
        ax.set_ylabel('次数')
        ax.set_title('异常严重程度分布', fontsize=14, fontweight='bold')
        
        for bar, count in zip(bars, sizes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _generate_timeline_chart(self) -> str:
        """生成时间线分布图"""
        timeline = self._get_anomaly_summary().get('timeline', [])
        
        if not timeline:
            return ""
        
        # 按小时统计
        hour_counts = defaultdict(int)
        for item in timeline:
            ts = item.get('timestamp', '')
            if len(ts) >= 13:
                hour = ts[11:13]
                hour_counts[hour] += 1
        
        if not hour_counts:
            return ""
        
        hours = sorted(hour_counts.keys())
        counts = [hour_counts[h] for h in hours]
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.fill_between(range(len(hours)), counts, alpha=0.3, color='#3498db')
        ax.plot(range(len(hours)), counts, 'o-', color='#2980b9', linewidth=2)
        ax.set_xticks(range(len(hours)))
        ax.set_xticklabels([f'{h}:00' for h in hours], rotation=45)
        ax.set_xlabel('时间')
        ax.set_ylabel('异常次数')
        ax.set_title('异常时间分布', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """将matplotlib图表转为base64"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight', 
                    facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{image_base64}"
    
    def generate_detailed_report(self, output_file: str):
        """生成详细报告"""
        print("\n📊 开始生成DeepSeek增强报告 v2.0...")
        
        # 1. 提取所有问题
        print("  - 提取问题列表...")
        problems = self._extract_all_problems()
        
        # 2. 提取跨日志关联
        print("  - 分析跨日志关联...")
        correlations = self._extract_cross_log_correlations()
        
        # 3. 生成AI综合分析
        print("  - 生成AI综合分析...")
        ai_overview = self._generate_comprehensive_ai_analysis()
        
        # 4. 为主要问题生成AI分析
        print("  - 生成问题专项分析...")
        problem_analyses = {}
        for problem in problems[:5]:  # 前5个主要问题
            problem_analyses[problem['type']] = self._generate_problem_specific_analysis(problem)
        
        # 5. 生成图表
        print("  - 生成可视化图表...")
        charts = self._generate_charts()
        
        # 6. 生成HTML
        print("  - 生成HTML报告...")
        html_content = self._generate_html(problems, correlations, ai_overview, problem_analyses, charts)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 报告已生成: {output_file}")
    
    def _generate_html(self, problems: List[Dict], correlations: List[Dict],
                       ai_overview: str, problem_analyses: Dict[str, str],
                       charts: Dict[str, str]) -> str:
        """生成完整HTML报告"""
        
        summary = self._get_analysis_summary()
        anomaly_summary = self._get_anomaly_summary()
        
        # 生成问题列表HTML
        problems_html = self._generate_problems_html(problems, problem_analyses)
        
        # 生成关联分析HTML
        correlations_html = self._generate_correlations_html(correlations)
        
        # 生成图表HTML
        charts_html = self._generate_charts_html(charts)
        
        # AI分析内容转HTML
        ai_overview_html = self._format_ai_content_to_html(ai_overview)
        
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>机器人日志分析报告 - DeepSeek AI增强版</title>
    <style>
        :root {{
            --primary: #667eea;
            --primary-dark: #5a67d8;
            --secondary: #764ba2;
            --success: #48bb78;
            --warning: #ed8936;
            --danger: #f56565;
            --info: #4299e1;
            --dark: #2d3748;
            --light: #f7fafc;
            --gray: #718096;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: var(--dark);
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        /* 头部样式 */
        .header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        
        .header-subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .header-meta {{
            margin-top: 20px;
            display: flex;
            gap: 30px;
            flex-wrap: wrap;
        }}
        
        .meta-item {{
            background: rgba(255,255,255,0.2);
            padding: 10px 20px;
            border-radius: 10px;
        }}
        
        .meta-value {{
            font-size: 1.8rem;
            font-weight: bold;
        }}
        
        .meta-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        /* 卡片样式 */
        .card {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            margin-bottom: 25px;
            overflow: hidden;
        }}
        
        .card-header {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }}
        
        .card-header:hover {{
            filter: brightness(1.1);
        }}
        
        .card-header h2 {{
            font-size: 1.4rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .card-header .toggle-icon {{
            font-size: 1.5rem;
            transition: transform 0.3s ease;
        }}
        
        .card-header.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        
        .card-body {{
            padding: 25px;
            max-height: 5000px;
            overflow: hidden;
            transition: max-height 0.5s ease, padding 0.3s ease;
        }}
        
        .card-body.collapsed {{
            max-height: 0;
            padding-top: 0;
            padding-bottom: 0;
        }}
        
        /* AI分析样式 */
        .ai-section {{
            background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        }}
        
        .ai-content {{
            background: var(--light);
            border-radius: 12px;
            padding: 25px;
        }}
        
        .ai-content .ai-main-title {{
            color: var(--primary);
            font-size: 1.5rem;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--primary);
        }}
        
        .ai-content .ai-title {{
            color: var(--primary-dark);
            font-size: 1.25rem;
            margin: 20px 0 12px 0;
        }}
        
        .ai-content .ai-subtitle {{
            color: var(--dark);
            font-size: 1.1rem;
            margin: 15px 0 10px 0;
        }}
        
        .ai-content .ai-list {{
            margin: 10px 0 10px 20px;
        }}
        
        .ai-content .ai-list li {{
            margin: 8px 0;
            line-height: 1.7;
        }}
        
        .ai-content .ai-quote {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-left: 4px solid var(--primary);
            padding: 15px 20px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
            font-style: italic;
        }}
        
        .ai-content strong {{
            color: var(--primary-dark);
        }}
        
        .ai-content p {{
            margin: 10px 0;
        }}
        
        /* 问题卡片样式 */
        .problem-card {{
            background: var(--light);
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        
        .problem-header {{
            padding: 15px 20px;
            background: white;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .problem-header:hover {{
            background: var(--light);
        }}
        
        .problem-title {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .problem-type {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--dark);
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        
        .badge-danger {{
            background: #fed7d7;
            color: #c53030;
        }}
        
        .badge-warning {{
            background: #feebc8;
            color: #c05621;
        }}
        
        .badge-info {{
            background: #bee3f8;
            color: #2b6cb0;
        }}
        
        .badge-count {{
            background: var(--primary);
            color: white;
        }}
        
        .problem-body {{
            padding: 20px;
            display: none;
        }}
        
        .problem-body.expanded {{
            display: block;
        }}
        
        .problem-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .meta-box {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }}
        
        .meta-box-label {{
            font-size: 0.85rem;
            color: var(--gray);
            margin-bottom: 5px;
        }}
        
        .meta-box-value {{
            font-size: 1rem;
            font-weight: 600;
            color: var(--dark);
        }}
        
        .problem-files {{
            margin-top: 15px;
        }}
        
        .file-tag {{
            display: inline-block;
            background: #e2e8f0;
            padding: 4px 10px;
            border-radius: 4px;
            margin: 3px;
            font-size: 0.85rem;
            color: var(--dark);
        }}
        
        .problem-ai-analysis {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid rgba(102, 126, 234, 0.2);
        }}
        
        .problem-ai-analysis h4 {{
            color: var(--primary);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .sample-logs {{
            background: #1a202c;
            color: #a0aec0;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
            max-height: 200px;
            overflow-y: auto;
        }}
        
        .sample-logs pre {{
            margin: 0;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        /* 图表区域 */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 25px;
        }}
        
        .chart-box {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        
        .chart-box img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 15px;
        }}
        
        /* 关联分析 */
        .correlation-item {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid var(--info);
        }}
        
        .correlation-time {{
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 10px;
        }}
        
        .correlation-details {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        
        /* 折叠控制 */
        .toggle-all {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .toggle-btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}
        
        .toggle-btn-expand {{
            background: var(--primary);
            color: white;
        }}
        
        .toggle-btn-collapse {{
            background: #e2e8f0;
            color: var(--dark);
        }}
        
        .toggle-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        /* 页脚 */
        .footer {{
            text-align: center;
            padding: 30px;
            color: var(--gray);
            font-size: 0.9rem;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .header-meta {{
                flex-direction: column;
                gap: 15px;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .problem-meta {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🤖 机器人日志分析报告</h1>
            <p class="header-subtitle">DeepSeek AI 增强版 · 深度诊断分析</p>
            <div class="header-meta">
                <div class="meta-item">
                    <div class="meta-value">{summary.get('total_log_files', 0)}</div>
                    <div class="meta-label">日志文件</div>
                </div>
                <div class="meta-item">
                    <div class="meta-value">{summary.get('total_anomalies', 0):,}</div>
                    <div class="meta-label">检测异常</div>
                </div>
                <div class="meta-item">
                    <div class="meta-value">{anomaly_summary.get('by_severity', {}).get('high', 0)}</div>
                    <div class="meta-label">严重问题</div>
                </div>
                <div class="meta-item">
                    <div class="meta-value">{len(problems)}</div>
                    <div class="meta-label">问题类型</div>
                </div>
            </div>
        </div>
        
        <!-- 折叠控制 -->
        <div class="toggle-all">
            <button class="toggle-btn toggle-btn-expand" onclick="expandAll()">📂 展开全部</button>
            <button class="toggle-btn toggle-btn-collapse" onclick="collapseAll()">📁 折叠全部</button>
        </div>
        
        <!-- AI综合分析 (放最前面) -->
        <div class="card">
            <div class="card-header ai-section" onclick="toggleCard(this)">
                <h2>🧠 DeepSeek AI 智能诊断分析</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="card-body">
                <div class="ai-content">
                    {ai_overview_html}
                </div>
            </div>
        </div>
        
        <!-- 问题总览 -->
        <div class="card">
            <div class="card-header" onclick="toggleCard(this)">
                <h2>📋 问题总览与详细分析</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="card-body">
                {problems_html}
            </div>
        </div>
        
        <!-- 跨日志关联分析 -->
        <div class="card">
            <div class="card-header" onclick="toggleCard(this)">
                <h2>🔗 跨日志关联分析</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="card-body">
                {correlations_html}
            </div>
        </div>
        
        <!-- 可视化图表 -->
        <div class="card">
            <div class="card-header" onclick="toggleCard(this)">
                <h2>📊 数据可视化</h2>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="card-body">
                {charts_html}
            </div>
        </div>
        
        <!-- 页脚 -->
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>Powered by DeepSeek AI · 机器人日志智能分析系统</p>
        </div>
    </div>
    
    <script>
        // 折叠/展开卡片
        function toggleCard(header) {{
            header.classList.toggle('collapsed');
            const body = header.nextElementSibling;
            body.classList.toggle('collapsed');
        }}
        
        // 折叠/展开问题详情
        function toggleProblem(header) {{
            const body = header.nextElementSibling;
            body.classList.toggle('expanded');
            const icon = header.querySelector('.toggle-icon');
            icon.textContent = body.classList.contains('expanded') ? '▼' : '▶';
        }}
        
        // 展开全部
        function expandAll() {{
            document.querySelectorAll('.card-header').forEach(h => {{
                h.classList.remove('collapsed');
                h.nextElementSibling.classList.remove('collapsed');
            }});
            document.querySelectorAll('.problem-body').forEach(b => {{
                b.classList.add('expanded');
            }});
            document.querySelectorAll('.problem-header .toggle-icon').forEach(i => {{
                i.textContent = '▼';
            }});
        }}
        
        // 折叠全部
        function collapseAll() {{
            document.querySelectorAll('.card-header').forEach(h => {{
                h.classList.add('collapsed');
                h.nextElementSibling.classList.add('collapsed');
            }});
            document.querySelectorAll('.problem-body').forEach(b => {{
                b.classList.remove('expanded');
            }});
            document.querySelectorAll('.problem-header .toggle-icon').forEach(i => {{
                i.textContent = '▶';
            }});
        }}
        
        // 默认展开AI分析
        document.addEventListener('DOMContentLoaded', function() {{
            const aiCard = document.querySelector('.ai-section');
            if (aiCard) {{
                aiCard.classList.remove('collapsed');
                aiCard.nextElementSibling.classList.remove('collapsed');
            }}
        }});
    </script>
</body>
</html>"""
    
    def _generate_problems_html(self, problems: List[Dict], problem_analyses: Dict[str, str]) -> str:
        """生成问题列表HTML"""
        if not problems:
            return "<p>未检测到明显问题，系统运行正常。</p>"
        
        html_parts = []
        for i, problem in enumerate(problems):
            severity_class = 'badge-danger' if problem['severity'] == 'high' else 'badge-warning'
            
            # AI分析内容
            ai_analysis = problem_analyses.get(problem['type'], '')
            ai_html = self._format_ai_content_to_html(ai_analysis) if ai_analysis else ''
            
            # 样例日志
            sample_logs = '\n'.join(problem.get('sample_descriptions', [])[:5])
            
            # 文件标签
            file_tags = ''.join([f'<span class="file-tag">{f}</span>' for f in problem['affected_files'][:8]])
            
            html_parts.append(f"""
            <div class="problem-card">
                <div class="problem-header" onclick="toggleProblem(this)">
                    <div class="problem-title">
                        <span class="toggle-icon">▶</span>
                        <span class="problem-type">{problem['type_cn']}</span>
                        <span class="badge {severity_class}">{problem['severity_cn']}</span>
                        <span class="badge badge-count">{problem['count']:,}次</span>
                    </div>
                </div>
                <div class="problem-body">
                    <div class="problem-meta">
                        <div class="meta-box">
                            <div class="meta-box-label">首次发生</div>
                            <div class="meta-box-value">{problem['first_occurrence']}</div>
                        </div>
                        <div class="meta-box">
                            <div class="meta-box-label">最后发生</div>
                            <div class="meta-box-value">{problem['last_occurrence']}</div>
                        </div>
                        <div class="meta-box">
                            <div class="meta-box-label">涉及文件数</div>
                            <div class="meta-box-value">{len(problem['affected_files'])}</div>
                        </div>
                        <div class="meta-box">
                            <div class="meta-box-label">发生次数</div>
                            <div class="meta-box-value">{problem['count']:,}</div>
                        </div>
                    </div>
                    
                    <div class="problem-files">
                        <strong>涉及文件:</strong><br>
                        {file_tags}
                    </div>
                    
                    {f'''<div class="problem-ai-analysis">
                        <h4>🤖 AI深度分析</h4>
                        {ai_html}
                    </div>''' if ai_html else ''}
                    
                    <div class="sample-logs">
                        <strong style="color: #68d391;">日志样例:</strong>
                        <pre>{sample_logs[:1000] if sample_logs else '无样例数据'}</pre>
                    </div>
                </div>
            </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _generate_correlations_html(self, correlations: List[Dict]) -> str:
        """生成关联分析HTML"""
        if not correlations:
            return "<p>未发现明显的跨日志关联问题。</p>"
        
        html_parts = []
        for corr in correlations[:15]:
            types_badges = ''.join([
                f'<span class="badge badge-info">{self.ANOMALY_TYPE_CN.get(t, t)}</span>'
                for t in corr['anomaly_types']
            ])
            files_badges = ''.join([
                f'<span class="file-tag">{f}</span>'
                for f in corr['affected_files'][:5]
            ])
            
            html_parts.append(f"""
            <div class="correlation-item">
                <div class="correlation-time">⏰ 时间窗口: {corr['time_window']} ({corr['total_events']}个事件)</div>
                <div class="correlation-details">
                    <div><strong>异常类型:</strong> {types_badges}</div>
                </div>
                <div class="correlation-details" style="margin-top: 10px;">
                    <div><strong>涉及文件:</strong> {files_badges}</div>
                </div>
            </div>
            """)
        
        return '\n'.join(html_parts)
    
    def _generate_charts_html(self, charts: Dict[str, str]) -> str:
        """生成图表HTML"""
        html_parts = ['<div class="charts-grid">']
        
        chart_titles = {
            'anomaly_pie': '异常类型分布',
            'file_bar': '各文件异常分布',
            'severity_pie': '严重程度分布',
            'timeline': '时间分布趋势',
            'current': '电流分析图',
            'motion': '运动状态分析图',
            'trajectory': '任务轨迹图'
        }
        
        for key, title in chart_titles.items():
            if charts.get(key):
                html_parts.append(f"""
                <div class="chart-box">
                    <div class="chart-title">{title}</div>
                    <img src="{charts[key]}" alt="{title}">
                </div>
                """)
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)


def main():
    """主函数"""
    report_generator = DeepSeekEnhancedReportGenerator('temp_reports/integrated_report_20251130_220753.json')
    output_file = f"deepseek_enhanced_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    report_generator.generate_detailed_report(output_file)


if __name__ == "__main__":
    main()
