<template>
  <div class="page-container">
    <div>
      <h1>404</h1>
      <h1>OOPS！你好像走丢了...</h1>
      <RouterLink :to="to" class="ant-btn ant-btn-primary">回到首页</RouterLink>
    </div>
    <img src="@/assets/404.gif" alt="" />
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref } from 'vue';
  import { useUserStore } from '@/store/modules/user';
  export default defineComponent({
    name: 'NotFound',
    setup() {
      const userStore = useUserStore();
      const route = `/${userStore.getUserType()}`;
      const to = ref({ path: route, replace: true });
      return {
        to,
      };
    },
  });
</script>

<style lang="less" scoped>
  .page-container {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    background-color: white;
  }
</style>
