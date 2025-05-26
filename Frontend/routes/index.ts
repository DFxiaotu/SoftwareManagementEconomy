import outsideLayout from './outsideLayout';
import basic from './basic';
import type { RouteRecordRaw } from 'vue-router';

export const basicRoutes: Array<RouteRecordRaw> = [
  // Layout之外的路由
  ...outsideLayout,
  // 基础路由
  ...basic,
];
