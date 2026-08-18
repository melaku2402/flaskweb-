from datetime import datetime
import json

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(120), nullable=False)
    items = db.Column(db.Text, nullable=False)          # JSON-encoded list of {name, price, qty}
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_price = db.Column(db.Float, nullable=False, default=0)
    date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    def get_items(self):
        """Decode the stored JSON items string back into a Python list."""
        try:
            return json.loads(self.items)
        except (TypeError, ValueError):
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "customer": self.customer,
            "items": self.get_items(),
            "quantity": self.quantity,
            "total_price": self.total_price,
            "date_time": self.date_time.strftime('%Y-%m-%d %H:%M:%S'),
            "status": self.status,
        }
