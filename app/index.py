import cloudinary.uploader
import random

import requests
from flask import render_template
from app import app, db, login, client
from app.models import Regulation
from flask import render_template, url_for, request, redirect, jsonify
from flask_login import login_user, logout_user, current_user


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


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
            customer = utils.get_customer_by_phone(request.form['customerPhoneNumber'])
            if customer:
                login_user(user=customer)
                return render_template('index.html')
    return render_template('index.html', current_phone=request.form['customerPhoneNumber'], error_code="Mã xác thực không hợp lệ.")


@app.route("/api/otp-auth", methods=['POST'])
def otp_auth():
    if request.method.__eq__('POST'):
        otp_code = random.randrange(100000, 999999)
        if request.json:
            session.modified = True
            session['response'] = str(otp_code)
            print("======================== OTP la " + str(otp_code))
            phone_number = request.json['phoneNumber']
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
            '''message = utils.send_messages(phone_number, '[Phòng mạch Hồng Hiền Vy Tiến] Mã số xác thực của bạn là: ' + str(otp_code)
                                              + '. Xin vui lòng không chia sẻ mã số này cho ai khác kể cả nhân viên của phòng mạch.')'''
    return 'OK'


@app.route("/api/logout", methods=['get', 'post'])
def customer_logout():
    logout_user()
    utils.session_clear('response')
    return redirect(url_for('index'))

if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)
