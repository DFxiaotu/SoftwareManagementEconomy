<template>
  <div class="profile-box">
    <div class="profile-avatar">
      <img
        v-if="userType === 'doctor'"
        src="~@/assets/images/doctor-avatar.png"
        alt="头像"
        class="avatar-image"
      />
      <img
        v-else-if="userType === 'patient' && profileData.gender"
        src="~@/assets/images/patient-avatar-male.png"
        alt="头像"
        class="avatar-image"
      />
      <img
        v-else-if="userType === 'patient'"
        src="~@/assets/images/patient-avatar-female.png"
        alt="头像"
        class="avatar-image"
      />
      <div v-else>
        <p class="incorrect-type">用户类型不正确！请先进行认证</p>
        <a-button type="primary" size="large" @click="redirectToAuth">实名认证</a-button>
      </div>
    </div>

    <div v-if="userType === 'doctor' || userType === 'patient'" class="profile-info">
      <a-descriptions title="个人信息" bordered :column="1">
        <a-descriptions-item label="姓名">{{ profileData.name }}</a-descriptions-item>
        <a-descriptions-item v-if="userType === 'doctor'" label="医院">{{
          profileData.hospital
        }}</a-descriptions-item>
        <a-descriptions-item v-if="userType === 'doctor'" label="部门">{{
          profileData.department
        }}</a-descriptions-item>
        <a-descriptions-item v-if="userType === 'doctor'" label="职称">{{
          profileData.title
        }}</a-descriptions-item>
        <a-descriptions-item v-if="userType === 'patient'" label="年龄">{{
          profileData.age
        }}</a-descriptions-item>
        <a-descriptions-item v-if="userType === 'patient'" label="性别">{{
          profileData.gender ? '男' : '女'
        }}</a-descriptions-item>
      </a-descriptions>
    </div>

    <div v-if="userType === 'doctor' || userType === 'patient'" class="profile-actions">
      <p class="auth-redirect">个人信息有变？点击下方按钮，重新进行实名认证</p>
      <a-button type="primary" size="large" @click="redirectToAuth">实名认证</a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue';
  import { useRouter } from 'vue-router';
  import { Modal } from 'ant-design-vue';
  import { useUserStore } from '@/store/modules/user';
  import Api from '@/api';
  import to from '@/utils/awaitTo';

  const router = useRouter();
  const userStore = useUserStore();

  const userInfo = ref(userStore.userInfo);
  const userType = ref(userStore.getUserType());
  const profileData = ref({
    name: '',
    hospital: '',
    department: '',
    title: '',
    age: 1,
    gender: false,
  });

  const getAccountInfo = async () => {
    if (userType.value === 'doctor') {
      const data = await Api.account.doctorAccountProfile(Number(userInfo.value.userId));
      console.log(data);
      profileData.value.name = data.name;
      profileData.value.hospital = data.hospital;
      profileData.value.department = data.department;
      profileData.value.title = data.title;
    } else if (userType.value === 'patient') {
      const data = await Api.account.patientAccountProfile(Number(userInfo.value.userId));
      console.log(data);
      profileData.value.name = data.name;
      profileData.value.age = data.age;
      profileData.value.gender = data.gender;
    }
  };

  const redirectToAuth = async () => {
    // 重新认证前重置认证状态
    const [err] = await to(userStore.resetAuth());

    if (err) {
      Modal.error({
        title: () => '提示',
        content: () => err.message,
      });
    } else {
      router.push('/auth');
    }
  };

  await getAccountInfo();
</script>

<style lang="less" scoped>
  .profile-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 20px;
    background: #f5f5f5;

    .profile-avatar {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 20px;

      .avatar-image {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 10px;
      }

      .avatar-placeholder {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background-color: #ddd;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
      }

      .avatar-upload-btn {
        font-size: 14px;
      }
    }

    .profile-info {
      width: 50vw;
      margin-bottom: 20px;
    }

    .profile-actions {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-top: 20px;
    }

    .incorrect-type {
      font-size: 16px;
      font-weight: bold;
      color: red;
      margin-top: 16px;
    }

    .auth-redirect {
      font-style: italic;
      color: gray;
      margin-top: 10px;
    }
  }
</style>
