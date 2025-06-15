# coding: utf-8
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BloodRoutine(db.Model):
    """血常规记录"""
    __tablename__ = 'blood_routine'

    blood_routine_id = db.Column(db.Integer, primary_key=True, unique=True, info='血常规标识')
    wbc_count = db.Column(db.Float(255), info='白细胞计数 (×10^9/L)')
    basophil_absolute = db.Column(db.Float(255), info='嗜碱性粒细胞绝对数 (×10^9/L)')
    eosinophil_absolute = db.Column(db.Float(255), info='嗜酸性粒细胞绝对数 (×10^9/L)')
    neutrophil_absolute = db.Column(db.Float(255), info='中性粒细胞绝对数 (×10^9/L)')
    lymphocyte_absolute = db.Column(db.Float(255), info='淋巴细胞绝对数 (×10^9/L)')
    monocyte_absolute = db.Column(db.Float(255), info='单核细胞绝对数 (×10^9/L)')
    rbc_count = db.Column(db.Float(255), info='红细胞计数 (×10^12/L)')
    hemoglobin = db.Column(db.Float(255), info='血红蛋白 (g/L)')
    hematocrit = db.Column(db.Float(255), info='红细胞比积 (%)')
    mcv = db.Column(db.Float(255), info='平均红细胞体积 (fL)')
    mch = db.Column(db.Float(255), info='平均血红蛋白含量 (pg)')
    mchc = db.Column(db.Float(255), info='平均血红蛋白浓度 (g/L)')
    rdw_cv = db.Column(db.Float(255), info='红细胞分布宽度-CV (%)')
    rdw_sd = db.Column(db.Float(255), info='红细胞分布宽度-SD (fL)')
    platelet_count = db.Column(db.Float(255), info='血小板计数 (×10^9/L)')
    pdw = db.Column(db.Float(255), info='血小板分布宽度 (%)')
    mpv = db.Column(db.Float(255), info='平均血小板体积 (fL)')
    neutrophil_percentage = db.Column(db.Float(255), info='中性粒细胞百分率 (%)')
    lymphocyte_percentage = db.Column(db.Float(255), info='淋巴细胞百分率 (%)')
    monocyte_percentage = db.Column(db.Float(255), info='单核细胞百分率 (%)')
    eosinophil_percentage = db.Column(db.Float(255), info='嗜酸性粒细胞百分率 (%)')
    basophil_percentage = db.Column(db.Float(255), info='嗜碱性粒细胞百分率 (%)')


class MriImage(db.Model):
    """MRI图像与相关临床指标"""
    __tablename__ = 'mri_image'

    image_id = db.Column(db.Integer, primary_key=True, unique=True, info='MRI图像标识')
    patient_id = db.Column(db.ForeignKey('patient.user_id', ondelete='SET NULL', onupdate='CASCADE'), index=True, info='图像对应的患者')
    t1_path = db.Column(db.String(80, 'utf8mb4_0900_ai_ci'), nullable=False, info='t1文件路径')
    t2_path = db.Column(db.String(80, 'utf8mb4_0900_ai_ci'), nullable=False, info='t2文件路径')
    imaging_date = db.Column(db.Date, nullable=False, info='图像拍摄日期')
    imaging_hospital = db.Column(db.String(60), info='图像拍摄机构（医院）')
    upload_date = db.Column(db.Date, nullable=False, info='上传日期')
    result = db.Column(db.Integer, info='图像识别结果')
    fibroids_present = db.Column(db.Integer, info='伴发肌瘤个数')
    avg_treatment_power = db.Column(db.Float(255), info='平均治疗功率（W）')
    total_energy = db.Column(db.Float(255), info='总能量（J）')
    treatment_volume = db.Column(db.Float(255), info='治疗体积（cc）')
    blood_routine_id = db.Column(db.ForeignKey('blood_routine.blood_routine_id', ondelete='SET NULL', onupdate='CASCADE'), index=True, info='血常规记录ID')
    parity = db.Column(db.Integer, info='产次')
    miscarriage_count = db.Column(db.Integer, info='流产次数')

    blood_routine = db.relationship('BloodRoutine', primaryjoin='MriImage.blood_routine_id == BloodRoutine.blood_routine_id', backref='mri_images')
    patient = db.relationship('Patient', primaryjoin='MriImage.patient_id == Patient.user_id', backref='mri_images')


class Report(db.Model):
    """MRI影响分析报告"""
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True, unique=True, info='报告标识')
    image_id = db.Column(db.ForeignKey('mri_image.image_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, info='MRI图像ID')
    doctor_id = db.Column(db.ForeignKey('doctor.user_id', ondelete='SET NULL', onupdate='CASCADE'), index=True, info='生成报告的医生的ID')
    roi_t1_path = db.Column(db.String(80, 'utf8mb4_0900_ai_ci'), info='ROI标注后的图像路径（t1）')
    roi_t2_path = db.Column(db.String(80, 'utf8mb4_0900_ai_ci'), info='ROI标注后的图像路径（t2）')
    radiomic_comment = db.Column(db.String(3000), info='影像学判断')
    therapy_comment = db.Column(db.String(6000), info='治疗建议')
    generation_date = db.Column(db.Date, nullable=False, info='报告生成日期')

    doctor = db.relationship('Doctor', primaryjoin='Report.doctor_id == Doctor.user_id', backref='reports')
    image = db.relationship('MriImage', primaryjoin='Report.image_id == MriImage.image_id', backref='reports')


class User(db.Model):
    """用户"""
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, unique=True, info='用户标识')
    name = db.Column(db.String(30), info='用户真实姓名')
    password = db.Column(db.String(255, 'utf8mb4_0900_ai_ci'), nullable=False, info='密文密码')
    phone_number = db.Column(db.String(11, 'utf8mb4_0900_ai_ci'), nullable=False, unique=True, info='手机号')
    user_type = db.Column(db.String(7, 'utf8mb4_0900_ai_ci'), nullable=False, info='用户类型（医生/患者）')
    is_authenticated = db.Column(db.Integer, nullable=False, info='是否通过认证')
    registration_time = db.Column(db.DateTime, nullable=False, info='注册时间')


class Doctor(User):
    """医生"""
    __tablename__ = 'doctor'

    user_id = db.Column(db.ForeignKey('user.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, info='用户标识')
    hospital = db.Column(db.String(60), info='所属医院')
    department = db.Column(db.String(60), info='所属科室')
    title = db.Column(db.String(30), info='职称')


class Patient(User):
    """患者"""
    __tablename__ = 'patient'

    user_id = db.Column(db.ForeignKey('user.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, unique=True, info='用户标识')
    doctor_id = db.Column(db.ForeignKey('doctor.user_id', ondelete='SET NULL', onupdate='CASCADE'), index=True, info='负责该患者的医生ID')
    age = db.Column(db.Integer, info='年龄')
    gender = db.Column(db.Integer, info='性别')

    doctor = db.relationship('Doctor', primaryjoin='Patient.doctor_id == Doctor.user_id', backref='patients')
