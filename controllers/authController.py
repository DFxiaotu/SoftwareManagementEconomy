# coding: utf-8
import re
from datetime import datetime, timedelta

import jwt
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from configs.encrypt import SECRET_KEY, ALGORITHM
from models.models import db, User, Doctor, Patient

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册接口"""
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    password = data.get('password')
    user_type = data.get('userType')

    # 参数校验
    if not all([phone_number, password, user_type]):
        return jsonify({'code': 400, 'message': '所有字段均为必填'}), 400
    if user_type not in ['doctor', 'patient']:
        return jsonify({'code': 400, 'message': '用户类型必须为医生或患者'}), 400
    if not re.match(r'^1[3-9]\d{9}$', phone_number):
        return jsonify({'code': 400, 'message': '手机号格式不正确'}), 400

    # 检查手机号是否已注册
    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({'code': 400, 'message': '手机号已被注册'}), 400

    # 密码加密
    hashed_password = generate_password_hash(password)

    # 创建新用户
    new_user = (Doctor if user_type == 'doctor' else Patient)(
        phone_number=phone_number,
        password=hashed_password,
        user_type=user_type,
        is_authenticated=False,  # 默认为未认证
        registration_time=datetime.utcnow()
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'code': 201, 'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'注册失败: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录接口"""
    data = request.get_json()
    phone_number = data.get('phoneNumber')
    password = data.get('password')

    # 参数校验
    if not all([phone_number, password]):
        return jsonify({'code': 400, 'message': '手机号和密码为必填'}), 400

    # 验证用户
    user = User.query.filter_by(phone_number=phone_number).first()
    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    if not check_password_hash(user.password, password):
        return jsonify({'code': 401, 'message': '密码错误'}), 401

    # 生成JWT令牌
    payload = {
        'sub': user.user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=2)  # 令牌2小时过期
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'token': token,
        'data': {
            'userId': user.user_id,
            'name': user.name,
            'phoneNumber': user.phone_number,
            'userType': user.user_type,
            'isAuthenticated': user.is_authenticated
        }
    }), 200


@auth_bp.route('/authenticate/doctor', methods=['POST'])
def doctor_authenticate():
    """医生认证接口"""
    data = request.get_json()
    user_id = data.get('userId')
    real_name = data.get('realName')
    hospital = data.get('hospital')
    department = data.get('department')
    title = data.get('title')

    # 参数校验
    if not all([user_id, real_name, hospital, department, title]):
        return jsonify({'code': 400, 'message': '用户ID、真实姓名、医院、部门、职称均为必填'}), 400

    # 查询用户
    doctor = Doctor.query.get(user_id)
    if not doctor:
        return jsonify({'code': 404, 'message': '医生不存在'}), 404
    if doctor.is_authenticated:
        return jsonify({'code': 403, 'message': '医生已认证，无需重复认证'}), 403

    # 更新认证信息
    doctor.name = real_name
    doctor.hospital = hospital
    doctor.department = department
    doctor.title = title
    doctor.is_authenticated = True

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '认证成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'认证失败: {str(e)}'}), 500


@auth_bp.route('/authenticate/patient', methods=['POST'])
def patient_authenticate():
    """患者认证接口"""
    data = request.get_json()
    user_id = data.get('userId')
    real_name = data.get('realName')
    age = data.get('age')
    gender = data.get('gender')

    # 参数校验
    if not all([user_id, real_name] or age is None or gender is None):
        return jsonify({'code': 400, 'message': '用户ID、真实姓名、年龄、性别均为必填'}), 400
    if type(age) is not int or type(gender) is not bool:
        return jsonify({'code': 400, 'message': '年龄应为整数，性别应为布尔值'}), 400
    if age <= 0 or age >= 150:
        return jsonify({'code': 400, 'message': '年龄范围应在0到150之间'}), 400
    if gender not in (0, 1):
        return jsonify({'code': 400, 'message': '性别应为1（男）或0（女）'}), 400

    # 查询用户
    patient = Patient.query.get(user_id)
    if not patient:
        return jsonify({'code': 404, 'message': '患者不存在'}), 404
    if patient.is_authenticated:
        return jsonify({'code': 403, 'message': '患者已认证，无需重复认证'}), 403

    # 更新认证信息
    patient.name = real_name
    patient.age = age
    patient.gender = gender
    patient.is_authenticated = True

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '认证成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'认证失败: {str(e)}'}), 500


@auth_bp.route('resetAuth/<int:user_id>', methods=['PATCH'])
def resetAuth(user_id):
    """认证状态重置接口（用于重新认证）"""
    user = User.query.get(user_id)

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404
    if not user.is_authenticated:
        return jsonify({'code': 403, 'message': '用户未认证，不可重置认证状态'}), 403

    # 重置认证状态
    user.is_authenticated = False

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '认证状态已重置'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'认证状态重置失败: {str(e)}'}), 500
