import time
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- 全局变量用于状态监控 ---
STATUS = {
    "memory": "Not Allocated",
    "cpu": "Running"
}

# --- HTTP 处理类 ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 如果访问根路径 /
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            # 返回当前状态给 Uptime Kuma
            response_text = f"Keepalive Running.\nMemory: {STATUS['memory']}\nCPU Target: 15%"
            self.wfile.write(response_text.encode('utf-8'))
        else:
            self.send_error(404)

    # 禁止显示日志到控制台，以免和keepalive日志混淆（可选）
    def log_message(self, format, *args):
        pass

def start_web_server(port=8080):
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"HTTP Monitor started on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Failed to start web server: {e}")

def run_keepalive():
    print("Starting Oracle Cloud Keepalive...")
    
    # --- 启动 HTTP 监控线程 ---
    # Daemon=True 表示主程序退出时，这个线程也会随之退出
    web_thread = threading.Thread(target=start_web_server, args=(8080,))
    web_thread.daemon = True
    web_thread.start()

    # --- 内存占用部分 ---
    try:
        print("Allocating 150MB Memory...")
        memory_hog = bytearray(150 * 1024 * 1024) 
        memory_hog[0] = 1 
        STATUS['memory'] = "Allocated (150MB)" # 更新状态
        print("Memory Allocated Successfully.")
    except Exception as e:
        STATUS['memory'] = f"Failed: {e}"
        print(f"Memory Allocation Failed: {e}")

    # --- CPU 占用部分 ---
    print("Starting CPU cycle (Target: 15%)...")
    
    work_duration = 0.015
    sleep_duration = 0.085
    
    while True:
        start_time = time.time()
        while time.time() - start_time < work_duration:
            _ = 123 * 456
        
        # 这里的 sleep 非常重要，它不仅控制 CPU 占用率，
        # 还释放了 GIL 锁，让 HTTP 线程有机会处理请求。
        time.sleep(sleep_duration)

if __name__ == "__main__":
    run_keepalive()