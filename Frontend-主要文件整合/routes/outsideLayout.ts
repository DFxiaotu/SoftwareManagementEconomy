import type { RouteRecordRaw } from 'vue-router';
import { LOGIN_NAME, REGISTER_NAME, AUTH_NAME } from '@/router/constant';

/**
 * layout布局之外的路由
 */
export const LoginRoute: RouteRecordRaw = {
  path: '/login',
  name: LOGIN_NAME,
  component: () => import('@/views/login/index.vue'),
  meta: {
    title: '登录',
    hideInMenu: true,
    hideInTabs: true,
  },
};

export const RegisterRoute: RouteRecordRaw = {
  path: '/register',
  name: REGISTER_NAME,
  component: () => import('@/views/register/index.vue'),
  meta: {
    title: '注册',
    hideInMenu: true,
    hideInTabs: true,
  },
};

export const AuthRoute: RouteRecordRaw = {
  path: '/auth',
  name: AUTH_NAME,
  component: () => import('@/views/auth/index.vue'),
  meta: {
    title: '认证',
    hideInMenu: true,
    hideInTabs: true,
  },
};

export default [LoginRoute, RegisterRoute, AuthRoute];
