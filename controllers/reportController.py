# coding: utf-8
from datetime import datetime

from flask import Blueprint, request, jsonify

from models.models import MriImage, Report, Doctor, db
from utils.dtoUtils import get_report_content, get_report_abstract
from utils.fileUtils import upload_files

report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/generate', methods=['POST'])
def generate_report():
    """报告生成接口"""
    # 参数校验
     # 从 form-data 中直接获取参数
    image_id = request.form.get('imageId')
    doctor_id = request.form.get('doctorId')
    radiomic_comment = request.form.get('radiomicComment', '')
    therapy_comment = request.form.get('therapyComment', '')

    # 参数校验
    if not image_id or not doctor_id:
        return jsonify({'code': 400, 'message': '缺少MRI图像ID或医生ID'}), 400

    # 获取MRI图像
    mri_image = MriImage.query.get(image_id)
    if not mri_image:
        return jsonify({'code': 404, 'message': '指定的MRI图像不存在'}), 404

    # 获取医生信息
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({'code': 404, 'message': '指定的医生不存在'}), 404

    # 处检查上传的ROI图像文件
    roi_t1_file = request.files.get('roi_t1')
    roi_t2_file = request.files.get('roi_t2')
    if not roi_t1_file or not roi_t2_file:
        return jsonify({'code': 400, 'message': '缺少ROI图像文件 (T1 或 T2)'}), 400

    # 使用静态文件存储服务存储上传的ROI图像文件
    try:
        roi_t1_path, roi_t2_path = upload_files((roi_t1_file, roi_t2_file),
                                                (('nrrd',), ('nrrd',)))
        new_report = Report(
            image_id=image_id,
            doctor_id=doctor_id,
            roi_t1_path=roi_t1_path,
            roi_t2_path=roi_t2_path,
            radiomic_comment=radiomic_comment,
            therapy_comment=therapy_comment,
            generation_date=datetime.utcnow()
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({
            'code': 201,
            'message': '报告生成成功',
            'data': get_report_content(new_report)
        }), 201
    except Exception as e:
        return jsonify({'code': 500, 'message': f'报告生成失败: {str(e)}'}), 500


@report_bp.route('/last', methods=['GET'])
def get_last_report():
    """获取患者上一份分析报告的粗略信息的接口"""
    # 参数校验
    patient_id = request.args.get('patientId')
    if not patient_id:
        return jsonify({'code': 400, 'message': '缺少患者ID'}), 400

    # 查询最近一份报告
    report = Report.query.join(Report.image).filter_by(patient_id=patient_id).order_by(Report.generation_date.desc()).first()
    if not report:
        return jsonify({'code': 404, 'message': '未找到任何报告'}), 404
    return jsonify({'code': 200, 'data': get_report_abstract(report)}), 200


@report_bp.route('/all', methods=['GET'])
def get_all_reports():
    """获取患者全部分析报告的粗略信息的接口"""
    # 参数校验
    patient_id = request.args.get('patientId')
    if not patient_id:
        return jsonify({'code': 400, 'message': '缺少患者ID'}), 400

    reports = Report.query.join(Report.image).filter_by(patient_id=patient_id).all()

    return jsonify({'code': 200, 'data': [get_report_abstract(report) for report in reports]}), 200


@report_bp.route('/detail/<int:report_id>', methods=['GET'])
def get_report_detail(report_id):
    """获取某一份报告的详细内容的接口"""
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '报告不存在'}), 404

    return jsonify({'code': 200, 'data': get_report_content(report)}), 200


@report_bp.route('/ofImage', methods=['GET'])
def get_report_of_image():
    """获取某个MRI图像对应的分析报告的接口"""
    # 参数校验
    image_id = request.args.get('imageId')
    if not image_id:
        return jsonify({'code': 400, 'message': '缺少MRI图像ID'}), 400

    report = Report.query.filter_by(image_id=image_id).first()
    if not report:
        return jsonify({'code': 404, 'message': '该MRI图像尚未生成分析报告'}), 404

    return jsonify({'code': 200, 'data': get_report_content(report)}), 200


@report_bp.route('/edit/<int:report_id>', methods=['POST'])
def edit_report(report_id):
    """报告编辑接口"""
    data = request.get_json()
    radiomic_comment = data.get('radiomicComment')
    therapy_comment = data.get('therapyComment')

    report = Report.query.get(report_id)
    if not report:
        return jsonify({'code': 404, 'message': '未找到相关报告'}), 404

    try:
        if radiomic_comment:
            report.radiomic_comment = radiomic_comment
        if therapy_comment:
            report.therapyComment = therapy_comment
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '报告编辑成功',
            'data': get_report_content(report)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'报告编辑失败: {str(e)}'}), 500
