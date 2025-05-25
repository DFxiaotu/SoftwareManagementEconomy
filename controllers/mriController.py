# coding: utf-8
import io
import json
from datetime import datetime
from email.encoders import encode_base64
from email.generator import Generator, BytesGenerator
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, request, jsonify, Response

from models.models import db, MriImage, Report, BloodRoutine
from utils.dtoUtils import *
from utils.fileUtils import upload_files, download_files
from utils.jsonUtils import snake_to_camel
from utils.nrrd2Base64 import nrrd2base64
from utils.machineAnalysis import predict_single_case, ResNet18_Feature
import torch
mri_bp = Blueprint('mri', __name__, url_prefix='/mri')


@mri_bp.route('/upload/<int:patient_id>', methods=['POST'])
def upload_mri(patient_id):
    """MRI图像上传接口"""
    if 't1File' not in request.files or 't2File' not in request.files:
        return jsonify({'code': 400, 'message': '需要上传t1和t2文件'}), 400

    t1_file = request.files['t1File']
    t2_file = request.files['t2File']
    imaging_date = request.form.get('imagingDate')

    # 参数校验
    if not imaging_date:
        return jsonify({'code': 400, 'message': '缺少图像拍摄日期'}), 400
    if not t1_file or not t2_file:
        return jsonify({'code': 400, 'message': '缺少图像文件'}), 400

    # 使用静态文件存储服务存储图像文件
    try:
        t1_path, t2_path = upload_files((t1_file, t2_file), (('nrrd',), ('nrrd',)))
        new_report = MriImage(
            patient_id=patient_id,
            t1_path=t1_path,
            t2_path=t2_path,
            upload_date=datetime.utcnow(),
            imaging_date=imaging_date
        )
        db.session.add(new_report)
        db.session.commit()
        return jsonify({'code': 201, 'message': '文件上传成功', 'data': {'imageId': new_report.image_id}}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'文件上传失败: {str(e)}'}), 500


@mri_bp.route('/all/<int:patient_id>', methods=['GET'])
def get_all_mris(patient_id):
    """全部MRI图像获取接口（单张）"""
    # 使用 JOIN 查询一次性获取所有需要的数据
    mris = (MriImage.query
            .filter_by(patient_id=patient_id)
            .outerjoin(Report, MriImage.image_id == Report.image_id)
            .add_columns(Report.report_id)
            .all())
    if not mris:
        return jsonify({'code': 404, 'message': '没有找到相关MRI图像'}), 404
    
    result = []
    for mri, report_id in mris:
        all_slices_t1, first_slice_t1 = nrrd2base64(mri.t1_path)
        all_slices_t2, first_slice_t2 = nrrd2base64(mri.t2_path)

        result.append({
            'imageId': mri.image_id,
            'allSlicesT1': all_slices_t1,
            'firstSliceT1': first_slice_t1,
            'allSlicesT2': all_slices_t2,
            'firstSliceT2': first_slice_t2,
            'hasReport': report_id is not None,
            'imageDate': mri.imaging_date,
            'uploadDate': mri.upload_date,
            'fibroidsPresent': mri.fibroids_present,
            'avgTreatmentPower': mri.avg_treatment_power,
            'totalEnergy': mri.total_energy,
            'treatmentVolume': mri.treatment_volume,
            'parity': mri.parity,
            'miscarriageCount': mri.miscarriage_count
        })
    # 这里返回一张切面图，以及图像ID和是否已经生成报告
    return jsonify(result), 200


@mri_bp.route('/period/<int:patient_id>', methods=['GET'])
def get_mris_by_period(patient_id):
    """MRI图像按时间段获取接口（单张）"""
    # 参数校验
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    if not all([start_date, end_date]):
        return jsonify({'code': 400, 'message': '缺少患者ID或时间范围'}), 400

    # 日期格式校验
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'code': 400, 'message': '日期格式错误，应为YYYY-MM-DD'}), 400

    # 按时间范围查找
    mris = MriImage.query.filter(
        MriImage.patient_id == patient_id,
        MriImage.upload_date >= start_date,
        MriImage.upload_date <= end_date
    ).all()
    if not mris:
        return jsonify({'code': 404, 'message': '没有找到相关MRI图像'}), 404

    image_ids = [mri.image_id for mri in mris]
    reports = Report.query.filter(Report.image_id.in_(image_ids)).all()
    report_ids = [report.report_id for report in reports]

    result = []
    for mri in mris:
        all_slices_t1, first_slice_t1 = nrrd2base64(mri.t1_path)
        all_slices_t2, first_slice_t2 = nrrd2base64(mri.t2_path)
        result.append({
            'imageId': mri.image_id,
            'allSlicesT1': all_slices_t1,
            'firstSliceT1': first_slice_t1,
            'allSlicesT2': all_slices_t2,
            'firstSliceT2': first_slice_t2,
            'hasReport': mri.image_id in report_ids,
            'imageDate': mri.imaging_date
        })
    # 这里返回一张切面图，以及图像ID和是否已经生成报告
    return jsonify(result), 200


@mri_bp.route('/details', methods=['GET'])
def get_image_file():
    """获取某个MRI图像的细节，包括t1文件、t2文件、临床指标"""
    # 参数校验
    image_id = request.args.get('imageId')
    if not image_id:
        return jsonify({'code': 400, 'message': '缺少MRI图像ID'}), 400

    mri = MriImage.query.get(image_id)
    if not mri:
        return jsonify({'code': 404, 'message': '没有找到相关MRI图像'}), 404

    # 临床指标数据
    clinical_data = {
        'code': 200,
        'data': get_clinical_indicators(mri)
    }

    # 创建多部分 MIME 响应
    multipart = MIMEMultipart('mixed')

    # JSON 部分
    json_part = MIMEText(json.dumps(clinical_data, ensure_ascii=False), 'json', 'utf-8')
    json_part.add_header('Content-Disposition', 'attachment', filename='clinical_indicators.json')
    multipart.attach(json_part)

    # 文件部分：T1 和 T2 文件打包成 ZIP
    zip_buffer = download_files({'t1': mri.t1_path, 't2': mri.t2_path})

    file_part = MIMEBase('application', 'zip')
    file_part.set_payload(zip_buffer.read())
    encode_base64(file_part)
    file_part.add_header('Content-Disposition', 'attachment', filename=f"MRI_Images_{mri.imaging_date}.zip")
    multipart.attach(file_part)

    # 转换为 HTTP 响应
    response_io = io.BytesIO()
    multipart_generator = BytesGenerator(response_io, mangle_from_=False)
    multipart_generator.flatten(multipart)

    response = Response(response_io.getvalue(), content_type=f'multipart/mixed; boundary="{multipart.get_boundary()}"')
    return response


@mri_bp.route('/clinical/<int:patient_id>', methods=['GET'])
def get_clinical(patient_id):
    """获取用户一段时间内的某个临床指标"""
    # 参数校验
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    indicator_type = request.args.get('indicatorType')
    if not all([start_date, end_date, indicator_type]):
        return jsonify({'code': 400, 'message': '时间范围或临床指标类型缺失'}), 400

    # 日期格式校验
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'code': 400, 'message': '日期格式错误，应为YYYY-MM-DD'}), 400

    # 临床指标类型校验
    if indicator_type not in [snake_to_camel(indicator) for indicator in CLINICAL_INDICATORS] and indicator_type != 'bloodRoutine':
        return jsonify({'code': 400, 'message': '临床指标类型不正确'})

    # 按时间范围查找
    mris = MriImage.query.filter(
        MriImage.patient_id == patient_id,
        MriImage.upload_date >= start_date,
        MriImage.upload_date <= end_date
    ).all()
    if not mris:
        return jsonify({'code': 404, 'message': '没有找到相关MRI图像'}), 404

    # 提取每个图像记录中临床指标字段的值
    clinical_data = [get_clinical_indicators(mri) for mri in mris]
    return jsonify({'code': 200,
                    'data': [clinical_indicators[indicator_type] for clinical_indicators in clinical_data]}), 200


@mri_bp.route('/analyse/<int:image_id>', methods=['GET'])
def analyse_mri(image_id):
    """MRI影像分析接口"""
    device = "cpu"
    
    # 加载模型
    model = ResNet18_Feature().to(device)
    model.load_state_dict(torch.load(".\\trainedModel\\best_resnet_model.pth",  map_location= torch.device('cpu')))
    
    # 示例：预测单个病例
    mri = MriImage.query.get(image_id)
    t1_path = mri.t1_path
    t2_path = mri.t2_path
    
    prediction, probability = predict_single_case(model, t1_path, t2_path, device)

    mri.result = prediction
    db.session.commit()

    if prediction and probability:
        return jsonify({'code': 200, 'data': {'prediction': prediction, 'probability': probability}}), 200
    else:
        return jsonify({'code': 500, 'message': '模型预测失败'}), 500
    
    
@mri_bp.route('/upload/all/<int:image_id>', methods=['POST'])
def upload_all_clinical_data(image_id):
    data = request.json
    mri = MriImage.query.get(image_id)
    if not mri:
        return jsonify({'code': 404, 'message': '没有找到相关MRI图像'}), 404
    

    # 如果没有对应的血常规记录,先创建一个
    if not mri.blood_routine_id:
        blood_routine = BloodRoutine()
        db.session.add(blood_routine)
        db.session.flush()  # 获取新生成的 ID
        mri.blood_routine_id = blood_routine.blood_routine_id
    else:
        blood_routine = BloodRoutine.query.get(mri.blood_routine_id)
    

    mri.imaging_date = data['imagingDate']
    mri.imaging_hospital = data['imagingHospital']
    mri.upload_date = datetime.utcnow()
    mri.fibroids_present = data['fibroidsPresent']
    mri.avg_treatment_power = data['avgTreatmentPower']
    mri.total_energy = data['totalEnergy']
    mri.treatment_volume = data['treatmentVolume']
    mri.parity = data['parity']
    mri.miscarriage_count = data['miscarriageCount']
    
    # 更新血常规数据
    blood_routine.wbc_count = data['wbcCount']
    blood_routine.basophil_absolute = data['basophilAbsolute']
    blood_routine.eosinophil_absolute = data['eosinophilAbsolute']
    blood_routine.neutrophil_absolute = data['neutrophilAbsolute']
    blood_routine.lymphocyte_absolute = data['lymphocyteAbsolute']
    blood_routine.monocyte_absolute = data['monocyteAbsolute']
    blood_routine.rbc_count = data['rbcCount']
    blood_routine.hemoglobin = data['hemoglobin']
    blood_routine.hematocrit = data['hematocrit']
    blood_routine.mcv = data['mcv']
    blood_routine.mch = data['mch']
    blood_routine.mchc = data['mchc']
    blood_routine.rdw_cv = data['rdwCv']
    blood_routine.rdw_sd = data['rdwSd']
    blood_routine.platelet_count = data['plateletCount']
    blood_routine.pdw = data['pdw']
    blood_routine.mpv = data['mpv']
    blood_routine.neutrophil_percentage = data['neutrophilPercentage']
    blood_routine.lymphocyte_percentage = data['lymphocytePercentage']
    blood_routine.monocyte_percentage = data['monocytePercentage']
    blood_routine.eosinophil_percentage = data['eosinophilPercentage']
    blood_routine.basophil_percentage = data['basophilPercentage']

    try:
        db.session.commit()
        return jsonify({'code': 200, 'message': '临床数据上传成功'}), 200
    except Exception as e:
        db.session.rollback()

        return jsonify({'code': 500, 'message': f'临床数据上传失败: {str(e)}'}), 500
