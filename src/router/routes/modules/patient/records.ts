import type { RouteRecordRaw } from 'vue-router';
import { t } from '@/hooks/useI18n';

const moduleName = 'records';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/records',
    name: moduleName,
    meta: {
      title: t('routes.patient.records'),
      icon: 'ant-design:line-chart-outlined'
    },
    component: () => import('@/views/patient/records/index.vue')
  }
];

export default routes;
