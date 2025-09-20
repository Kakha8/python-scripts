from flask import Flask, Response, render_template
import psutil
import time

app = Flask(__name__)

def stream_usage():
    psutil.cpu_percent(interval=None)  # warm up

    while True:
        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory().percent
        ram_used = psutil.virtual_memory().used / (1024 ** 3)  # GB
        disk = psutil.disk_usage("C:\\").percent
        # SSE format: "data: ...\n\n"
        yield f"data: CPU: {cpu:.1f}% | RAM: {ram:.1f}% ({ram_used:.2f} GB) | Disk: {disk:.1f}%\n\n"
        time.sleep(1)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/stream")
def stream():
    return Response(
        stream_usage(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True, use_reloader=False)
