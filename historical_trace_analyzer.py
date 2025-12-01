#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史追溯分析模块
实现问题发生时的历史任务追溯分析功能
"""

import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from typing import Dict, List, Tuple, Optional, Any

class HistoricalTraceAnalyzer:
    """历史追溯分析器"""
    
    def __init__(self, log_dir: str):
        self.log_dir = log_dir
        self.log_files = []
        self.task_segments = []
        self.anomaly_events = []
        self.position_data = []
        self.system_status_data = []
        
        # 历史追溯参数
        self.trace_params = {
            'lookback_tasks': 2,  # 追溯任务数量
            'time_window_hours': 24,  # 时间窗口
            'min_task_duration_minutes': 5,  # 最小任务持续时间
            'max_task_gap_hours': 6  # 最大任务间隔
        }
        
        # 任务状态模式
        self.task_status_patterns = {
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
            'task_success': [
                r'task.*success',
                r'任务.*成功',
                r'完成.*正常',
                r'success.*complete'
            ],
            'task_failure': [
                r'task.*fail',
                r'任务.*失败',
                r'异常.*终止',
                r'error.*task',
                r'failed.*complete'
            ]
        }
        
        # 系统状态模式
        self.system_status_patterns = {
            'cpu_usage': r'CPU.*usage.*?(\d+)%',
            'memory_usage': r'memory.*usage.*?(\d+)%',
            'battery_level': r'battery.*?(\d+)%',
            'temperature': r'temperature.*?(\d+)',
            'sensor_status': r'sensor.*?(online|offline|error)',
            'network_status': r'network.*?(connected|disconnected|error)'
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
    
    def extract_task_segments(self, file_path: str):
        """提取任务段"""
        self.logger.info(f"提取任务段: {os.path.basename(file_path)}")
        
        current_task = None
        task_start_time = None
        task_events = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                timestamp = self.parse_timestamp(line)
                if not timestamp:
                    continue
                
                # 检测任务开始
                for pattern in self.task_status_patterns['task_start']:
                    if re.search(pattern, line, re.IGNORECASE):
                        if not current_task:
                            current_task = {
                                'start_time': timestamp,
                                'file': os.path.basename(file_path),
                                'events': [],
                                'status': 'running'
                            }
                            task_start_time = timestamp
                            task_events = []
                        break
                
                # 检测任务结束
                for pattern in self.task_status_patterns['task_end']:
                    if re.search(pattern, line, re.IGNORECASE):
                        if current_task:
                            current_task['end_time'] = timestamp
                            current_task['duration'] = (timestamp - task_start_time).total_seconds()
                            
                            # 检测任务成功/失败
                            for success_pattern in self.task_status_patterns['task_success']:
                                if re.search(success_pattern, line, re.IGNORECASE):
                                    current_task['status'] = 'success'
                                    break
                            
                            for failure_pattern in self.task_status_patterns['task_failure']:
                                if re.search(failure_pattern, line, re.IGNORECASE):
                                    current_task['status'] = 'failure'
                                    break
                            
                            # 过滤过短的任务
                            if current_task['duration'] >= self.trace_params['min_task_duration_minutes'] * 60:
                                self.task_segments.append(current_task)
                            
                            current_task = None
                            task_start_time = None
                        break
                
                # 记录任务事件
                if current_task:
                    event = {
                        'timestamp': timestamp,
                        'line': line.strip(),
                        'type': self.classify_event_type(line)
                    }
                    current_task['events'].append(event)
    
    def classify_event_type(self, line: str) -> str:
        """分类事件类型"""
        event_types = {
            'navigation': [r'navigation', r'导航', r'路径', r'goal'],
            'sensor': [r'sensor', r'传感器', r'激光雷达', r'camera'],
            'system': [r'cpu', r'memory', r'battery', r'temperature'],
            'error': [r'error', r'fail', r'异常', r'错误'],
            'warning': [r'warn', r'警告', r'注意'],
            'status': [r'status', r'状态', r'online', r'offline']
        }
        
        for event_type, patterns in event_types.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return event_type
        
        return 'general'
    
    def extract_system_status(self, file_path: str):
        """提取系统状态数据"""
        self.logger.info(f"提取系统状态: {os.path.basename(file_path)}")
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                timestamp = self.parse_timestamp(line)
                if not timestamp:
                    continue
                
                status_data = {}
                
                # 提取CPU使用率
                cpu_match = re.search(self.system_status_patterns['cpu_usage'], line, re.IGNORECASE)
                if cpu_match:
                    status_data['cpu_usage'] = int(cpu_match.group(1))
                
                # 提取内存使用率
                memory_match = re.search(self.system_status_patterns['memory_usage'], line, re.IGNORECASE)
                if memory_match:
                    status_data['memory_usage'] = int(memory_match.group(1))
                
                # 提取电池电量
                battery_match = re.search(self.system_status_patterns['battery_level'], line, re.IGNORECASE)
                if battery_match:
                    status_data['battery_level'] = int(battery_match.group(1))
                
                # 提取温度
                temp_match = re.search(self.system_status_patterns['temperature'], line, re.IGNORECASE)
                if temp_match:
                    status_data['temperature'] = int(temp_match.group(1))
                
                # 提取传感器状态
                sensor_match = re.search(self.system_status_patterns['sensor_status'], line, re.IGNORECASE)
                if sensor_match:
                    status_data['sensor_status'] = sensor_match.group(1)
                
                # 提取网络状态
                network_match = re.search(self.system_status_patterns['network_status'], line, re.IGNORECASE)
                if network_match:
                    status_data['network_status'] = network_match.group(1)
                
                if status_data:
                    status_data['timestamp'] = timestamp
                    status_data['file'] = os.path.basename(file_path)
                    self.system_status_data.append(status_data)
    
    def perform_historical_trace(self, target_task_time: datetime = None, 
                                lookback_tasks: int = None) -> Dict:
        """执行历史追溯分析"""
        if not self.task_segments:
            return {'message': '没有发现任务数据'}
        
        # 设置参数
        if lookback_tasks is None:
            lookback_tasks = self.trace_params['lookback_tasks']
        
        # 按时间排序任务
        sorted_tasks = sorted(self.task_segments, key=lambda x: x['start_time'])
        
        # 确定目标任务
        if target_task_time is None:
            target_task_index = len(sorted_tasks) - 1  # 默认分析最后一个任务
        else:
            # 找到最接近目标时间的任务
            target_task_index = 0
            min_time_diff = float('inf')
            
            for i, task in enumerate(sorted_tasks):
                time_diff = abs((task['start_time'] - target_task_time).total_seconds())
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    target_task_index = i
        
        trace_analysis = {
            'target_task_index': target_task_index,
            'lookback_tasks': lookback_tasks,
            'target_task_time': target_task_time.isoformat() if target_task_time else None,
            'task_sequences': [],
            'cross_task_analysis': {},
            'trend_analysis': {},
            'root_cause_indicators': []
        }
        
        # 分析连续任务序列
        start_index = max(0, target_task_index - lookback_tasks)
        end_index = min(len(sorted_tasks), target_task_index + 1)
        
        sequence = sorted_tasks[start_index:end_index]
        
        if not sequence:
            return {'message': '没有找到符合条件的任务序列'}
        
        sequence_analysis = self.analyze_task_sequence(sequence)
        trace_analysis['task_sequences'].append(sequence_analysis)
        
        # 跨任务分析
        trace_analysis['cross_task_analysis'] = self.analyze_cross_task_patterns(sequence)
        
        # 趋势分析
        trace_analysis['trend_analysis'] = self.analyze_trends(sequence)
        
        # 根因指示器
        trace_analysis['root_cause_indicators'] = self.detect_root_cause_indicators(sequence)
        
        return trace_analysis
    
    def analyze_task_sequence(self, task_sequence: List[Dict]) -> Dict:
        """分析任务序列"""
        sequence_analysis = {
            'sequence_id': f'tasks_{len(task_sequence)}',
            'tasks': [],
            'total_duration_hours': 0,
            'success_rate': 0,
            'avg_task_duration_minutes': 0,
            'event_statistics': defaultdict(int),
            'anomaly_count': 0
        }
        
        success_count = 0
        total_duration = 0
        
        for i, task in enumerate(task_sequence):
            task_analysis = {
                'task_index': i,
                'start_time': task['start_time'].isoformat(),
                'duration_minutes': task.get('duration', 0) / 60,
                'status': task.get('status', 'unknown'),
                'event_count': len(task.get('events', [])),
                'event_types': defaultdict(int)
            }
            
            # 统计事件类型
            for event in task.get('events', []):
                task_analysis['event_types'][event['type']] += 1
                sequence_analysis['event_statistics'][event['type']] += 1
            
            sequence_analysis['tasks'].append(task_analysis)
            
            # 统计成功率和持续时间
            if task.get('status') == 'success':
                success_count += 1
            
            total_duration += task.get('duration', 0)
            sequence_analysis['total_duration_hours'] += task.get('duration', 0) / 3600
        
        # 计算统计指标
        if task_sequence:
            sequence_analysis['success_rate'] = success_count / len(task_sequence) * 100
            sequence_analysis['avg_task_duration_minutes'] = total_duration / len(task_sequence) / 60
        
        return sequence_analysis
    
    def analyze_cross_task_patterns(self, task_sequence: List[Dict]) -> Dict:
        """分析跨任务模式"""
        cross_analysis = {
            'performance_degradation': False,
            'error_escalation': False,
            'resource_trend': 'stable',
            'event_patterns': {}
        }
        
        if len(task_sequence) < 2:
            return cross_analysis
        
        # 分析性能退化
        durations = [task.get('duration', 0) for task in task_sequence]
        if len(durations) >= 3:
            # 检查持续时间是否逐渐增加（可能表示性能退化）
            duration_increase = all(durations[i] > durations[i-1] * 1.2 for i in range(1, len(durations)))
            cross_analysis['performance_degradation'] = duration_increase
        
        # 分析错误升级
        error_counts = []
        for task in task_sequence:
            error_count = sum(1 for event in task.get('events', []) if event['type'] == 'error')
            error_counts.append(error_count)
        
        if len(error_counts) >= 2:
            error_escalation = all(error_counts[i] > error_counts[i-1] for i in range(1, len(error_counts)))
            cross_analysis['error_escalation'] = error_escalation
        
        # 分析资源趋势
        if self.system_status_data:
            cpu_trend = self.analyze_resource_trend('cpu_usage', task_sequence)
            memory_trend = self.analyze_resource_trend('memory_usage', task_sequence)
            
            if cpu_trend == 'increasing' or memory_trend == 'increasing':
                cross_analysis['resource_trend'] = 'increasing'
            elif cpu_trend == 'decreasing' or memory_trend == 'decreasing':
                cross_analysis['resource_trend'] = 'decreasing'
        
        return cross_analysis
    
    def analyze_resource_trend(self, resource_type: str, task_sequence: List[Dict]) -> str:
        """分析资源使用趋势"""
        resource_values = []
        
        for task in task_sequence:
            # 查找任务期间的系统状态数据
            task_status_data = [s for s in self.system_status_data 
                              if task['start_time'] <= s['timestamp'] <= task.get('end_time', task['start_time'] + timedelta(hours=1))]
            
            if task_status_data:
                avg_value = sum(s.get(resource_type, 0) for s in task_status_data) / len(task_status_data)
                resource_values.append(avg_value)
        
        if len(resource_values) >= 3:
            # 简单趋势分析
            if all(resource_values[i] > resource_values[i-1] * 1.1 for i in range(1, len(resource_values))):
                return 'increasing'
            elif all(resource_values[i] < resource_values[i-1] * 0.9 for i in range(1, len(resource_values))):
                return 'decreasing'
        
        return 'stable'
    
    def analyze_trends(self, task_sequence: List[Dict]) -> Dict:
        """分析趋势"""
        trend_analysis = {
            'duration_trend': 'stable',
            'error_trend': 'stable',
            'performance_trend': 'stable',
            'stability_trend': 'stable'
        }
        
        if len(task_sequence) < 2:
            return trend_analysis
        
        # 持续时间趋势
        durations = [task.get('duration', 0) for task in task_sequence]
        if self.calculate_trend(durations) > 0.1:
            trend_analysis['duration_trend'] = 'increasing'
        elif self.calculate_trend(durations) < -0.1:
            trend_analysis['duration_trend'] = 'decreasing'
        
        # 错误趋势
        error_counts = []
        for task in task_sequence:
            error_count = sum(1 for event in task.get('events', []) if event['type'] == 'error')
            error_counts.append(error_count)
        
        if self.calculate_trend(error_counts) > 0.1:
            trend_analysis['error_trend'] = 'increasing'
        elif self.calculate_trend(error_counts) < -0.1:
            trend_analysis['error_trend'] = 'decreasing'
        
        return trend_analysis
    
    def calculate_trend(self, values: List[float]) -> float:
        """计算趋势（简单线性回归斜率）"""
        if len(values) < 2:
            return 0
        
        n = len(values)
        x = list(range(n))
        y = values
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        return slope
    
    def detect_root_cause_indicators(self, task_sequence: List[Dict]) -> List[Dict]:
        """检测根因指示器"""
        indicators = []
        
        if len(task_sequence) < 2:
            return indicators
        
        # 检测错误升级模式
        error_counts = []
        for task in task_sequence:
            error_count = sum(1 for event in task.get('events', []) if event['type'] == 'error')
            error_counts.append(error_count)
        
        if len(error_counts) >= 3 and all(error_counts[i] > error_counts[i-1] for i in range(1, len(error_counts))):
            indicators.append({
                'type': 'error_escalation',
                'description': '检测到错误数量逐任务增加',
                'confidence': 'medium',
                'suggested_action': '检查系统稳定性和错误处理机制'
            })
        
        # 检测性能退化
        durations = [task.get('duration', 0) for task in task_sequence]
        if len(durations) >= 3 and all(durations[i] > durations[i-1] * 1.2 for i in range(1, len(durations))):
            indicators.append({
                'type': 'performance_degradation',
                'description': '检测到任务持续时间逐渐增加',
                'confidence': 'medium',
                'suggested_action': '检查系统性能和资源使用情况'
            })
        
        # 检测资源使用趋势
        if self.system_status_data:
            cpu_values = []
            for task in task_sequence:
                task_status_data = [s for s in self.system_status_data 
                                  if task['start_time'] <= s['timestamp'] <= task.get('end_time', task['start_time'] + timedelta(hours=1))]
                if task_status_data:
                    avg_cpu = sum(s.get('cpu_usage', 0) for s in task_status_data) / len(task_status_data)
                    cpu_values.append(avg_cpu)
            
            if len(cpu_values) >= 3 and self.calculate_trend(cpu_values) > 5:
                indicators.append({
                    'type': 'cpu_increase',
                    'description': '检测到CPU使用率逐渐增加',
                    'confidence': 'low',
                    'suggested_action': '优化系统资源使用和进程管理'
                })
        
        return indicators
    
    def analyze_all_logs(self):
        """分析所有日志文件"""
        self.discover_log_files()
        
        for file_path in self.log_files:
            try:
                self.extract_task_segments(file_path)
                self.extract_system_status(file_path)
            except Exception as e:
                self.logger.error(f"分析文件 {file_path} 时出错: {e}")
        
        self.logger.info("历史追溯分析完成")
    
    def generate_trace_report(self, target_task_time: datetime = None, 
                            output_file: str = 'historical_trace_report.json') -> Dict:
        """生成历史追溯报告"""
        # 执行历史追溯分析
        trace_analysis = self.perform_historical_trace(target_task_time)
        
        # 生成报告
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyzer_version': '1.0',
                'log_files_analyzed': len(self.log_files),
                'tasks_analyzed': len(self.task_segments)
            },
            'trace_parameters': {
                'lookback_tasks': trace_analysis.get('lookback_tasks', 2),
                'target_task_time': trace_analysis.get('target_task_time'),
                'target_task_index': trace_analysis.get('target_task_index', -1)
            },
            'analysis_results': trace_analysis,
            'summary': {
                'task_sequences_count': len(trace_analysis.get('task_sequences', [])),
                'root_cause_indicators_count': len(trace_analysis.get('root_cause_indicators', [])),
                'performance_degradation': trace_analysis.get('cross_task_analysis', {}).get('performance_degradation', False),
                'error_escalation': trace_analysis.get('cross_task_analysis', {}).get('error_escalation', False)
            }
        }
        
        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"历史追溯报告已保存到: {output_file}")
        
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='历史追溯分析系统')
    parser.add_argument('-d', '--directory', required=True, help='日志目录路径')
    parser.add_argument('-t', '--target-time', help='目标任务时间 (格式: YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('-o', '--output', default='historical_trace_report.json', 
                       help='输出报告文件路径')
    parser.add_argument('--lookback-tasks', type=int, default=2, 
                       help='追溯任务数量 (默认: 2)')
    
    args = parser.parse_args()
    
    # 解析目标时间
    target_time = None
    if args.target_time:
        try:
            target_time = datetime.strptime(args.target_time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print("错误: 目标时间格式不正确，请使用 YYYY-MM-DD HH:MM:SS 格式")
            return
    
    # 创建分析器
    analyzer = HistoricalTraceAnalyzer(args.directory)
    
    # 分析日志
    analyzer.analyze_all_logs()
    
    # 生成历史追溯报告
    report = analyzer.generate_trace_report(target_time, args.output)
    
    # 打印摘要
    print("\n=== 历史追溯分析摘要 ===")
    print(f"分析日志文件数: {report['report_metadata']['log_files_analyzed']}")
    print(f"分析任务数: {report['report_metadata']['tasks_analyzed']}")
    print(f"追溯任务数: {report['trace_parameters']['lookback_tasks']}")
    print(f"任务序列数: {report['summary']['task_sequences_count']}")
    print(f"根因指示器: {report['summary']['root_cause_indicators_count']} 个")
    
    if report['summary']['performance_degradation']:
        print("⚠️  检测到性能退化")
    
    if report['summary']['error_escalation']:
        print("⚠️  检测到错误升级")
    
    if report['analysis_results']['root_cause_indicators']:
        print("\n=== 根因指示器 ===")
        for indicator in report['analysis_results']['root_cause_indicators']:
            print(f"- {indicator['description']} ({indicator['confidence']} 置信度)")

if __name__ == "__main__":
    main()