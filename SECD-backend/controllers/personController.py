# coding: utf-8
from flask import Blueprint, request, jsonify
from models.models import db, Doctor, Patient, User
from utils.dtoUtils import get_doctor_info, get_patient_info

person_bp = Blueprint('person', __name__, url_prefix='/person')


@person_bp.route('/doctor/all', methods=['GET'])
def get_all_doctors():
    """全部医生基本信息获取接口"""
    try:
        doctors = Doctor.query.all()
        result = [get_doctor_info(doctor) for doctor in doctors]
        return jsonify({'code': 200, 'data': result}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取医生信息失败: {str(e)}'}), 500


@person_bp.route('/doctor/select/<int:doctor_id>', methods=['GET'])
def get_doctor_by_id(doctor_id):
    """指定ID医生基本信息获取接口"""
    try:
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'code': 400, 'message': '医生不存在'}), 404
        return jsonify({'code': 200, 'data': get_doctor_info(doctor)}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取医生信息失败: {str(e)}'}), 500


@person_bp.route('/doctor/charge', methods=['GET'])
def get_doctor_by_patient():
    """患者主管医生基本信息获取接口"""
    # 参数校验
    patient_id = request.args.get('patient_id', type=int)
    if not patient_id:
        return jsonify({'code': 400, 'message': '患者ID为必填参数'}), 400

    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
        if not patient.doctor:
            return jsonify({'code': 404, 'message': '该患者没有主管医生'}), 404
        return jsonify({'code': 200, 'data': get_doctor_info(patient.doctor)}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取主管医生信息失败: {str(e)}'}), 500


@person_bp.route('/patient/all', methods=['GET'])
def get_all_patients():
    """全部患者基本信息获取接口"""
    try:
        patients = Patient.query.all()
        result = [get_patient_info(patient) for patient in patients]
        return jsonify({'code': 200, 'data': result}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取患者信息失败: {str(e)}'}), 500


@person_bp.route('/patient/select/<int:patient_id>', methods=['GET'])
def get_patient_by_id(patient_id):
    """指定ID患者基本信息获取接口"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
        return jsonify({'code': 200, 'data': get_patient_info(patient)}), 200
    except Exception as e:
        return jsonify({'code': 500, 'message': f'获取患者信息失败: {str(e)}'}), 500


@person_bp.route('/patient/charge', methods=['GET'])
def get_patients_by_doctor():
    """医生负责患者列表获取接口"""
    doctor_id = request.args.get('doctor_id', type=int)
    if not doctor_id:
        return jsonify({'code': 400, 'message': '医生ID为必填参数'}), 400

    try:
        # 先检查医生是否存在
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            return jsonify({'error': '医生不存在'}), 404
        # 再查询医生负责的患者列表
        patients = Patient.query.filter_by(doctor_id=doctor_id).all()
        result = [get_patient_info(patient) for patient in patients]
        return jsonify({'code': 200, 'data': result}), 200
    except Exception as e:
        return jsonify({'error': f'获取患者列表失败: {str(e)}'}), 500

@person_bp.route('/patient/search', methods=['GET'])
def search_patient():
    """患者搜索接口"""
    name = request.args.get('name')
    phone_number = request.args.get('phoneNumber')
    if not name or not phone_number:
        return jsonify({'code': 400, 'message': '缺失患者姓名和电话号码'}), 400

    try:
         # 先在 User 表中查找符合条件的用户
        user = User.query.filter_by(
            name=name, 
            phone_number=phone_number, 
            user_type='patient'  # 确保是患者类型
        ).first()
        
        if not user:
            return jsonify({'code': 404, 'message': '患者不存在'}), 404
            
        # 根据 user_id 查找对应的 Patient 记录
        patient = Patient.query.filter_by(user_id=user.user_id).first()
        if not patient:
            return jsonify({'code': 404, 'message': '患者信息不完整'}), 404
            
        return jsonify({'code': 200, 'data': get_patient_info(patient)}), 200
    except Exception as e:
        return jsonify({'error': f'获取患者列表失败: {str(e)}'}), 500
