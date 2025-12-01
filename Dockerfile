# 机器人日志分析系统 Dockerfile
# 基于 Python 3.11 slim 镜像

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    TZ=Asia/Shanghai \
    LOG_DIRECTORY=/app/logs \
    REPORTS_DIRECTORY=/app/reports \
    TEMP_REPORTS_DIRECTORY=/app/temp_reports

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # 中文字体支持 (用于报告生成)
    fonts-noto-cjk \
    fonts-wqy-microhei \
    # 其他依赖
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p /app/logs /app/reports /app/temp_reports /app/reports_new /app/final_reports \
    && chmod -R 755 /app

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/status || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "2", "--timeout", "120", "backend.server:app"]
