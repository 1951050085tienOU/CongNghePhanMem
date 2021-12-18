from datetime import datetime
from app import app, db
from sqlalchemy.sql import func
from sqlalchemy.orm import session, query
from sqlalchemy import func, extract
from app.models import *
from flask_login import current_user
import hashlib


def check_password(username, password):          #kiểm tra mật khẩu, tài khoản trên database
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def get_user_by_id(user_id):    #lấy thông tin user dùng cho xử lý đăng nhập
    return User.query.get(user_id)


def revenue_stats(month, year):  #Thống kê doanh thu mỗi ngày trong tháng
    p = db.session.query(extract('day', Receipt.created_date),
                         func.sum(Receipt.total_price))\
                        .filter(extract('month', Receipt.created_date) == month,
                                extract('year', Receipt.created_date) == year)\
                        .group_by(extract('day', Receipt.created_date))\
                        .order_by(extract('day', Receipt.created_date))

    return p.all()


def create_list_of_months(present_month):     #lập danh sách những (6) tháng liền kề
    months = 6   #số tháng được tính
    list_of_months = []
    if present_month >= 6:  #những trường hợp tháng hiện tại qua tháng 6
        for mm in range(present_month, present_month-months, -1):
            list_of_months.append(mm)
    else:                    #những trường hợp tháng hiện tại chưa qua tháng 6
        for mm in range(present_month, 0, -1):
            list_of_months.append(mm)
        for mm in range(12, 12 - months + len(list_of_months), -1):
            list_of_months.append(mm)
    return list_of_months


def all_revenue_stats(month, year):    #Thống kê doanh thu tất cả trong tháng trong năm
    revenue_values = revenue_stats(month, year)
    amount = 0
    for value in revenue_values:
        amount += value[1]
    return amount


def get_all_amount_of_medicine():         #lấy số lượng thuốc đang tồn kho
    list_medicine = Medicine.query.all()
    amount = 0
    for medicine in list_medicine:
        amount += medicine.quantity
    return amount


def get_medicine_by_id(medicine_id):    #lấy tên thuốc bằng id của thuốc
    return Medicine.query.get(medicine_id).name


def get_auth_orders(date):
    return db.session.query(Schedule.id).filter(extract('year', Schedule.examination_date) == date.year,
                                                extract('month', Schedule.examination_date) == date.month,
                                                extract('day', Schedule.examination_date) == date.day).all()


def get_amount_orders_in_date(date):
    all_in_date = get_auth_orders(date)
    count = 0
    for order in all_in_date:
        count += 1
    return count


def get_regulation():
    value = []
    primary = Regulation.query.get(1) #primary đang sử dụng
    value.append(primary.customer_quantity)
    value.append(primary.examination_price)
    return value


def medine_stock_percent_over_5():             #lấy danh sách phần trăm thuốc trong tổng dưới dạng [id, percent, ..., 'OTHER', percent]
    list_medicine = db.session.query(Medicine.id, Medicine.quantity)\
            .order_by(-Medicine.quantity).all()
    max_quantity = get_all_amount_of_medicine()
    list_off = []
    count = 0
    for medicine in list_medicine:        #tính toán đưa ra những giá trị hơn 5% và ghi vào list
        if medicine.quantity / max_quantity * 100 >= 5:
            list_off.append(medicine.id)
            list_off.append(medicine.quantity)
            count += medicine.quantity
    list_off.append('OTHER')
    list_off.append(max_quantity - count)
    return list_off


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


def medicine_fill():
    return Medicine.query.filter(Medicine.quantity>0, Medicine.quantity<10).all()


def medicine_out_of_stock():
    return Medicine.query.filter(Medicine.quantity==0)


def medicine_in_stock():
    medicines = Medicine.query.all()
    q = 0
    for m in medicines:
        q += m.quantity
    return q


def used_medicine():
    medicals = MedicalBillDetail.query.all()
    q = 0
    for m in medicals:
        q += m.quantity
    return q