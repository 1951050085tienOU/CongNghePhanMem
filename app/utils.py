import math
from datetime import datetime, timedelta
from app import app, db, CustomObject, client, keys
from sqlalchemy.sql import func
from sqlalchemy import orm
from sqlalchemy.orm import session, query
from sqlalchemy import func, extract
from app.models import *
from flask_login import current_user
from flask import session, request
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


def revenue_stats(month,doanhthu):
    p = db.session.query(extract('day', Receipt.created_date), func.count(Customer.id),
                         func.sum(Receipt.total_price), (func.sum(Receipt.total_price)/doanhthu)*100)\
                        .join(Customer, Receipt.customer_id.__eq__(Customer.id))\
                        .filter(extract('month', Receipt.created_date) == month)\
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


def get_user_information():
    return get_user_by_id(current_user.id)


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


def reformat_phone_number(phone_number):
    if phone_number[:1] == '84' and len(phone_number) == 11:
        return '+' + phone_number
    elif phone_number[0] == '0' and len(phone_number) == 10:
        return '+84' + phone_number[1:]
    else:
        return 0


def reformat_0_phone_number(phone_number):
    if phone_number[0] == '0' and len(phone_number) == 10:
        return phone_number
    elif phone_number[:1] == '84' and len(phone_number) == 11:
        return '0' + phone_number[2:]
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
    return Customer.query.filter(Customer.phone_number.__eq__(phone_number)).order_by(Customer.id.desc()).first()


def get_accepted_customer_by_phone(phone_number): ################################
    return db.session.query(Customer).filter(Customer.phone_number == phone_number, Customer.id == Receipt.customer_id,
                                             Receipt.medical_bill == MedicalBill.id).order_by(Customer.appointment_date.
                                                                                              desc()).first()


def get_customer_by_id(customer_id):
    return Customer.query.get(customer_id)


def get_id_of_date_exist_in_schedule(in_date):
    if in_date is datetime:
        in_date = in_date.date()
    dates = db.session.query(Schedule.id).filter(Schedule.examination_date == in_date).\
        order_by(Schedule.examination_date.desc()).first()
    if dates:
        returned_id = dates.id
    if not dates:
        new_schedule = Schedule(examination_date=datetime(in_date.year, in_date.month, in_date.day, 0))
        db.session.add(new_schedule)
        db.session.commit()
        returned_id = new_schedule.id

    return returned_id


def add_new_order(first_name, last_name, birthday, phone_number, gender_id, appointment_date, note, ordered_date):
    #new Schedule or not
    schedule_id = get_id_of_date_exist_in_schedule(ordered_date.date())

    #order in Customer
    customer = Customer(first_name=first_name, last_name=last_name, birthday=birthday, phone_number=phone_number,
                        gender_id=gender_id, appointment_date=appointment_date, note=note)
    db.session.add(customer)

    db.session.commit()

    #customer schedule
    customer_sche = CustomerSche(schedule_id=schedule_id, customer_id=customer.id, timer=time(ordered_date.hour,
                                                                                              ordered_date.minute,
                                                                                              ordered_date.second))
    db.session.add(customer_sche)
    db.session.commit()


def get_order_history(phone_number):
    return db.session.query(Customer).filter(Customer.phone_number == phone_number).all()


def get_bill_history(phone_number):
    return_value = []
    joined_order_customer = db.session.query(MedicalBill.id).filter(Customer.phone_number == phone_number, Customer.id
                                                                    == Receipt.customer_id, Receipt.medical_bill ==
                                                                    MedicalBill.id).all()
    if joined_order_customer:
        for obj in range(len(joined_order_customer)):
            return_value.append(joined_order_customer[obj][0])   #[bill_id_1, bill_id_2, bill_id_3]

    return return_value


def get_medical_bill_by_id(medical_bill_id):
    return MedicalBill.query.get(medical_bill_id)


def get_receipt_by_id(receipt_id):
    return Receipt.query.get(receipt_id)


def get_customer_phone_list():
    customers = db.session.query(Customer.phone_number).group_by(Customer.phone_number).all()
    list_cutted_phone_number = []
    for customer in customers:
        list_cutted_phone_number.append(str(customer)[-7:-3])
    return list_cutted_phone_number


def get_history_look_up(phone_number):
    orders_history = []
    orders = get_order_history(phone_number)
    for order in orders:
        new_obj = CustomObject.CustomObjectHistoryMedicalBill()
        new_obj.name = order.first_name + ' ' + order.last_name
        new_obj.ordered_date = order.appointment_date
        if order.receipts:
            new_obj.disease_diagnostic = get_medical_bill_by_id(order.receipts[0].medical_bill).diagnostic_disease
            new_obj.order_state = order.receipts
        new_obj.was_scheduled = order.was_scheduled

        orders_history.append(new_obj)

    return orders_history


def rounded_time(date_time): #10 minutes for each order time
    hour = date_time.hour
    minute = date_time.minute
    if minute < 55:
        math_minute = minute % 10
        if math_minute < 5:
            minute -= math_minute
        else:
            minute += 10 - math_minute
    else:
        return date_time + timedelta(hours=+1, minutes=-minute)

    return date_time.replace(hour=hour, minute=minute)


def get_sat_in_date(date):
    if date is datetime:
        date = date.date()
    return_value = []
    list_order = db.session.query(CustomerSche.timer).filter(CustomerSche.schedule_id == Schedule.id).\
        filter(extract('day', Schedule.examination_date) == date.day, extract('month', Schedule.examination_date) ==
               date.month, extract('year', Schedule.examination_date) == date.year).order_by(CustomerSche.timer)\
        .all()
    if list_order:
        for item in list_order:
            return_value.append(item[0])
    return return_value      #[time1, time2, time3,...] in the same date


def get_date_from_to(from_date, to_date):
    if from_date is datetime:
        from_date = from_date.date()
    if to_date is datetime:
        to_date = to_date.date()
    if from_date >= to_date:
        return from_date

    list_date = []
    while from_date != to_date:
        list_date.append(from_date)
        from_date = from_date + timedelta(days=+1)
    return list_date


def get_not_free_order_time():
    #js checked khung ngày giờ còn trống trong khoảng 1.5 ngày tính từ (now + 1/24) ngày, không đăng ký vào break time
    #min (+ 1.5) ||||||| max (36 -) (hours)
    #check in 37 hours for time loss reservation
    current_date_time_seconds = datetime.now().timestamp()
    from_date_time = datetime.fromtimestamp(current_date_time_seconds + 1.5 * 60 ** 2)          #current + 1.5 hours
    to_date_time = datetime.fromtimestamp(current_date_time_seconds + 37 * 60 ** 2)             #current + 37 hours

    #date need to check
    from_date = from_date_time.date()
    to_date = to_date_time.date()
    list_date_need_to_check = get_date_from_to(from_date, to_date)

    #list free oder time (order sat)
    list_free_order_time = {}
    for date_check in list_date_need_to_check:

        list_date_not_free = get_sat_in_date(date_check.date())

        list_not_free = []

        count = 0
        list_length = len(list_date_not_free)
        while count in range(count, list_length):
            count_j = count + 1
            new_obj = CustomObject.CustomObjectTimeFree()
            new_obj.hour = list_date_not_free[count].hour
            new_obj.minute.append(list_date_not_free[count].minute)
            while count_j in range(count_j, list_length):
                if new_obj.hour == list_date_not_free[count_j].hour:
                    new_obj.minute.append(list_date_not_free[count_j].minute)
                    count_j += 1
                else:
                    if count_j - count > 1:
                        count = count_j - 2
                    break
            list_not_free.append(new_obj)
            count += 1

        list_free_order_time[date_check.strftime("%Y-%m-%d")] = list_not_free

    return list_free_order_time      #{key_date : [<obj1>,<obj2>,<obj3>,<obj4>,...]}   <obj1> = {hour=x, minute=[]}


def check_exist_order_at_date_time(date_time):
    list_orders = get_sat_in_date(date_time.date())
    for order in list_orders:
        if date_time.hour == order.hour and date_time.minute == order.minute:
            return True     #exist

    return False   #not exist


def check_customer_exist_on_date(date_time, phone_number):
    if date_time is datetime:
        date_time = date_time.date()
    check_exist = db.session.query(CustomerSche.timer).filter(Customer.phone_number == phone_number, CustomerSche.
                                                              customer_id == Customer.id, Schedule.id == CustomerSche.
                                                              schedule_id, Schedule.examination_date == date_time)\
        .first()

    if check_exist:
        return True   #exist
    return False      #not_exist


def session_clear(key):
     if key in session:
         del session[key]
