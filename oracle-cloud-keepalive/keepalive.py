import time
import os
import threading
import math
import subprocess
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 全局状态与锁 ---
STATUS = {
    "memory": "Not Allocated",
    "cpu": "Running",
    "traffic": "Idle"
}
# 关键：线程锁，确保同一时间只有一个下载任务在运行
traffic_lock = threading.Lock()

# --- HTTP 处理类 (用于监控查看) ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            
            response_text = (
                f"Oracle Cloud Keepalive Monitor\n"
                f"----------------------------\n"
                f"Memory Status  : {STATUS['memory']}\n"
                f"CPU Status     : {STATUS['cpu']}\n"
                f"Traffic Status : {STATUS['traffic']}\n"
                f"Schedule       : Daily 00:00 - 05:00 (System Time)\n"
                f"Current Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            self.wfile.write(response_text.encode('utf-8'))
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass

# --- 流量下载任务 (长周期保活逻辑) ---
def download_traffic_job():
    # 1. 尝试获取锁，如果拿不到，说明上一个任务还在跑
    if not traffic_lock.acquire(blocking=False):
        print(f"[{datetime.now()}] ⚠️ 任务跳过：上一个周期的任务尚未结束，为防止流量叠加，本次不启动。")
        return

    try:
        # 参数配置：1.3M Byte/s ≈ 10.4 Mbps (超过50M带宽的20%)
        target_url = "https://speed.cloudflare.com/__down?bytes=104857600" # 100MB
        rate_limit = "1.3M" 
        total_segments = 32 # 32段 * 100MB ≈ 3.2GB，总时长约 40-45 分钟

        print(f"[{datetime.now()}] 🚀 启动长周期保活任务 (限速: {rate_limit})...")
        
        for i in range(total_segments): 
            STATUS['traffic'] = f"Downloading: {i+1}/{total_segments} (@{rate_limit})"
            
            try:
                # 使用 wget 进行限速下载，结果丢弃到 /dev/null
                cmd = ["wget", f"--limit-rate={rate_limit}", "--tries=2", "-O", "/dev/null", target_url]
                subprocess.run(cmd, check=True)
                
                # 每段下载完稍作休息
                if i < (total_segments - 1):
                    time.sleep(5)
            except Exception as e:
                print(f"[{datetime.now()}] 分段下载异常: {e}")
                time.sleep(10)
                
    finally:
        # 2. 无论成功失败，最终都要释放锁，允许下次任务进入
        traffic_lock.release()
        STATUS['traffic'] = f"Idle (Finished at {datetime.now().strftime('%H:%M:%S')})"
        print(f"[{datetime.now()}] ✅ 本轮任务处理完毕。")

# --- 定时器监控线程 ---
def scheduler_loop():
    print("⏰ 定时任务监控线程已启动 (目标时间段: 00:00-04:59)")
    while True:
        now = datetime.now()
        # 每天 0, 1, 2, 3, 4 点的 00 分触发
        if now.hour in [0, 1, 2, 3, 4] and now.minute == 0:
            # 异步启动下载任务，不阻塞时间判断
            t = threading.Thread(target=download_traffic_job)
            t.start()
            time.sleep(65) # 避开当前分钟重复触发

        time.sleep(30)

def start_web_server(port=65080):
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"HTTP Monitor started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start web server: {e}")

def run_keepalive():
    print("Starting Oracle Cloud Keepalive Service...")
    
    # 1. 启动 Web 监控线程
    web_thread = threading.Thread(target=start_web_server, args=(65080,))
    web_thread.daemon = True
    web_thread.start()

    # 2. 启动定时器线程
    traffic_thread = threading.Thread(target=scheduler_loop)
    traffic_thread.daemon = True
    traffic_thread.start()

    # --- 获取 CPU 和 内存 参数 ---
    try:
        cpu_target_env = int(os.environ.get('TARGET_CPU_PERCENT', '15'))
        global_target = cpu_target_env / 100.0
    except:
        global_target = 0.15
        cpu_target_env = 15

    try:
        memory_mb_env = int(os.environ.get('TARGET_MEMORY_MB', '150'))
    except:
        memory_mb_env = 150

    STATUS['cpu'] = f"Running (Target: {cpu_target_env}%)"

    # 3. 内存占用
    if memory_mb_env > 0:
        try:
            print(f"Allocating {memory_mb_env}MB Memory...")
            memory_hog = bytearray(memory_mb_env * 1024 * 1024)
            if len(memory_hog) > 0: memory_hog[0] = 1
            STATUS['memory'] = f"Allocated ({memory_mb_env}MB)"
        except Exception as e:
            STATUS['memory'] = f"Failed: {e}"
    else:
        STATUS['memory'] = "Disabled"

    # 4. CPU 周期占用主循环
    print(f"Starting CPU cycle (Target: {cpu_target_env}%)...")
    cycle_total = 0.1
    while True:
        cycle_start = time.time()
        active_load = 0.35 + 0.15 * math.sin(cycle_start)
        work_quantum = cycle_total * global_target
        active_duration = work_quantum / active_load
        
        t0 = time.time()
        while time.time() - t0 < active_duration:
            _ = 123 * 456
        
        elapsed_total = time.time() - cycle_start
        sleep_remainder = cycle_total - elapsed_total
        if sleep_remainder > 0.001:
            time.sleep(sleep_remainder)

if __name__ == "__main__":
    run_keepalive()