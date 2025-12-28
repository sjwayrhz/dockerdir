FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app

# 安装 wget 和时区数据
RUN apk add --no-cache wget tzdata

# 强制设置容器时区为上海，确保 Python datetime.now() 准确
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制脚本
COPY keepalive.py .

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV TARGET_CPU_PERCENT=15
ENV TARGET_MEMORY_MB=150

# 暴露监控端口
EXPOSE 65080

# 启动程序
CMD ["python", "keepalive.py"]