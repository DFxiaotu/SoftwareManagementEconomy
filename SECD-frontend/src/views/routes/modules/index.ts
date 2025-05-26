import type { RouteRecordRaw } from 'vue-router';

export const doctorRootRoute: RouteRecordRaw = {
  path: '/doctor',
  name: 'DoctorLayout',
  redirect: '/doctor/manage',
  component: () => import('@/layout/index.vue'),
  meta: {
    title: '医生界面根路由',
  },
  children: [],
};

export const patientRootRoute: RouteRecordRaw = {
  path: '/patient',
  name: 'PatientLayout',
  redirect: '/patient/dashboard',
  component: () => import('@/layout/index.vue'),
  meta: {
    title: '患者界面根路由',
  },
  children: [],
};
