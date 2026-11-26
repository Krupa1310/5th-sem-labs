from flask import Flask, jsonify

app = Flask(__name__)

users = {
    1: {"id": 1, "name": "Monika", "email": "monika@example.com"},
    2: {"id": 2, "name": "Krupa", "email": "krupa@example.com"},
    3: {"id": 3, "name": "Srujana", "email": "Srujana@example.com"}
}

@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "User Service",
        "status": "running"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)


