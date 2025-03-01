from flask import Flask, request, jsonify, render_template_string
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

# HTML Template for Key Management Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Key Management</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        button {
            padding: 6px 12px;
            margin: 5px;
            cursor: pointer;
        }
        h1 {
            text-align: center;
        }
    </style>
</head>
<body>
    <h1>Key Management</h1>
    <table>
        <tr>
            <th>Key</th>
            <th>UUID</th>
            <th>Action</th>
        </tr>
        {% for key, uuid in keys.items() %}
        <tr>
            <td>{{ key }}</td>
            <td>{{ uuid }}</td>
            <td>
                <form method="POST" action="/remove_key/{{ key }}">
                    <button type="submit">Remove Key</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Route to view keys and UUIDs
@app.route("/admin")
def admin():
    keys_db = load_data()
    return render_template_string(HTML_TEMPLATE, keys=keys_db)

# Route to remove a key
@app.route("/remove_key/<key>", methods=["POST"])
def remove_key(key):
    keys_db = load_data()
    if key in keys_db:
        del keys_db[key]
        save_data(keys_db)
        return jsonify({"status": "success", "message": "Key removed"})
    else:
        return jsonify({"status": "error", "message": "Key not found"}), 404

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
