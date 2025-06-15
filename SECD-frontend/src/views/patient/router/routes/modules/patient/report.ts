import type { RouteRecordRaw } from 'vue-router';

const moduleName = 'report';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/report',
    name: moduleName,
    meta: {
      title: '检查报告',
      icon: 'ant-design:file-text-outlined'
    },
    component: () => import('@/views/patient/report/index.vue'),
  }
];

export default routes;
