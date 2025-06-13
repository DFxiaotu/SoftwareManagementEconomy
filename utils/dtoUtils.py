from utils.jsonUtils import to_dict

# DTO字段定义
PATIENT_INFO = ('user_id', 'name', 'age', 'gender')
DOCTOR_INFO = ('user_id', 'name', 'hospital', 'department', 'title')
CLINICAL_INDICATORS = (
    'fibroids_present',
    'avg_treatment_power',
    'total_energy',
    'treatment_volume',
    'parity',
    'miscarriage_count'
)
MRI_ABSTRACT = ('image_id', 'result')
REPORT_CONTENT = (
    'image_id',
    'doctor_id',
    'radiomic_comment',
    'therapy_comment',
    'generation_date'
)
REPORT_ABSTRACT = ('report_id', 'generation_date')


def get_doctor_info(doctor):
    """从医生记录中提取患者可见的信息"""
    return to_dict(doctor, require=DOCTOR_INFO)


def get_patient_info(patient):
    """从患者记录中提取医生可见的信息"""
    return to_dict(patient, require=PATIENT_INFO)


def get_clinical_indicators(mri):
    """从MRI图像记录中提取血常规对象"""
    indicators = to_dict(mri, require=CLINICAL_INDICATORS)
    indicators['bloodRoutine'] = to_dict(mri.blood_routine, ignore=('blood_routine_id',))
    return indicators


def get_mri_abstract(mri):
    """从MRI图像记录中提取MRI图像概要（包括封面图）"""
    abstract = to_dict(mri, require=MRI_ABSTRACT)

    # 这个abstract是一个需要和封面图一起返回的字典，把取封面图和返回所有数据的代码放这即可。取封面图的过程如有必要可以在fileUtils里定义工具函数。
    # 这个return语句只是示例，可以按需求改。
    return abstract


def get_report_content(report):
    """从报告记录中提取报告详细内容"""
    content = to_dict(report, require=REPORT_CONTENT)
    content['doctorName'] = report.doctor.name
    content['result'] = report.image.result
    content['clinicalIndicators'] = get_clinical_indicators(report.image)

    return content


def get_report_abstract(report):
    """从报告记录中提取报告简略信息"""
    abstract = to_dict(report, require=REPORT_ABSTRACT)
    abstract['result'] = report.image.result
    abstract['clinicalIndicators'] = get_clinical_indicators(report.image)

    return abstract
