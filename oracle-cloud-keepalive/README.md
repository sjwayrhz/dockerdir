# 0. 快速启动
默认15%CPU，150MB内存
```
docker run -d -p 65080:65080 --name oracle-keepalive --restart always sjwayrhz/oracle-alive:latest
```
自定义CPU和内存，例如15%CPU，100MB内存
```
docker run --rm -p 65080:65080 -e TARGET_CPU_PERCENT=15 -e TARGET_MEMORY_MB=100 --name oracle-keepalive --restart always sjwayrhz/oracle-alive:latest
```
# 1. 构建镜像（命名为 oracle-alive）

```
docker build -t sjwayrhz/oracle-alive:latest .
```

# 2. 删除旧容器（如果有）并启动新容器

```
docker rm -f oracle-keepalive 2>/dev/null
docker run -d --name oracle-keepalive --restart always sjwayrhz/oracle-alive:latest
```

# 验证方法

容器启动后，等待 10 秒钟，然后检查：

1. 确认进程在跑：

```
docker logs oracle-keepalive
```

2. 查看资源占用：

```
docker stats
```


# 核心功能简介 v1.1
## 智能 CPU 负载模拟 (Smart CPU Keepalive)
正弦波动态控制：与简单的死循环不同，它使用数学正弦函数（Sine Wave）来模拟波动的负载。瞬时负载在 20% 到 50% 之间平滑切换。

精准占用来控制：通过计算“活跃期”和“休眠期”，确保整体平均 CPU 占用率稳定在 15% 左右。

自然行为模拟：这种波动的占用曲线比直线更像真实业务，降低了被云平台监测为恶意保活脚本的风险。

## 内存占用固定 (Memory Allocation)
静态申请：脚本启动时会申请 150MB 的内存（通过 bytearray）。

真实活跃：通过给字节数组首位赋值（memory_hog[0] = 1），确保这块内存被系统真正分配并计入活跃占用，而不是仅停留在虚拟内存阶段。

## 健康检查 HTTP 服务 (Health Check Monitor)
状态反馈：在 65080 端口启动了一个轻量级 Web 服务器。

外部监控对接：可以直接对接 Uptime Kuma 或面板，通过访问该端口实时查看脚本的内存和 CPU 运行状态。
