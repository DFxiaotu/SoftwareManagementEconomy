import type { RouteRecordRaw } from 'vue-router';

const moduleName = 'account';

const routes: Array<RouteRecordRaw> = [
  {
    path: '/account',
    name: moduleName,
    meta: {
      title: '个人中心',
      icon: 'ant-design:user-outlined',
    },
    component: () => import('@/views/account/index.vue'),
  },
];

export default routes;
