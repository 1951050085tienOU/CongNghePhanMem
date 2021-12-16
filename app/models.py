from app import db, app
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from datetime import datetime
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


class District(db.Model):
    __tablename__ = 'district'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    wards = relationship('Ward', backref='district', lazy=True)
    province_id = Column(Integer, ForeignKey(Province.id), nullable=False)

class Ward(db.Model):
    __tablename__ = 'ward'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)
    addresss = relationship('Address', backref='ward', lazy=True)
    district_id = Column(Integer, ForeignKey(District.id), nullable=False)

class Address(db.Model):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    info = Column(String(50))
    ward_id = Column(Integer, ForeignKey(Ward.id), nullable=False)

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
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False, primary_key=True)
    examined = Column(Boolean, default=False)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True, autoincrement=True)
    examination_date = Column(DateTime, nullable=False)  #ngày khám
    medical_bill = relationship('MedicalBill', backref='schedule', lazy=True, uselist=False)
    customers = relationship('CustomerSche', backref='schedules', lazy=True)

class MedicalBill(db.Model):
    __tablename__ = 'medical_bill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symptom = Column(String(100))   #triệu chứng
    diagnostic_disease = Column(String(100))    #bệnh chuẩn đoán
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False)
    details = relationship('MedicalBillDetail', backref='medicalbill', lazy=True)
    receipt = relationship('Receipt', backref='medicalbill', uselist=False, lazy=True)

class Producer(db.Model):
    __tablename__ = 'producer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    medicines = relationship('Medicine', backref='producer', lazy=True)

class MedicineType(db.Model):
    __tablename__ = 'medicine_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50))
    medicines = relationship('Medicine', backref='medicinetype', lazy=True)

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
    id = Column(Integer, primary_key=True, autoincrement=True)
    examination_price = Column(Float, default=150000)
    customer_quantity = Column(Integer, default=30)
    receipts = relationship('Receipt', backref='regulations', lazy=True)


if __name__ == "__main__":
    '''p1 = Province(name='Hồ Chí Minh')
    d1 = District(name='Quận 1', province_id=1)
    d2 = District(name='Quận 2', province_id=1)
    db.session.add(p1)
    db.session.add(d1)
    db.session.add(d2)
    #Add user
    u1 = User(first_name='Hien', last_name='Tran', birthday=datetime.now(), phone_number='0987654321',
    username='hien', password='123', user_role= UserRole.MANAGER)
    u2 = User(first_name='Hong', last_name='Tran', birthday=datetime.now(), phone_number='09876541',
              username='hong', password='123', user_role=UserRole.DOCTOR)
    u3 = User(first_name='Vi', last_name='Nguyen', birthday=datetime.now(), phone_number='09876321',
              username='vi', password='123', user_role=UserRole.NURSE)
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)
    #Add customer, schedule, customer_sche
    c1 = Customer(first_name='Li', last_name='Tran', birthday=datetime.now(),
                    phone_number='09654321', appointment_date=datetime.now())
    c2 = Customer(first_name='Ben', last_name='Tran', birthday=datetime.now(),
                    phone_number='0964321', appointment_date=datetime.now())
    c3 = Customer(first_name='Bo', last_name='Tran', birthday=datetime.now(),
                    phone_number='096544321', appointment_date=datetime.now())
    s1 = Schedule(examination_date=datetime.now())
    cs1 = CustomerSche(customer_id=1, schedule_id=1, examined=True)
    cs2 = CustomerSche(customer_id=2, schedule_id=1, examined=True)
    cs3 = CustomerSche(customer_id=3, schedule_id=1, examined=True)
    db.session.add(c1)
    db.session.add(c2)
    db.session.add(c3)
    db.session.add(s1)
    db.session.add(cs1)
    db.session.add(cs2)
    db.session.add(cs3)
    # Add regulation
    r1 = Regulation()
    db.session.add(r1)
    #Add medicine
    m1 = Medicine(name='AB', quantity=50, price=20000)
    m2 = Medicine(name='CD', quantity=50, price=30000)
    m3 = Medicine(name='EF', quantity=50, price=40000)
    db.session.add(m1)
    db.session.add(m2)
    db.session.add(m3)
    #Add medicall_bill
    mb1 = MedicalBill(user_id=2, schedule_id=1)
    mb2 = MedicalBill(user_id=2, schedule_id=1)
    mb3 = MedicalBill(user_id=2, schedule_id=1)
    db.session.add(mb1)
    db.session.add(mb2)
    db.session.add(mb3)
    #Add medical_bill_detail
    mbd1 = MedicalBillDetail(medical_bill=1, medicine=2, quantity=5, unit_price=30000)
    mbd2 = MedicalBillDetail(medical_bill=1, medicine=3, quantity=10, unit_price=40000)
    mbd3 = MedicalBillDetail(medical_bill=2, medicine=1, quantity=15, unit_price=20000)
    mbd4 = MedicalBillDetail(medical_bill=3, medicine=2, quantity=7, unit_price=30000)
    db.session.add(mbd1)
    db.session.add(mbd2)
    db.session.add(mbd3)
    db.session.add(mbd4)
    #Add receipt
    w1 = Receipt(total_price=230000, regulation=1, medical_bill=1, customer_id=1, user_id=3)
    w2 = Receipt(total_price=250000, regulation=1, medical_bill=2, customer_id=2, user_id=3)
    w3 = Receipt(total_price=520000, regulation=1, medical_bill=3, customer_id=3, user_id=3)
    db.session.add(w1)
    db.session.add(w2)
    db.session.add(w3)

    m4 = Medicine(name="JJ", quantity=0, price=10000)
    m5 = Medicine(name="AE", quantity=5, price=15000)
    db.session.add(m4)
    db.session.add(m5)
    db.session.commit()'''
    db.create_all()

