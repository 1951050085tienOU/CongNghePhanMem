from app import app, db
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from app.models import Medicine


class General(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/general.html')


class ManagerStatistic(BaseView):
    @expose('/')
    def __index__(self):
        return self.render('admin/manager_statistics.html')


class Management(BaseView):
    @expose('/')
    def __index__(self):
        return self.render('admin/management.html')


class ManagerRegulation(BaseView):
    @expose('/')
    def __index__(self):
        return self.render('admin/manager_regulation.html')


class AccountSet(BaseView):
    @expose('/')
    def __index__(self):
        return self.render('admin/account_set.html')


class View(ModelView):
    can_view_details = True


admin = Admin(app=app, template_mode='Bootstrap4', name='current_use',
              index_view=General(name="Tổng quan"))

admin.add_view(ManagerStatistic(name='Thống kê'))
admin.add_view(Management(name='Quản lý'))
admin.add_view(ManagerRegulation(name='Quy định'))
admin.add_view(AccountSet(name='Tài khoản'))
