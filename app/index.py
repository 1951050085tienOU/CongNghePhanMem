import cloudinary.uploader
from flask import render_template
from app import app, db, login
from app.models import Regulation
from flask import render_template, url_for, request, redirect, session, jsonify
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


if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)