from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "keys.json"

# Load existing key-UUID mappings
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Save key-UUID mappings
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/verify", methods=["POST"])
def verify_key():
    data = request.get_json()
    uuid = data.get("uuid")
    key = data.get("key")

    if not uuid or not key:
        return jsonify({"status": "error", "message": "Missing UUID or key"}), 400

    keys_db = load_data()

    if key in keys_db:
        if keys_db[key] != uuid:
            return jsonify({"status": "error", "message": "Key already used with a different UUID"}), 403
    else:
        keys_db[key] = uuid
        save_data(keys_db)

    return jsonify({"status": "success", "message": "Key verified"})

if __name__ == "__main__":
    # Render and many other platforms use the PORT environment variable.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
