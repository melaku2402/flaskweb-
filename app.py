import json
import os

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash

from models import db, Order

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tastybite-secret-key'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'orders.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# menu data, kept hardcoded since it's just menu content, not order data
menu = [
    {"id": 1, "name": "Doro Wat", "description": "Spicy chicken stew cooked in berbere sauce and butter.", "price": 120, "image": "images/doro.jpg"},
    {"id": 2, "name": "Shiro Wat", "description": "Chickpea stew simmered with spices and berbere.", "price": 100, "image": "images/shiro.jpg"},
    {"id": 3, "name": "Kitfo", "description": "Minced raw beef seasoned with mitmita and spices.", "price": 150, "image": "images/kitfo.jpg"},
    {"id": 4, "name": "Tibs", "description": "Stir-fried beef with onions, peppers and spices.", "price": 230, "image": "images/tibs.jpg"},
    {"id": 5, "name": "Veggie Combo", "description": "A combination of our delicious vegetarian dishes.", "price": 90, "image": "images/veggie.jpg"}
]


# ---------- Public site ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/menu', methods=['GET'])
def api_get_menu():
    return jsonify(menu)


# ---------- Order API (backed by SQLite) ----------

@app.route('/api/orders', methods=['POST'])
def api_add_order():
    data = request.get_json()

    if not data or 'items' not in data or len(data['items']) < 1:
        return jsonify({"error": "order needs at least one item"}), 400

    customer = (data.get('customer') or '').strip() or 'Walk-in Customer'
    items = data['items']
    quantity = sum(int(item.get('qty', 0)) for item in items)
    total_price = float(data.get('total', 0))

    order = Order(
        customer=customer,
        items=json.dumps(items),
        quantity=quantity,
        total_price=total_price,
        status='Pending'
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({"message": "order saved", "order": order.to_dict()}), 201


@app.route('/api/orders', methods=['GET'])
def api_get_orders():
    orders = Order.query.order_by(Order.date_time.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def api_update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    new_status = data.get('status')

    if not new_status:
        return jsonify({"error": "status is required"}), 400

    order.status = new_status
    db.session.commit()
    return jsonify({"message": "order updated", "order": order.to_dict()})


@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "order deleted"})


# ---------- Admin routes ----------

@app.route('/admin/orders', methods=['GET', 'POST'])
def admin_orders():
    if request.method == 'POST':
        order_id = request.form.get('order_id', type=int)
        action = request.form.get('action')
        order = Order.query.get(order_id)

        if order:
            if action == 'cancel':
                order.status = 'Cancelled'
                db.session.commit()
                flash(f'Order #{order.id} was cancelled.', 'success')
            elif action == 'delete':
                db.session.delete(order)
                db.session.commit()
                flash(f'Order #{order_id} was deleted.', 'success')
        else:
            flash('Order not found.', 'error')

        return redirect(url_for('admin_orders'))

    orders = Order.query.order_by(Order.date_time.desc()).all()
    return render_template('admin_orders.html', orders=orders)


@app.route('/admin/add', methods=['GET', 'POST'])
def admin_add():
    if request.method == 'POST':
        customer = request.form.get('customer', '').strip()
        item_names = request.form.getlist('item_name[]')
        item_qtys = request.form.getlist('item_qty[]')
        total_price = request.form.get('total_price', type=float)

        items = []
        quantity = 0
        for name, qty in zip(item_names, item_qtys):
            name = name.strip()
            if not name:
                continue
            qty = int(qty) if qty and qty.isdigit() else 1
            menu_item = next((m for m in menu if m['name'] == name), None)
            price = menu_item['price'] if menu_item else 0
            items.append({"name": name, "price": price, "qty": qty})
            quantity += qty

        if not customer or not items or total_price is None:
            flash('Please fill in customer, at least one item, and total price.', 'error')
            return render_template('admin_add.html', menu=menu)

        order = Order(
            customer=customer,
            items=json.dumps(items),
            quantity=quantity,
            total_price=total_price,
            status='Pending'
        )
        db.session.add(order)
        db.session.commit()
        flash(f'Order #{order.id} for {customer} was added.', 'success')
        return redirect(url_for('admin_orders'))

    return render_template('admin_add.html', menu=menu)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
