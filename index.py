from app import app, db, login
from app.models import Regulation, UserRole
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
@app.route("/add-new-appoinment", methods=['get', 'post'])
def new_orderCus():
    if current_user.is_authenticated:
        if request.method.__eq__('POST'):
            first_name = request.form.get('customer-fname')
            last_name = request.form.get('customer-lname')
            birthday = request.form.get('customer-birth')
            gender_id = request.form.get('customer-gender')
            phone_number = request.form.get('customer-phone')
            appointment_date = request.form.get('alert-for-order-date')
            #New data
            note = str(request.form.get('customer-note'))
            schedules = request.form.get('order-date')
            if not utils.check_customer_exist_on_date(schedules, phone_number):
                if not utils.check_exist_order_at_date_time(schedules):
                    #commit to database
                    utils.add_new_Customer(first_name, last_name, birthday, phone_number, gender_id, appointment_date, note
                                        , schedules)
                    return render_template('/nurse_appoinment,html', notification_code='submitSuccess')
                else:
                    return render_template('/nurse_appoinment,html', notification_code='ExistOne')
            else:
                return render_template('/nurse_appoinment,html', notification_code='justOneADay')
    return render_template('admin/login.html')

@app.route("/new_order", methods=['post'])
def new_order():
    if request.method.__eq__('POST'):
        if current_user.is_authenticated:
            return render_template('admin/form_appoinment.html')


if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)