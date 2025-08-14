from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Mengizinkan semua origin

URL = "http://192.168.88.123:20080/api_jsonrpc.php"
USERNAME = "Admin"
PASSWORD = "zabbix"
GROUP_ID = "32"

def login():
    payload = {
        "jsonrpc": "2.0",
        "method": "user.login",
        "params": {
            "username": USERNAME,
            "password": PASSWORD
        },
        "id": 1
    }
    r = requests.post(URL, json=payload)
    result = r.json()
    return result.get("result")

def get_problems(token):
    payload = {
        "jsonrpc": "2.0",
        "method": "problem.get",
        "params": {
            "output": "extend",
            "groupids": [GROUP_ID],
            "recent": True,
            "sortfield": "eventid",
            "sortorder": "DESC"
        },
        "id": 1
    }
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(URL, json=payload, headers=headers)
    problems = r.json().get("result", [])
    return [p["eventid"] for p in problems]

def acknowledge(token, eventids):
    payload = {
        "jsonrpc": "2.0",
        "method": "event.acknowledge",
        "params": {
            "eventids": eventids,
            "action": 2,
            "message": "Problem investigated and resolved."
        },
        "id": 1
    }
    headers = {"Authorization": f"Bearer {token}"}
    return requests.post(URL, json=payload, headers=headers).json()

@app.route("/ack", methods=["GET"])
def ack_all():
    token = login()
    if not token:
        return jsonify({"status": "error", "message": "Login failed"})
    event_ids = get_problems(token)
    if not event_ids:
        return jsonify({"status": "ok", "message": "No problems to acknowledge"})
    result = acknowledge(token, event_ids)
    return jsonify({"status": "ok", "ack_response": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
