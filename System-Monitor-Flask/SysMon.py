from flask import Flask, Response, render_template, jsonify
import psutil
import platform
import time
import json
import cpuinfo
import wmi



app = Flask(__name__)

def getCpuSpecs():
    cpu_spec = cpuinfo.get_cpu_info()

    architechture = cpu_spec['arch']
    cpu_general = cpu_spec['brand_raw']
    clock_speed = cpu_spec['hz_advertised_friendly']

    cpu_info = {
        "CPU": cpu_general,
        "Architecture": architechture,
        "Cores": psutil.cpu_count(logical=False),
        "Clock_speed": clock_speed
    }
    #print(cpu_spec['brand_raw'])
    print(cpu_spec)

    return cpu_info

def getRamSpecs():
    ram_total = psutil.virtual_memory().total / (1024 ** 3)
    ram_total = round(ram_total, 1)
    return {"ram_total": ram_total}

def getDiskSpecs():
    disk_total = psutil.disk_usage("C:\\").total / (1024 ** 3)
    disk_total = round(disk_total, 1)
    return {"disk_total": disk_total}

def stream_usage():
    psutil.cpu_percent(interval=None)  # warm up

    while True:
        cpu = psutil.cpu_percent(interval=0)
        ram = psutil.virtual_memory().percent
        ram_used = psutil.virtual_memory().used / (1024 ** 3)  # GB
        disk = psutil.disk_usage("C:\\").percent


        # Dictionary with values
        result = {"cpu": cpu, "ram": ram, "ram_used": ram_used, "disk": disk}

        # SSE requires text, so dump dict as JSON
        yield f"data: {json.dumps(result)}\n\n"

        time.sleep(1)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/live_usage")
def liveUsage():
    return Response(
        stream_usage(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.route("/specs")
def specs():
    return jsonify({
        "cpu": getCpuSpecs(),
        "ram": getRamSpecs(),
        "disk": getDiskSpecs()
    })

if __name__ == "__main__":
    #getCpuSpecs()
    app.run(host="127.0.0.1", port=5000, debug=True, threaded=True, use_reloader=False)
