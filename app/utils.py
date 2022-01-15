from datetime import datetime
from app import app, db, client, keys
from sqlalchemy.sql import func
from sqlalchemy.orm import session, query
from sqlalchemy import func, extract
from app.models import *
from flask_login import current_user
from flask import session, request, jsonify
import hashlib


def check_password(username, password):          #kiểm tra mật khẩu, tài khoản trên database
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())

    return User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password)).first()


def get_user_by_id(user_id):    #lấy thông tin user dùng cho xử lý đăng nhập
    return User.query.get(user_id)


def check_real_information(user_id):
    user_all = User.query.all()
    for us in user_all:
        if user_id.__eq__(us.id):
            return True
    return False


def revenue_stats_by_day(month, year):  #Thống kê doanh thu mỗi ngày trong tháng
    p = db.session.query(extract('day', Receipt.created_date),
                         func.sum(Receipt.total_price))\
                        .filter(extract('month', Receipt.created_date) == month,
                                extract('year', Receipt.created_date) == year)\
                        .group_by(extract('day', Receipt.created_date))\
                        .order_by(extract('day', Receipt.created_date))

    return p.all()


def revenue_stats(month, year, doanhthu):
    p = db.session.query(extract('day', Receipt.created_date), func.count(Customer.id),
                         func.sum(Receipt.total_price), (func.sum(Receipt.total_price)/doanhthu)*100)\
                        .join(Customer, Receipt.customer_id.__eq__(Customer.id))\
                        .filter(extract('month', Receipt.created_date) == month, extract('year', Receipt.created_date) == year)\
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
    revenue_values = revenue_stats_by_day(month, year)
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


def get_last_reg():
    all_reg = Regulation.query.all()
    for reg in all_reg[::-1]:
        return reg.id


def get_regulation():
    value = []
    primary = Regulation.query.get(get_last_reg()) #primary đang sử dụng
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


def examination_stats(month, year):
    p = db.session.query(extract('day', Schedule.examination_date), func.count(CustomerSche.customer_id))\
                        .join(Customer, CustomerSche.customer_id.__eq__(Customer.id))\
                        .join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                        .filter(CustomerSche.examined == True, extract('month', Schedule.examination_date) == month,
                                extract('year', Schedule.examination_date) == year)\
                        .group_by(extract('day', Schedule.examination_date))\
                        .order_by(extract('day', Schedule.examination_date))
    return p.all()

def medicine_stats(month,year):
    return Medicine.query.join(MedicalBillDetail, MedicalBillDetail.medicine.__eq__(Medicine.id))\
        .join(MedicalBill, MedicalBillDetail.medical_bill.__eq__(MedicalBill.id))\
        .join(Receipt, Receipt.medical_bill.__eq__(MedicalBill.id))\
        .filter(extract('month', Receipt.created_date) == month, extract('year', Receipt.created_date) == year)\
        .add_columns(func.sum(MedicalBillDetail.quantity)).add_columns(func.count(MedicalBillDetail.medicine))\
        .order_by(Medicine.id).group_by(Medicine.id).all()

# def medicine_stats(month, year):
#     return db.session.query(Medicine.name, Medicine.quantity)\
#                         .filter(Medicine.quantity>0)\
#                         .group_by(Medicine.name).all()


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


def get_user_information():
    return current_user


def edit_user_information(user_id, first_name, last_name, birthday, phone_number, gender):
    user = get_user_by_id(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.birthday = birthday
    user.phone_number = phone_number
    #user.gender_id = gender
    db.session.add(user)
    db.session.commit()


def thuoc_bo_sung():
    return Medicine.query.filter(Medicine.quantity > 0, Medicine.quantity < 10).all()


def thuoc_het_sl():
    return Medicine.query.filter(Medicine.quantity == 0)


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


# def luot_kham(date):
#     customers = [0, 0, 0]
#     #Số lượt khám tối đa
#     customers[0] = Regulation.query.filter(extract('day', Regulation.created_date).__le__(date)).all()[-1].customer_quantity
#     # Số lượt khám đã hẹn
#     customers[1] = len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
#                                 .filter(extract('day', Schedule.examination_date) == date).all())
#     #Số lượt khám còn lại
#     customers[2] = (customers[0] - customers[1])
#     return customers


def reformat_phone_number(phone_number):
    phone_number = str(phone_number)
    print(phone_number)
    #only in vietnam
    if phone_number.startswith('84') and phone_number.__len__() == 11:
        return '+' + phone_number
    elif phone_number.startswith('0') and phone_number.__len__() == 10:
        return '+84' + phone_number[1:]
    else:
        return 0


def send_messages(to_phone, content):
    to_phone = reformat_phone_number(to_phone)
    if to_phone != '' and content !='':
        message = client.messages.create(
            body=content,
            from_=keys['twilio_number'],
            to=to_phone)


def get_customer_by_phone(phone_number):
    return Customer.query.filter(Customer.phone_number.__eq__(phone_number)).first()

def session_clear(key):
     if key in session:
         del session[key]

def luot_kham(date):
    customers = [0, 0, 0]
    #Số lượt khám tối đa
    customers[0] = Regulation.query.filter(extract('day', Regulation.created_date).__le__(date)).all()[-1].customer_quantity
    # Số lượt khám đã hẹn
    customers[1] = len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                                .filter(Schedule.examination_date.__eq__(date)).all())
    #Số lượt khám còn lại
    customers[2] = (customers[0] - customers[1])
    return customers

def KiemTraRole(user):
    return str(user.user_role)

def LichHenNgay(date):
    return Customer.query.join(CustomerSche, CustomerSche.customer_id.__eq__(Customer.id))\
        .join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
        .filter(Schedule.examination_date.__eq__(date)).all()

def BenhNhanHienTai(date):
    return Customer.query.join(CustomerSche, CustomerSche.customer_id.__eq__(Customer.id)) \
        .join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id)) \
        .filter(Schedule.examination_date.__eq__(date), CustomerSche.examined == False).first()

def ThongKeBenhNhan(date):
    customers = [0, 0, 0]
    # Số bênh nhân
    customers[0] = len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                       .filter(extract('day', Schedule.examination_date) == date).all())
    # Số bênh nhân đã khám
    customers[1] = len(CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
                       .filter(extract('day', Schedule.examination_date) == date, CustomerSche.examined == True).all())
    # Số bệnh nhân chưa khám
    customers[2] = (customers[0] - customers[1])
    return customers

def DanhSachBenhNhan(date):
    # return db.session.query(Customer.first_name, extract('year',Customer.birthday), extract('day', Schedule.examination_date))\
    #         .join(CustomerSche, CustomerSche.customer_id.__eq__(Customer.id)).join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
    #         .filter(extract('day', Schedule.examination_date) == date)\
    #         .group_by(Customer.first_name).all()
    return Customer.query.join(CustomerSche, CustomerSche.customer_id.__eq__(Customer.id)).join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
            .filter(extract('day', Schedule.examination_date) == date).add_columns(Schedule.examination_date).all()

def load_customers(name=None, phone=None, codeMedicalBill=None):
    kq = {}
    if name:
        for p in Customer.query.all():
            if p.first_name.strip().__eq__(name.strip()):
                kq = p
    if phone:
        for p in Customer.query.all():
            if p.phone_number.strip().__eq__(phone.strip()):
                kq = p
    if codeMedicalBill:
        for p in MedicalBill.query.all():
            if p.id.strip().__eq__(codeMedicalBill.strip()):
                kq = p
    return kq

def tim_khach_hang(sdt, **kwargs):
    return Customer.query.filter(Customer.phone_number.__eq__(sdt)).first()

def lich_su_kham(customer_id, medical_id=None):
    if medical_id:
        return MedicalBill.query.join(CustomerSche, MedicalBill.customer_sche.__eq__(CustomerSche.id)).\
        join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id)).add_columns(Schedule.examination_date)\
        .join(Customer, CustomerSche.customer_id.__eq__(Customer.id))\
        .filter(MedicalBill.id.__eq__(medical_id)).add_columns(Customer.first_name)\
        .add_columns(Customer.last_name).add_columns(extract('year', Customer.birthday)).all()
    else:
        return MedicalBill.query.join(CustomerSche, MedicalBill.customer_sche.__eq__(CustomerSche.id)).\
            join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id)).add_columns(Schedule.examination_date)\
            .join(Customer, CustomerSche.customer_id.__eq__(Customer.id))\
            .filter(CustomerSche.customer_id.__eq__(customer_id)).add_columns(Customer.first_name)\
            .add_columns(Customer.last_name).add_columns(extract('year', Customer.birthday)).group_by(MedicalBill.id)\
            .order_by(MedicalBill.id).all()

def get_medicine_by_name(name):
    return Medicine.query.filter(Medicine.name.__eq__(name)).first()

def add_medical_bill(cs, medicalinfo, medicinebilldetails):
    medicalbill = MedicalBill(user=current_user, symptom=medicalinfo['trieuchung'],
                              diagnostic_disease=medicalinfo['benhchuandoan'], customer_sche=cs.id)
    db.session.add(medicalbill)
    db.session.commit()
    for m in medicinebilldetails:
        m = MedicalBillDetail(medicalbill=medicalbill, medicine=m['id'], quantity=m['quantity'],
                              how_to_use=m['how_to_use'], unit_price=m['quantity']*(Medicine.query.get(m['id']).price))
        db.session.add(m)
    db.session.commit()
    return medicalbill

def get_customersche(customer_id, date):
    return CustomerSche.query.join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id))\
        .filter(Schedule.examination_date == date, CustomerSche.customer_id.__eq__(customer_id)).first()

