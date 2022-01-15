from app import db, app
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum, ForeignKey, Time, Date
from sqlalchemy.orm import relationship, backref
from datetime import datetime, time, date
from enum import Enum as ENUM
from sqlalchemy.ext.declarative import declared_attr
from flask_login import UserMixin

class Gender(ENUM):
    NAM = 1
    NU = 2
    KHAC = 3

class Province(db.Model):
    __tablename__ = 'province'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    districts = relationship('District', backref='province', lazy=True)

    def __str__(self):
        return self.name


class District(db.Model):
    __tablename__ = 'district'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    wards = relationship('Ward', backref='district', lazy=True)
    province_id = Column(Integer, ForeignKey(Province.id), nullable=False)

    def __str__(self):
        return self.name + ', ' + str(Province.query.get(self.province_id))


class Ward(db.Model):
    __tablename__ = 'ward'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    addresss = relationship('Address', backref='ward', lazy=True)
    district_id = Column(Integer, ForeignKey(District.id), nullable=False)

    def __str__(self):
        return self.name + ', ' + str(District.query.get(self.district_id))


class Address(db.Model):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    info = Column(String(50))
    ward_id = Column(Integer, ForeignKey(Ward.id), nullable=False)

    def __str__(self):
        return self.info + ', ' + str(Ward.query.get(self.ward_id))

class Person(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(10), nullable=False)
    last_name = Column(String(50))
    birthday = Column(DateTime, nullable=False)
    phone_number = Column(String(20), nullable=False)
    gender_id = Column(Enum(Gender))
    @declared_attr
    def address_id(self):
        return Column(Integer, ForeignKey(Address.id))


class UserRole(ENUM):
    MANAGER = 1
    DOCTOR = 2
    NURSE = 3


class User(Person, UserMixin):
    __tablename__ = 'user'
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    join_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)
    user_role = Column(Enum(UserRole), nullable=False)
    medical_bills = relationship('MedicalBill', backref='user', lazy=True)
    receipts = relationship('Receipt', backref='user', lazy=True)


class Customer(Person):
    __tablename__ = 'customer'
    appointment_date = Column(DateTime, nullable=False) #ngày hẹn
    note = Column(String(100))
    was_scheduled = Column(Boolean, default=False)  #sau khi được xác nhận lịch hẹn -> True
    schedules = relationship('CustomerSche', backref='customers', lazy=True)
    receipts = relationship('Receipt', backref='customer', lazy='subquery')

class CustomerSche(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False, primary_key=True)
    examined = Column(Boolean, default=False)
    timer = Column(Time, nullable=False)
    medical_bill = relationship('MedicalBill', backref='customersche', lazy=True, uselist=False)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    examination_date = Column(Date, nullable=False)  #ngày khám đã xác nhận
    customers = relationship('CustomerSche', backref='schedules', lazy=True)


class MedicalBill(db.Model):
    __tablename__ = 'medical_bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symptom = Column(String(100))   #triệu chứng
    diagnostic_disease = Column(String(100))    #bệnh chuẩn đoán
    customer_sche = Column(Integer, ForeignKey(CustomerSche.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('MedicalBillDetail', backref='medicalbill', lazy=True)
    receipt = relationship('Receipt', backref='medicalbill', uselist=False, lazy=True)


class Producer(db.Model):
    __tablename__ = 'producer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    medicines = relationship('Medicine', backref='producer', lazy=True)

    def __str__(self):
        return self.name


class MedicineType(db.Model):
    __tablename__ = 'medicine_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50))
    medicines = relationship('Medicine', backref='medicinetype', lazy=True)

    def __str__(self):
        return self.type_name


class Medicine(db.Model):
    __tablename__ = 'medicine'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    quantity = Column(Integer, default=0)
    unit = Column(String(20))
    price = Column(Float, default=0)
    out_of_date = Column(DateTime)
    producer_id = Column(Integer, ForeignKey('producer.id'))
    medicine_type = Column(Integer, ForeignKey('medicine_type.id'))
    medical_bill_details = relationship('MedicalBillDetail', backref='medicines', lazy=True)
    def __str__(self):
        return self.name


class MedicalBillDetail(db.Model):
    medical_bill = Column(Integer, ForeignKey('medical_bill.id'), nullable=False, primary_key=True)
    medicine = Column(Integer, ForeignKey('medicine.id'), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    how_to_use = Column(String(100))
    unit_price = Column(Float, default=0)


class Receipt(db.Model):
    __tablename__ = 'receipt'
    id = Column(Integer, primary_key=True, autoincrement=True)
    total_price = Column(Float, default=0)
    created_date = Column(DateTime, default=datetime.now())
    regulation = Column(Integer, ForeignKey('regulation.id')) #quy định
    medical_bill = Column(Integer, ForeignKey('medical_bill.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

class Regulation(db.Model):
    __tablename__ = 'regulation'
    id = Column(Integer, primary_key=True)
    examination_price = Column(Float, default=150000)
    customer_quantity = Column(Integer, default=30)
    receipts = relationship('Receipt', backref='regulations', lazy=True)


if __name__ == "__main__":
    # #Add adrress
    # p1 = Province(name='Hồ Chí Minh')
    # db.session.add(p1)
    #
    # d1 = District(name='Quận 1', province_id=1)
    # d2 = District(name='Quận 2', province_id=1)
    # db.session.add(d1)
    # db.session.add(d2)

    # #Add user
    # u1 = User(first_name='Hien', last_name='Tran', birthday=datetime(2001, 8, 6, 0), phone_number='0964345626',
    #           username='hien', password='202cb962ac59075b964b07152d234b70', user_role=UserRole.MANAGER, gender_id=Gender.NU)
    # u2 = User(first_name='Hong', last_name='Tran', birthday=datetime(2001, 7, 11, 0), phone_number='0912123321',
    #           username='hong', password='202cb962ac59075b964b07152d234b70', user_role=UserRole.DOCTOR, gender_id=Gender.NU)
    # u3 = User(first_name='Vi', last_name='Nguyen', birthday=datetime(2001, 11, 29, 0), phone_number='0987632121',
    #           username='vi', password='202cb962ac59075b964b07152d234b70', user_role=UserRole.NURSE, gender_id=Gender.NU)
    # db.session.add(u1)
    # db.session.add(u2)
    # db.session.add(u3)
    # #Add customer
    # c1 = Customer(first_name='Hien', last_name='Tran Thi Thu', birthday=datetime(2001, 8, 6, 0),
    #               phone_number='0943123253', appointment_date=datetime(2021, 12, 18, 0), gender_id=Gender.NU)
    # c2 = Customer(first_name='Vi', last_name='Nguyen Thi Trieu', birthday=datetime(2001, 11, 29, 0),
    #               phone_number='0964321321', appointment_date=datetime(2021, 12, 18, 0), gender_id=Gender.NU)
    # c3 = Customer(first_name='Hong', last_name='Tran Thi Bich', birthday=datetime(2001, 7, 11, 0),
    #               phone_number='0965443215', appointment_date=datetime(2021, 12, 18, 0), gender_id=Gender.NU)
    # c4 = Customer(first_name='Tien', last_name='Nguyen Minh', birthday=datetime(2001, 1, 1, 0),
    #               phone_number='0965443219', appointment_date=datetime(2021, 12, 20, 0))
    # db.session.add(c1)
    # db.session.add(c2)
    # db.session.add(c3)
    # db.session.add(c4)
    # s1 = Schedule(examination_date=date(2021, 12, 18))
    # s2 = Schedule(examination_date=date(2021, 12, 20))
    # db.session.add(s1)
    # db.session.add(s2)
    # cs1 = CustomerSche(customer_id=1, schedule_id=1, examined=True, timer=time(9, 3, 2, 3))
    # cs2 = CustomerSche(customer_id=2, schedule_id=1, examined=True, timer=time(10, 0, 0, 0))
    # cs3 = CustomerSche(customer_id=3, schedule_id=1, examined=True, timer=time(11, 0, 0, 0))
    # cs4 = CustomerSche(customer_id=4, schedule_id=2, examined=True, timer=time(15, 0, 0, 0))
    # db.session.add(cs1)
    # db.session.add(cs2)
    # db.session.add(cs3)
    # db.session.add(cs4)
    # #Add regulation
    # r1 = Regulation()
    # db.session.add(r1)
    # #Add medicine
    # m1 = Medicine(name='Thuốc ho', quantity=100, price=20000)
    # m2 = Medicine(name='Thuốc đau bụng', quantity=120, price=30000)
    # m3 = Medicine(name='Thuốc giảm đau', quantity=70, price=40000)
    # m4 = Medicine(name="Thuốc an thần", quantity=0, price=10000)
    # m5 = Medicine(name="Thuốc trợ tim", quantity=10, price=15000)
    # db.session.add(m1)
    # db.session.add(m2)
    # db.session.add(m3)
    # db.session.add(m4)
    # db.session.add(m5)
    # #Add medicall_bill
    # mb1 = MedicalBill(user_id=2, customer_sche=1, symptom='Đau đầu, sổ mũi', diagnostic_disease= 'Đau đầu')
    # mb2 = MedicalBill(user_id=2, customer_sche=2, symptom='Ho, mất vị giác', diagnostic_disease= 'Sốt')
    # mb3 = MedicalBill(user_id=2, customer_sche=3, symptom='Đau lưng, mỏi gối', diagnostic_disease= 'Dấu hiệu tuổi già')
    # mb4 = MedicalBill(user_id=2, customer_sche=4, symptom='Chảy máu mũi', diagnostic_disease= 'Viêm xoang')
    # db.session.add(mb1)
    # db.session.add(mb2)
    # db.session.add(mb3)
    # db.session.add(mb4)
    # #Add medical_bill_detail
    # mbd1 = MedicalBillDetail(medical_bill=1, medicine=2, quantity=5, unit_price=30000, how_to_use='1 ngày uống 2 lần')
    # mbd2 = MedicalBillDetail(medical_bill=1, medicine=3, quantity=10, unit_price=40000, how_to_use='1 ngày uống 3 lần')
    # mbd3 = MedicalBillDetail(medical_bill=2, medicine=1, quantity=15, unit_price=20000, how_to_use='2 ngày uống 1 lần')
    # mbd4 = MedicalBillDetail(medical_bill=4, medicine=2, quantity=30, unit_price=30000, how_to_use='1 tuần uống 3 lần')
    # mbd5 = MedicalBillDetail(medical_bill=3, medicine=1, quantity=13, unit_price=30000, how_to_use='1 tuần uống 7 lần')
    # db.session.add(mbd1)
    # db.session.add(mbd2)
    # db.session.add(mbd3)
    # db.session.add(mbd4)
    # db.session.add(mbd5)
    # #Add receipt
    # w1 = Receipt(total_price=230000, regulation=1, medical_bill=1, customer_id=1, user_id=3, created_date=datetime(2021,12,18,0))
    # w2 = Receipt(total_price=250000, regulation=1, medical_bill=2, customer_id=2, user_id=3, created_date=datetime(2021,12,18,0))
    # w3 = Receipt(total_price=520000, regulation=1, medical_bill=3, customer_id=3, user_id=3, created_date=datetime(2021,12,18,0))
    # w4 = Receipt(total_price=720000, regulation=1, medical_bill=4, customer_id=4, user_id=3, created_date=datetime(2021,12,20,0))
    # db.session.add(w1)
    # db.session.add(w2)
    # db.session.add(w3)
    # db.session.add(w4)
    # r1 = Regulation()
    # db.session.add(r1)
    
    #Thêm dữ liệu hiện tại để xem thống kê
    # c5 = Customer(first_name='A', last_name='Nguyen Van', birthday=datetime(2000, 8, 6, 0),
    #               phone_number='0943423253', appointment_date=datetime.now(), gender_id=Gender.NAM)
    # c6 = Customer(first_name='B', last_name='Le Ngoc', birthday=datetime(1999, 8, 6, 0),
    #               phone_number='0943423983', appointment_date=datetime.now(), gender_id=Gender.NAM)
    # db.session.add(c5)
    # db.session.add(c6)

    # s3 = Schedule(examination_date=datetime.now())
    # db.session.add(s3)

    # cs5 = CustomerSche(customer_id=5, schedule_id=3, examined=True, timer=time(9, 30, 20))
    # cs6 = CustomerSche(customer_id=6, schedule_id=3, examined=True, timer=time(10, 30, 20))
    # cs7 = CustomerSche(customer_id=2, schedule_id=3, examined=False, timer=time(13, 30, 20))
    # db.session.add(cs5)
    # db.session.add(cs6)
    # db.session.add(cs7)
    #
    # mb5 = MedicalBill(user_id=2, customer_sche=5, symptom='Đau đầu, sổ mũi', diagnostic_disease= 'Đau đầu')
    # mb6 = MedicalBill(user_id=2, customer_sche=6, symptom='Ho, mất vị giác', diagnostic_disease= 'Covid')
    # db.session.add(mb5)
    # db.session.add(mb6)

    # mbd6 = MedicalBillDetail(medical_bill=5, medicine=1, quantity=15, unit_price=20000, how_to_use='2 ngày uống 1 lần')
    # mbd7 = MedicalBillDetail(medical_bill=6, medicine=3, quantity=15, unit_price=50000, how_to_use='2 ngày uống 2 lần')
    # db.session.add(mbd6)
    # db.session.add(mbd7)
    #
    # r5 = Receipt(total_price=740000, regulation=1, medical_bill=5, customer_id=5, user_id=3, created_date=datetime.now())
    # r6 = Receipt(total_price=740000, regulation=1, medical_bill=6, customer_id=6, user_id=3, created_date=datetime.now())
    # db.session.add(r5)
    # db.session.add(r6)
    
    #db.session.commit()
    db.create_all()

