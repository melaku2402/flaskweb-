# TastyBite - Hotel Menu Flask Project (SQLite Edition)

Ethiopian restaurant menu & ordering site, upgraded to persist orders in **SQLite** via **Flask-SQLAlchemy** instead of `orders.json`.

## Setup

```bash
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Visit `http://127.0.0.1:5000/`. The SQLite database file `orders.db` is created automatically on first run.

## Database

- Engine: **SQLite** (`orders.db`, auto-created)
- ORM: **Flask-SQLAlchemy**
- Model: `Order` (`models.py`) — id, customer, items (JSON), quantity, total_price, date_time, status

## Routes

**Public**
- `GET /` — homepage / menu / cart
- `GET /api/menu` — menu data (JSON)
- `POST /api/orders` — place an order (saved to SQLite)
- `GET /api/orders` — list all orders (JSON)
- `PUT /api/orders/<id>` — update an order's status
- `DELETE /api/orders/<id>` — delete an order

**Admin**
- `GET/POST /admin/orders` — view all orders, cancel or delete an order
- `GET/POST /admin/add` — add a new order manually

## Notes

- `orders.db` and `venv/` are excluded via `.gitignore`.
- Menu items stay hardcoded in `app.py` (not order data, so no DB table needed for them).
