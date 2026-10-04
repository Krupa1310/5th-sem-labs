from flask import Flask, jsonify

app = Flask(__name__)

products = {
    1: {"id": 1, "name": "Laptop", "price": 50000},
    2: {"id": 2, "name": "Headphones", "price": 2000},
    3: {"id": 3, "name": "Keyboard", "price": 1500}
}

@app.route("/product/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = products.get(product_id)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "Product Service",
        "status": "running"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)



