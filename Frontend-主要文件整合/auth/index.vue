<template>
  <div class="auth-box">
    <div class="auth-logo">
      <img src="~@/assets/images/logo.png" width="45" />
      <h1 class="mb-0 ml-2 text-3xl font-bold">MRI海扶疗效评估系统</h1>
    </div>

    <h2 v-if="userType === 'doctor' || userType === 'patient'" class="auth-notice"
      >您还未实名认证，请先完成认证！</h2
    >
    <h2 v-else class="auth-notice">本系统只对医生和患者开放！</h2>

    <a-form layout="horizontal" :model="authFormModel" @submit.prevent="handleAuth">
      <a-form-item v-if="userType === 'doctor'">
        <a-input v-model:value="authFormModel.realName" size="large" placeholder="真实姓名">
          <template #prefix><Icon icon="ant-design:user-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'doctor'">
        <a-input v-model:value="authFormModel.hospital" size="large" placeholder="所属医院">
          <template #prefix><Icon icon="ant-design:home-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'doctor'">
        <a-input v-model:value="authFormModel.department" size="large" placeholder="部门">
          <template #prefix><Icon icon="ant-design:appstore-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'doctor'">
        <a-input v-model:value="authFormModel.title" size="large" placeholder="职称">
          <template #prefix><Icon icon="ant-design:solution-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'doctor'">
        <a-upload
          list-type="picture"
          :show-upload-list="true"
          :max-count="1"
          :before-upload="handleFileUpload(authFormModel.licensePhoto)"
        >
          <a-button><Icon icon="ant-design:upload-outlined" />上传执业医师证照片</a-button>
          <p class="upload-notice">请上传带有身份信息一面的清晰照片</p>
          <img
            v-if="authFormModel.licensePhoto"
            :src="authFormModel.licensePhoto"
            alt="执业医师证照片"
            class="uploaded-image"
          />
        </a-upload>
      </a-form-item>

      <a-form-item v-if="userType === 'patient'">
        <a-input v-model:value="authFormModel.realName" size="large" placeholder="真实姓名">
          <template #prefix><Icon icon="ant-design:user-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'patient'">
        <a-input
          v-model:value="authFormModel.age"
          size="large"
          placeholder="年龄"
          type="number"
          min="1"
          max="150"
        >
          <template #prefix><Icon icon="ant-design:number-outlined" /></template>
        </a-input>
      </a-form-item>
      <a-form-item v-if="userType === 'patient'">
        <a-select v-model:value="authFormModel.gender" size="large" placeholder="性别">
          <a-select-option :value="true">男</a-select-option>
          <a-select-option :value="false">女</a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item v-if="userType === 'patient'">
        <a-upload
          list-type="picture"
          :show-upload-list="true"
          :max-count="1"
          :before-upload="handleFileUpload(authFormModel.idCardPhoto)"
        >
          <a-button><Icon icon="ant-design:upload-outlined" />上传身份证照片</a-button>
          <p class="upload-notice">请上传带有身份信息一面的清晰照片</p>
          <img
            v-if="authFormModel.idCardPhoto"
            :src="authFormModel.idCardPhoto"
            alt="身份证照片"
            class="uploaded-image"
          />
        </a-upload>
      </a-form-item>

      <a-form-item v-if="userType === 'doctor' || userType === 'patient'">
        <a-button type="primary" html-type="submit" size="large" :loading="loading" block>
          提交认证
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useRouter, useRoute } from 'vue-router';
  import { message, Modal } from 'ant-design-vue';
  import { Icon } from '@/components/basic/icon';
  import { useUserStore } from '@/store/modules/user';
  import { to } from '@/utils/awaitTo';

  const router = useRouter();
  const route = useRoute();
  const userStore = useUserStore();

  const userType = ref(userStore.getUserType());
  const userId = ref(userStore.userInfo.userId);
  const loading = ref(false);
  const authFormModel = ref({
    realName: '',
    hospital: '',
    department: '',
    title: '',
    age: 0,
    gender: false,
    licensePhoto: '',
    idCardPhoto: '',
  });
  const hasFileUploaded = ref(false);

  const handleFileUpload = (field: string) => (file: File) => {
    const reader = new FileReader();
    reader.onload = (e: ProgressEvent<FileReader>) => {
      authFormModel.value[field] = e.target?.result as string;
    };
    reader.readAsDataURL(file);
    hasFileUploaded.value = true;
    return false; // 阻止默认上传行为
  };

  const handleAuth = async () => {
    const { realName, hospital, department, title, age } = authFormModel.value;

    if (!realName.trim()) {
      message.error('真实姓名不能为空！');
      return;
    }
    if (userType.value === 'doctor' && (!hospital.trim() || !department.trim() || !title.trim())) {
      message.error('请完整填写医生认证信息！');
      return;
    }
    if (userType.value === 'patient' && age === 0) {
      message.error('请完整填写患者认证信息！');
      return;
    }
    if (!hasFileUploaded.value) {
      message.error('请上传证件照片！');
    }

    loading.value = true;
    message.loading('提交认证中...', 0);

    const authDoctorForm = {
      userId: Number(userId.value),
      realName: authFormModel.value.realName,
      hospital: authFormModel.value.hospital,
      department: authFormModel.value.department,
      title: authFormModel.value.title,
    };
    const authPatientForm = {
      userId: Number(userId.value),
      realName: authFormModel.value.realName,
      age: Number(authFormModel.value.age),
      gender: Boolean(authFormModel.value.gender),
    };

    console.log(authPatientForm);

    // 执行认证请求逻辑
    const [err] = await to(
      userType.value === 'doctor'
        ? userStore.authenticateDoctor(authDoctorForm)
        : userStore.authenticatePatient(authPatientForm),
    );

    if (err) {
      message.destroy();
      Modal.error({
        title: () => '提示',
        content: () => err.message,
      });
    } else {
      message.destroy();
      message.success('认证成功！');
      setTimeout(() =>
        router.replace((route.query.redirect as string) || `/${userStore.getUserType()}`),
      );
    }
    loading.value = false;
  };
</script>

<style lang="less" scoped>
  .auth-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100vw;
    height: 100vh;
    padding-top: 240px;
    background: url('@/assets/login.svg');
    background-size: 100%;

    .auth-logo {
      display: flex;
      align-items: center;
      margin-bottom: 30px;

      .svg-icon {
        font-size: 48px;
      }
    }

    .auth-notice {
      font-weight: bold;
      color: red;
      margin-bottom: 20px;
    }

    .upload-notice {
      font-size: 16px;
      font-style: italic;
      color: gray;
      margin-top: 10px;
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
