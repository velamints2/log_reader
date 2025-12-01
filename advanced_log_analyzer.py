#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级机器人日志分析系统
功能：
1. 日志分段与任务识别
2. 定位与状态分析  
3. 异常检测与事件报告
4. 投诉问题定位（停机点分析）
5. 报告生成
6. 历史追溯分析
"""

import os
import re
import json
import glob
from datetime import datetime, timedelta
from collections import defaultdict, deque
import argparse
import logging
from typing import Dict, List, Tuple, Optional, Any

class RobotLogAnalyzer:
    """高级机器人日志分析器"""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_files = []
        self.task_segments = []
        self.position_data = []
        self.anomalies = []
        self.system_status = {}
        
        # 任务阶段识别模式
        self.task_patterns = {
            'task_start': [
                r'wait_for_delivery_task entry',
                r'任务开始',
                r'clean.*start',
                r'mission.*start'
            ],
            'task_end': [
                r'finish task',
                r'任务结束', 
                r'clean.*finish',
                r'mission.*complete',
                r'navigation no task'
            ],
            'charging': [
                r'charging',
                r'充电',
                r'charge station',
                r'电桩'
            ],
            'debugging': [
                r'debug',
                r'调试',
                r'test mode'
            ],
            'map_maintenance': [
                r'map.*maintenance',
                r'地图维护',
                r'slam.*build'
            ],
            'idle': [
                r'idle',
                r'闲置',
                r'waiting'
            ]
        }
        
        # 异常检测模式
        self.anomaly_patterns = {
            'sensor_offline': [
                r'sensor.*offline',
                r'传感器.*掉线',
                r'motor offline',
                r'get transform.*fail'
            ],
            'mechanical_issue': [
                r'脚落异常',
                r'机械.*异常',
                r'collision',
                r'碰撞'
            ],
            'cpu_high': [
                r'cpu.*load.*[789]\d',
                r'cpu.*[789]\d%',
                r'cpu.*100%'
            ],
            'speed_anomaly': [
                r'速度异常',
                r'speed.*anomaly',
                r'VCLra',
                r'Ara'
            ],
            'localization_drop': [
                r'定位.*下降',
                r'localization.*drop',
                r'score.*0'
            ]
        }
        
        # 位置信息提取模式
        self.position_patterns = {
            'slam_pose': r'Slam pose: \[([-\d.]+),([-\d.]+),([-\d.]+)\]',
            'odom_pose': r'pose\(([-\d.]+),([-\d.]+),([-\d.]+)\)',
            'charge_station': r'Charge station pose.*\[([-\d.]+),([-\d.]+)\]',
            'goal_pose': r'goal_pose=\(([-\d.]+),([-\d.]+)\)'
        }
        
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志记录"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def discover_log_files(self):
        """发现所有日志文件"""
        self.logger.info("正在发现日志文件...")
        patterns = [
            '*.log',
            '*.txt',
            '*.INFO',
            '*.WARNING',
            '*.ERROR'
        ]
        
        for pattern in patterns:
            files = glob.glob(os.path.join(self.log_dir, pattern))
            self.log_files.extend(files)
        
        self.logger.info(f"发现 {len(self.log_files)} 个日志文件")
        return self.log_files
    
    def parse_timestamp(self, line: str) -> Optional[datetime]:
        """解析时间戳"""
        timestamp_patterns = [
            # 标准格式: 2025-10-16 10:38:24
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            # ROS格式: [1760683956.753609073]
            r'\[(\d+)\.(\d+)\]',
            # 其他格式: 2025-10-12 00:00:03:207
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3})'
        ]
        
        for pattern in timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(1)
                try:
                    if ':' in timestamp_str and timestamp_str.count(':') == 2:
                        return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    elif timestamp_str.count(':') == 3:
                        return datetime.strptime(timestamp_str[:19], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
        
        return None
    
    def extract_position_info(self, line: str, timestamp: datetime) -> Optional[Dict]:
        """提取位置信息"""
        for pattern_name, pattern in self.position_patterns.items():
            match = re.search(pattern, line)
            if match:
                try:
                    if pattern_name == 'slam_pose':
                        x, y, z = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'type': 'slam',
                            'x': x,
                            'y': y,
                            'z': z,
                            'source': pattern_name
                        }
                    elif pattern_name == 'odom_pose':
                        x, y, z = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'type': 'odometry',
                            'x': x,
                            'y': y,
                            'z': z,
                            'source': pattern_name
                        }
                    elif pattern_name in ['charge_station', 'goal_pose']:
                        x, y = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'type': 'reference',
                            'x': x,
                            'y': y,
                            'source': pattern_name
                        }
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def detect_task_phase(self, line: str, timestamp: datetime) -> Optional[str]:
        """检测任务阶段"""
        for phase, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return phase
        
        return None
    
    def detect_anomalies(self, line: str, timestamp: datetime) -> List[Dict]:
        """检测异常事件"""
        anomalies = []
        
        for anomaly_type, patterns in self.anomaly_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    anomaly = {
                        'timestamp': timestamp,
                        'type': anomaly_type,
                        'description': line.strip(),
                        'severity': self.assess_anomaly_severity(anomaly_type, line)
                    }
                    anomalies.append(anomaly)
        
        return anomalies
    
    def assess_anomaly_severity(self, anomaly_type: str, line: str) -> str:
        """评估异常严重程度"""
        severity_map = {
            'sensor_offline': 'medium',
            'mechanical_issue': 'high',
            'cpu_high': 'high',
            'speed_anomaly': 'medium',
            'localization_drop': 'high'
        }
        
        base_severity = severity_map.get(anomaly_type, 'low')
        
        # 根据具体内容调整严重程度
        if 'ERROR' in line:
            return 'high'
        elif 'WARN' in line:
            return 'medium'
        
        return base_severity
    
    def analyze_log_file(self, file_path: str):
        """分析单个日志文件"""
        self.logger.info(f"正在分析文件: {os.path.basename(file_path)}")
        
        current_task = None
        task_start_time = None
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                timestamp = self.parse_timestamp(line)
                if not timestamp:
                    continue
                
                # 检测任务阶段
                phase = self.detect_task_phase(line, timestamp)
                if phase:
                    if phase in ['task_start'] and not current_task:
                        current_task = {
                            'start_time': timestamp,
                            'type': 'task',
                            'file': os.path.basename(file_path),
                            'events': []
                        }
                        task_start_time = timestamp
                    elif phase in ['task_end'] and current_task:
                        current_task['end_time'] = timestamp
                        current_task['duration'] = (timestamp - task_start_time).total_seconds()
                        self.task_segments.append(current_task)
                        current_task = None
                        task_start_time = None
                
                # 提取位置信息
                position = self.extract_position_info(line, timestamp)
                if position:
                    self.position_data.append(position)
                
                # 检测异常
                detected_anomalies = self.detect_anomalies(line, timestamp)
                self.anomalies.extend(detected_anomalies)
                
                # 记录事件到当前任务
                if current_task:
                    event = {
                        'timestamp': timestamp,
                        'line': line.strip(),
                        'position': position,
                        'anomalies': detected_anomalies
                    }
                    current_task['events'].append(event)
    
    def analyze_all_logs(self):
        """分析所有日志文件"""
        self.discover_log_files()
        
        for file_path in self.log_files:
            try:
                self.analyze_log_file(file_path)
            except Exception as e:
                self.logger.error(f"分析文件 {file_path} 时出错: {e}")
        
        self.logger.info("日志分析完成")
    
    def identify_charging_station_proximity(self, position: Dict) -> str:
        """识别充电站接近程度"""
        # 从位置数据中查找充电站位置
        charge_stations = [p for p in self.position_data if p['type'] == 'reference']
        
        if not charge_stations:
            return 'unknown'
        
        # 使用最近的充电站作为参考
        nearest_station = charge_stations[0]  # 简化处理
        
        if 'x' not in position or 'y' not in position:
            return 'unknown'
        
        distance = ((position['x'] - nearest_station['x']) ** 2 + 
                   (position['y'] - nearest_station['y']) ** 2) ** 0.5
        
        if distance < 1.0:
            return 'on_charger'
        elif distance < 3.0:
            return 'near_charger'
        else:
            return 'away_from_charger'
    
    def analyze_localization_quality(self):
        """分析定位质量"""
        localization_scores = []
        
        for position in self.position_data:
            if position['type'] == 'slam':
                # 简化的定位质量评估
                score = 100  # 默认高分
                
                # 根据位置变化稳定性评估
                localization_scores.append({
                    'timestamp': position['timestamp'],
                    'score': score,
                    'position': position
                })
        
        return localization_scores
    
    def detect_stop_points(self, time_window_minutes: int = 10):
        """检测停机点"""
        stop_points = []
        position_window = deque()
        
        # 按时间排序位置数据
        sorted_positions = sorted(self.position_data, key=lambda x: x['timestamp'])
        
        for i, position in enumerate(sorted_positions):
            position_window.append(position)
            
            # 移除超出时间窗口的数据
            while position_window and (position['timestamp'] - position_window[0]['timestamp']).total_seconds() > time_window_minutes * 60:
                position_window.popleft()
            
            # 检查是否停止运动
            if len(position_window) >= 5:  # 至少有5个位置点
                positions = list(position_window)
                
                # 计算位置变化
                x_changes = [abs(positions[j]['x'] - positions[j-1]['x']) for j in range(1, len(positions))]
                y_changes = [abs(positions[j]['y'] - positions[j-1]['y']) for j in range(1, len(positions))]
                
                avg_x_change = sum(x_changes) / len(x_changes)
                avg_y_change = sum(y_changes) / len(y_changes)
                
                # 如果平均变化很小，认为机器人停止
                if avg_x_change < 0.01 and avg_y_change < 0.01:
                    stop_point = {
                        'timestamp': position['timestamp'],
                        'position': position,
                        'duration_minutes': time_window_minutes,
                        'avg_movement': (avg_x_change + avg_y_change) / 2
                    }
                    stop_points.append(stop_point)
        
        return stop_points
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合报告"""
        report = {
            'analysis_summary': {
                'total_log_files': len(self.log_files),
                'total_task_segments': len(self.task_segments),
                'total_position_records': len(self.position_data),
                'total_anomalies': len(self.anomalies),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'task_overview': self.analyze_task_overview(),
            'localization_analysis': self.analyze_localization_quality(),
            'anomaly_summary': self.analyze_anomalies(),
            'stop_point_analysis': self.detect_stop_points(),
            'historical_trace_analysis': self.perform_historical_trace(),
            'recommendations': self.generate_recommendations()
        }
        
        return report
    
    def analyze_task_overview(self) -> Dict:
        """分析任务概览"""
        task_stats = {
            'total_tasks': len(self.task_segments),
            'total_duration_hours': sum(task.get('duration', 0) for task in self.task_segments) / 3600,
            'avg_task_duration_minutes': 0,
            'task_types': defaultdict(int),
            'task_timeline': []
        }
        
        if self.task_segments:
            task_stats['avg_task_duration_minutes'] = (
                sum(task.get('duration', 0) for task in self.task_segments) / 
                len(self.task_segments) / 60
            )
        
        for task in self.task_segments:
            task_stats['task_types'][task.get('type', 'unknown')] += 1
            task_stats['task_timeline'].append({
                'start': task['start_time'].isoformat(),
                'end': task.get('end_time', task['start_time']).isoformat(),
                'duration_minutes': task.get('duration', 0) / 60,
                'file': task['file']
            })
        
        return task_stats
    
    def analyze_anomalies(self) -> Dict:
        """分析异常统计"""
        anomaly_stats = {
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int),
            'timeline': [],
            'most_common': []
        }
        
        for anomaly in self.anomalies:
            anomaly_stats['by_type'][anomaly['type']] += 1
            anomaly_stats['by_severity'][anomaly['severity']] += 1
            anomaly_stats['timeline'].append({
                'timestamp': anomaly['timestamp'].isoformat(),
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'description': anomaly['description'][:100]  # 截断描述
            })
        
        # 找出最常见的异常类型
        if anomaly_stats['by_type']:
            anomaly_stats['most_common'] = sorted(
                anomaly_stats['by_type'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        
        return anomaly_stats
    
    def perform_historical_trace(self, lookback_tasks: int = 2) -> Dict:
        """执行历史追溯分析"""
        if not self.task_segments:
            return {'message': '没有发现任务数据'}
        
        # 按时间排序任务
        sorted_tasks = sorted(self.task_segments, key=lambda x: x['start_time'])
        
        trace_analysis = {
            'total_tasks_analyzed': len(sorted_tasks),
            'task_sequences': [],
            'cross_task_anomalies': []
        }
        
        # 分析连续任务序列
        for i in range(len(sorted_tasks)):
            if i >= lookback_tasks:
                sequence = sorted_tasks[i-lookback_tasks:i+1]
                sequence_analysis = {
                    'sequence_id': f'tasks_{i-lookback_tasks+1}_to_{i+1}',
                    'tasks': [],
                    'total_duration_hours': 0,
                    'anomaly_count': 0
                }
                
                for task in sequence:
                    task_anomalies = sum(1 for event in task.get('events', []) 
                                      if event.get('anomalies'))
                    sequence_analysis['tasks'].append({
                        'start_time': task['start_time'].isoformat(),
                        'duration_minutes': task.get('duration', 0) / 60,
                        'anomaly_count': task_anomalies
                    })
                    sequence_analysis['total_duration_hours'] += task.get('duration', 0) / 3600
                    sequence_analysis['anomaly_count'] += task_anomalies
                
                trace_analysis['task_sequences'].append(sequence_analysis)
        
        return trace_analysis
    
    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于异常统计的建议
        anomaly_counts = defaultdict(int)
        for anomaly in self.anomalies:
            anomaly_counts[anomaly['type']] += 1
        
        if anomaly_counts.get('sensor_offline', 0) > 5:
            recommendations.append("检测到多次传感器掉线，建议检查传感器连接和稳定性")
        
        if anomaly_counts.get('cpu_high', 0) > 3:
            recommendations.append("检测到CPU高负载情况，建议优化系统资源使用")
        
        if anomaly_counts.get('localization_drop', 0) > 2:
            recommendations.append("检测到定位质量下降，建议检查SLAM配置和环境特征")
        
        # 基于任务统计的建议
        if self.task_segments:
            avg_duration = sum(task.get('duration', 0) for task in self.task_segments) / len(self.task_segments)
            if avg_duration > 3600:  # 超过1小时
                recommendations.append("任务平均持续时间较长，建议优化任务规划和路径")
        
        if not recommendations:
            recommendations.append("系统运行状况良好，未发现明显问题")
        
        return recommendations
    
    def save_report(self, report: Dict, output_file: str):
        """保存报告到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"报告已保存到: {output_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='高级机器人日志分析系统')
    parser.add_argument('-d', '--directory', required=True, help='日志目录路径')
    parser.add_argument('-o', '--output', default='advanced_robot_analysis_report.json', 
                       help='输出报告文件路径')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = RobotLogAnalyzer(args.directory)
    
    # 分析日志
    analyzer.analyze_all_logs()
    
    # 生成报告
    report = analyzer.generate_comprehensive_report()
    
    # 保存报告
    analyzer.save_report(report, args.output)
    
    # 打印摘要
    print("\n=== 分析摘要 ===")
    print(f"分析文件数: {report['analysis_summary']['total_log_files']}")
    print(f"发现任务段: {report['analysis_summary']['total_task_segments']}")
    print(f"位置记录数: {report['analysis_summary']['total_position_records']}")
    print(f"检测异常数: {report['analysis_summary']['total_anomalies']}")
    
    if report['anomaly_summary']['most_common']:
        print("\n=== 最常见异常 ===")
        for anomaly_type, count in report['anomaly_summary']['most_common'][:3]:
            print(f"{anomaly_type}: {count} 次")
    
    if report['recommendations']:
        print("\n=== 改进建议 ===")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"{i}. {recommendation}")

if __name__ == "__main__":
    main()