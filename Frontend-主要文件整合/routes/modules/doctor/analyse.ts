import type { RouteRecordRaw } from 'vue-router';
import { t } from '@/hooks/useI18n';

const moduleName = 'doctor';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/doctor/analyse',
    name: `${moduleName}-analyse`,
    meta: {
      title: t('routes.doctor.analyse'),
      icon: 'ant-design:file-image-outlined',
    },
    component: () => import('@/views/doctor/analyse/index.vue'),
  },
  {
    path: '/doctor/analyse/upload/:id',
    name: `${moduleName}-analyse-upload`,
    component: () => import('@/views/doctor/analyse/upload.vue'),
    meta: {
      title: '上传影像',
      hideInMenu: true
    }
  },
  {
    path: '/doctor/analyse/detail/:id',
    name: `${moduleName}-analyse-detail`,
    component: () => import('@/views/doctor/analyse/detail.vue'),
    meta: {
      title: '影像详情',
      hideInMenu: true
    }
  },
  {
    path: '/doctor/analyse/edit/:reportId',
    name: `${moduleName}-analyse-edit`,
    component: () => import('@/views/doctor/analyse/edit.vue'),
    meta: {
      title: '编辑切片',
      hideInMenu: true
    }
  }
];

export default routes;
