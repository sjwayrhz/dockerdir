FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 将脚本复制进去
COPY keepalive.py .

# 设置无缓冲输出
ENV PYTHONUNBUFFERED=1
ENV TARGET_CPU_PERCENT=15
ENV TARGET_MEMORY_MB=150

# 暴露 65080 端口
EXPOSE 65080

# 启动命令
CMD ["python", "keepalive.py"]