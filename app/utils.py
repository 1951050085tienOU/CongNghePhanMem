from app import app, db
from app.models import User, Receipt, Schedule, MedicalBill, Customer, CustomerSche, \
    Medicine, MedicalBillDetail, Regulation
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

def examination_stats(month):
    p = db.session.query(extract('day', Schedule.examination_date), func.count(CustomerSche.customer_id))\
                        .join(Customer, CustomerSche.customer_id.__eq__(Customer.id))\
                        .join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                        .filter(CustomerSche.examined == True)\
                        .filter(extract('month', Schedule.examination_date) == month)\
                        .group_by(extract('day', Schedule.examination_date))\
                        .order_by(extract('day', Schedule.examination_date))
    return p.all()

def medicine_stats():
    return db.session.query(Medicine.name, Medicine.quantity)\
                        .filter(Medicine.quantity>0)\
                        .group_by(Medicine.name).all()

def thuoc_bo_sung():
    return Medicine.query.filter(Medicine.quantity>0, Medicine.quantity<10).all()

def thuoc_het_sl():
    return Medicine.query.filter(Medicine.quantity==0)

def thuoc_ton_kho():
    medicines = Medicine.query.all()
    q = 0
    for m in medicines:
        q += m.quantity
    return q

def thuoc_da_dung():
    medicals = MedicalBillDetail.query.all()
    q = 0
    for m in medicals:
        q += m.quantity
    return q

def luot_kham(date):
    customers = [0, 0, 0]
    #Số lượt khám tối đa
    customers[0] = Regulation.query.filter(extract('day', Regulation.created_date).__le__(date)).all()[-1].customer_quantity
    # Số lượt khám đã hẹn
    customers[1] = len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                                .filter(extract('day', Schedule.examination_date) == date).all())
    #Số lượt khám còn lại
    customers[2] = (customers[0] - customers[1])
    return customers


'''#Số khách chưa khám
return len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                                .filter(extract('day', Schedule.examination_date) == date)\
                                .filter(CustomerSche.examined == False).all())
#Số khách đã khám
return len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                                .filter(extract('day', Schedule.examination_date) == date)\
                                .filter(CustomerSche.examined == True).all())'''


