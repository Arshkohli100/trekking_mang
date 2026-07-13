from flask import Flask
from models import init_db

app = Flask(__name__)
app.secret_key = 'trekking_secret_key'

from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    init_db()
