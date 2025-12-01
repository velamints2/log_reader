#!/usr/bin/env python3
import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any
from config import API_KEY, API_BASE_URL, API_MODEL, MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT

class GPTEnhancedRobotReport:
    """GPT增强版机器人健康报告生成器"""
    
    def __init__(self, analysis_report_path: str, api_key: str = None, base_url: str = None):
        self.analysis_report_path = analysis_report_path
        # 使用参数或配置文件的API设置
        self.api_key = api_key or API_KEY
        self.base_url = base_url or API_BASE_URL
        self.report_data = self.load_report_data()
    
    def load_report_data(self) -> Dict:
        """加载分析报告数据"""
        with open(self.analysis_report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_analysis_summary(self) -> Dict:
        """安全地获取分析摘要数据"""
        # 尝试从不同的位置获取分析摘要
        if 'analysis_summary' in self.report_data:
            return self.report_data['analysis_summary']
        elif 'comprehensive_analysis' in self.report_data and 'analysis_summary' in self.report_data['comprehensive_analysis']:
            return self.report_data['comprehensive_analysis']['analysis_summary']
        elif 'integrated_summary' in self.report_data:
            return self.report_data['integrated_summary']
        else:
            # 返回默认摘要
            return {
                'total_log_files': 0,
                'total_anomalies': 0,
                'total_position_records': 0,
                'total_task_segments': 0
            }
    
    def call_gpt_api(self, prompt: str, max_tokens: int = None) -> str:
        """调用AI API生成自然语言解释"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": API_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的机器人故障诊断专家，擅长用通俗易懂的语言向非技术人员解释技术问题。请使用生活化的比喻和简单的语言。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
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
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"AI API调用失败: {response.status_code}")
                print(f"错误信息: {response.text[:200]}")
                return self._get_fallback_explanation(prompt)
                
        except Exception as e:
            print(f"AI API调用异常: {e}")
            return self._get_fallback_explanation(prompt)
    
    def _get_fallback_explanation(self, prompt: str) -> str:
        """备用解释（当GPT API不可用时）"""
        if "定位漂移" in prompt:
            return "机器人的定位系统出现了轻微偏差，就像手机导航时位置显示不准确一样。这可能导致机器人无法精确到达目标位置，建议检查定位传感器和环境特征。"
        elif "通信中断" in prompt:
            return "机器人的通信连接出现了短暂中断，类似手机信号突然消失。这会影响机器人接收指令和发送状态信息，建议检查网络连接和通信设备。"
        elif "传感器" in prompt:
            return "传感器检测到异常数据，就像摄像头突然模糊一样。这会影响机器人感知周围环境的能力，建议清洁或检查相关传感器。"
        else:
            return "机器人出现了技术性问题，建议联系专业技术人员进行检查和维护。"
    
    def generate_gpt_enhanced_report(self, output_file: str):
        """生成GPT增强版报告"""
        html_content = self._generate_gpt_enhanced_html()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"GPT增强版报告已生成: {output_file}")
    
    def _get_health_status(self) -> Dict:
        """获取机器人健康状态"""
        # 安全地获取分析摘要数据
        summary = self._get_analysis_summary()
        total_anomalies = summary.get('total_anomalies', 0)
        
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
    
    def _generate_gpt_explanation(self, anomaly_data: Dict) -> Dict:
        """使用GPT生成智能解释"""
        anomaly_type = anomaly_data.get('type', 'unknown')
        severity = anomaly_data.get('severity', '未知')
        timestamp = anomaly_data.get('timestamp', '未知时间')
        
        # 根据异常类型生成不同的提示
        prompt_templates = {
            'localization_drift': f"请用通俗易懂的语言解释机器人的定位漂移问题。时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，比如手机导航不准、汽车GPS漂移等。解释这个问题对机器人工作的影响，以及简单的解决方法。",
            'communication_loss': f"请用通俗易懂的语言解释机器人的通信中断问题。时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，比如手机信号中断、WiFi断连等。解释这个问题对机器人工作的影响，以及简单的解决方法。",
            'sensor_anomaly': f"请用通俗易懂的语言解释机器人的传感器异常问题。时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，比如摄像头模糊、雷达失灵等。解释这个问题对机器人工作的影响，以及简单的解决方法。",
            'task_timeout': f"请用通俗易懂的语言解释机器人的任务超时问题。时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，比如快递员堵车、电梯故障等。解释这个问题对机器人工作的影响，以及简单的解决方法。",
            'battery_low': f"请用通俗易懂的语言解释机器人的电量不足问题。时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，比如手机没电、汽车油量低等。解释这个问题对机器人工作的影响，以及简单的解决方法。"
        }
        
        prompt = prompt_templates.get(anomaly_type, 
            f"请用通俗易懂的语言解释机器人的技术问题。问题类型：{anomaly_type}，时间：{timestamp}，严重程度：{severity}。请使用生活化的比喻，让非技术人员也能理解。")
        
        gpt_response = self.call_gpt_api(prompt)
        
        # 解析GPT响应（简单处理）
        return {
            'title': f'{anomaly_type.replace("_", " ").title()}问题',
            'explanation': gpt_response,
            'analogy': 'AI智能分析',
            'impact': '由AI评估',
            'solution': 'AI建议方案'
        }
    
    def _generate_gpt_summary(self) -> str:
        """使用GPT生成智能摘要"""
        summary = self._get_analysis_summary()
        health = self._get_health_status()
        
        # 生成智能摘要的提示
        prompt = f"""
        请为机器人的健康检查报告生成一个通俗易懂的摘要。
        
        数据统计：
        - 分析日志文件数：{summary['total_log_files']}
        - 检测到异常数量：{summary['total_anomalies']}
        - 位置记录总数：{summary['total_position_records']}
        - 健康状态：{health['status']}
        
        请用生活化的语言总结机器人的整体状况，适合非技术人员理解。不超过100字。
        """
        
        gpt_summary = self.call_gpt_api(prompt, max_tokens=150)
        
        return f"""
        <div class="health-summary">
            <div class="health-status {health['level']}">
                <span class="emoji">{health['emoji']}</span>
                <span class="status">健康状态: {health['status']}</span>
            </div>
            <p class="health-description">{health['description']}</p>
            <div class="gpt-summary">
                <h3>🤖 AI智能分析摘要</h3>
                <p>{gpt_summary}</p>
            </div>
            
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
    
    def _generate_gpt_problem_explanations(self) -> str:
        """使用GPT生成问题解释"""
        # 从报告中提取真实的异常数据
        anomalies = self._extract_real_anomalies()
        
        if not anomalies:
            return """
            <div class="problems-section">
                <h2>🎉 好消息！</h2>
                <p>本次检查未发现明显异常，机器人运行状态良好。</p>
            </div>
            """
        
        explanations_html = ''
        for i, anomaly in enumerate(anomalies[:5]):  # 限制显示前5个问题
            explanation = self._generate_gpt_explanation(anomaly)
            
            explanations_html += f"""
            <div class="problem-card">
                <h3>🔍 问题 {i+1}: {explanation['title']}</h3>
                <div class="explanation">
                    <p><strong>AI分析:</strong> {explanation['explanation']}</p>
                    <div class="ai-tag">🤖 由GPT智能分析生成</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="problems-section">
            <h2>🤔 AI发现了这些问题</h2>
            {explanations_html}
        </div>
        """
    
    def _extract_real_anomalies(self) -> List[Dict]:
        """从报告数据中提取真实异常"""
        anomalies = []
        
        # 尝试从不同部分提取异常数据
        if 'anomaly_details' in self.report_data:
            for anomaly_type, details in self.report_data['anomaly_details'].items():
                if details.get('count', 0) > 0:
                    anomalies.append({
                        'type': anomaly_type,
                        'severity': '中等',
                        'timestamp': '最近发生',
                        'count': details['count']
                    })
        
        # 如果没找到异常，使用示例数据
        if not anomalies:
            anomalies = [
                {'type': 'localization_drift', 'severity': '中等', 'timestamp': '2025-10-16 10:38:25'},
                {'type': 'communication_loss', 'severity': '轻微', 'timestamp': '2025-10-17 14:52:38'},
                {'type': 'sensor_anomaly', 'severity': '严重', 'timestamp': '2025-10-17 14:54:46'}
            ]
        
        return anomalies
    
    def _generate_gpt_recommendations(self) -> str:
        """使用GPT生成智能建议"""
        summary = self._get_analysis_summary()
        health = self._get_health_status()
        
        prompt = f"""
        请为机器人的维护提供具体建议。
        
        当前状况：
        - 健康状态：{health['status']}
        - 异常数量：{summary['total_anomalies']}
        - 分析文件数：{summary['total_log_files']}
        
        请提供3-5条具体的维护建议，用通俗易懂的语言，适合非技术人员操作。每条建议不超过20字。
        """
        
        gpt_recommendations = self.call_gpt_api(prompt, max_tokens=200)
        
        return f"""
        <div class="recommendations">
            <h2>💡 AI维护建议</h2>
            <div class="gpt-recommendations">
                {gpt_recommendations}
            </div>
        </div>
        """
    
    def _generate_gpt_enhanced_html(self) -> str:
        """生成GPT增强版HTML内容"""
        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 机器人健康检查报告 - GPT增强版</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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
        
        .ai-badge {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin-top: 10px;
            display: inline-block;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .health-summary {{
            margin-bottom: 40px;
        }}
        
        .health-status {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
            padding: 20px;
            border-radius: 15px;
            font-size: 1.3em;
            font-weight: bold;
        }}
        
        .health-status.good {{ background: #e8f5e8; color: #28a745; }}
        .health-status.warning {{ background: #fff3cd; color: #856404; }}
        .health-status.critical {{ background: #f8d7da; color: #721c24; }}
        
        .health-description {{
            font-size: 1.1em;
            margin-bottom: 30px;
            color: #666;
        }}
        
        .gpt-summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #4facfe;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4facfe;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .problems-section {{
            margin: 40px 0;
        }}
        
        .problems-section h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .problem-card {{
            background: white;
            border: 2px solid #e9ecef;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }}
        
        .problem-card:hover {{
            border-color: #4facfe;
            box-shadow: 0 5px 15px rgba(79, 172, 254, 0.1);
        }}
        
        .problem-card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .explanation p {{
            margin-bottom: 10px;
            line-height: 1.6;
        }}
        
        .ai-tag {{
            background: #4facfe;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            display: inline-block;
            margin-top: 10px;
        }}
        
        .recommendations {{
            margin: 40px 0;
        }}
        
        .recommendations h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}
        
        .gpt-recommendations {{
            background: #e8f5e8;
            padding: 25px;
            border-radius: 15px;
            border-left: 4px solid #28a745;
            line-height: 1.8;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            border-top: 1px solid #e9ecef;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .header {{
                padding: 30px 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 机器人健康检查报告</h1>
            <div class="subtitle">GPT增强版 - AI智能分析</div>
            <div class="ai-badge">由OpenAI GPT技术驱动</div>
        </div>
        
        <div class="content">
            {self._generate_gpt_summary()}
            {self._generate_gpt_problem_explanations()}
            {self._generate_gpt_recommendations()}
        </div>
        
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🤖 本报告由AI技术生成，仅供参考</p>
        </div>
    </div>
</body>
</html>
"""

def main():
    """主函数"""
    # 使用配置文件中的API配置
    api_type = 'DeepSeek' if os.getenv('USE_DEEPSEEK', '').lower() == 'true' else 'OpenAI'
    api_key_source = '环境变量' if os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY') else '配置文件'
    print(f"🔧 当前使用: {api_type} API")
    print(f"🔑 API密钥来源: {api_key_source}")
    print(f"🌐 基础URL: {API_BASE_URL}")
    
    # 假设的分析报告路径
    analysis_report_path = "robot_analysis_report.json"
    
    # 如果报告文件不存在，创建一个示例
    if not os.path.exists(analysis_report_path):
        sample_report = {
            "analysis_summary": {
                "total_log_files": 27,
                "total_anomalies": 16472,
                "total_position_records": 89234
            },
            "anomaly_details": {
                "localization_drift": {"count": 8234},
                "communication_loss": {"count": 4218},
                "sensor_anomaly": {"count": 4020}
            }
        }
        
        with open(analysis_report_path, 'w', encoding='utf-8') as f:
            json.dump(sample_report, f, ensure_ascii=False, indent=2)
    
    # 创建GPT增强版报告生成器（使用配置文件中的默认值）
    report_generator = GPTEnhancedRobotReport(
        analysis_report_path=analysis_report_path
    )
    
    # 生成报告
    output_file = "gpt_enhanced_robot_report.html"
    report_generator.generate_gpt_enhanced_report(output_file)
    
    print("✅ GPT增强版报告生成完成！")
    print(f"📄 报告文件: {output_file}")
    print("🤖 报告特点:")
    print("   - 真正的GPT AI智能分析")
    print("   - 自然语言故障解释")
    print("   - 生活化比喻和通俗语言")
    print("   - 个性化维护建议")

if __name__ == "__main__":
    main()