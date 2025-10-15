import time, socket, shutil, os

now = time.strftime("%Y-%m-%d %H:%M:%S")
host = socket.gethostname()
t,u,f = shutil.disk_usage("/")
disk = f"disk: used {u//(1024**3)}G / {t//(1024**3)}G, free {f//(1024**3)}G"
try:
    with open("/proc/uptime") as fp:
        up = int(float(fp.read().split()[0]))
    uptime = f"uptime: {up//3600}h {(up%3600)//60}m"
except Exception:
    uptime = "uptime: n/a"

line = f"{now} [{host}] {disk}; {uptime}\n"

os.makedirs("/var/log", exist_ok=True)  # usually exists, safe
with open("/var/log/report.log", "a") as f:
    f.write(line)