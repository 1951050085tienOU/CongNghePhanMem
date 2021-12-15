from app import app, db, login
from flask import redirect, request
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from app.models import UserRole
from flask_login import current_user, logout_user
import utils
from datetime import datetime

class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated

class AuthenticatedManagerView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and 'UserRole.MANAGER' in str(current_user.user_role)

class AuthenticatedDoctorView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and 'UserRole.DOCTOR' in str(current_user.user_role)

class AuthenticatedNurseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and 'UserRole.NURSE' in str(current_user.user_role)

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


class General(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/general.html')

class ManagerStatistic(AuthenticatedManagerView):
    @expose('/')
    def index(self):
        month = request.args.get('month', datetime.now().month)
        return self.render('admin/manager_statistics.html', revenue_stats=utils.revenue_stats(month=month))


class Management(AuthenticatedManagerView):
    @expose('/')
    def __index__(self):
        return self.render('admin/management.html')


class ManagerRegulation(AuthenticatedManagerView):
    @expose('/')
    def __index__(self):
        return self.render('admin/manager_regulation.html')


class AccountSet(AuthenticatedBaseView):
    @expose('/')
    def __index__(self):
        return self.render('admin/account_set.html')

class Logout(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class View(ModelView):
    can_view_details = True


admin = Admin(app=app, template_mode='Bootstrap4', name='PHÒNG KHÁM HỒNG HIỀN VI TIẾN',
              index_view=MyAdminIndex(name="Trang chủ"))

admin.add_view(General(name='Tổng quan'))
admin.add_view(ManagerStatistic(name='Thống kê'))
admin.add_view(Management(name='Quản lý'))
admin.add_view(ManagerRegulation(name='Quy định'))
admin.add_view(AccountSet(name='Tài khoản'))
admin.add_view(Logout(name='Đăng xuất'))
