import os

LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "./logs")
REPORTS_DIRECTORY = os.getenv("REPORTS_DIRECTORY", "./reports")
TEMP_REPORTS_DIRECTORY = os.getenv("TEMP_REPORTS_DIRECTORY", "./temp_reports")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-447bc662de434c39b3a6fbc13598004b")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
USE_DEEPSEEK = os.getenv("USE_DEEPSEEK", "false").lower() == "true"
BASE_URL = os.getenv("BASE_URL", "https://api.openai.com/v1")

# AI请求配置
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# 动态API配置
API_KEY = DEEPSEEK_API_KEY if USE_DEEPSEEK else OPENAI_API_KEY
API_BASE_URL = DEEPSEEK_BASE_URL if USE_DEEPSEEK else BASE_URL
API_MODEL = DEEPSEEK_MODEL if USE_DEEPSEEK else "gpt-3.5-turbo"