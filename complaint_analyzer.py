#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投诉问题定位和停机点分析模块
专门处理客户投诉场景下的机器人问题定位
"""

import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from typing import Dict, List, Tuple, Optional, Any

class ComplaintAnalyzer:
    """投诉问题分析器"""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_files = []
        self.position_data = []
        self.movement_data = []
        self.stop_events = []
        self.anomaly_events = []
        self.task_segments = []
        
        # 停机检测参数
        self.stop_detection_params = {
            'time_window_minutes': 5,  # 检测窗口
            'movement_threshold': 0.01,  # 移动阈值(米)
            'min_stop_duration': 2,  # 最小停机时间(分钟)
            'max_stop_duration': 120  # 最大停机时间(分钟)
        }
        
        # 投诉问题模式
        self.complaint_patterns = {
            'stop_complaint': [
                r'停在.*不动',
                r'停止.*运动',
                r'卡死',
                r'stuck',
                r'无法移动',
                r'不动了',
                r'停止工作'
            ],
            'navigation_fail': [
                r'导航.*失败',
                r'navigation.*fail',
                r'路径.*规划.*失败',
                r'无法到达',
                r'目标.*不可达',
                r'导航.*错误'
            ],
            'sensor_issue': [
                r'传感器.*问题',
                r'感知.*异常',
                r'检测.*失败',
                r'激光雷达.*异常',
                r'相机.*故障',
                r'超声波.*异常'
            ],
            'battery_issue': [
                r'电池.*问题',
                r'电量.*异常',
                r'充电.*失败',
                r'电源.*故障',
                r'低电量'
            ],
            'mechanical_issue': [
                r'机械.*故障',
                r'电机.*异常',
                r'轮子.*卡住',
                r'传动.*问题',
                r'机械结构.*异常'
            ]
        }
        
        # 停机原因分析模式
        self.stop_reason_patterns = {
            'obstacle_blocked': [
                r'障碍物.*阻挡',
                r'obstacle.*block',
                r'路径.*阻塞',
                r'前方.*障碍',
                r'collision.*avoidance'
            ],
            'navigation_error': [
                r'导航.*错误',
                r'定位.*丢失',
                r'slam.*失败',
                r'地图.*错误',
                r'路径.*规划.*错误'
            ],
            'sensor_failure': [
                r'传感器.*失效',
                r'激光雷达.*掉线',
                r'相机.*断开',
                r'感知.*系统.*故障',
                r'sensor.*offline'
            ],
            'battery_low': [
                r'电池.*低',
                r'电量.*不足',
                r'需要充电',
                r'battery.*low',
                r'power.*critical'
            ],
            'system_error': [
                r'系统.*错误',
                r'程序.*崩溃',
                r'软件.*异常',
                r'进程.*终止',
                r'system.*error'
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
        """发现日志文件"""
        import glob
        patterns = ['*.log', '*.txt', '*.INFO', '*.WARNING', '*.ERROR']
        
        for pattern in patterns:
            files = glob.glob(os.path.join(self.log_dir, pattern))
            self.log_files.extend(files)
        
        self.logger.info(f"发现 {len(self.log_files)} 个日志文件")
    
    def parse_timestamp(self, line: str) -> Optional[datetime]:
        """解析时间戳"""
        timestamp_patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'\[(\d+)\.(\d+)\]',
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3})',
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
                    elif len(timestamp_str) == 13:
                        timestamp_int = int(timestamp_str)
                        return datetime.fromtimestamp(timestamp_int / 1000.0)
                except (ValueError, OverflowError):
                    continue
        
        return None
    
    def extract_position_data(self, line: str, timestamp: datetime) -> Optional[Dict]:
        """提取位置数据"""
        position_patterns = {
            'slam_pose': r'Slam pose: \[([-\d.]+),([-\d.]+),([-\d.]+)\]',
            'odom_pose': r'pose\(([-\d.]+),([-\d.]+),([-\d.]+)\)',
            'robot_position': r'position.*\[([-\d.]+),([-\d.]+)\]',
            'trajectory_point': r'point.*\[([-\d.]+),([-\d.]+)\]'
        }
        
        for pattern_name, pattern in position_patterns.items():
            match = re.search(pattern, line)
            if match:
                try:
                    if pattern_name in ['slam_pose', 'odom_pose']:
                        x, y, z = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'x': x,
                            'y': y,
                            'z': z,
                            'type': pattern_name
                        }
                    elif pattern_name in ['robot_position', 'trajectory_point']:
                        x, y = map(float, match.groups())
                        return {
                            'timestamp': timestamp,
                            'x': x,
                            'y': y,
                            'type': pattern_name
                        }
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def detect_stop_events(self, file_path: str):
        """检测停机事件"""
        self.logger.info(f"检测停机事件: {os.path.basename(file_path)}")
        
        position_buffer = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                timestamp = self.parse_timestamp(line)
                if not timestamp:
                    continue
                
                # 提取位置数据
                position = self.extract_position_data(line, timestamp)
                if position:
                    position_buffer.append(position)
                    
                    # 保持缓冲区大小
                    if len(position_buffer) > 100:
                        position_buffer.pop(0)
                    
                    # 检测停机
                    self.analyze_movement_pattern(position_buffer, timestamp, file_path)
                
                # 检测停机相关日志
                self.detect_stop_related_logs(line, timestamp, file_path)
    
    def analyze_movement_pattern(self, position_buffer: List[Dict], current_time: datetime, file_path: str):
        """分析运动模式检测停机"""
        if len(position_buffer) < 10:  # 需要足够的数据点
            return
        
        # 分析最近时间窗口内的运动
        window_minutes = self.stop_detection_params['time_window_minutes']
        threshold = self.stop_detection_params['movement_threshold']
        
        # 获取时间窗口内的位置数据
        window_start_time = current_time - timedelta(minutes=window_minutes)
        window_positions = [p for p in position_buffer if p['timestamp'] >= window_start_time]
        
        if len(window_positions) < 5:  # 窗口内数据点不足
            return
        
        # 计算位置变化
        x_changes = []
        y_changes = []
        
        for i in range(1, len(window_positions)):
            prev_pos = window_positions[i-1]
            curr_pos = window_positions[i]
            
            x_change = abs(curr_pos['x'] - prev_pos['x'])
            y_change = abs(curr_pos['y'] - prev_pos['y'])
            
            x_changes.append(x_change)
            y_changes.append(y_change)
        
        # 计算平均变化
        avg_x_change = sum(x_changes) / len(x_changes) if x_changes else 0
        avg_y_change = sum(y_changes) / len(y_changes) if y_changes else 0
        
        # 判断是否停机
        if avg_x_change < threshold and avg_y_change < threshold:
            # 检查是否已经记录了类似的停机事件
            if not self.is_duplicate_stop_event(current_time):
                stop_event = {
                    'timestamp': current_time,
                    'position': window_positions[-1],
                    'duration_minutes': window_minutes,
                    'avg_movement': (avg_x_change + avg_y_change) / 2,
                    'data_points': len(window_positions),
                    'file': os.path.basename(file_path),
                    'type': 'movement_analysis'
                }
                self.stop_events.append(stop_event)
                
                self.logger.info(f"检测到停机事件: {current_time}, 平均移动: {stop_event['avg_movement']:.4f}m")
    
    def is_duplicate_stop_event(self, timestamp: datetime) -> bool:
        """检查是否为重复的停机事件"""
        for event in self.stop_events:
            time_diff = abs((event['timestamp'] - timestamp).total_seconds())
            if time_diff < 300:  # 5分钟内视为重复
                return True
        return False
    
    def detect_stop_related_logs(self, line: str, timestamp: datetime, file_path: str):
        """检测停机相关日志"""
        # 检测停机原因相关日志
        for reason_type, patterns in self.stop_reason_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    stop_event = {
                        'timestamp': timestamp,
                        'reason': reason_type,
                        'description': line.strip(),
                        'file': os.path.basename(file_path),
                        'type': 'log_analysis'
                    }
                    self.stop_events.append(stop_event)
                    
                    self.logger.info(f"检测到停机原因: {reason_type}, 时间: {timestamp}")
    
    def analyze_complaint_scenario(self, complaint_time: datetime, time_window_minutes: int = 30) -> Dict:
        """分析投诉场景"""
        self.logger.info(f"分析投诉场景: {complaint_time}")
        
        complaint_analysis = {
            'complaint_time': complaint_time.isoformat(),
            'time_window_minutes': time_window_minutes,
            'stop_events_nearby': [],
            'anomalies_nearby': [],
            'position_data_nearby': [],
            'movement_analysis': {},
            'root_cause_analysis': [],
            'recommendations': []
        }
        
        # 查找附近的停机事件
        time_window_seconds = time_window_minutes * 60
        
        for stop_event in self.stop_events:
            time_diff = abs((stop_event['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_seconds:
                complaint_analysis['stop_events_nearby'].append(stop_event)
        
        # 查找附近的异常事件
        for anomaly in self.anomaly_events:
            time_diff = abs((anomaly['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_seconds:
                complaint_analysis['anomalies_nearby'].append(anomaly)
        
        # 查找附近的位置数据
        for position in self.position_data:
            time_diff = abs((position['timestamp'] - complaint_time).total_seconds())
            if time_diff <= time_window_seconds:
                complaint_analysis['position_data_nearby'].append(position)
        
        # 分析运动模式
        complaint_analysis['movement_analysis'] = self.analyze_movement_around_complaint(
            complaint_time, time_window_minutes
        )
        
        # 根因分析
        complaint_analysis['root_cause_analysis'] = self.analyze_root_cause(complaint_analysis)
        
        # 生成建议
        complaint_analysis['recommendations'] = self.generate_complaint_recommendations(complaint_analysis)
        
        return complaint_analysis
    
    def analyze_movement_around_complaint(self, complaint_time: datetime, time_window_minutes: int) -> Dict:
        """分析投诉时间附近的运动模式"""
        movement_analysis = {
            'pre_complaint_movement': 'unknown',
            'post_complaint_movement': 'unknown',
            'movement_trend': 'unknown',
            'stop_duration_minutes': 0
        }
        
        # 分析投诉前运动
        pre_window_start = complaint_time - timedelta(minutes=time_window_minutes)
        pre_positions = [p for p in self.position_data if pre_window_start <= p['timestamp'] <= complaint_time]
        
        if len(pre_positions) >= 2:
            movement_analysis['pre_complaint_movement'] = self.assess_movement_pattern(pre_positions)
        
        # 分析投诉后运动
        post_window_end = complaint_time + timedelta(minutes=time_window_minutes)
        post_positions = [p for p in self.position_data if complaint_time <= p['timestamp'] <= post_window_end]
        
        if len(post_positions) >= 2:
            movement_analysis['post_complaint_movement'] = self.assess_movement_pattern(post_positions)
        
        # 分析运动趋势
        if movement_analysis['pre_complaint_movement'] != 'unknown' and movement_analysis['post_complaint_movement'] != 'unknown':
            if movement_analysis['pre_complaint_movement'] == 'moving' and movement_analysis['post_complaint_movement'] == 'stopped':
                movement_analysis['movement_trend'] = 'stopped_after_complaint'
            elif movement_analysis['pre_complaint_movement'] == 'stopped' and movement_analysis['post_complaint_movement'] == 'moving':
                movement_analysis['movement_trend'] = 'resumed_after_complaint'
            elif movement_analysis['pre_complaint_movement'] == 'stopped' and movement_analysis['post_complaint_movement'] == 'stopped':
                movement_analysis['movement_trend'] = 'continuous_stop'
        
        # 计算停机持续时间
        stop_duration = self.calculate_stop_duration_around_complaint(complaint_time, time_window_minutes)
        movement_analysis['stop_duration_minutes'] = stop_duration
        
        return movement_analysis
    
    def assess_movement_pattern(self, positions: List[Dict]) -> str:
        """评估运动模式"""
        if len(positions) < 2:
            return 'unknown'
        
        # 计算总移动距离
        total_distance = 0
        for i in range(1, len(positions)):
            prev_pos = positions[i-1]
            curr_pos = positions[i]
            distance = ((curr_pos['x'] - prev_pos['x'])**2 + (curr_pos['y'] - prev_pos['y'])**2)**0.5
            total_distance += distance
        
        # 判断运动状态
        threshold = self.stop_detection_params['movement_threshold'] * len(positions)
        
        if total_distance < threshold:
            return 'stopped'
        else:
            return 'moving'
    
    def calculate_stop_duration_around_complaint(self, complaint_time: datetime, time_window_minutes: int) -> float:
        """计算投诉时间附近的停机持续时间"""
        window_start = complaint_time - timedelta(minutes=time_window_minutes)
        window_end = complaint_time + timedelta(minutes=time_window_minutes)
        
        # 查找窗口内的停机事件
        window_stops = [s for s in self.stop_events if window_start <= s['timestamp'] <= window_end]
        
        if not window_stops:
            return 0
        
        # 计算总停机时间
        total_stop_duration = 0
        for stop in window_stops:
            if 'duration_minutes' in stop:
                total_stop_duration += stop['duration_minutes']
        
        return total_stop_duration
    
    def analyze_root_cause(self, complaint_analysis: Dict) -> List[Dict]:
        """分析根因"""
        root_causes = []
        
        # 基于停机事件分析
        if complaint_analysis['stop_events_nearby']:
            for stop_event in complaint_analysis['stop_events_nearby']:
                cause_analysis = {
                    'type': 'stop_event',
                    'timestamp': stop_event['timestamp'],
                    'confidence': 'high',
                    'description': f"检测到停机事件: {stop_event.get('reason', 'unknown')}",
                    'evidence': stop_event
                }
                root_causes.append(cause_analysis)
        
        # 基于异常事件分析
        if complaint_analysis['anomalies_nearby']:
            high_severity_anomalies = [a for a in complaint_analysis['anomalies_nearby'] if a.get('severity') == 'high']
            if high_severity_anomalies:
                cause_analysis = {
                    'type': 'system_anomaly',
                    'timestamp': high_severity_anomalies[0]['timestamp'],
                    'confidence': 'medium',
                    'description': f"检测到高严重度异常: {high_severity_anomalies[0].get('type', 'unknown')}",
                    'evidence': high_severity_anomalies[0]
                }
                root_causes.append(cause_analysis)
        
        # 基于运动模式分析
        movement_trend = complaint_analysis['movement_analysis'].get('movement_trend')
        if movement_trend == 'continuous_stop':
            cause_analysis = {
                'type': 'continuous_stop',
                'timestamp': complaint_analysis['complaint_time'],
                'confidence': 'medium',
                'description': '检测到持续停机模式',
                'evidence': complaint_analysis['movement_analysis']
            }
            root_causes.append(cause_analysis)
        
        return root_causes
    
    def generate_complaint_recommendations(self, complaint_analysis: Dict) -> List[str]:
        """生成投诉处理建议"""
        recommendations = []
        
        # 基于停机事件的建议
        if complaint_analysis['stop_events_nearby']:
            stop_reasons = [s.get('reason', 'unknown') for s in complaint_analysis['stop_events_nearby']]
            
            if 'obstacle_blocked' in stop_reasons:
                recommendations.append("检测到障碍物阻挡，建议检查环境障碍物和避障系统")
            
            if 'navigation_error' in stop_reasons:
                recommendations.append("检测到导航错误，建议检查SLAM系统和地图数据")
            
            if 'sensor_failure' in stop_reasons:
                recommendations.append("检测到传感器故障，建议检查传感器连接和状态")
            
            if 'battery_low' in stop_reasons:
                recommendations.append("检测到电池问题，建议检查充电系统和电池状态")
        
        # 基于异常事件的建议
        if complaint_analysis['anomalies_nearby']:
            anomaly_types = [a.get('type', 'unknown') for a in complaint_analysis['anomalies_nearby']]
            
            if 'sensor_offline' in anomaly_types:
                recommendations.append("检测到传感器掉线，建议检查传感器稳定性和连接")
            
            if 'cpu_high' in anomaly_types:
                recommendations.append("检测到CPU高负载，建议优化系统资源使用")
        
        # 基于运动模式的建议
        movement_trend = complaint_analysis['movement_analysis'].get('movement_trend')
        if movement_trend == 'continuous_stop':
            recommendations.append("检测到持续停机，建议检查机器人运动系统和控制逻辑")
        
        if not recommendations:
            recommendations.append("未发现明显问题原因，建议进行现场检查和详细诊断")
        
        return recommendations
    
    def analyze_all_logs(self):
        """分析所有日志文件"""
        self.discover_log_files()
        
        for file_path in self.log_files:
            try:
                self.detect_stop_events(file_path)
            except Exception as e:
                self.logger.error(f"分析文件 {file_path} 时出错: {e}")
        
        self.logger.info("投诉分析完成")
    
    def generate_complaint_report(self, complaint_time: datetime, output_file: str):
        """生成投诉分析报告"""
        # 分析投诉场景
        complaint_analysis = self.analyze_complaint_scenario(complaint_time)
        
        # 生成报告
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyzer_version': '1.0',
                'log_files_analyzed': len(self.log_files)
            },
            'complaint_details': {
                'complaint_time': complaint_time.isoformat(),
                'analysis_time_window': '30分钟',
                'complaint_type': '停机问题'
            },
            'analysis_results': complaint_analysis,
            'summary': {
                'stop_events_count': len(complaint_analysis['stop_events_nearby']),
                'anomalies_count': len(complaint_analysis['anomalies_nearby']),
                'root_causes_count': len(complaint_analysis['root_cause_analysis']),
                'movement_pattern': complaint_analysis['movement_analysis']['movement_trend']
            }
        }
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"投诉分析报告已保存到: {output_file}")
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='投诉问题定位分析系统')
    parser.add_argument('-d', '--directory', required=True, help='日志目录路径')
    parser.add_argument('-t', '--complaint-time', required=True, 
                       help='投诉时间 (格式: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('-o', '--output', default='complaint_analysis_report.json', 
                       help='输出报告文件路径')
    
    args = parser.parse_args()
    
    # 解析投诉时间
    try:
        complaint_time = datetime.strptime(args.complaint_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("错误: 投诉时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式")
        return
    
    # 创建分析器
    analyzer = ComplaintAnalyzer(args.directory)
    
    # 分析日志
    analyzer.analyze_all_logs()
    
    # 生成投诉分析报告
    report = analyzer.generate_complaint_report(complaint_time, args.output)
    
    # 打印摘要
    print("\n=== 投诉分析摘要 ===")
    print(f"投诉时间: {complaint_time}")
    print(f"分析日志文件数: {report['report_metadata']['log_files_analyzed']}")
    print(f"检测到停机事件: {report['summary']['stop_events_count']} 个")
    print(f"检测到异常事件: {report['summary']['anomalies_count']} 个")
    print(f"识别根因: {report['summary']['root_causes_count']} 个")
    print(f"运动模式: {report['summary']['movement_pattern']}")
    
    if report['analysis_results']['recommendations']:
        print("\n=== 处理建议 ===")
        for i, recommendation in enumerate(report['analysis_results']['recommendations'], 1):
            print(f"{i}. {recommendation}")

if __name__ == "__main__":
    main()