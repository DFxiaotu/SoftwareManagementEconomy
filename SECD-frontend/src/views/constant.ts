export const LOGIN_NAME = 'Login';

export const REGISTER_NAME = 'Register';

export const REDIRECT_NAME = 'Redirect';

export const AUTH_NAME = 'Auth';

export const DOCTOR_ROOT_NAME = 'DoctorRoot';

export const PATIENT_ROOT_NAME = 'PatientRoot';

export const PAGE_NOT_FOUND_NAME = 'PageNotFound';

// 路由白名单
export const whiteNameList = [
  LOGIN_NAME,
  REGISTER_NAME,
  DOCTOR_ROOT_NAME,
  PATIENT_ROOT_NAME,
  'icons',
  'error',
  'error-404',
] as const; // no redirect whitelist

export type WhiteNameList = typeof whiteNameList;

export type WhiteName = (typeof whiteNameList)[number];
