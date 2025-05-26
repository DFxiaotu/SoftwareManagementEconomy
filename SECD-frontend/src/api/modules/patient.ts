import { request } from '@/utils/request';

// MRI图像相关接口
// 上传MRI图像
export function uploadMriImage(patientId: string, data: FormData) {
  return request({
    url: `/mri/upload/${patientId}`,
    method: 'POST',
    data,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}

// 获取MRI图像详情
export function getMRIDetails(imageId: string) {
  return request({
    url: '/mri/details',  // 根据接口文档修改路径
    method: 'GET',
    params: { imageId }
  });
}

// 获取某时间段内的临床指标
export function getClinicalIndicators(patientId: string, startDate: string, endDate: string, indicatorType: string) {
  return request({
    url: `/mri/clinical/${patientId}`,  // 根据接口文档修改路径
    method: 'GET',
    params: { startDate, endDate, indicatorType }
  });
}

// 报告相关接口
// 获取患者最近一份报告的粗略信息
export function getLastReport(patientId: string) {
  return request({
    url: '/report/last',  // 根据接口文档修改路径
    method: 'GET',
    params: { patientId }
  });
}

// 获取患者所有报告的粗略信息
export function getAllReports(patientId: string) {
  return request({
    url: '/report/all',  // 根据接口文档修改路径
    method: 'GET',
    params: { patientId }
  });
}

// 获取某一份报告的详细内容
export function getReportDetail(reportId: string) {
  return request({
    url: `/report/detail/${reportId}`,  // 根据接口文档修改路径
    method: 'GET'
  });
}

// 获取MRI图像对应的分析报告
export function getReportOfImage(imageId: string) {
  return request({
    url: '/report/ofImage',  // 根据接口文档修改路径
    method: 'GET',
    params: { imageId }
  });
}

// 获取所有患者基本信息
export function getAllPatients() {
  return request({
    url: '/person/patient/all',  // 根据接口文档修改路径
    method: 'GET'
  });
}

// 根据患者ID获取患者基本信息
export function getPatientInfo(patientId: string) {
  return request({
    url: `/person/patient/select/${patientId}`,  // 根据接口文档修改路径
    method: 'GET'
  });
}

// 根据患者ID获取主管医生基本信息
export function getChargeDoctor(patientId: string) {
  return request({
    url: '/person/doctor/charge',  // 根据接口文档修改路径
    method: 'GET',
    params: { patient_id: patientId }
  });
}

// 根据医生ID获取医生基本信息
export function getDoctorInfo(doctorId: string) {
  return request({
    url: `/person/doctor/select/${doctorId}`,  // 根据接口文档修改路径
    method: 'GET'
  });
}

// ... 其他接口保持不变 ...

// 上传 MRI 临床数据（包含血常规数据）
export function uploadMriClinicalData(imageId: string, data: {
  imagingDate: string;
  imagingHospital: string;
  result: number;
  fibroidsPresent: number;
  avgTreatmentPower: number;
  totalEnergy: number;
  treatmentVolume: number;
  parity: number;
  miscarriageCount: number;
  wbcCount: number;
  basophilAbsolute: number;
  eosinophilAbsolute: number;
  neutrophilAbsolute: number;
  lymphocyteAbsolute: number;
  monocyteAbsolute: number;
  rbcCount: number;
  hemoglobin: number;
  hematocrit: number;
  mcv: number;
  mch: number;
  mchc: number;
  rdwCv: number;
  rdwSd: number;
  plateletCount: number;
  pdw: number;
  mpv: number;
  neutrophilPercentage: number;
  lymphocytePercentage: number;
  monocytePercentage: number;
  eosinophilPercentage: number;
  basophilPercentage: number;
}) {
  return request({
    url: `/mri/upload/all/${imageId}`,
    method: 'POST',
    data
  });
}
