#!/bin/bash

# Docker 容器运行示例
# 本脚本展示如何使用环境变量运行 Ubuntu Cloudflare Tunnel 容器

# 方法 1: 直接在命令行中指定环境变量

docker run -d \
  --name ubuntu-tunnel \
  -e CLOUDFLARE_TUNNEL_TOKEN="your_cloudflare_tunnel_token_here" \
  sjwayrhz/ubuntu:tunnel-v0.2

# 方法 2: 使用环境变量文件
# 首先创建 .env 文件:
# echo "CLOUDFLARE_TUNNEL_TOKEN=your_cloudflare_tunnel_token_here" > .env
#
# 然后运行:
# docker run -d \
#   --name ubuntu-tunnel \
#   --env-file .env \
#   sjwayrhz/ubuntu:tunnel-v0.2

# 注意: 请将 "your_cloudflare_tunnel_token_here" 替换为你的实际 Cloudflare Tunnel token
