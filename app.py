from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__)

ORDERS_FILE = 'orders.json'

# menu data
menu = [
    {"id": 1, "name": "Doro Wat", "description": "Spicy chicken stew cooked in berbere sauce and butter.", "price": 120, "image": "images/doro.jpg"},
    {"id": 2, "name": "Shiro Wat", "description": "Chickpea stew simmered with spices and berbere.", "price": 100, "image": "images/shiro.jpg"},
    {"id": 3, "name": "Kitfo", "description": "Minced raw beef seasoned with mitmita and spices.", "price": 150, "image": "images/kitfo.jpg"},
    {"id": 4, "name": "Tibs", "description": "Stir-fried beef with onions, peppers and spices.", "price": 230, "image": "images/tibs.jpg"},
    {"id": 5, "name": "Veggie Combo", "description": "A combination of our delicious vegetarian dishes.", "price": 90, "image": "images/veggie.jpg"}
]


def read_orders():
    if not os.path.exists(ORDERS_FILE):
        return []
    with open(ORDERS_FILE, 'r') as f:
        content = f.read().strip()
        if content == '':
            return []
        return json.loads(content)


def write_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=2)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/menu', methods=['GET'])
def api_get_menu():
    return jsonify(menu)


@app.route('/api/orders', methods=['POST'])
def api_add_order():
    data = request.get_json()

    if not data or 'items' not in data or len(data['items']) < 1:
        return jsonify({"error": "order needs at least one item"}), 400

    orders = read_orders()

    order = {
        "id": len(orders) + 1,
        "items": data['items'],
        "total": data.get('total', 0)
    }

    orders.append(order)
    write_orders(orders)

    return jsonify({"message": "order saved", "order": order}), 201


@app.route('/api/orders', methods=['GET'])
def api_get_orders():
    return jsonify(read_orders())


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
