# 安全配置说明

## 环境变量配置指南

### 1. 设置环境变量

#### Linux/macOS
```bash
# 临时设置（当前终端会话有效）
# 使用OpenAI API
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_BASE_URL="https://api5.xhub.chat/v1"

# 使用DeepSeek API
export USE_DEEPSEEK=true
export DEEPSEEK_API_KEY="your-deepseek-api-key-here"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"

# 永久设置（添加到~/.bashrc或~/.zshrc）
echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export OPENAI_BASE_URL="https://api5.xhub.chat/v1"' >> ~/.bashrc
echo 'export DEEPSEEK_API_KEY="your-deepseek-api-key-here"' >> ~/.bashrc
echo 'export DEEPSEEK_BASE_URL="https://api.deepseek.com"' >> ~/.bashrc
source ~/.bashrc
```

#### Windows
```cmd
# 临时设置（当前命令提示符会话有效）
# 使用OpenAI API
set OPENAI_API_KEY=your-api-key-here
set OPENAI_BASE_URL=https://api5.xhub.chat/v1

# 使用DeepSeek API
set USE_DEEPSEEK=true
set DEEPSEEK_API_KEY=your-deepseek-api-key-here
set DEEPSEEK_BASE_URL=https://api.deepseek.com

# 永久设置（系统环境变量）
# 通过系统属性 -> 高级 -> 环境变量 设置
```

### 2. 使用.env文件（推荐）

1. 复制模板文件：
```bash
cp .env.example .env
```

2. 编辑.env文件，填入您的实际配置：
```bash
# 使用文本编辑器编辑
nano .env
# 或
vim .env
```

3. 安装python-dotenv包（可选）：
```bash
pip3 install python-dotenv
```

### 3. 配置优先级

系统按以下优先级使用配置：
1. **命令行参数**（最高优先级）
2. **环境变量**
3. **配置文件默认值**（最低优先级）

## 安全最佳实践

### 1. API密钥保护
- ❌ **不要**将API密钥硬编码在源代码中
- ❌ **不要**将API密钥提交到版本控制系统
- ✅ **使用**环境变量或配置文件
- ✅ **使用**.gitignore保护敏感文件

### 2. 文件保护
- 确保`.env`文件不被提交到Git
- 设置适当的文件权限（600）
- 定期轮换API密钥

### 测试配置

使用以下命令测试配置是否生效：

```bash
# 测试环境变量
python3 -c "import os; print('OpenAI API密钥已设置:', 'OPENAI_API_KEY' in os.environ)"
python3 -c "import os; print('DeepSeek API密钥已设置:', 'DEEPSEEK_API_KEY' in os.environ)"
python3 -c "import os; print('当前使用API:', 'DeepSeek' if os.getenv('USE_DEEPSEEK', '').lower() == 'true' else 'OpenAI')"

# 测试AI增强版报告生成器
python3 test_gpt_enhanced_report.py

# 测试完整集成系统
python3 complete_gpt_integration.py --test-only
```

## 故障排除

### 常见问题

1. **API密钥无效**
   - 检查密钥是否正确
   - 确认密钥是否过期
   - 验证API端点是否可达

2. **环境变量未生效**
   - 重新加载shell配置：`source ~/.bashrc`
   - 重启终端
   - 检查变量名拼写

3. **配置文件未找到**
   - 确认`.env`文件存在
   - 检查文件路径
   - 验证文件权限

### 调试信息

每个脚本都会显示API配置来源：
- 🔧 当前使用: OpenAI/DeepSeek API
- 🔑 API密钥来源: 环境变量/配置文件
- 🌐 基础URL: [显示实际URL]

## 配置选项

### API选择开关
- `USE_DEEPSEEK`: 是否使用DeepSeek API（默认：false，使用OpenAI）

### OpenAI配置
- `OPENAI_API_KEY`: OpenAI API密钥
- `OPENAI_BASE_URL`: OpenAI API基础URL（默认：https://api5.xhub.chat/v1）

### DeepSeek配置
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `DEEPSEEK_BASE_URL`: DeepSeek API基础URL（默认：https://api.deepseek.com）
- `DEEPSEEK_MODEL`: DeepSeek模型（默认：deepseek-chat）

### 通用配置
- `GPT_MODEL`: GPT模型（默认：gpt-3.5-turbo）
- `MAX_TOKENS`: 最大令牌数（默认：1000）
- `TEMPERATURE`: 温度参数（默认：0.7）
- `REQUEST_TIMEOUT`: 请求超时（默认：30秒）
- `REPORT_OUTPUT_DIR`: 报告输出目录（默认：./reports）
- `DEFAULT_ANALYSIS_FILE`: 默认分析文件（默认：robot_analysis_report.json）

## 紧急备用方案

如果环境变量配置失败，系统会自动使用配置文件中的默认值作为备用方案。