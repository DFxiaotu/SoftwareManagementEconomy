from flask import Blueprint, request, jsonify

from models.models import *
from utils.dtoUtils import get_patient_info

manage_bp = Blueprint('manage', __name__, url_prefix='/manage')


@manage_bp.route('/<int:doctor_id>/all', methods=['GET'])
def get_patient_list(doctor_id):
    """患者列表接口"""
    # 检验医生是否存在
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'code': 404, 'message': '医生不存在'}), 404

    patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    return jsonify({'code': 200, 'data': [get_patient_info(patient) for patient in patients]})


@manage_bp.route('/<int:doctor_id>/add', methods=['PATCH'])
def add_patient(doctor_id):
    """添加患者接口"""
    # 参数校验
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({'code': 400, 'message': '缺失患者ID'}), 400

    # 检验医生是否存在
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'code': 404, 'message': '医生不存在'}), 404

    # 检验患者是否存在
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'code': 404, 'message': '患者不存在'}), 404

    # 医患绑定
    try:
        patient.doctor_id = doctor_id
        db.session.commit()
        return jsonify({'code': 200, 'message': '添加患者成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'添加患者失败: {str(e)}'}), 500


@manage_bp.route('/<int:doctor_id>/remove', methods=['PATCH'])
def remove_patient(doctor_id):
    """移除患者接口"""
    # 参数校验
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({'code': 400, 'message': '缺失患者ID'}), 400

    # 检验医生是否存在
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'code': 404, 'message': '医生不存在'}), 404

    # 检验患者是否存在
    patient = Patient.query.get(patient_id)
    if not patient:
        return jsonify({'code': 404, 'message': '患者不存在'}), 404

    # 检查医患是否配对
    if patient.doctor_id != doctor_id:
        return jsonify({'code': 400, 'message': f'医生 {doctor_id} 不是患者 {patient_id} 的主管医生'}), 400

    # 医患解绑
    try:
        patient.doctor_id = None
        db.session.commit()
        return jsonify({'code': 200, 'message': '移除患者成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'移除患者失败: {str(e)}'}), 500
