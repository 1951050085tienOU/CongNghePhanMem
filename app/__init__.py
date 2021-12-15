from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = "akj+fg823762531341=2901r-9sd-7g2f98r3sa8d1-2751849"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:hien0608@localhost/demo?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 4

cloudinary.config(
    cloud_name='xianchenw',
    api_key='861389157297511',
    api_secret='QSm5aPp6Lu5TI7j2hOBrDBwjSz0'
)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)