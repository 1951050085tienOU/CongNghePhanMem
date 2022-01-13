from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = "akj+fg823762531341=2901r-9sd-7g2f98r3sa8d1-2751849"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Trieuvi2911@localhost/phongmachhonghienvytiendb?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4

cloudinary.config(
    cloud_name='suna12846ke',
    api_key='577991942497348',
    api_secret='9NlOoMXXLUZZS-ExY9XX4Gpsnes'
)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)