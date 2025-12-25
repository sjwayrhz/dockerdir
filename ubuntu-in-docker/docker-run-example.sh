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


# 安装 Cloudflare CLI 工具
# curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb && sudo dpkg -i cloudflared.deb
# 
# 设置配置文件
# vim .ssh/config
# 
# Host my_tunnel
#     HostName ssh.hsafj.dpdns.org
#     User root
#         IdentityFile ~/.ssh/id_ed25519
#     ProxyCommand /usr/bin/cloudflared access ssh --hostname %h
# 
# 运行 SSH 连接
# ssh my_tunnel