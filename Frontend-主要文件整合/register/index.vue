<template>
  <div class="register-box">
    <div class="register-logo">
      <img src="~@/assets/images/logo.png" width="45" />
      <h1 class="mb-0 ml-2 text-3xl font-bold">MRI海扶疗效评估系统</h1>
    </div>
    <a-form layout="horizontal" :model="registerFormModel" @submit.prevent="handleRegister">
      <a-form-item>
        <a-input v-model:value="registerFormModel.phoneNumber" size="large" placeholder="手机号">
          <template #prefix> <Icon icon="ant-design:mobile-outlined" /> </template>
        </a-input>
      </a-form-item>
      <a-form-item>
        <a-input
          v-model:value="registerFormModel.password"
          size="large"
          type="password"
          placeholder="密码"
          autocomplete="new-password"
        >
          <template #prefix> <Icon icon="ant-design:lock-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item>
        <a-input
          v-model:value="registerFormModel.confirmPassword"
          size="large"
          type="password"
          placeholder="确认密码"
          autocomplete="new-password"
        >
          <template #prefix> <Icon icon="ant-design:lock-outlined" /></template>
        </a-input>
      </a-form-item>
      <!-- <a-form-item>
        <a-input
          v-model:value="registerFormModel.verifyCode"
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
      <div class="register-button-box">
        <a-form-item class="register-button">
          <a-button
            id="doctor"
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            医生注册
          </a-button>
        </a-form-item>
        <a-form-item class="register-button">
          <a-button
            id="patient"
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            患者注册
          </a-button>
        </a-form-item>
      </div>
      <!-- 返回登录按钮 -->
      <a-form-item>
        <a-button type="link" block @click="goToLogin">已有账号？点击登录</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { message, Modal } from 'ant-design-vue';
  import { Icon } from '@/components/basic/icon';
  import { useUserStore } from '@/store/modules/user';
  // import Api from '@/api/';
  import { to } from '@/utils/awaitTo';

  const router = useRouter();
  const userStore = useUserStore();

  const loading = ref(false);
  // const captcha = ref('');
  const registerFormModel = ref({
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    // captchaId: '',
    // verifyCode: '',
  });

  // const updateCaptcha = async () => {
  //   const data = await Api.captcha.captchaCaptchaByImg({ width: 100, height: 50 });
  //   captcha.value = data.img;
  //   registerFormModel.value.captchaId = data.id;
  // };
  // updateCaptcha();

  const handleRegister = async (event) => {
    // 注册逻辑（如手机号、密码验证）
    const { phoneNumber, password, confirmPassword } = registerFormModel.value;
    if (phoneNumber.trim() == '' || password.trim() == '') {
      message.error('手机号或密码不能为空！');
      return;
    }
    if (password !== confirmPassword) {
      message.error('密码和确认密码不一致！');
      return;
    }
    message.loading('注册中...', 0);
    loading.value = true;

    const userType = event.submitter.__vnode.props.id;
    const registerForm = {
      phoneNumber,
      password,
      userType,
    };

    // 执行注册逻辑
    const [err] = await to(userStore.register(registerForm));

    if (err) {
      message.destroy();
      Modal.error({
        title: () => '提示',
        content: () => err.message,
      });
      // updateCaptcha();
    } else {
      message.destroy();
      message.success('注册成功！');
      setTimeout(() => router.replace('/login'));
    }
    loading.value = false;
  };

  const goToLogin = () => {
    router.replace('/login');
  };
</script>

<style lang="less" scoped>
  .register-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100vw;
    height: 100vh;
    padding-top: 240px;
    background: url('@/assets/login.svg');
    background-size: 100%;

    .register-logo {
      display: flex;
      align-items: center;
      margin-bottom: 30px;

      .svg-icon {
        font-size: 48px;
      }
    }

    .register-button-box {
      display: flex;
    }

    .register-button {
      flex: 1;
      margin: 0 10px;
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
