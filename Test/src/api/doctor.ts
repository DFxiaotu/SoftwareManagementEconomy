import { request } from '@/utils/request';

export function getDoctorInfo(params: { doctorId: number | undefined }) {
  return request({
    url: `/person/doctor/select/${params.doctorId}`,
    method: 'get'
  });
}

export function getPatientList(params: { doctorId: number | undefined }) {
  return request({
    url: `/manage/${params.doctorId}/all`,
    method: 'get'
  });
}

export function getPatientInfo(params: { patientId: number | undefined }) {
  return request({
    url: `/person/patient/select/${params.patientId}`,
    method: 'get'
  });
}

export function getPatientInfoByName(params: { patientName: string, patientPhone: string }) {
  return request({
    url: `/person/patient/search`,
    method: 'get',
    params: {
      name: params.patientName,
      phoneNumber: params.patientPhone
    }
  });
}

export function addPatient(params: { doctorId: number | undefined, patientId: number | undefined }) {
  return request({
    url: `/manage/${params.doctorId}/add?patient_id=${params.patientId}`,
    method: 'patch'
  });
}

export function removePatient(params: { doctorId: number | undefined, patientId: number | undefined }) {
  return request({
    url: `/manage/${params.doctorId}/remove?patient_id=${params.patientId}`,
    method: 'patch'
  });
}

export function getLastReportData(params: {patientId: number | undefined }) {
  return request({
    url: `/report/last`,
    method: 'get',
    params: {
      patientId: params.patientId
    }
  });
}

export function editReport(params: {reportId: number | undefined}){
  return request({
    url: `/analyse/edit/${params.reportId}`,
    method: 'post'
  });
}

export function uploadMriImage(patientId: string, data: FormData) {
  return request({
    url: `/mri/upload/${patientId}`,
    method: 'POST',
    data
  });
}

export function getAllMRIDetails(patientId: number) {
  console.log('Requesting MRI details for patient:', patientId);
  return request({
    url: `/mri/all/${patientId}`,
    method: 'get',
    timeout: 120000,
    isReturnResult: false
  });
}

export function getPeriodMRIDetails(patientId: number, startDate: string, endDate: string) {
  return request({
    url: `/mri/period/${patientId}`,
    method: 'get',
    params: {
      startDate,
      endDate
    },
    timeout: 60000,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

export function getMRIDetails(imageId: number) {
  console.log('Requesting specific MRI details:', imageId);
  return request({
    url: `/mri/details/${imageId}`,
    method: 'get',
    timeout: 120000,
    isReturnResult: false
  });
}

export function getPeriodClinicalData(patientId: number, startDate: string, endDate: string, indicatorType: string) {
  return request({
    url: `/mri/clinical/${patientId}`,
    method: 'get',
    params: {
      startDate,
      endDate,
      indicatorType
    }
  });
}

export function analyseReport(params: {imageId: number | undefined}){
  return request({
    url: `/mri/analyse/${params.imageId}`,
    method: 'get'
  });
}

export function generateReport(data: FormData) {
  return request({
    url: '/report/generate',
    method: 'POST',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

// 上传 MRI 临床数据（包含血常规数据）
export function uploadMriClinicalData(imageId: string, data: any) {
  console.log("upload data", data);
  return request({
    url: `/mri/upload/all/${imageId}`,
    method: 'POST',
    data,
    transformRequest: [(data) => {
      console.log('Request data:', data);
      return JSON.stringify(data);
    }],
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

export function getReport(params: {imageId: number}){
  return request({
    url: `/report/ofImage`,
    method: 'get',
    params: {
      imageId: params.imageId
    }
  });
}


