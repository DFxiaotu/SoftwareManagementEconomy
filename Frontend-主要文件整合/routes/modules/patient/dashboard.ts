import type { RouteRecordRaw } from 'vue-router';

const moduleName = 'dashboard';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/dashboard',
    name: moduleName,
    meta: {
      title: '患者总览',
      icon: 'ant-design:dashboard-outlined',
    },
    component: () => import('@/views/patient/dashboard/index.vue'),
  },
];

export default routes;
