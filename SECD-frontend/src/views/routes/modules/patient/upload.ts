import type { RouteRecordRaw } from 'vue-router';
import { t } from '@/hooks/useI18n';

const moduleName = 'upload';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/upload',
    name: moduleName,
    meta: {
      title: t('routes.patient.upload'),
      icon: 'ant-design:upload-outlined'
    },
    component: () => import('@/views/patient/upload/index.vue')
  }
];

export default routes;
