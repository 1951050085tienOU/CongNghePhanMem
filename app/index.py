from app import app, db, login
from app.models import Regulation, MedicalBillDetail, Person
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

def add_new_medicalBill():
    customer_names = request.form.get('new_customer_name')
    phoneNumbers = request.form.get('new_phoneNumber')
    ages = request.form.get('new_age')
    genders = request.form.get('new_gender')
    maPhieuKhams = request.form.get('new_maPhieuKham')
    symptoms = request.form.get('new_symptom')
    diagnostic_diseases = request.form.get('new_diagnostic_disease')
    how_to_uses = request.form.get('new_how_to_use')
    medicine_names = request.form.get('new_medicine_name')

    all_med = db.session.query(MedicalBill).all()
    for med in all_med:
        med.id = med.id + 1
        db.session.add(med)
    news = MedicalBill(id=1, symptom=symptoms, diagnostic_disease=diagnostic_diseases)
    db.session.add(news)
    db.session.commit()

    all_med = db.session.query(Medicine).all()
    for med in all_med:
        med.id = med.id + 1
        db.session.add(med)
    news = Medicine(id=1, name=medicine_names)
    db.session.add(news)
    db.session.commit()

    all_med = db.session.query(MedicalBillDetail).all()
    for med in all_med:
        med.id = med.id + 1
        db.session.add(med)
    news = MedicalBillDetail(how_to_use=how_to_uses)
    db.session.add(news)
    db.session.commit()

    all_med = db.session.query(Person).all()
    for med in all_med:
        med.id = med.id + 1
        db.session.add(med)
    news = Person(first_name=customer_names)
    db.session.add(news)
    db.session.commit()

if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)