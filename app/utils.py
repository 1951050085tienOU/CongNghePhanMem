from app import app, db
from app.models import User, Receipt, Schedule, MedicalBill, Customer, CustomerSche
import hashlib
from sqlalchemy import func, extract

def get_user_by_id(user_id):
    return User.query.get(user_id)

def check_login(username, password):
    if username and password:
        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password.strip())).first()

def revenue_stats(month):
    p = db.session.query(extract('day', Receipt.created_date),
                         func.sum(Receipt.total_price))\
                        .filter(extract('month', Receipt.created_date) == month)\
                        .group_by(extract('day', Receipt.created_date))\
                        .order_by(extract('day', Receipt.created_date))
    return p.all()



