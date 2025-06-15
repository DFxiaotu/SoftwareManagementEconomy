<template>
  <div class="doctor-relation">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h2><user-outlined /> 我的主管医生</h2>
        <a-button type="primary" @click="fetchChargeDoctor" :loading="loading">
          <sync-outlined :spin="loading" /> 刷新信息
        </a-button>
      </div>
    </div>

    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card class="doctor-card">
          <div v-if="chargeDoctor" class="doctor-info">
            <div class="doctor-header">
              <div class="avatar-section">
                <a-avatar :size="100" :style="{ backgroundColor: '#1890ff' }">
                  <template #icon><user-outlined /></template>
                </a-avatar>
                <div class="status-badge">
                  <a-badge status="success" text="在线" />
                </div>
              </div>
              <div class="info-section">
                <div class="name-title">
                  <h3>{{ chargeDoctor.name }}</h3>
                  <div class="tags">
                    <a-tag color="blue">{{ chargeDoctor.title }}</a-tag>
                    <a-tag color="cyan">{{ chargeDoctor.department }}</a-tag>
                    <a-tag color="green">主管医生</a-tag>
                  </div>
                </div>
                <div class="hospital-section">
                  <medicine-box-outlined />
                  <span class="hospital-name">{{ chargeDoctor.hospital }}</span>
                </div>
                <a-divider />
                <div class="detail-items">
                  <div class="detail-item">
                    <team-outlined />
                    <span class="label">所在科室</span>
                    <span class="value">{{ chargeDoctor.department }}</span>
                  </div>
                  <div class="detail-item">
                    <idcard-outlined />
                    <span class="label">医生ID</span>
                    <span class="value">{{ chargeDoctor.userId }}</span>
                  </div>
                  <div class="detail-item">
                    <clock-circle-outlined />
                    <span class="label">出诊时间</span>
                    <span class="value">周一至周五</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <a-empty v-else description="暂无主管医生信息" />
        </a-card>
      </a-col>

      <a-col :span="24">
        <a-card class="notice-card">
          <template #title>
            <span class="card-title">
              <notification-outlined /> 就医须知
            </span>
          </template>
          <div class="notice-content">
            <a-alert
              message="温馨提示"
              description="1. 问诊前请准备好近期检查资料
2. 建议提前10分钟到达诊室
3. 如需更改预约时间请提前告知"
              type="info"
              show-icon
            />
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { getChargeDoctor } from '@/api/modules/patient';
import {
  UserOutlined,
  MedicineBoxOutlined,
  TeamOutlined,
  SyncOutlined,
  IdcardOutlined,
  ClockCircleOutlined,
  NotificationOutlined
} from '@ant-design/icons-vue';

// 当前登录患者信息
const loggedInPatient = reactive({
  id: '' // 患者ID
});

// 主管医生信息
const chargeDoctor = ref<any>(null);

// 解析 JWT Token 的有效载荷部分
const decodeJWT = (token: string) => {
  try {
    const base64Payload = token.split('.')[1]; // 提取JWT的payload部分
    const payload = atob(base64Payload); // 解码Base64
    return JSON.parse(payload); // 解析为对象
  } catch (error) {
    console.error('JWT解析失败:', error);
    return null;
  }
};

// 从 localStorage 中获取已登录患者信息
const loadLoggedInPatient = () => {
  try {
    const persistedUser = localStorage.getItem('__persisted__user');
    if (persistedUser) {
      const userData = JSON.parse(persistedUser);
      const token = userData.token;
      if (token) {
        const decodedToken = decodeJWT(token);
        loggedInPatient.id = decodedToken?.sub || ''; // 提取患者ID（sub字段）
      } else {
        message.error('未找到有效的登录Token，请重新登录');
      }
    } else {
      message.error('未找到登录的患者信息，请重新登录');
    }
  } catch (error) {
    console.error('获取本地存储的患者信息失败:', error);
    message.error('加载患者信息失败');
  }
};

// 获取主管医生信息
const fetchChargeDoctor = async () => {
  if (!loggedInPatient.id) {
    message.error('无法获取患者ID，请检查登录状态');
    return;
  }
  try {
    const res = await getChargeDoctor(loggedInPatient.id);
    if (res && res.department && res.hospital && res.name && res.title && res.userId) {
      chargeDoctor.value = res; // 直接将接口返回的数据赋值
      message.success('获取主管医生信息成功');
    } else {
      console.error('接口返回数据格式不符合预期:', res);
      message.error('接口返回的数据无效');
    }
  } catch (error) {
    console.error('获取主管医生信息失败:', error);
    message.error('获取主管医生信息失败');
  }
};

// 页面加载时自动获取患者和医生信息
onMounted(() => {
  loadLoggedInPatient();
  if (loggedInPatient.id) {
    fetchChargeDoctor();
  }
});
</script>

<style scoped>
.doctor-relation {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  color: #1890ff;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
}

.doctor-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.doctor-info {
  padding: 24px;
}

.doctor-header {
  display: flex;
  gap: 32px;
}

.avatar-section {
  text-align: center;
}

.status-badge {
  margin-top: 12px;
}

.info-section {
  flex: 1;
}

.name-title {
  margin-bottom: 16px;
}

.name-title h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: rgba(0, 0, 0, 0.85);
}

.tags {
  display: flex;
  gap: 8px;
}

.hospital-section {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1890ff;
  font-size: 16px;
  margin-bottom: 16px;
}

.hospital-name {
  font-weight: 500;
}

.detail-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
  transition: all 0.3s;
}

.detail-item:hover {
  background: #e6f7ff;
}

.label {
  color: rgba(0, 0, 0, 0.45);
  margin-right: 8px;
}

.value {
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
}

.notice-card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.notice-content {
  padding: 8px 0;
}

:deep(.ant-alert-description) {
  white-space: pre-line;
}

:deep(.ant-btn) {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 16px;
}

:deep(.anticon) {
  font-size: 16px;
}

:deep(.ant-card) {
  transition: all 0.3s;
}

:deep(.ant-card:hover) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
</style>
