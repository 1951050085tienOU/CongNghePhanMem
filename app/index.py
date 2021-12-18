from app import app, db, login, utils
from flask import render_template, url_for, request, redirect
from flask_login import login_user, logout_user


@app.route('/')
def index():
    return render_template('index.html')


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


@app.route('/employee-auth/signin/', methods=['get', 'post'])
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

    return render_template('admin/login.html', err_msg=err_msg)


@app.route('/employee-auth/logout')
def logout():
    logout_user()
    return redirect(url_for('signin'))


if __name__ == '__main__':
    pre_user = None
    from admin import *
    app.run(debug=True)