#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的AI集成示例
将AI增强版报告生成器与现有系统集成
支持OpenAI和DeepSeek API
"""

import os
import json
import argparse
from datetime import datetime
from gpt_enhanced_report_generator import GPTEnhancedRobotReport
from config import API_KEY, API_BASE_URL, API_MODEL, USE_DEEPSEEK

class CompleteGPTIntegration:
    """完整的AI集成系统"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        # 使用参数或配置文件的API设置
        self.api_key = api_key or API_KEY
        self.base_url = base_url or API_BASE_URL
        self.model = model or API_MODEL
    
    def generate_comprehensive_report(self, analysis_report_path: str, output_dir: str):
        """生成全面的GPT增强版报告"""
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成时间戳
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建AI增强版报告生成器
        gpt_report_generator = GPTEnhancedRobotReport(
            analysis_report_path=analysis_report_path,
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 生成GPT增强版报告
        gpt_output_file = os.path.join(output_dir, f"gpt_enhanced_robot_report_{timestamp}.html")
        gpt_report_generator.generate_gpt_enhanced_report(gpt_output_file)
        
        # 生成报告摘要
        self._generate_report_summary(analysis_report_path, output_dir, timestamp)
        
        return {
            'gpt_report': gpt_output_file,
            'timestamp': timestamp,
            'status': 'completed'
        }
    
    def _generate_report_summary(self, analysis_report_path: str, output_dir: str, timestamp: str):
        """生成报告摘要"""
        
        # 加载分析报告数据
        with open(analysis_report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        summary_data = {
            'generation_time': datetime.now().isoformat(),
            'analysis_summary': report_data.get('analysis_summary', {}),
            'anomaly_types': list(report_data.get('anomaly_details', {}).keys()),
            'total_anomalies': report_data.get('analysis_summary', {}).get('total_anomalies', 0),
            'gpt_integration': True
        }
        
        # 保存摘要文件
        summary_file = os.path.join(output_dir, f"report_summary_{timestamp}.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    def test_gpt_connection(self):
        """测试GPT API连接"""
        
        # 测试连接
        test_prompt = "请回复'连接测试成功'以确认API连接正常。"
        
        try:
            # 直接调用API，不依赖报告文件
            response = self._call_gpt_api_directly(test_prompt, max_tokens=20)
            return {
                'status': 'success' if '连接测试成功' in response else 'partial',
                'response': response,
                'message': 'AI API连接正常' if '连接测试成功' in response else 'AI API连接可用，但响应异常'
            }
        except Exception as e:
            return {
                'status': 'error',
                'response': str(e),
                'message': 'AI API连接失败'
            }
    
    def _call_gpt_api_directly(self, prompt: str, max_tokens: int = None) -> str:
        """直接调用GPT API，不依赖报告文件"""
        import requests
        from config import MAX_TOKENS, TEMPERATURE, REQUEST_TIMEOUT
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 确保base_url以/结尾，但如果已经包含/chat/completions则直接使用
        if not self.base_url.endswith('/'):
            if self.base_url.endswith('/chat/completions'):
                # 如果base_url已经是完整的端点URL，直接使用
                api_url = self.base_url
            else:
                # 如果base_url是基础URL，添加端点路径
                api_url = f"{self.base_url}/chat/completions"
        else:
            if self.base_url.endswith('/chat/completions'):
                api_url = self.base_url
            else:
                api_url = f"{self.base_url}chat/completions"
        
        data = {
            "model": self.model,
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
        
        print(f"🔗 测试连接 - API URL: {api_url}")
        print(f"🔑 模型: {self.model}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"❌ API响应错误: {response.status_code}")
            print(f"📝 响应内容: {response.text[:500]}")
            raise Exception(f"API调用失败: {response.status_code} - {response.text[:200]}")

def main():
    """主函数"""
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='AI增强版机器人健康报告生成器')
    parser.add_argument('--analysis-report', '-a', required=True, 
                       help='分析报告JSON文件路径')
    parser.add_argument('--output-dir', '-o', default='./reports',
                       help='输出目录路径')
    parser.add_argument('--test-only', action='store_true',
                       help='仅测试AI连接，不生成报告')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🤖 完整的AI集成系统 - 机器人健康报告生成器")
    print("=" * 70)
    
    # 显示API配置信息
    api_type = 'DeepSeek' if USE_DEEPSEEK else 'OpenAI'
    api_key_source = '环境变量' if os.getenv('OPENAI_API_KEY') or os.getenv('DEEPSEEK_API_KEY') else '配置文件'
    print(f"🔧 当前使用: {api_type} API")
    print(f"🔑 API密钥来源: {api_key_source}")
    print(f"🌐 基础URL: {API_BASE_URL}")
    
    # 创建集成系统（使用配置文件中的默认值）
    integration_system = CompleteGPTIntegration()
    
    # 测试AI连接
    print("\n🔗 测试AI API连接...")
    connection_test = integration_system.test_gpt_connection()
    
    print(f"📊 连接状态: {connection_test['status']}")
    print(f"💬 响应信息: {connection_test['message']}")
    
    if connection_test['status'] == 'error':
        print(f"\n⚠️ {api_type} API连接失败，将使用备用解释模式")
        print("💡 可能的原因:")
        print("   - API密钥无效或过期")
        print("   - 网络连接问题")
        print("   - API服务暂时不可用")
    else:
        print(f"\n✅ {api_type} API连接正常，将使用AI智能分析")
    
    if args.test_only:
        print("\n🧪 测试模式完成")
        return
    
    # 检查分析报告文件
    if not os.path.exists(args.analysis_report):
        print(f"\n❌ 分析报告文件不存在: {args.analysis_report}")
        print("💡 请先运行机器人日志分析器生成分析报告")
        return
    
    # 生成报告
    print(f"\n📝 开始生成GPT增强版报告...")
    print(f"   📄 分析报告: {args.analysis_report}")
    print(f"   📁 输出目录: {args.output_dir}")
    
    try:
        result = integration_system.generate_comprehensive_report(
            analysis_report_path=args.analysis_report,
            output_dir=args.output_dir
        )
        
        print("\n🎉 报告生成完成!")
        print(f"   📊 GPT增强版报告: {result['gpt_report']}")
        print(f"   ⏰ 生成时间: {result['timestamp']}")
        
        # 显示报告特点
        print("\n🌟 报告特点:")
        print("   ✅ 真正的GPT AI智能分析")
        print("   ✅ 自然语言故障解释")
        print("   ✅ 生活化比喻和通俗语言")
        print("   ✅ 个性化维护建议")
        print("   ✅ 美观的响应式界面")
        
        if connection_test['status'] == 'error':
            print("\n💡 当前使用备用解释模式，如需AI智能分析，请检查API配置")
        
    except Exception as e:
        print(f"\n❌ 报告生成失败: {e}")
    
    print("\n" + "=" * 70)
    print("📋 使用说明:")
    print("   1. 首先运行机器人日志分析器生成分析报告")
    print("   2. 使用本工具生成GPT增强版报告")
    print("   3. 打开生成的HTML文件查看报告")
    print("=" * 70)

if __name__ == "__main__":
    main()