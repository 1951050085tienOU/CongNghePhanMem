from app import app, db
from flask import render_template, url_for


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    from admin import *
    app.run(debug=True)