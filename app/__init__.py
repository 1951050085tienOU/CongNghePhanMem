from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager
from twilio.rest import Client
import keys

app = Flask(__name__)

app.secret_key = "akj+fg823762531341=2901r-9sd-7g2f98r3sa8d1-2751849"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/phongmachhonghienvytiendb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4

cloudinary.config(
    cloud_name='suna12846ke',
    api_key='577991942497348',
    api_secret='9NlOoMXXLUZZS-ExY9XX4Gpsnes'
)

#client = Client(account_sid, auth_token)
client = Client('ACc43453d6fe20ba148ba31d6c427675c4', 'fbfeabcd879873b8848ae248788c9087')
#twilio infomation
keys = {
    'account_sid': 'ACc43453d6fe20ba148ba31d6c427675c4',
    'auth_token': 'fbfeabcd879873b8848ae248788c9087',
    'twilio_number': '+16514482448'
}

db = SQLAlchemy(app=app)
login = LoginManager(app=app)