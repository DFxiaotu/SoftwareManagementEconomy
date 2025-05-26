<template>
  <div class="login-box">
    <div class="login-logo">
      <!-- <svg-icon name="logo" :size="45" /> -->
      <img src="~@/assets/images/logo.png" width="45" />
      <h1 class="mb-0 ml-2 text-3xl font-bold">MRI海扶疗效评估系统</h1>
    </div>
    <a-form layout="horizontal" :model="loginFormModel" @submit.prevent="handleSubmit">
      <a-form-item>
        <a-input v-model:value="loginFormModel.phoneNumber" size="large" placeholder="手机号">
          <template #prefix> <Icon icon="ant-design:mobile-outlined" /> </template>
        </a-input>
      </a-form-item>
      <a-form-item>
        <a-input
          v-model:value="loginFormModel.password"
          size="large"
          type="password"
          placeholder="密码"
          autocomplete="new-password"
        >
          <template #prefix> <Icon icon="ant-design:lock-outlined" /></template>
        </a-input>
      </a-form-item>
      <!-- <a-form-item>
        <a-input
          v-model:value="loginFormModel.verifyCode"
          placeholder="验证码"
          :maxlength="4"
          size="large"
        >
          <template #prefix> <Icon icon="ant-design:safety-outlined" /> </template>
          <template #suffix>
            <img
              :src="captcha"
              class="absolute right-0 h-full cursor-pointer"
              @click="updateCaptcha"
            />
          </template>
        </a-input>
      </a-form-item> -->
      <a-form-item>
        <a-button type="primary" html-type="submit" size="large" :loading="loading" block>
          登录
        </a-button>
      </a-form-item>
      <a-form-item>
        <a-button type="link" block @click="goToRegister">没有账号？点击注册</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useRoute, useRouter } from 'vue-router';
  import { message, Modal } from 'ant-design-vue';
  import { Icon } from '@/components/basic/icon';
  import { useUserStore } from '@/store/modules/user';
  // import Api from '@/api/';
  import { to } from '@/utils/awaitTo';

  const route = useRoute();
  const router = useRouter();
  const userStore = useUserStore();

  const loading = ref(false);
  // const captcha = ref('');
  const loginFormModel = ref({
    phoneNumber: '',
    password: '',
    // captchaId: '',
    // verifyCode: '',
  });

  // const updateCaptcha = async () => {
  //   const data = await Api.captcha.captchaCaptchaByImg({ width: 100, height: 50 });
  //   captcha.value = data.img;
  //   loginFormModel.value.captchaId = data.id;
  // };
  // updateCaptcha();

  const handleSubmit = async () => {
    const { phoneNumber, password } = loginFormModel.value;
    if (phoneNumber.trim() == '' || password.trim() == '') {
      return message.warning('手机号或密码不能为空！');
    }
    message.loading('登录中...', 0);
    loading.value = true;
    console.log(loginFormModel.value);

    const [err] = await to(userStore.login(loginFormModel.value));

    if (err) {
      message.destroy();
      Modal.error({
        title: () => '提示',
        content: () => err.message,
      });
      // updateCaptcha();
    } else {
      message.destroy();
      message.success('登录成功！');
      setTimeout(() =>
        router.replace((route.query.redirect as string) || `/${userStore.getUserType()}`),
      );
    }
    loading.value = false;
  };

  const goToRegister = () => {
    router.push('/register');
  };
</script>

<style lang="less" scoped>
  .login-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100vw;
    height: 100vh;
    padding-top: 240px;
    background: url('@/assets/login.svg');
    background-size: 100%;

    .login-logo {
      display: flex;
      align-items: center;
      margin-bottom: 30px;

      .svg-icon {
        font-size: 48px;
      }
    }

    :deep(.ant-form) {
      width: 400px;

      .ant-col {
        width: 100%;
      }

      .ant-form-item-label {
        padding-right: 6px;
      }
    }
  }
</style>
