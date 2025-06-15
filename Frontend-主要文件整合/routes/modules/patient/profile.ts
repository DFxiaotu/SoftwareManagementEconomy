import type { RouteRecordRaw } from 'vue-router';
import { t } from '@/hooks/useI18n';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/profile',
    name: 'profile',
    meta: {
      title: t('routes.patient.profile'),
      icon: 'ant-design:user-outlined',
    },
    component: () => import('@/views/patient/profile/index.vue'),
  },
];

export default routes;
