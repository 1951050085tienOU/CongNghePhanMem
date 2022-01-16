import cloudinary.uploader
import random

import flask

from app import CustomObject
from app import app, db, login#, client
from flask import render_template, url_for, request, redirect, jsonify
from flask_login import login_user, logout_user, current_user, login_required


@app.route('/')
def index():
    notification_code = request.args.get('notification_code')
    if not notification_code:
        notification_code = ''
    if current_user.is_authenticated:
        orders_history = utils.get_history_look_up(current_user.phone_number)
        return render_template('index.html', current_user=current_user, orders_history=orders_history,
                               notif=notification_code)
    else:
        customers_list = utils.get_customer_phone_list()
        return render_template('index.html', customers_list=customers_list, notif=notification_code)


@login.user_loader
def user_load(user_id):
    user = utils.get_user_by_id(user_id=user_id)
    if user.user_role:
        return user
    else:
        return utils.get_customer_by_id(customer_id=user_id)


@app.route('/admin/sign-in', methods=['get', 'post'])
def signin():
    if current_user.is_authenticated:
        return redirect('/admin')
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_password(username=username, password=password)
        if user:
            login_user(user=user)
            return redirect('/admin')
        else:
            err_msg = 'Tài khoản hoặc mật khẩu sai.'

    return render_template('admin/login.html', err_msg=err_msg, cur=current_user)


def add_new_regulation():
    max_customer = request.form.get('new_max_customer')
    medical_fee = request.form.get('new_fee')

    all_reg = db.session.query(Regulation).all()
    for reg in all_reg:
        reg.id = reg.id + 1
        db.session.add(reg)
    new = Regulation(id=1, examination_price=medical_fee, customer_quantity=max_customer)
    db.session.add(new)
    db.session.commit()

    return


@app.route("/admin/submit-change", methods=['get', 'post'])
def submit_change():
    if current_user.is_authenticated:
        if request.method.__eq__('POST'):
            id_access = utils.get_user_information().id
            user = utils.get_user_by_id(id_access)
            avatar = request.files.get('avatar')

            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
                user.avatar = avatar_path
                db.session.add(user)
                db.session.commit()
                return redirect("/admin/accountset")

            if request.form:
                user.first_name = request.form['first_name']
                user.last_name = request.form['last_name']
                user.birthday = request.form['birthday']
                user.phone_number = request.form['phone']
                user.gender_id = list(Gender)[int(request.form['gender']) - 1]

                db.session.add(user)
                db.session.commit()

        return redirect("/admin/accountset")


@app.route("/admin/submit-change-pass", methods=['get', 'post'])
def change_pass():
    if current_user.is_authenticated:
        if request.method.__eq__('POST'):
            user = utils.get_user_information()
            us = request.form.get('username')
            if us.__eq__(user.username):
                mode = 0
                user.password = str(hashlib.md5(request.form.get('new-pass').encode('utf-8')).hexdigest())
                db.session.add(user)
                db.session.commit()
    return redirect(url_for('accountset.__index__'))


@app.route('/api/login', methods=['POST'])
def customer_login():
    if request.method.__eq__('POST'):
        otp_code = session.pop('response', None)
        otp = str(request.form.get('otp_code'))
        if otp == otp_code:
            #get customer
            customer = utils.get_accepted_customer_by_phone(request.form['customerPhoneNumber'])
            if customer:
                login_user(user=customer)
                return redirect(url_for('index'))
            else:
                return redirect(url_for('index', notification_code='noSuccessReceipt'))
    return render_template('index.html', current_phone=request.form['customerPhoneNumber'], error_code="Mã xác thực không hợp lệ.")


@app.route("/api/otp-auth", methods=['POST'])
def otp_auth():
    if request.method.__eq__('POST'):
        otp_code = random.randrange(100000, 999999)
        if request.json:
            phone_number = request.json['phoneNumber']
            session.modified = True
            session['response'] = str(otp_code)
            print("======================== OTP la " + str(otp_code))
            ###########Enable this line to send OTP for customer validation########################
            '''message = utils.send_messages(phone_number, '[Phòng mạch Hồng Hiền Vy Tiến] Mã số xác thực của bạn là: ' + str(otp_code)
                                              + '. Xin vui lòng không chia sẻ mã số này cho ai khác kể cả nhân viên của phòng mạch.')'''
    return 'OK'


@app.route("/api/otp-auth-again", methods=['POST'])
def otp_auth_again():
    if request.method.__eq__('POST'):
        otp_code = random.randrange(100000, 999999)
        if request.json:
            utils.session_clear('response')
            session.modified = True
            session['response'] = str(otp_code)
            print("======================== AGAIN OTP la " + str(otp_code))
            phone_number = request.json['phoneNumber']
            ###########Enable this line to send OTP for again customer validation########################
            '''message = utils.send_messages(phone_number, '[Phòng mạch Hồng Hiền Vy Tiến] Mã số xác thực của bạn là: ' + str(otp_code)
                                              + '. Xin vui lòng không chia sẻ mã số này cho ai khác kể cả nhân viên của phòng mạch.')'''
    return 'OK'


@app.route("/api/logout", methods=['get', 'post'])
def customer_logout():
    logout_user()
    if session:
        utils.session_clear('response')
    return redirect(url_for('index'))


@app.route("/api/add-new-order", methods=['get', 'post'])
@login_required
def new_order_from_client():
    if current_user.is_authenticated:
        if request.method.__eq__('POST'):
            first_name = current_user.first_name
            last_name = current_user.last_name
            birthday = current_user.birthday
            gender_id = current_user.gender_id
            phone_number = current_user.phone_number
            appointment_date = datetime.now()
            #New data
            note = str(request.form.get('customer-note'))
            schedules = utils.rounded_time(datetime.strptime(request.form.get('order-date'), '%Y-%m-%dT%H:%M'))
            print(phone_number)
            print(schedules)
            if not utils.check_customer_exist_on_date(schedules.date(), phone_number):
                if not utils.check_exist_order_at_date_time(schedules):
                    #commit to database
                    utils.add_new_order(first_name, last_name, birthday, phone_number, gender_id, appointment_date, note
                                        , schedules)
                    return redirect(url_for('index', notification_code='submitSuccess'))
                else:
                    return redirect(url_for('index', notification_code='ExistOne'))
            else:
                return redirect(url_for('index', notification_code='justOneADay'))
    return redirect(url_for('index', notification_code='none'))


########## NURSE #################
#tạo lịch hẹn mới trên trang y tá
@app.route("/add-new-appoinment", methods=['get', 'post'])
def new_orderCus():
    if current_user.is_authenticated:
        if request.method.__eq__('POST'):
            first_name = request.form.get('customer-fname')
            last_name = request.form.get('customer-lname')
            birthday = request.form.get('customer-birth')
            gender_id = request.form.get('customer-gender')
            phone_number = request.form.get('customer-phone')
            appointment_date = request.form.get('order-date')
            note = str(request.form.get('customer-note'))
            schedules = utils.rounded_time(datetime.strptime(request.form.get('order-date'), '%Y-%m-%dT%H:%M'))
            if not utils.check_customer_exist_on_date(schedules, phone_number):
                if not utils.check_exist_order_at_date_time(schedules):
                    # commit to database
                    utils. add_new_appoinment(first_name, last_name, birthday, phone_number, gender_id, appointment_date,
                                              note, schedules)
                    return redirect(url_for('new_order', notification_code='submitSuccess'))
                else:
                    return redirect(url_for('new_order', notification_code='ExistOne'))
            else:
                return redirect(url_for('new_order', notification_code='justOneADay'))
        return redirect(url_for('index', notification_code='RequestLogin'))


@app.route("/new_order", methods=['get, post'])
def new_order():
    return render_template('admin/nurse_appoinments.html')


@app.route('/api/payment', methods=['get', 'post'])
def pay():
    if current_user.is_authenticated:
        if request.method.__eq__("POST"):
            medical_id = request.form['medical-bill-id']
            if medical_id:
                customer_id = utils.get_customer_sche_information(
                    utils.get_medical_bill_by_id(medical_id).customer_sche).customer_id
                regulation = utils.get_last_reg()

                utils.add_new_receipt(regulation_id=regulation, medical_bill_id=medical_id,
                                      customer_id=customer_id)
                utils.pdf_create_receipt(medical_bill_id=medical_id)
                return redirect('/admin/payment' + "?statusPayment=submitSuccess")
    return redirect('/admin/payment' + "?statusPayment=falseCheckout")



@app.route('/api/check-receipt', methods=['get', 'post'])
def check_receipt_history():
    if current_user.is_authenticated:
        if request.method.__eq__("POST"):
            phone_check = request.form['phone-check']
            list_re = utils.get_receipt_history(phone_check)
            if list_re:
                return render_template('/admin/receipt_history.html', phone_check=phone_check, list_re=list_re)
    return render_template('/admin/receipt_history.html')


if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)
