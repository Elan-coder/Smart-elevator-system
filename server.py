from flask import Flask, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)

# Initial lift and floor status
lift_data = {
    "current_floor": 1,
    "target_floor": None,
    "lift_status": "Stationary",
    "direction": "None",
    "floors": {
        "1": False,
        "2": False,
        "3": False
    },
    "last_update": {
        "1": "No update",
        "2": "No update",
        "3": "No update"
    }
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Lift Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef3f8;
            margin: 0;
            padding: 20px;
        }

        .header {
            background: #111827;
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
        }

        .header h1 {
            margin: 0;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 5px 15px rgba(0,0,0,0.08);
        }

        .card h2 {
            margin: 10px 0 0;
            font-size: 28px;
        }

        .label {
            color: #64748b;
            font-weight: bold;
        }

        .main {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
        }

        .floor-card {
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .active {
            background: #f0fdf4;
            border-color: #22c55e;
        }

        .no-person {
            background: #fee2e2;
            color: #991b1b;
            padding: 8px 14px;
            border-radius: 20px;
            font-weight: bold;
        }

        .person {
            background: #dcfce7;
            color: #166534;
            padding: 8px 14px;
            border-radius: 20px;
            font-weight: bold;
        }

        .moving {
            color: #2563eb;
        }

        .stationary {
            color: #16a34a;
        }

        .shaft {
            position: relative;
            height: 360px;
            background: #f8fafc;
            border: 3px solid #cbd5e1;
            border-radius: 18px;
            overflow: hidden;
        }

        .floor-line {
            position: absolute;
            left: 0;
            right: 0;
            border-top: 2px dashed #94a3b8;
        }

        .floor-line span {
            background: #f8fafc;
            padding: 5px 10px;
            position: relative;
            top: -15px;
            left: 15px;
            font-weight: bold;
        }

        .floor3 { top: 60px; }
        .floor2 { top: 170px; }
        .floor1 { top: 280px; }

        .lift {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: 110px;
            height: 70px;
            background: #1d4ed8;
            color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            transition: bottom 1s;
        }

        .log {
            background: #0f172a;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 12px;
            min-height: 80px;
        }

        @media(max-width: 900px) {
            .grid, .main {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <div class="header">
        <h1>Smart Lift Monitoring Dashboard</h1>
        <p>Live person detection from Floor 1, Floor 2 and Floor 3 laptops</p>
    </div>

    <div class="grid">
        <div class="card">
            <div class="label">Current Floor</div>
            <h2 id="currentFloor">Floor 1</h2>
        </div>

        <div class="card">
            <div class="label">Lift Status</div>
            <h2 id="liftStatus">Stationary</h2>
        </div>

        <div class="card">
            <div class="label">Direction</div>
            <h2 id="direction">None</h2>
        </div>

        <div class="card">
            <div class="label">Moving Towards</div>
            <h2 id="targetFloor">None</h2>
        </div>
    </div>

    <div class="main">
        <div class="card">
            <h2>Floor Person Detection</h2>

            <div class="floor-card" id="floorCard1">
                <div>
                    <h3>Floor 1</h3>
                    <p id="floorTime1">No update</p>
                </div>
                <span id="floorStatus1" class="no-person">NO</span>
            </div>

            <div class="floor-card" id="floorCard2">
                <div>
                    <h3>Floor 2</h3>
                    <p id="floorTime2">No update</p>
                </div>
                <span id="floorStatus2" class="no-person">NO</span>
            </div>

            <div class="floor-card" id="floorCard3">
                <div>
                    <h3>Floor 3</h3>
                    <p id="floorTime3">No update</p>
                </div>
                <span id="floorStatus3" class="no-person">NO</span>
            </div>
        </div>

        <div class="card">
            <h2>Lift Shaft View</h2>

            <div class="shaft">
                <div class="floor-line floor3"><span>Floor 3</span></div>
                <div class="floor-line floor2"><span>Floor 2</span></div>
                <div class="floor-line floor1"><span>Floor 1</span></div>
                <div class="lift" id="liftBox">LIFT</div>
            </div>
        </div>
    </div>

    <br>

    <div class="card">
        <h2>System Log</h2>
        <div class="log" id="systemLog">
            Waiting for floor laptop data...
        </div>
    </div>

<script>
    const floorPositions = {
        1: 35,
        2: 145,
        3: 255
    };

    async function loadStatus() {
        const response = await fetch("/status");
        const data = await response.json();

        document.getElementById("currentFloor").innerText = "Floor " + data.current_floor;
        document.getElementById("liftStatus").innerText = data.lift_status;
        document.getElementById("direction").innerText = data.direction;
        document.getElementById("targetFloor").innerText = data.target_floor ? "Floor " + data.target_floor : "None";

        let liftStatus = document.getElementById("liftStatus");
        liftStatus.className = data.lift_status === "Moving" ? "moving" : "stationary";

        document.getElementById("liftBox").style.bottom = floorPositions[data.current_floor] + "px";

        for (let i = 1; i <= 3; i++) {
            let card = document.getElementById("floorCard" + i);
            let status = document.getElementById("floorStatus" + i);
            let time = document.getElementById("floorTime" + i);

            if (data.floors[i] === true) {
                card.classList.add("active");
                status.innerText = "PERSON";
                status.className = "person";
            } else {
                card.classList.remove("active");
                status.innerText = "NO";
                status.className = "no-person";
            }

            time.innerText = "Last update: " + data.last_update[i];
        }

        document.getElementById("systemLog").innerText =
            "Lift is " + data.lift_status +
            " | Current Floor: " + data.current_floor +
            " | Moving Towards: " + (data.target_floor ? "Floor " + data.target_floor : "None");
    }

    setInterval(loadStatus, 1000);
    loadStatus();
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/update", methods=["POST"])
def update_floor():
    data = request.get_json()

    floor = str(data.get("floor"))
    detected = bool(data.get("person_detected"))

    if floor not in lift_data["floors"]:
        return jsonify({"error": "Invalid floor"}), 400

    lift_data["floors"][floor] = detected
    lift_data["last_update"][floor] = datetime.now().strftime("%H:%M:%S")

    # If person detected, set lift target floor
    if detected:
        target = int(floor)

        if target != lift_data["current_floor"]:
            lift_data["target_floor"] = target
            lift_data["lift_status"] = "Moving"

            if target > lift_data["current_floor"]:
                lift_data["direction"] = "Up"
            else:
                lift_data["direction"] = "Down"

            # Simulate lift reaching after some time
            lift_data["current_floor"] = target
            lift_data["lift_status"] = "Stationary"
            lift_data["direction"] = "None"
            lift_data["target_floor"] = None

        # Request served
        lift_data["floors"][floor] = False

    return jsonify({"message": "Updated successfully", "data": lift_data})


@app.route("/status")
def status():
    return jsonify(lift_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)