import type { RouteRecordRaw } from 'vue-router';
import { t } from '@/hooks/useI18n';

const moduleName = 'doctor';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/doctor/manage',
    name: `${moduleName}-manage`,
    meta: {
      title: t('routes.doctor.manage'),
      icon: 'ant-design:usergroup-add-outlined',
    },
    component: () => import('@/views/doctor/manage/index.vue'),
  },
];

export default routes;
