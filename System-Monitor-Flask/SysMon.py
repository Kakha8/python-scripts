from flask import Flask, Response
import psutil
import time

app = Flask(__name__)

def stream_usage():
    # kick browser out of buffering
    yield ("Streaming CPU/RAM. Ctrl+C to stop.\n" + (" " * 2048) + "\n")

    # warm up so first cpu_percent isn't 0.0
    psutil.cpu_percent(interval=None)

    while True:

        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory().percent
        ram_used = psutil.virtual_memory().used
        disk = psutil.disk_usage("C:\\").percent
        yield (f"CPU: {cpu:5.1f}% | RAM: {ram:5.1f}% | {ram_used:5.1f}% | {disk:5.1f}%\n")
        time.sleep(1)  # 1 line/sec

@app.route("/")
def index():
    return Response(
        stream_usage(),
        mimetype="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # defeats some proxies (harmless locally)
        },
    )

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True, use_reloader=False)
