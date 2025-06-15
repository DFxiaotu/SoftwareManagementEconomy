import logging

from flask import Flask
from flask_cors import CORS

from configs import database, web
from controllers.authController import auth_bp
from controllers.manageController import manage_bp
from controllers.mriController import mri_bp
from controllers.reportController import report_bp
from controllers.personController import person_bp
from models.models import db
from utils.jsonUtils import CustomJSONEncoder

app = Flask(__name__)

# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{database.USER}:{database.PASSWORD}@{database.HOST}:{database.PORT}/{database.NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# CORS配置
CORS(app, resources={r'/*': {'origins': f'{web.HOST}:{web.PORT}'}})

# 注册蓝图
app.register_blueprint(auth_bp)
app.register_blueprint(mri_bp)
app.register_blueprint(report_bp)
app.register_blueprint(manage_bp)
app.register_blueprint(person_bp)

# 配置JSON解码器
app.json_encoder = CustomJSONEncoder

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True)
