// @ts-ignore
/* eslint-disable */

/**
 * 该文件为 @umijs/openapi 插件自动生成，请勿随意修改。如需修改请通过配置 openapi.config.ts 进行定制化。
 * */

import { request, type RequestOptions } from '@/utils/request';

/** 登录 POST /auth/login */
export async function authLogin(data: API.LoginDto, options?: RequestOptions) {
  return request<API.LoginResponse>('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data,
    isReturnResult: false,
    ...(options || {}),
  });
}

/** 注册 POST /auth/register */
export async function authRegister(data: API.RegisterDto, options?: RequestOptions) {
  return request('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data,
    isReturnResult: false,
    ...(options || {}),
  });
}

/** 医生认证 POST /auth/authenticate/doctor */
export async function authAuthenticateDoctor(data: API.AuthenticateDoctorDto, options?: RequestOptions) {
  return request('/auth/authenticate/doctor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data,
    isReturnResult: false,
    ...(options || {}),
  });
}

/** 患者认证 POST /auth/authenticate/patient */
export async function authAuthenticatePatient(data: API.AuthenticatePatientDto, options?: RequestOptions) {
  return request('/auth/authenticate/patient', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    data,
    isReturnResult: false,
    ...(options || {}),
  });
}


/** 重置认证状态 PATCH /auth/resetAuth/<userId> */
export async function authResetAuth(userId: number, options?: RequestOptions) {
  return request(`/auth/resetAuth/${userId}`, {
    method: 'PATCH',
    isReturnResult: false,
    ...(options || {}),
  })
};
