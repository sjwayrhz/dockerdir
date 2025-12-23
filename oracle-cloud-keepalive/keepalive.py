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

def start_web_server(port=65080):
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
    web_thread = threading.Thread(target=start_web_server, args=(65080,))
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
    
    
    # --- 数学模型参数 ---
    # 目标：总周期 0.1s，整体平均CPU占用率 15%。
    # 动态调整：我们将 0.1s 分为 "活跃期 (Active Phase)" 和 "休眠期 (Rest Phase)"。
    # 活跃期内的 CPU 瞬时占用率 (active_load) 服从正弦曲线变化：
    # active_load(t) = 35% + 15% * sin(t) -> 范围 [20%, 50%]
    # 
    # 计算公式：
    # 1. Total_Cycle = 0.1s
    # 2. Global_Target_Load = 0.15 (15%)
    # 3. Active_Load(t) = 0.35 + 0.15 * math.sin(time.time())
    # 4. 所需活跃期时长 (Active_Duration) = (Total_Cycle * Global_Target_Load) / Active_Load(t)
    #    推导: Active_Duration * Active_Load = Total_Cycle * Global_Target_Load = 0.015s (固定的15ms工作量)
    # 5. 休眠期时长 (Rest_Duration) = Total_Cycle - Active_Duration
    
    import math
    cycle_total = 0.1
    global_target = 0.15
    print(f"Smart Curve Mode: Cycle={cycle_total}s, Global Target={global_target*100}%")
    
    while True:
        cycle_start = time.time()
        
        # 1. 计算当前的瞬时负载目标 (20% ~ 50%)
        # 使用 time.time() 产生平滑的正弦波变化
        active_load = 0.35 + 0.15 * math.sin(cycle_start)
        
        # 2. 计算活跃期时长
        # 无论 active_load 是多少，我们每 0.1s 都要完成 0.015s 的纯计算工作
        work_quantum = cycle_total * global_target # 0.015s
        active_duration = work_quantum / active_load
        
        # 3. 执行活跃期 (Active Phase)
        # 在 active_duration 这段时间内，我们需要通过微小的 sleep 来模拟 active_load 的占用率
        # 为了平滑，我们把 active_duration 切分成若干个微切片 (slice)
        # 假设最小切片时长为 0.01s (10ms)
        param_slice = 0.01
        if active_duration < param_slice:
             param_slice = active_duration # 如果活跃期很短，就只做一个切片
             
        elapsed_active = 0
        while elapsed_active < active_duration:
            slice_start = time.time()
            
            # 本切片内应该工作多久？
            # slice_work = slice_duration * active_load
            # 为保证精确，我们直接计算剩余需要的总工作量，比较复杂，这里简化：
            # 既然目标是在 active_duration 内维持 active_load，
            # 那么每个 slice 也维持 active_load 即可。
            
            current_slice_work = param_slice * active_load
            current_slice_sleep = param_slice * (1 - active_load)
            
            # --- Work ---
            t0 = time.time()
            while time.time() - t0 < current_slice_work:
                _ = 123 * 456
                
            # --- Sleep (Active Phase internal sleep) ---
            # 只有当 sleep 时间足够长才 sleep，避免 overhead
            if current_slice_sleep > 0.001:
                time.sleep(current_slice_sleep)
                
            elapsed_active = time.time() - cycle_start
            
            # 如果已经超过了预计的活跃时间，强制跳出
            if elapsed_active >= active_duration:
                break
        
        # 4. 执行休眠期 (Rest Phase)
        # 补足剩余的 Total Cycle
        elapsed_total = time.time() - cycle_start
        sleep_remainder = cycle_total - elapsed_total
        
        if sleep_remainder > 0.001:
            time.sleep(sleep_remainder)


if __name__ == "__main__":
    run_keepalive()