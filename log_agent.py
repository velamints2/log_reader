#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能日志诊断Agent
- 理解每个log文件的用途
- 根据FAE描述的问题智能选择相关日志
- 多轮分析，深度诊断
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import requests
from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, 
    MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT, LOG_DIRECTORY
)

# 日志文件知识库 - 描述每个日志文件记录什么内容
LOG_KNOWLEDGE_BASE = {
    # ===== 核心驱动层 =====
    "ikitbot_driver.log": {
        "category": "核心驱动",
        "description": "机器人底层驱动日志，记录IMU、电池、超声波、电机等硬件状态",
        "keywords": ["imu", "battery", "ultrasonic", "motor", "driver", "collision", "bump"],
        "problems": ["电机故障", "传感器异常", "碰撞", "电池问题", "IMU异常", "超声波故障", "硬件离线"],
        "importance": "high"
    },
    "odometry_node.log": {
        "category": "核心驱动",
        "description": "里程计节点日志，记录机器人位置、速度、姿态等运动数据",
        "keywords": ["odom", "pose", "velocity", "position", "orientation", "wheel"],
        "problems": ["里程计漂移", "位置不准", "速度异常", "轮子打滑"],
        "importance": "high"
    },
    
    # ===== 导航层 =====
    "navigation_move_base.log": {
        "category": "导航",
        "description": "导航核心日志，记录路径规划、代价地图、导航状态",
        "keywords": ["navigation", "costmap", "path", "goal", "plan", "obstacle", "slam"],
        "problems": ["导航失败", "路径规划失败", "避障异常", "目标不可达", "代价地图问题"],
        "importance": "high"
    },
    "navigation_hsm_flex.log": {
        "category": "导航",
        "description": "导航状态机日志，记录导航任务状态转换和跨楼层导航",
        "keywords": ["navigation", "state", "floor", "elevator", "trans_vel"],
        "problems": ["导航状态异常", "跨楼层问题", "速度控制异常"],
        "importance": "medium"
    },
    "cartographer_node.INFO": {
        "category": "定位建图",
        "description": "Cartographer SLAM日志(INFO级别)，记录建图和定位信息",
        "keywords": ["cartographer", "slam", "map", "localization", "submap", "scan"],
        "problems": ["定位丢失", "建图失败", "SLAM异常"],
        "importance": "high"
    },
    "cartographer_node.WARNING": {
        "category": "定位建图",
        "description": "Cartographer SLAM日志(WARNING级别)，记录建图和定位警告",
        "keywords": ["cartographer", "slam", "warning"],
        "problems": ["定位漂移", "建图质量问题"],
        "importance": "medium"
    },
    "cartographer_node.ERROR": {
        "category": "定位建图",
        "description": "Cartographer SLAM日志(ERROR级别)，记录严重错误",
        "keywords": ["cartographer", "slam", "error"],
        "problems": ["SLAM崩溃", "严重定位错误"],
        "importance": "high"
    },
    "carto_restart.log": {
        "category": "定位建图",
        "description": "Cartographer重启日志，记录SLAM重启和恢复",
        "keywords": ["restart", "carto", "switch", "lidar"],
        "problems": ["SLAM频繁重启", "定位恢复失败"],
        "importance": "medium"
    },
    
    # ===== 传感器层 =====
    "bluesea2_node.log": {
        "category": "传感器",
        "description": "激光雷达日志，记录激光雷达连接和数据状态",
        "keywords": ["lidar", "laser", "scan", "uart", "connect"],
        "problems": ["雷达断连", "雷达数据异常", "扫描失败"],
        "importance": "high"
    },
    "ascamera_rgbd_up.log": {
        "category": "传感器",
        "description": "上方RGBD相机日志，记录深度相机状态",
        "keywords": ["camera", "rgbd", "depth", "image"],
        "problems": ["上相机异常", "深度图异常", "相机断连"],
        "importance": "medium"
    },
    "ascamera_rgbd_down.log": {
        "category": "传感器",
        "description": "下方RGBD相机日志，记录避障相机状态",
        "keywords": ["camera", "rgbd", "depth", "obstacle"],
        "problems": ["下相机异常", "避障相机故障"],
        "importance": "medium"
    },
    "camera_calibration.log": {
        "category": "传感器",
        "description": "相机标定日志，记录相机外参和标定结果",
        "keywords": ["calibration", "tf", "transform", "camera"],
        "problems": ["标定异常", "相机位姿错误"],
        "importance": "low"
    },
    "ydlidar_ros_driver.log": {
        "category": "传感器",
        "description": "YDLidar激光雷达驱动日志",
        "keywords": ["ydlidar", "lidar", "scan"],
        "problems": ["雷达驱动问题"],
        "importance": "medium"
    },
    "virtual_bumper.log": {
        "category": "传感器",
        "description": "虚拟碰撞带日志，记录虚拟安全边界",
        "keywords": ["bumper", "virtual", "safety", "collision"],
        "problems": ["虚拟碰撞异常", "安全区域问题"],
        "importance": "medium"
    },
    
    # ===== 任务层 =====
    "auto_docking.log": {
        "category": "任务",
        "description": "自动回充日志，记录回充桩对接过程",
        "keywords": ["docking", "charge", "dock", "ultrasonic", "laser"],
        "problems": ["回充失败", "对桩失败", "充电异常"],
        "importance": "high"
    },
    "ipa_room_exploration.log": {
        "category": "任务",
        "description": "房间探索日志，记录清扫路径规划",
        "keywords": ["exploration", "room", "path", "boustrophedon", "coverage"],
        "problems": ["清扫路径异常", "区域覆盖不全"],
        "importance": "medium"
    },
    "ipa_room_segmentation.log": {
        "category": "任务",
        "description": "房间分割日志，记录地图区域分割",
        "keywords": ["segmentation", "room", "map", "morphological"],
        "problems": ["房间分割错误", "区域识别异常"],
        "importance": "low"
    },
    "elevator.log": {
        "category": "任务",
        "description": "电梯控制日志，记录跨楼层和电梯交互",
        "keywords": ["elevator", "floor", "lift"],
        "problems": ["电梯对接失败", "跨楼层异常"],
        "importance": "medium"
    },
    
    # ===== 通信层 =====
    "01_00_58_grpc.log": {
        "category": "通信",
        "description": "gRPC通信日志，记录内网通信和ROS LAN通信",
        "keywords": ["grpc", "network", "connect", "lan", "roslan"],
        "problems": ["网络断连", "gRPC通信失败", "内网异常"],
        "importance": "high"
    },
    "00_00_04_mqtt.txt": {
        "category": "通信",
        "description": "MQTT通信日志，记录云端通信和消息收发",
        "keywords": ["mqtt", "cloud", "message", "connect", "ssl"],
        "problems": ["云端断连", "MQTT通信失败", "消息丢失"],
        "importance": "high"
    },
    
    # ===== 系统层 =====
    "app_base.log": {
        "category": "系统",
        "description": "应用基础日志，记录版本信息和系统配置",
        "keywords": ["version", "config", "app", "robot"],
        "problems": ["版本不匹配", "配置错误"],
        "importance": "low"
    },
    "ikitrobot_one.log": {
        "category": "系统",
        "description": "机器人主节点日志，记录ROS系统启动",
        "keywords": ["roslaunch", "node", "startup"],
        "problems": ["节点启动失败", "ROS系统异常"],
        "importance": "medium"
    },
    "state_publish.log": {
        "category": "系统",
        "description": "状态发布日志，记录机器人状态广播",
        "keywords": ["state", "publish", "status"],
        "problems": ["状态发布异常"],
        "importance": "low"
    },
    "robot_demo2.log": {
        "category": "系统",
        "description": "机器人演示和任务执行日志",
        "keywords": ["demo", "task", "execute"],
        "problems": ["任务执行异常"],
        "importance": "medium"
    },
    
    # ===== 通用日志 =====
    "00_00_00.txt": {
        "category": "通用",
        "description": "通用系统日志，记录WiFi、商户信息等",
        "keywords": ["wifi", "merchant", "task", "system"],
        "problems": ["WiFi断连", "系统异常"],
        "importance": "medium"
    },
    "00_00_04_can.txt": {
        "category": "通用",
        "description": "CAN总线日志，记录电池和清洁模块状态",
        "keywords": ["can", "battery", "clean", "water"],
        "problems": ["CAN通信异常", "清洁模块故障", "水箱问题"],
        "importance": "medium"
    },
    "01_01_31_action.txt": {
        "category": "通用",
        "description": "动作日志，记录定位状态和全局位姿",
        "keywords": ["action", "localization", "pose", "global"],
        "problems": ["定位状态异常", "位姿错误"],
        "importance": "medium"
    },
}

# 问题类型到日志文件的映射
PROBLEM_LOG_MAPPING = {
    "导航": ["navigation_move_base.log", "navigation_hsm_flex.log", "cartographer_node.INFO", "odometry_node.log"],
    "定位": ["cartographer_node.INFO", "cartographer_node.WARNING", "cartographer_node.ERROR", "carto_restart.log", "01_01_31_action.txt"],
    "建图": ["cartographer_node.INFO", "cartographer_node.WARNING", "carto_restart.log"],
    "充电": ["auto_docking.log", "ikitbot_driver.log", "00_00_04_can.txt"],
    "回充": ["auto_docking.log", "ikitbot_driver.log", "navigation_move_base.log"],
    "电池": ["ikitbot_driver.log", "00_00_04_can.txt"],
    "电机": ["ikitbot_driver.log", "odometry_node.log"],
    "传感器": ["ikitbot_driver.log", "bluesea2_node.log", "ascamera_rgbd_up.log", "ascamera_rgbd_down.log"],
    "雷达": ["bluesea2_node.log", "cartographer_node.INFO", "carto_restart.log"],
    "相机": ["ascamera_rgbd_up.log", "ascamera_rgbd_down.log", "camera_calibration.log"],
    "碰撞": ["ikitbot_driver.log", "virtual_bumper.log"],
    "避障": ["navigation_move_base.log", "virtual_bumper.log", "ascamera_rgbd_down.log"],
    "网络": ["01_00_58_grpc.log", "00_00_04_mqtt.txt", "00_00_00.txt"],
    "通信": ["01_00_58_grpc.log", "00_00_04_mqtt.txt"],
    "WiFi": ["00_00_00.txt", "00_00_04_mqtt.txt"],
    "清扫": ["ipa_room_exploration.log", "ipa_room_segmentation.log", "robot_demo2.log"],
    "任务": ["robot_demo2.log", "ipa_room_exploration.log", "navigation_hsm_flex.log"],
    "电梯": ["elevator.log", "navigation_hsm_flex.log"],
    "启动": ["ikitrobot_one.log", "app_base.log"],
    "系统": ["app_base.log", "ikitrobot_one.log", "state_publish.log"],
}


class LogDiagnosticAgent:
    """智能日志诊断Agent"""
    
    def __init__(self, log_directory: str = None, api_key: str = None, base_url: str = None):
        self.log_directory = log_directory or LOG_DIRECTORY
        self.api_key = api_key or DEEPSEEK_API_KEY
        self.base_url = base_url or DEEPSEEK_BASE_URL
        self.conversation_history = []
        self.analyzed_logs = {}  # 缓存已分析的日志内容
        self.diagnosis_context = {}  # 诊断上下文
        
    def _call_llm(self, messages: List[Dict], max_tokens: int = None) -> str:
        """调用LLM"""
        if not self.api_key or self.api_key == 'your-deepseek-api-key-here':
            return self._fallback_response(messages[-1].get('content', ''))
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": DEEPSEEK_MODEL,
                "messages": messages,
                "max_tokens": max_tokens or 2000,
                "temperature": 0.3  # 使用较低温度以获得更确定的结果
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"LLM调用失败: {response.status_code}")
                return self._fallback_response(messages[-1].get('content', ''))
                
        except Exception as e:
            print(f"LLM调用异常: {e}")
            return self._fallback_response(messages[-1].get('content', ''))
    
    def _fallback_response(self, query: str) -> str:
        """备用响应"""
        return json.dumps({
            "action": "analyze",
            "relevant_logs": ["ikitbot_driver.log", "navigation_move_base.log"],
            "reasoning": "API不可用，使用默认日志进行分析"
        })
    
    def _get_available_logs(self) -> List[str]:
        """获取可用的日志文件列表"""
        logs = []
        if os.path.exists(self.log_directory):
            for f in os.listdir(self.log_directory):
                if f.endswith(('.log', '.txt', '.INFO', '.WARNING', '.ERROR')):
                    logs.append(f)
        return logs
    
    def get_log_knowledge(self) -> Dict[str, Any]:
        """获取日志知识库信息（供API调用）"""
        return LOG_KNOWLEDGE_BASE
    
    def list_available_logs(self) -> List[Dict[str, Any]]:
        """列出当前日志目录中可用的日志文件及其信息"""
        available = []
        if not os.path.exists(self.log_directory):
            return available
        
        for filename in os.listdir(self.log_directory):
            if not filename.endswith(('.log', '.txt', '.INFO', '.WARNING', '.ERROR')):
                continue
            
            file_path = os.path.join(self.log_directory, filename)
            file_size = os.path.getsize(file_path)
            
            # 查找知识库中的描述
            description = "未知日志类型"
            category = "未分类"
            keywords = []
            
            for pattern, info in LOG_KNOWLEDGE_BASE.items():
                # 精确匹配或模式匹配
                if pattern == filename or pattern in filename:
                    description = info.get('description', '未知')
                    category = info.get('category', '未分类')
                    keywords = info.get('keywords', [])
                    break
            
            available.append({
                'name': filename,
                'path': file_path,
                'size': file_size,
                'size_readable': f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / 1024 / 1024:.1f} MB",
                'category': category,
                'description': description,
                'keywords': keywords
            })
        
        # 按类别排序
        available.sort(key=lambda x: (x['category'], x['name']))
        return available
    
    def _read_log_content(self, log_file: str, max_lines: int = 500, 
                          time_filter: Optional[Tuple[datetime, datetime]] = None) -> str:
        """读取日志内容"""
        file_path = os.path.join(self.log_directory, log_file)
        if not os.path.exists(file_path):
            return f"[日志文件不存在: {log_file}]"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # 如果有时间过滤
            if time_filter:
                start_time, end_time = time_filter
                filtered_lines = []
                for line in lines:
                    ts = self._extract_timestamp(line)
                    if ts and start_time <= ts <= end_time:
                        filtered_lines.append(line)
                lines = filtered_lines
            
            # 限制行数
            if len(lines) > max_lines:
                # 取前后部分，中间省略
                half = max_lines // 2
                lines = lines[:half] + [f"\n... [省略 {len(lines) - max_lines} 行] ...\n"] + lines[-half:]
            
            return ''.join(lines)
        except Exception as e:
            return f"[读取失败: {e}]"
    
    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """从日志行提取时间戳"""
        patterns = [
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',
            r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',
        ]
        for p in patterns:
            m = re.search(p, line)
            if m:
                try:
                    return datetime.strptime(m.group(1).replace('T', ' '), '%Y-%m-%d %H:%M:%S')
                except:
                    continue
        return None
    
    def _build_knowledge_context(self) -> str:
        """构建日志知识库上下文"""
        available_logs = self._get_available_logs()
        
        context = "## 可用日志文件及其说明\n\n"
        
        # 按类别组织
        by_category = defaultdict(list)
        for log_file in available_logs:
            info = LOG_KNOWLEDGE_BASE.get(log_file, {})
            category = info.get('category', '其他')
            by_category[category].append((log_file, info))
        
        for category, logs in sorted(by_category.items()):
            context += f"### {category}\n"
            for log_file, info in logs:
                desc = info.get('description', '未知用途')
                problems = ', '.join(info.get('problems', [])[:3])
                context += f"- **{log_file}**: {desc}\n"
                if problems:
                    context += f"  - 相关问题: {problems}\n"
            context += "\n"
        
        return context
    
    def _build_agent_system_prompt(self) -> str:
        """构建Agent系统提示"""
        knowledge = self._build_knowledge_context()
        
        return f"""你是一个专业的机器人日志诊断Agent。你的任务是帮助FAE（现场应用工程师）分析机器人问题。

{knowledge}

## 你的工作流程

1. **理解问题**: 仔细分析FAE描述的问题，识别关键信息（症状、时间、频率等）
2. **选择日志**: 根据问题类型，选择最相关的日志文件进行分析
3. **分析日志**: 从日志中找出异常和关键信息
4. **关联分析**: 跨多个日志进行关联分析，找出根本原因
5. **给出建议**: 提供具体的排查步骤和解决方案

## 响应格式

你需要以JSON格式响应，包含以下字段：

```json
{{
    "action": "select_logs" | "analyze" | "need_more_info" | "conclude",
    "reasoning": "你的推理过程",
    "relevant_logs": ["日志文件1", "日志文件2"],
    "time_range": {{"start": "YYYY-MM-DD HH:MM:SS", "end": "YYYY-MM-DD HH:MM:SS"}} | null,
    "questions": ["需要FAE补充的问题"] | null,
    "analysis": "分析结果" | null,
    "root_cause": "根本原因" | null,
    "suggestions": ["建议1", "建议2"] | null
}}
```

## 注意事项

- 优先选择与问题最相关的日志，避免分析不相关的日志
- 注意日志之间的时间关联
- 关注ERROR、WARN级别的日志
- 寻找异常模式和重复出现的问题
- 给出的建议要具体可执行"""
    
    def diagnose(self, problem_description: str, issue_time: str = None, 
                 window_minutes: int = 10) -> Dict[str, Any]:
        """
        诊断入口
        
        Args:
            problem_description: FAE描述的问题
            issue_time: 问题发生时间 (YYYY-MM-DD HH:MM:SS)
            window_minutes: 时间窗口（分钟）
        
        Returns:
            诊断结果
        """
        print(f"\n🤖 启动日志诊断Agent...")
        print(f"   问题描述: {problem_description}")
        if issue_time:
            print(f"   问题时间: {issue_time}")
        
        # 初始化诊断上下文
        self.diagnosis_context = {
            'problem': problem_description,
            'issue_time': issue_time,
            'window_minutes': window_minutes,
            'steps': [],
            'analyzed_logs': [],
            'findings': [],
        }
        
        # 计算时间范围
        time_filter = None
        if issue_time:
            try:
                center_time = datetime.strptime(issue_time, "%Y-%m-%d %H:%M:%S")
                time_filter = (
                    center_time - timedelta(minutes=window_minutes),
                    center_time + timedelta(minutes=window_minutes)
                )
            except:
                pass
        
        # Step 1: 让Agent选择相关日志
        step1_result = self._step_select_logs(problem_description)
        self.diagnosis_context['steps'].append(('select_logs', step1_result))
        
        if step1_result.get('action') == 'need_more_info':
            return {
                'status': 'need_more_info',
                'questions': step1_result.get('questions', []),
                'reasoning': step1_result.get('reasoning', '')
            }
        
        relevant_logs = step1_result.get('relevant_logs', [])
        
        # Step 2: 读取并分析相关日志
        log_contents = {}
        for log_file in relevant_logs[:5]:  # 最多分析5个日志
            content = self._read_log_content(log_file, max_lines=300, time_filter=time_filter)
            log_contents[log_file] = content
            self.diagnosis_context['analyzed_logs'].append(log_file)
        
        # Step 3: 让Agent分析日志内容
        step2_result = self._step_analyze_logs(problem_description, log_contents)
        self.diagnosis_context['steps'].append(('analyze', step2_result))
        
        # Step 4: 生成最终诊断报告
        final_result = self._step_conclude(problem_description, step1_result, step2_result)
        self.diagnosis_context['steps'].append(('conclude', final_result))
        
        return {
            'status': 'completed',
            'problem': problem_description,
            'issue_time': issue_time,
            'analyzed_logs': relevant_logs,
            'log_selection_reasoning': step1_result.get('reasoning', ''),
            'analysis': step2_result.get('analysis', ''),
            'root_cause': final_result.get('root_cause', ''),
            'suggestions': final_result.get('suggestions', []),
            'key_findings': final_result.get('key_findings', []),
            'confidence': final_result.get('confidence', 'medium'),
        }
    
    def _step_select_logs(self, problem: str) -> Dict:
        """Step 1: 选择相关日志"""
        print("   📋 Step 1: 分析问题，选择相关日志...")
        
        messages = [
            {"role": "system", "content": self._build_agent_system_prompt()},
            {"role": "user", "content": f"""FAE反馈的问题：
{problem}

请分析这个问题，选择需要查看的日志文件。
注意：只选择与问题最相关的日志（建议3-5个），不要选择不相关的日志。

请以JSON格式响应。"""}
        ]
        
        response = self._call_llm(messages, max_tokens=1000)
        
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                print(f"   ✅ 选择了 {len(result.get('relevant_logs', []))} 个日志文件")
                return result
        except:
            pass
        
        # 备用：使用关键词匹配
        return self._fallback_log_selection(problem)
    
    def _fallback_log_selection(self, problem: str) -> Dict:
        """备用日志选择逻辑"""
        selected_logs = set()
        problem_lower = problem.lower()
        
        # 基于关键词匹配
        for keyword, logs in PROBLEM_LOG_MAPPING.items():
            if keyword in problem_lower or keyword in problem:
                selected_logs.update(logs)
        
        # 如果没匹配到，返回默认日志
        if not selected_logs:
            selected_logs = {"ikitbot_driver.log", "navigation_move_base.log", "cartographer_node.INFO"}
        
        available = set(self._get_available_logs())
        selected_logs = list(selected_logs & available)[:5]
        
        return {
            "action": "analyze",
            "relevant_logs": selected_logs,
            "reasoning": "基于关键词匹配选择日志文件"
        }
    
    def _step_analyze_logs(self, problem: str, log_contents: Dict[str, str]) -> Dict:
        """Step 2: 分析日志内容"""
        print("   🔍 Step 2: 分析日志内容...")
        
        # 构建日志内容摘要
        logs_text = ""
        for log_file, content in log_contents.items():
            # 截取内容，避免超出token限制
            truncated = content[:8000] if len(content) > 8000 else content
            logs_text += f"\n\n### {log_file}\n```\n{truncated}\n```"
        
        messages = [
            {"role": "system", "content": self._build_agent_system_prompt()},
            {"role": "user", "content": f"""FAE反馈的问题：
{problem}

以下是相关日志内容：
{logs_text}

请分析这些日志：
1. 找出与问题相关的异常和错误
2. 识别关键的日志行
3. 分析可能的原因
4. 注意不同日志之间的时间关联

请以JSON格式响应，包含详细的analysis字段。"""}
        ]
        
        response = self._call_llm(messages, max_tokens=2000)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                print(f"   ✅ 日志分析完成")
                return result
        except:
            pass
        
        return {
            "action": "analyze",
            "analysis": response,
            "reasoning": "日志分析结果"
        }
    
    def _step_conclude(self, problem: str, selection_result: Dict, analysis_result: Dict) -> Dict:
        """Step 3: 生成结论"""
        print("   📊 Step 3: 生成诊断结论...")
        
        messages = [
            {"role": "system", "content": """你是专业的机器人故障诊断专家。请根据之前的分析，生成最终的诊断结论。

输出要求：
1. root_cause: 明确指出根本原因
2. key_findings: 列出关键发现（具体的日志证据）
3. suggestions: 给出具体可执行的解决建议
4. confidence: 诊断置信度 (high/medium/low)

请以JSON格式响应。"""},
            {"role": "user", "content": f"""问题描述: {problem}

日志选择依据: {selection_result.get('reasoning', '')}

日志分析结果: {analysis_result.get('analysis', '')}

请生成最终诊断结论。"""}
        ]
        
        response = self._call_llm(messages, max_tokens=1500)
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                print(f"   ✅ 诊断结论生成完成")
                return result
        except:
            pass
        
        return {
            "root_cause": "需要进一步分析",
            "key_findings": [],
            "suggestions": ["请提供更多信息以便深入分析"],
            "confidence": "low"
        }
    
    def interactive_diagnose(self):
        """交互式诊断模式"""
        print("\n" + "="*60)
        print("🤖 机器人智能日志诊断系统")
        print("="*60)
        print("输入问题描述开始诊断，输入 'quit' 退出\n")
        
        while True:
            problem = input("📝 请描述问题: ").strip()
            if problem.lower() == 'quit':
                print("再见！")
                break
            
            if not problem:
                continue
            
            # 询问时间
            issue_time = input("⏰ 问题发生时间 (YYYY-MM-DD HH:MM:SS，可选): ").strip()
            if not issue_time:
                issue_time = None
            
            # 执行诊断
            result = self.diagnose(problem, issue_time)
            
            # 输出结果
            print("\n" + "-"*60)
            print("📋 诊断结果")
            print("-"*60)
            
            if result.get('status') == 'need_more_info':
                print("需要补充信息:")
                for q in result.get('questions', []):
                    print(f"  ❓ {q}")
            else:
                print(f"\n🔍 分析的日志: {', '.join(result.get('analyzed_logs', []))}")
                print(f"\n📝 选择依据: {result.get('log_selection_reasoning', '')}")
                print(f"\n🔬 分析结果:\n{result.get('analysis', '')}")
                print(f"\n🎯 根本原因: {result.get('root_cause', '')}")
                print(f"\n💡 建议:")
                for s in result.get('suggestions', []):
                    print(f"  • {s}")
                print(f"\n📊 置信度: {result.get('confidence', '')}")
            
            print("\n" + "="*60 + "\n")


def create_agent_api_handler(log_directory: str = None):
    """创建Agent API处理函数（供Flask使用）"""
    agent = LogDiagnosticAgent(log_directory=log_directory)
    
    def handle_diagnose(problem: str, issue_time: str = None, window: int = 10) -> Dict:
        return agent.diagnose(problem, issue_time, window)
    
    return handle_diagnose


if __name__ == "__main__":
    # 测试
    agent = LogDiagnosticAgent()
    agent.interactive_diagnose()
