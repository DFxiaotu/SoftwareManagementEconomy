import { ref } from 'vue';
import { defineStore } from 'pinia';
import { useLockscreenStore } from './lockscreen';
import { useSSEStore } from './sse';
import { useTabsViewStore } from './tabsView';
import type { RouteRecordRaw } from 'vue-router';
import { store } from '@/store';
import Api from '@/api/';
import { resetRouter } from '@/router';
import { generateDynamicRoutes } from '@/router/helper/routeHelper';

export const useUserStore = defineStore(
  'user',
  () => {
    const sseStore = useSSEStore();
    const lockscreenStore = useLockscreenStore();
    const tabsViewStore = useTabsViewStore();
    const token = ref<string>();
    const menus = ref<RouteRecordRaw[]>([]);
    const userInfo = ref<Partial<API.UserEntity>>({});

    const sortMenus = (menus: RouteRecordRaw[] = []) => {
      return menus
        .filter((n) => {
          const flag = !n.meta?.hideInMenu;
          if (flag && n.children?.length) {
            n.children = sortMenus(n.children);
          }
          return flag;
        })
        .sort((a, b) => ~~Number(a.meta?.orderNo) - ~~Number(b.meta?.orderNo));
    };

    /** 清空登录态(token、userInfo...) */
    const clearLoginStatus = () => {
      token.value = '';
      menus.value = [];
      userInfo.value = {};
      resetRouter();
      setTimeout(() => {
        localStorage.clear();
      });
    };
    /** 登录成功保存token */
    const setToken = (_token: string) => {
      token.value = _token;
    };
    /** 登录 */
    const login = async (params: API.LoginDto) => {
      const data = await Api.auth.authLogin(params);
      console.log(data);

      if (data.code == 200) {
        setToken(data.token);
        userInfo.value = data.data;
        console.log(userInfo.value);
        await fetchMenus();
        lockscreenStore.setLock(false);
        lockscreenStore.saveLoginPwd(params.password);
      } else {
        return Promise.reject(data.message);
      }
    };
    /** 获取菜单 */
    const fetchMenus = async () => {
      const result = generateDynamicRoutes(getUserType());
      menus.value = sortMenus(result);
    };
    /** 登出 */
    const logout = async () => {
      // await Api.account.accountLogout();
      sseStore.closeEventSource();
      tabsViewStore.closeAllTabs();
      clearLoginStatus();
    };
    /** 注册 */
    const register = async (params: API.RegisterDto) => {
      const data = await Api.auth.authRegister(params);
      console.log(data);

      if (data.code != 201) {
        return Promise.reject(data.message);
      }
    };
    /** 获取用户类型 */
    const getUserType = () => {
      const userType = userInfo.value.userType;

      if (userType == 'doctor' || userType == 'patient') {
        return userType;
      } else {
        return 'unknown';
      }
    };
    /** 检查认证状态 */
    const checkAuth = () => {
      return userInfo.value.isAuthenticated;
    };
    /** 重置认证状态 */
    const resetAuth = async () => {
      const data = await Api.auth.authResetAuth(Number(userInfo.value.userId));
      console.log(data);

      if (data.code == 200) {
        userInfo.value.isAuthenticated = false;
      } else {
        return Promise.reject(data.message);
      }
    };
    /** 医生认证 */
    const authenticateDoctor = async (params: API.AuthenticateDoctorDto) => {
      const data = await Api.auth.authAuthenticateDoctor(params);
      console.log(data);

      if (data.code == 200) {
        // 本地同步认证标志
        userInfo.value.isAuthenticated = true;
      } else {
        return Promise.reject(data.message);
      }
    };
    /** 患者认证 */
    const authenticatePatient = async (params: API.AuthenticatePatientDto) => {
      const data = await Api.auth.authAuthenticatePatient(params);
      console.log(data);

      if (data.code == 200) {
        // 本地同步认证标志
        userInfo.value.isAuthenticated = true;
      } else {
        return Promise.reject(data.message);
      }
    };

    return {
      token,
      menus,
      userInfo,
      login,
      logout,
      clearLoginStatus,
      fetchMenus,
      register,
      getUserType,
      checkAuth,
      resetAuth,
      authenticateDoctor,
      authenticatePatient,
    };
  },
  {
    persist: {
      pick: ['token'],
    },
  },
);

// 在组件setup函数外使用
export function useUserStoreWithOut() {
  return useUserStore(store);
}
