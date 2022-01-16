import datetime
from datetime import date
import hashlib
from datetime import datetime, timedelta
from app import app, utils, db
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import  MenuLink
from app.models import Medicine, Regulation, MedicineType
from flask_login import current_user
from app.models import UserRole, Gender
from flask import request, session, url_for, redirect
from flask_login import logout_user
from sqlalchemy.sql import extract
from app.models import *


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


class ManagerView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and str(current_user.user_role).__eq__('UserRole.MANAGER')


class DoctorView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and str(current_user.user_role).__eq__('UserRole.DOCTOR')


class NurseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and str(current_user.user_role).__eq__('UserRole.NURSE')


class General(AdminIndexView, ModelAuthenticated):
    @expose('/')
    def index(self):
        userrole = utils.KiemTraRole(current_user)
        us = utils.get_user_information()
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


        #Tra cứu bác sĩ & y tá
        now = datetime.now()
        search_customer = utils.load_customers(request.args.get('customer_name'), request.args.get('phoneNumber'),
                                               request.args.get('address_id'))
        #Y tá
        cus = utils.load_sche()
        list_was_examination = utils.ThongKeLichHen(now)

        #khách tiếp theo
        #danh sách khám trong ngày
        next_order_customer = ''
        next_order_number = 0
        orders_list = utils.get_orders_list_in_date(datetime.now().date())
        the_next_order = utils.get_info_next_customer_in_orders()
        if the_next_order:
            next_order_customer = utils.get_customer_by_id(customer_id=the_next_order.customer_id)

            for order in orders_list:
                next_order_number += 1
                if order[0] == the_next_order.customer_id:
                    break

        if next_order_number == len(orders_list) + 1:
            next_order_number = ''

        """Tổng quan của bác sĩ"""
        now = date.today()
        utils.update_customersche(MedicalBill.query.all()[-1].id)
        # Bệnh nhân hiện tại
        customer_now = utils.BenhNhanHienTai(now)

        # Lịch hẹn ngày
        customers_today = utils.LichHenNgay(now)

        # Thống Kê bệnh nhân
        patient_stats = utils.ThongKeBenhNhan(now)

        # Danh sách Bệnh nhân
        patient_list = utils.DanhSachBenhNhan(now)
        # Tra cứu
        # search_customer = utils.load_customers(request.args.get('customer_name'), request.args.get('phoneNumber'))
        if request.args.__eq__('GET'):
            customer = utils.tim_khach_hang(sdt=request.args.get('phoneNumber'))

        customer = customer_now
        if customer:
            search_customer = utils.lich_su_kham(customer.id)
        else:
            search_customer = None
            # search_customer = MedicalBill.query.join(CustomerSche, MedicalBill.customer_sche.__eq__(CustomerSche.id))\
            #     .join(Schedule, CustomerSche.schedule_id.__eq__(Schedule.id)).join(Customer, CustomerSche.customer_id.__eq__(Customer.id))\
            #     .add_column(Schedule.examination_date).add_columns(Customer.first_name)\
            #     .add_columns(Customer.last_name).add_columns(extract('year', Customer.birthday)).group_by(MedicalBill.id)\
            #     .order_by(MedicalBill.id).all()

        return self.render('admin/general.html', revenue_statistics=revenue_statistics, list_of_months=pre_months,
                           medicine_statistics_name=medicine_name, medicine_statistics_percent=medicine_percent,
                           max_customer=max_customer, medical_fee=medical_fee, ordered_today=ordered_today,
                           ordered_tomorrow=ordered_tomorrow, us=us, current_user=current_user,
                           search_customer=search_customer, list_was_examination=list_was_examination, now=now, cus=cus,
                           next_order_time=the_next_order, next_order_info=next_order_customer,
                           next_order_number=next_order_number, userrole=userrole, customer_now=customer_now,
                           customers_today=customers_today, patient_stats=patient_stats, patient_list=patient_list)


class ManagerStatistics(ManagerView):
    @expose('/')
    def __index__(self):
        now = datetime.now()
        month = request.args.get('month', datetime.now().month)
        year = request.args.get('year', now.year)
        doanhthu = request.args.get('doanhthu', 5000000)
        types = [{
            'value': 'line',
            'text': 'Đường'
        }, {
            'value': 'bar',
            'text': 'Cột'
        }, {
            'value': 'pie',
            'text': 'Tròn'
        }]
        type = request.args.get('chart')

        thong_ke_doanh_thu = utils.revenue_stats(month=month, doanhthu=doanhthu)
        utils.pdf_month_revenue(year=now.year, month=month, data_list=thong_ke_doanh_thu)
        #utils.pdf_create_medicine_usage(year, month,)     //tao file pdf

        return self.render('admin/manager_statistics.html',
                           revenue_stats=utils.revenue_stats(month=month, year=year, doanhthu=doanhthu),
                           examination_stats=utils.examination_stats(month=month, year=year),
                           medicine_stats=utils.medicine_stats(month=month, year=year), thuoc_bo_sung=utils.thuoc_bo_sung(),
                           thuoc_het_sl=utils.thuoc_het_sl(), thuoc_ton_kho=utils.thuoc_ton_kho(),
                           thuoc_da_dung=utils.thuoc_da_dung(), types=types, type=type, now=now,
                           month=month, year=year)


class ManageMedicine(ModelView):
    can_view_details = True
    can_edit = True
    can_create = True
    can_delete = True
    column_labels = {
        'name': 'Tên',
        'quantity': 'Số lượng',
        'unit': 'Đơn vị tính',
        'price': 'Đơn giá',
        'out_of_date': 'Ngày hết hạn',
        'producer': 'Nhà cung cấp',
        'medicinetype': 'Loại thuốc',
        'type_name': 'Loại thuốc'
    }

    def is_accessible(self):
        if current_user.user_role.name == 'DOCTOR':
            return False
        return True

    def is_visible(self):
        if current_user.user_role.name == 'DOCTOR':
            return False
        return True


class ManageMedicine(ModelView):
    can_view_details = True
    can_edit = True
    can_create = True
    can_delete = True
    column_labels = {
        'name': 'Tên',
        'quantity': 'Số lượng',
        'unit': 'Đơn vị tính',
        'price': 'Đơn giá',
        'out_of_date': 'Ngày hết hạn',
        'producer': 'Nhà cung cấp',
        'medicinetype': 'Loại thuốc',
        'type_name': 'Tên đơn vị'
    }

    def is_accessible(self):
        if current_user.user_role.name == 'MANAGER':
            return True
        return False

    def is_visible(self):
        if current_user.user_role.name == 'MANAGER':
            return True
        return False


class MedicineManage(ManageMedicine):
    column_searchable_list = ['id', 'name']


class MedicineTypeManage(ManageMedicine):
    column_searchable_list = ['id', 'type_name']


class Management(ManagerView):

    @expose('/')
    def __index__(self):
        return self.render('admin/management.html')


class ManagerRegulation(ManagerView):
    @expose('/')
    def __index__(self):
        reg = utils.get_regulation()  # lấy quy định
        max_customer = int(reg[0])
        medical_fee = int(reg[1])

        if request.args:
            max_customer_new = request.args.get('new_max_customer', max_customer, type=int)
            medical_fee_new = request.args.get('new_fee', medical_fee, type=int)
            if medical_fee == int(medical_fee_new) and max_customer == int(max_customer_new):
                pass
            else:
                medical_fee = medical_fee_new
                max_customer = max_customer_new
                new = Regulation(examination_price=medical_fee_new, customer_quantity=max_customer_new)
                db.session.add(new)
                db.session.commit()
        return self.render('admin/manager_regulation.html', max_customer=max_customer, medical_fee=medical_fee)


class AccountSet(ModelAuthenticated):
    @expose('/')
    def __index__(self):
        mode = request.args.get('password_model_change', 0, type=int)
        user = utils.get_user_information()

        if mode == 0:    #thông thường
            if request.data:
                data = request.form
                utils.edit_user_information(user.id, request.form.get('first_name'), request.form.get('last_name'),
                                            request.form.get('birthday'), request.form.get('phone'))

            user_role_vi = {
                'MANAGER': 'Quản lý',
                'NURSE': 'Y tá',
                'DOCTOR': 'Bác sĩ',
                'OTHER': 'Nhân viên'
            }
            user_gender = {
                'NAM': 1,
                'NU': 2,
                'KHAC': 3
            }
            user_id = user.id
            user_role = user.user_role.name
            user_first_name = user.first_name
            user_last_name = user.last_name
            user_phone = user.phone_number
            user_birthday = user.birthday.date()
            user_gender_id = user_gender[user.gender_id.name]
            if user.avatar:
                user_avatar = user.avatar
            else:
                user_avatar = url_for('static', filename='avatar/default.jpg')

            return self.render('admin/account_set.html', user_id=user_id, user_role=user_role_vi[user_role],
                               user_first_name=user_first_name, user_last_name=user_last_name, user_phone=user_phone,
                               user_birthday=user_birthday, user_avatar=user_avatar, user_birth=user.birthday,
                               user_gender=str(user_gender_id))
        elif mode == 1:     #mode thay đổi mật khẩu)
            return self.render('admin/change_password.html', current_password=user.password)
        else:
            return self.render('temp.html')


class LogOutUser(BaseView):
    @expose('/')
    def logout(self):
        logout_user()

        return redirect('/admin/sign-in')


class CreateMedicalBill(DoctorView):
    @expose('/')
    def __index__(self):
        maphieu = MedicalBill.query.all()[-1].id
        symptom_available = MedicalBill.query.all()
        medical_name = Medicine.query.all()

        return self.render('admin/doctor_medicalBill.html',  symptom_available=symptom_available,
                           medical_name=medical_name, maphieumoi=maphieu+1)


class SeeMedicalRecord(DoctorView):
    @expose('/')
    def __index__(self):
        # Tra cứu
        now = datetime.now()
        customer = utils.tim_khach_hang(request.args.get('phone_number'))
        medical_id = request.args.get('medical-id', None)

        if customer:
            # search_customers = utils.load_customers(request.args.get('customer_name'), request.args.get('maPhieuKham'), request.args.get('phoneNumber'))
            search_customers = utils.lich_su_kham(customer_id=customer.id, medical_id=medical_id)
        else:
            search_customers = None

        return self.render('admin/doctor_medicalRecord.html', search_customers=search_customers, now=now)


class appoinments(NurseView):
    @expose('/')
    def __index__(self):
        now = datetime.now()
        cus = utils.load_sche()
        list_wasnt_sche = utils.list_cus_wasnt_axam(now)

        return self.render('admin/nurse_appoinments.html', cus=cus, now=now, list_wasnt_sche=list_wasnt_sche)


class payment(NurseView):
    @expose('/')
    def __index__(self):
        rq = request.args.get('receipt-history', 0)
        if not rq:
            #danh sach cho thanh toan
            orders_list_need_to_checkout = utils.get_orders_need_to_checkout()     #[(cus_id, medical_id),...]
            checkout_orders = []
            count = -1
            for order in orders_list_need_to_checkout:
                count += 1
                customer = utils.get_customer_by_id(order[0])
                checkout_orders.append([])
                checkout_orders[count].append(order[1])  #medical_id
                checkout_orders[count].append(customer.first_name + ' ' + customer.last_name)         #customer_name
                checkout_orders[count].append(customer.birthday.year)
                checkout_orders[count].append(utils.format_currency_vi(utils.get_total_price_in_receipt(order[1])))

            return self.render('admin/payment.html', checkout_orders=checkout_orders, order_checkout_num=count+1)
        else:

            return self.render('admin/receipt_history.html')


admin = Admin(app=app, template_mode='Bootstrap4', name='PHÒNG MẠCH',
              index_view=General(name="Tổng quan"))

admin.add_view(ManagerStatistics(name='Thống kê'))

#nurse view
admin.add_view(appoinments(name='Đặt hẹn'))
admin.add_view(payment(name='Thanh toán'))

#Doctor View
admin.add_view(CreateMedicalBill(name='Lập phiếu'))
admin.add_view(SeeMedicalRecord(name='Xem phiếu khám'))

#medicine quản lý
admin.add_view(MedicineManage(Medicine, db.session, category="Quản lý", name='Kho thuốc'))
admin.add_view(MedicineTypeManage(MedicineType, db.session, category="Quản lý", name='Kho đơn vị'))
admin.add_sub_category(parent_name="Quản lý", name="ManageMedicine")
admin.add_sub_category(name="Links", parent_name="Team")
admin.add_view(ManagerRegulation(name='Quy định'))
admin.add_view(AccountSet(name='Tài khoản'))
admin.add_view(LogOutUser(name='Đăng xuất'))

'''nonesj = Admin(app=app, template_mode='Bootstrap4', name='haj',
              index_view=General(name="Tổng quan"))
ModelAuthenticated.is_accessible(self=ModelAuthenticated)'''
