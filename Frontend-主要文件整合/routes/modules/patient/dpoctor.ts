import type { RouteRecordRaw } from 'vue-router';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/patient/pdoctor',
    name: 'pdoctor',
    meta: {
      title: '主管医生',
      icon: 'ant-design:team-outlined'
    },
    component: () => import('@/views/patient/doctor/index.vue')
  }
];

export default routes; 