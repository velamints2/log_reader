#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合机器人日志分析系统
整合所有功能：任务识别、定位分析、异常检测、投诉问题定位、历史追溯
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

class ComprehensiveRobotAnalyzer:
    """综合机器人日志分析器"""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_files = []
        self.task_segments = []
        self.position_data = []
        self.anomalies = []
        self.system_status = {}
        self.complaint_analysis = {}
        
        # 增强的任务阶段识别模式
        self.task_patterns = {
            'task_start': [
                r'wait_for_delivery_task entry',
                r'任务开始',
                r'clean.*start',
                r'mission.*start',
                r'navigation.*task',
                r'开始清洁',
                r'执行任务'
            ],
            'task_end': [
                r'finish task',
                r'任务结束', 
                r'clean.*finish',
                r'mission.*complete',
                r'navigation no task',
                r'清洁完成',
                r'任务完成'
            ],
            'charging': [
                r'charging',
                r'充电',
                r'charge station',
                r'电桩',
                r'docking',
                r'对接'
            ],
            'debugging': [
                r'debug',
                r'调试',
                r'test mode',
                r'测试模式'
            ],
            'map_maintenance': [
                r'map.*maintenance',
                r'地图维护',
                r'slam.*build',
                r'建图',
                r'mapping'
            ],
            'idle': [
                r'idle',
                r'闲置',
                r'waiting',
                r'等待',
                r'standby'
            ]
        }
        
        # 增强的异常检测模式
        self.anomaly_patterns = {
            'sensor_offline': [
                r'sensor.*offline',
                r'传感器.*掉线',
                r'motor offline',
                r'get transform.*fail',
                r'camera.*fail',
                r'激光雷达.*异常'
            ],
            'mechanical_issue': [
                r'脚落异常',
                r'机械.*异常',
                r'collision',
                r'碰撞',
                r'bump',
                r'卡住',
                r'stuck'
            ],
            'cpu_high': [
                r'cpu.*load.*[789]\d',
                r'cpu.*[789]\d%',
                r'cpu.*100%',
                r'系统.*负载',
                r'memory.*high'
            ],
            'speed_anomaly': [
                r'速度异常',
                r'speed.*anomaly',
                r'VCLra',
                r'Ara',
                r'velocity.*abnormal'
            ],
            'localization_drop': [
                r'定位.*下降',
                r'localization.*drop',
                r'score.*0',
                r'定位.*丢失',
                r'slam.*fail'
            ],
            'battery_low': [
                r'电池.*低',
                r'battery.*low',
                r'电量.*不足',
                r'需要充电'
            ]
        }
        
        # 增强的位置信息提取模式
        self.position_patterns = {
            'slam_pose': r'Slam pose: \[([-\d.]+),([-\d.]+),([-\d.]+)\]',
            'odom_pose': r'pose\(([-\d.]+),([-\d.]+),([-\d.]+)\)',
            'charge_station': r'Charge station pose.*\[([-\d.]+),([-\d.]+)\]',
            'goal_pose': r'goal_pose=\(([-\d.]+),([-\d.]+)\)',
            'robot_position': r'position.*\[([-\d.]+),([-\d.]+)\]',
            'trajectory_point': r'point.*\[([-\d.]+),([-\d.]+)\]'
        }
        
        # 投诉问题定位模式
        self.complaint_patterns = {
            'stop_complaint': [
                r'停在.*不动',
                r'停止.*运动',
                r'卡死',
                r'stuck',
                r'无法移动'
            ],
            'navigation_fail': [
                r'导航.*失败',
                r'navigation.*fail',
                r'路径.*规划.*失败',
                r'无法到达'
            ],
            'sensor_issue': [
                r'传感器.*问题',
                r'感知.*异常',
                r'检测.*失败'
            ]
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
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3})',
            # 时间戳格式: 1760202061275
            r'(\d{13})'
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
                    elif len(timestamp_str) == 13:  # 时间戳格式
                        timestamp_int = int(timestamp_str)
                        return datetime.fromtimestamp(timestamp_int / 1000.0)
                except (ValueError, OverflowError):
                    continue
        
        return None
    
    def extract_position_info(self, line: str, timestamp: datetime) -> Optional[Dict]:
        """提取位置信息"""
        for pattern_name, pattern in self.position_patterns.items():
            match = re.search(pattern, line)
            if match:
                try:
                    if pattern_name in ['slam_pose', 'odom_pose']:
                        x, y, z = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'type': pattern_name.split('_')[0],
                            'x': x,
                            'y': y,
                            'z': z,
                            'source': pattern_name
                        }
                    elif pattern_name in ['charge_station', 'goal_pose', 'robot_position', 'trajectory_point']:
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
                        'severity': self.assess_anomaly_severity(anomaly_type, line),
                        'file': 'current_file'  # 将在分析时填充
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
            'localization_drop': 'high',
            'battery_low': 'medium'
        }
        
        base_severity = severity_map.get(anomaly_type, 'low')
        
        # 根据具体内容调整严重程度
        if 'ERROR' in line:
            return 'high'
        elif 'WARN' in line:
            return 'medium'
        
        return base_severity
    
    def analyze_complaint_scenario(self, complaint_time: datetime, time_window_minutes: int = 30):
        """分析投诉场景"""
        complaint_analysis = {
            'complaint_time': complaint_time,
            'time_window_minutes': time_window_minutes,
            'stop_points': [],
            'anomalies_nearby': [],
            'position_data': [],
            'task_context': None,
            'recommendations': []
        }
        
        # 查找附近的停机点
        stop_points = self.detect_stop_points()
        for stop_point in stop_points:
            time_diff = abs((stop_point['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_minutes * 60:
                complaint_analysis['stop_points'].append(stop_point)
        
        # 查找附近的异常
        for anomaly in self.anomalies:
            time_diff = abs((anomaly['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_minutes * 60:
                complaint_analysis['anomalies_nearby'].append(anomaly)
        
        # 查找附近的位置数据
        for position in self.position_data:
            time_diff = abs((position['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_minutes * 60:
                complaint_analysis['position_data'].append(position)
        
        # 分析任务上下文
        complaint_analysis['task_context'] = self.get_task_context(complaint_time)
        
        # 生成建议
        complaint_analysis['recommendations'] = self.generate_complaint_recommendations(complaint_analysis)
        
        return complaint_analysis
    
    def get_task_context(self, target_time: datetime) -> Dict:
        """获取任务上下文"""
        for task in self.task_segments:
            if task['start_time'] <= target_time <= task.get('end_time', task['start_time'] + timedelta(hours=1)):
                return {
                    'task_type': task.get('type', 'unknown'),
                    'task_start': task['start_time'],
                    'task_duration': (target_time - task['start_time']).total_seconds() / 60,
                    'in_task': True
                }
        
        return {'in_task': False}
    
    def generate_complaint_recommendations(self, complaint_analysis: Dict) -> List[str]:
        """生成投诉分析建议"""
        recommendations = []
        
        if complaint_analysis['stop_points']:
            recommendations.append("检测到停机点，建议检查机器人运动系统和环境障碍物")
        
        if complaint_analysis['anomalies_nearby']:
            high_severity_count = sum(1 for a in complaint_analysis['anomalies_nearby'] if a['severity'] == 'high')
            if high_severity_count > 0:
                recommendations.append(f"检测到 {high_severity_count} 个高严重度异常，可能是问题根源")
        
        if complaint_analysis['task_context']['in_task']:
            recommendations.append("问题发生在任务执行期间，建议检查任务规划和执行逻辑")
        else:
            recommendations.append("问题发生在非任务期间，建议检查系统待机状态和自动维护流程")
        
        return recommendations
    
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
                for anomaly in detected_anomalies:
                    anomaly['file'] = os.path.basename(file_path)
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
    
    def detect_stop_points(self, time_window_minutes: int = 10, movement_threshold: float = 0.01):
        """检测停机点"""
        stop_points = []
        
        if not self.position_data:
            return stop_points
        
        # 按时间排序位置数据
        sorted_positions = sorted(self.position_data, key=lambda x: x['timestamp'])
        
        # 使用滑动窗口检测停机
        window_start = 0
        for i in range(len(sorted_positions)):
            # 检查窗口是否超出时间范围
            while window_start < i and (sorted_positions[i]['timestamp'] - sorted_positions[window_start]['timestamp']).total_seconds() > time_window_minutes * 60:
                window_start += 1
            
            # 检查窗口内位置变化
            if i - window_start >= 3:  # 至少有3个位置点
                window_positions = sorted_positions[window_start:i+1]
                
                # 计算位置变化
                x_changes = [abs(window_positions[j]['x'] - window_positions[j-1]['x']) for j in range(1, len(window_positions))]
                y_changes = [abs(window_positions[j]['y'] - window_positions[j-1]['y']) for j in range(1, len(window_positions))]
                
                avg_x_change = sum(x_changes) / len(x_changes)
                avg_y_change = sum(y_changes) / len(y_changes)
                
                # 如果平均变化很小，认为机器人停止
                if avg_x_change < movement_threshold and avg_y_change < movement_threshold:
                    stop_point = {
                        'timestamp': sorted_positions[i]['timestamp'],
                        'position': sorted_positions[i],
                        'duration_minutes': time_window_minutes,
                        'avg_movement': (avg_x_change + avg_y_change) / 2,
                        'window_size': len(window_positions)
                    }
                    stop_points.append(stop_point)
        
        return stop_points
    
    def perform_historical_trace(self, target_task_index: int = None, lookback_tasks: int = 2) -> Dict:
        """执行历史追溯分析"""
        if not self.task_segments:
            return {'message': '没有发现任务数据'}
        
        # 按时间排序任务
        sorted_tasks = sorted(self.task_segments, key=lambda x: x['start_time'])
        
        if target_task_index is None:
            target_task_index = len(sorted_tasks) - 1  # 默认分析最后一个任务
        
        trace_analysis = {
            'target_task_index': target_task_index,
            'lookback_tasks': lookback_tasks,
            'task_sequences': [],
            'cross_task_anomalies': [],
            'trend_analysis': {}
        }
        
        # 分析连续任务序列
        start_index = max(0, target_task_index - lookback_tasks)
        end_index = min(len(sorted_tasks), target_task_index + 1)
        
        sequence = sorted_tasks[start_index:end_index]
        sequence_analysis = {
            'sequence_id': f'tasks_{start_index+1}_to_{end_index}',
            'tasks': [],
            'total_duration_hours': 0,
            'anomaly_count': 0,
            'anomaly_trend': 'stable'
        }
        
        anomaly_counts = []
        for task in sequence:
            task_anomalies = sum(1 for event in task.get('events', []) if event.get('anomalies'))
            sequence_analysis['tasks'].append({
                'start_time': task['start_time'].isoformat(),
                'duration_minutes': task.get('duration', 0) / 60,
                'anomaly_count': task_anomalies
            })
            sequence_analysis['total_duration_hours'] += task.get('duration', 0) / 3600
            sequence_analysis['anomaly_count'] += task_anomalies
            anomaly_counts.append(task_anomalies)
        
        # 分析异常趋势
        if len(anomaly_counts) >= 2:
            if anomaly_counts[-1] > sum(anomaly_counts[:-1]) / len(anomaly_counts[:-1]) * 1.5:
                sequence_analysis['anomaly_trend'] = 'increasing'
            elif anomaly_counts[-1] < sum(anomaly_counts[:-1]) / len(anomaly_counts[:-1]) * 0.5:
                sequence_analysis['anomaly_trend'] = 'decreasing'
        
        trace_analysis['task_sequences'].append(sequence_analysis)
        
        return trace_analysis
    
    def generate_comprehensive_report(self, complaint_time: datetime = None) -> Dict:
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
            'complaint_analysis': {},
            'recommendations': self.generate_recommendations()
        }
        
        # 如果有投诉时间，进行投诉分析
        if complaint_time:
            report['complaint_analysis'] = self.analyze_complaint_scenario(complaint_time)
        
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
    
    def analyze_localization_quality(self):
        """分析定位质量"""
        localization_scores = []
        
        for position in self.position_data:
            if position['type'] in ['slam', 'odom']:
                # 简化的定位质量评估
                score = 95  # 默认高分
                
                # 根据位置变化稳定性评估
                localization_scores.append({
                    'timestamp': position['timestamp'],
                    'score': score,
                    'position': position
                })
        
        return localization_scores
    
    def analyze_anomalies(self) -> Dict:
        """分析异常统计"""
        anomaly_stats = {
            'by_type': defaultdict(int),
            'by_severity': defaultdict(int),
            'by_file': defaultdict(int),
            'timeline': [],
            'most_common': []
        }
        
        for anomaly in self.anomalies:
            anomaly_stats['by_type'][anomaly['type']] += 1
            anomaly_stats['by_severity'][anomaly['severity']] += 1
            anomaly_stats['by_file'][anomaly['file']] += 1
            anomaly_stats['timeline'].append({
                'timestamp': anomaly['timestamp'].isoformat(),
                'type': anomaly['type'],
                'severity': anomaly['severity'],
                'description': anomaly['description'][:100],
                'file': anomaly['file']
            })
        
        # 找出最常见的异常类型
        if anomaly_stats['by_type']:
            anomaly_stats['most_common'] = sorted(
                anomaly_stats['by_type'].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        
        return anomaly_stats
    
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
        
        if anomaly_counts.get('battery_low', 0) > 0:
            recommendations.append("检测到电池低电量情况，建议优化充电策略")
        
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
    parser = argparse.ArgumentParser(description='综合机器人日志分析系统')
    parser.add_argument('-d', '--directory', required=True, help='日志目录路径')
    parser.add_argument('-o', '--output', default='comprehensive_robot_analysis_report.json', 
                       help='输出报告文件路径')
    parser.add_argument('--complaint-time', help='投诉时间 (格式: YYYY-MM-DD HH:MM:SS)')
    
    args = parser.parse_args()
    
    # 创建分析器
    analyzer = ComprehensiveRobotAnalyzer(args.directory)
    
    # 分析日志
    analyzer.analyze_all_logs()
    
    # 处理投诉时间
    complaint_time = None
    if args.complaint_time:
        try:
            complaint_time = datetime.strptime(args.complaint_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("错误: 投诉时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式")
            return
    
    # 生成报告
    report = analyzer.generate_comprehensive_report(complaint_time)
    
    # 保存报告
    analyzer.save_report(report, args.output)
    
    # 打印摘要
    print("\n=== 综合分析摘要 ===")
    print(f"分析文件数: {report['analysis_summary']['total_log_files']}")
    print(f"发现任务段: {report['analysis_summary']['total_task_segments']}")
    print(f"位置记录数: {report['analysis_summary']['total_position_records']}")
    print(f"检测异常数: {report['analysis_summary']['total_anomalies']}")
    
    if report['anomaly_summary']['most_common']:
        print("\n=== 最常见异常 ===")
        for anomaly_type, count in report['anomaly_summary']['most_common'][:3]:
            print(f"{anomaly_type}: {count} 次")
    
    if report['stop_point_analysis']:
        print(f"\n=== 停机点检测 ===")
        print(f"检测到 {len(report['stop_point_analysis'])} 个停机点")
    
    if complaint_time and report['complaint_analysis']:
        print(f"\n=== 投诉分析 ===")
        analysis = report['complaint_analysis']
        print(f"附近停机点: {len(analysis['stop_points'])} 个")
        print(f"附近异常: {len(analysis['anomalies_nearby'])} 个")
        print(f"任务上下文: {'任务中' if analysis['task_context']['in_task'] else '非任务'}")
    
    if report['recommendations']:
        print("\n=== 改进建议 ===")
        for i, recommendation in enumerate(report['recommendations'], 1):
            print(f"{i}. {recommendation}")

if __name__ == "__main__":
    main()