import datetime
from datetime import datetime, timedelta
from app import app, utils
from flask_admin import Admin, AdminIndexView, expose, BaseView
from app.models import Medicine
from flask_login import current_user
from app.models import UserRole


class ModelAuthenticated(BaseView):
    user_type = 'NONE'

    def is_accessible(self):
        ModelAuthenticated.user_type = None
        if current_user.is_authenticated:
            pass
        else:
            return False
        for role in list(dict(list(UserRole.__members__.items()))):
            if current_user.user_role == (UserRole[str(role)]):
                ModelAuthenticated.user_type = role
                return True
        return False


class General(AdminIndexView, ModelAuthenticated):
    @expose('/')
    def index(self):
        #thống kê doanh thu tổng quát
        revenue_statistics = [] #danh sách chứa dữ liệu thống kê
        pre_months = utils.create_list_of_months(datetime.now().month) #danh sách tháng
        for mm in pre_months:
            revenue_statistics.append(utils.all_revenue_stats(mm, datetime.now().year))

        #thống kê lượt khách hẹn
            reg = utils.get_regulation() #lấy quy định
            max_customer = reg[0]
            medical_fee = reg[1]
            ordered_today = utils.get_amount_orders_in_date(datetime.today()) #khách hẹn ngày hôm nay
            ordered_tomorrow = utils.get_amount_orders_in_date(
                                    datetime.today() + timedelta(days=1))    # khách hẹn ngày hôm qua
        #thống kê thuốc trong kho
            percent_record = utils.medine_stock_percent_over_5()
            medicine_name = []
            medicine_percent = []
            for count in range(0, len(percent_record), 2):
                if percent_record[count] != 'OTHER':
                    medicine_name.append(utils.get_medicine_by_id(percent_record[count]))
                else:
                    medicine_name.append('Others')
                medicine_percent.append(percent_record[count + 1])
        return self.render('admin/general.html', revenue_statistics=revenue_statistics, list_of_months=pre_months,
                           medicine_statistics_name=medicine_name, medicine_statistics_percent=medicine_percent,
                           max_customer=max_customer, medical_fee=medical_fee, ordered_today=ordered_today,
                           ordered_tomorrow=ordered_tomorrow)


class ManagerStatistics(ModelAuthenticated):
    @expose('/')
    def __index__(self):
        #thống kê doanh thu tổng quát
        revenue_statistics = [] #danh sách chứa dữ liệu thống kê
        pre_months = utils.create_list_of_months(datetime.now().month) #danh sách tháng
        for mm in pre_months:
            revenue_statistics.append(utils.all_revenue_stats(mm, datetime.now().year))

        return self.render('admin/manager_statistics.html', revenue_statistics=revenue_statistics, list_of_months=pre_months)


class ManagementMedicine(ModelAuthenticated):
    can_view_details = True
    can_delete = False
    column_searchable_list = (Medicine.id, Medicine.name)
    column_labels = {
        'id': 'Mã',
        'name': 'Tên',
        'quantity': 'Số lượng',
        'unit': 'Đơn vị tính',
        'price': 'Đơn giá',
        'out_of_date': 'Ngày hết hạn',
        'producer': 'Nhà cung cấp',
        'medicinetype': 'Loại thuốc'
    }


class Management(ModelAuthenticated):

    @expose('/')
    def __index__(self):
        return self.render('admin/management.html')


class ManagerRegulation(ModelAuthenticated):
    @expose('/')
    def __index__(self):
        return self.render('admin/manager_regulation.html')


class AccountSet(ModelAuthenticated):
    @expose('/')
    def __index__(self):
        return self.render('admin/account_set.html')

admin = Admin(app=app, template_mode='Bootstrap4', name='PHÒNG MẠCH',
              index_view=General(name="Tổng quan"))

admin.add_view(ManagerStatistics(name='Thống kê'))
admin.add_view(Management(name='Quản lý'))
admin.add_view(ManagerRegulation(name='Quy định'))
admin.add_view(AccountSet(name='Tài khoản'))


'''nonesj = Admin(app=app, template_mode='Bootstrap4', name='haj',
              index_view=General(name="Tổng quan"))
ModelAuthenticated.is_accessible(self=ModelAuthenticated)'''
