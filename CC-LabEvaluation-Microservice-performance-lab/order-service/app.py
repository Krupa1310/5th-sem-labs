from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route("/order", methods=["POST"])
def create_order():
    data = request.get_json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")

    user_response = requests.get(
        f"http://user-service:5002/user/{user_id}"
    )

    product_response = requests.get(
        f"http://product-service:5001/product/{product_id}"
    )

    if user_response.status_code != 200:
        return jsonify({"error": "User not found"}), 404

    if product_response.status_code != 200:
        return jsonify({"error": "Product not found"}), 404

    user = user_response.json()
    product = product_response.json()

    return jsonify({
        "message": "Order created successfully",
        "user": user,
        "product": product
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Order Service",
        "status": "running"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


