<template>
  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h2><dashboard-outlined /> 患者总览</h2>
        <p class="subtitle">欢迎回来，祝您身体健康</p>
      </div>
    </div>

    <a-row :gutter="[24, 24]">
      <!-- 左侧：医生信息和最新报告 -->
      <a-col :xs="24" :lg="7">
        <!-- 主管医生信息卡片 -->
        <a-card class="info-card" :loading="loading.doctor">
          <template #title>
            <div class="card-title">
              <user-outlined />
              <span>我的主管医生</span>
            </div>
          </template>
          <div v-if="chargeDoctor" class="doctor-info">
            <div class="doctor-avatar">
              <a-avatar :size="64" :style="{ backgroundColor: '#1890ff' }">
                <template #icon><user-outlined /></template>
              </a-avatar>
              <a-badge status="success" text="在线" />
            </div>
            <div class="doctor-details">
              <h3>{{ chargeDoctor.name }}</h3>
              <div class="doctor-tags">
                <a-tag color="blue">{{ chargeDoctor.title }}</a-tag>
                <a-tag color="cyan">{{ chargeDoctor.department }}</a-tag>
              </div>
              <div class="hospital-info">
                <medicine-box-outlined />
                <span>{{ chargeDoctor.hospital }}</span>
              </div>
              <div class="contact-info">
                <phone-outlined />
                <span>{{ chargeDoctor.phone || '暂无联系方式' }}</span>
              </div>
            </div>
            <div class="doctor-actions">
              <a-button type="primary" @click="goToDoctor">
                查看详情
              </a-button>
            </div>
          </div>
          <a-empty v-else description="暂无主管医生信息" />
        </a-card>

        <!-- 最新报告卡片 -->
        <a-card class="info-card" :loading="loading.report">
          <template #title>
            <div class="card-title">
              <file-text-outlined />
              <span>最新检查报告</span>
            </div>
          </template>
          <div v-if="lastReport" class="report-info">
            <div class="report-header">
              <div class="report-date">
                <calendar-outlined />
                <span>{{ formatDate(lastReport.generationDate) }}</span>
              </div>
              <a-tag :color="getStatusColor(lastReport.result)">
                {{ lastReport.result || '未知' }}
              </a-tag>
            </div>
            <div class="report-content">
              <div class="report-item">
                <span class="label">肌瘤个数</span>
                <span class="value">{{ lastReport.clinicalIndicators?.fibroidsPresent ?? '未知' }}</span>
              </div>
              <div class="report-item">
                <span class="label">治疗体积</span>
                <span class="value">{{ lastReport.clinicalIndicators?.treatmentVolume ?? '未知' }} cm³</span>
              </div>
            </div>
            <div class="report-actions">
              <a-button type="primary" @click="goToReport">查看详情</a-button>
            </div>
          </div>
          <a-empty v-else description="暂无最新报告" />
        </a-card>
      </a-col>

      <!-- 右侧：趋势图表和快捷操作 -->
      <a-col :xs="24" :lg="17">
        <!-- 趋势图表 -->
        <a-card class="chart-card">
          <template #title>
            <div class="card-title">
              <line-chart-outlined />
              <span>病情趋势分析</span>
            </div>
          </template>
          <a-spin :spinning="loading.chart">
            <div class="chart-wrapper">
              <div ref="chartRef" class="chart-container"></div>
              <a-empty v-if="!reportList.length" description="暂无历史数据" />
            </div>
          </a-spin>
        </a-card>

        <!-- 快捷操作区 -->
        <div class="quick-actions">
          <a-row :gutter="[24, 24]">
            <a-col :xs="24" :sm="12">
              <div class="action-card" @click="goToUpload">
                <div class="action-icon">
                  <upload-outlined />
                </div>
                <div class="action-content">
                  <h4>上传MRI影像</h4>
                  <p>上传最新的MRI检查影像</p>
                </div>
              </div>
            </a-col>
            <a-col :xs="24" :sm="12">
              <div class="action-card" @click="goToReport">
                <div class="action-icon">
                  <file-text-outlined />
                </div>
                <div class="action-content">
                  <h4>查看检查报告</h4>
                  <p>查看历史检查报告记录</p>
                </div>
              </div>
            </a-col>
          </a-row>
        </div>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import * as echarts from 'echarts';
import {
  DashboardOutlined,
  UserOutlined,
  UploadOutlined,
  FileTextOutlined,
  RightOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  LineChartOutlined,
  PhoneOutlined
} from '@ant-design/icons-vue';
import { getLastReport, getChargeDoctor, getAllReports } from '@/api/modules/patient';
import dayjs from 'dayjs';

const router = useRouter();

// 加载状态
const loading = ref({
  doctor: true,  // 默认为加载状态
  report: true,
  chart: false
});

// 数据状态
const chargeDoctor = ref(null);
const lastReport = ref(null);
const reportList = ref([]);

// 格式化日期
const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm');
};

// 获取患者ID
const getLoggedInPatientId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('__persisted__user') || '{}');
    const token = user.token;
    if (!token) {
      message.error('请先登录');
      router.push('/login');
      return null;
    }
    const base64Payload = token.split('.')[1];
    const payload = JSON.parse(atob(base64Payload));
    return payload.sub;
  } catch (error) {
    console.error('获取患者ID失败:', error);
    message.error('获取用户信息失败，请重新登录');
    router.push('/login');
    return null;
  }
};

// 获取主管医生信息
const fetchDoctorInfo = async (patientId: string) => {
  try {
    loading.value.doctor = true;
    console.log('正在获取医生信息...');
    const res = await getChargeDoctor(patientId);
    console.log('医生信息返回:', res);
    
    if (res && res.name) {
      chargeDoctor.value = res;
      console.log('设置医生信息成功:', chargeDoctor.value);
    } else {
      console.warn('未找到医生信息');
      message.warning('未找到主管医生信息');
    }
  } catch (error) {
    console.error('获取医生信息失败:', error);
    message.error('获取医生信息失败');
  } finally {
    loading.value.doctor = false;
  }
};

// 获取最新报告
const fetchLatestReport = async (patientId: string) => {
  try {
    loading.value.report = true;
    console.log('正在获取最新报告...');
    const res = await getLastReport(patientId);
    console.log('最新报告返回:', res);
    
    if (res && res.generationDate) {
      lastReport.value = res;
      console.log('设置最新报告成功:', lastReport.value);
    } else {
      console.warn('未找到最新报告');
    }
  } catch (error) {
    console.error('获取最新报告失败:', error);
    message.error('获取最新报告失败');
  } finally {
    loading.value.report = false;
  }
};

// 获取所有报告用于图表
const fetchAllReports = async (patientId: string) => {
  try {
    loading.value.chart = true;
    console.log('正在获取所有报告...');
    const res = await getAllReports(patientId);
    console.log('所有报告返回:', res);
    
    if (Array.isArray(res)) {
      reportList.value = res;
      console.log('设置报告列表成功:', reportList.value);
      // 初始化图表
      setTimeout(() => {
        initChart();
      }, 100);
    }
  } catch (error) {
    console.error('获取报告列表失败:', error);
    message.error('获取报告列表失败');
  } finally {
    loading.value.chart = false;
  }
};

// 初始化数据
const initData = async () => {
  const patientId = getLoggedInPatientId();
  if (!patientId) return;

  try {
    // 先获取医生信息
    await fetchDoctorInfo(patientId);
    
    // 然后获取报告信息
    await fetchLatestReport(patientId);
    
    // 最后获取所有报告用于图表
    await fetchAllReports(patientId);
  } catch (error) {
    console.error('初始化数据失败:', error);
  }
};

// 页面跳转函数
const goToUpload = () => router.push('/patient/upload');
const goToDoctor = () => router.push('/patient/pdoctor');
const goToReport = () => router.push('/patient/report');

// 图表相关
const chartRef = ref(null);
const chartInstance = ref(null);

// 初始化图表
const initChart = () => {
  if (chartRef.value) {
    try {
      // 先清理已存在的实例
      if (chartInstance.value) {
        chartInstance.value.dispose();
      }
      chartInstance.value = echarts.init(chartRef.value);
      window.addEventListener('resize', handleResize);
      
      // 如果已有数据，立即更新图表
      if (reportList.value.length > 0) {
        updateChart();
      }
    } catch (error) {
      console.error('图表初始化失败:', error);
    }
  }
};

// 处理窗口大小变化
const handleResize = () => {
  chartInstance.value?.resize();
};

// 更新图表数据
const updateChart = () => {
  if (!chartInstance.value || !reportList.value.length) return;

  const sortedReports = [...reportList.value].sort((a, b) => 
    new Date(a.generationDate).getTime() - new Date(b.generationDate).getTime()
  );

  const dates = sortedReports.map(report => dayjs(report.generationDate).format('MM-DD'));
  
  // 准备多个指标的数据
  const fibroids = sortedReports.map(report => 
    report.clinicalIndicators?.fibroidsPresent || null
  );
  const volumes = sortedReports.map(report => 
    report.clinicalIndicators?.treatmentVolume || null
  );
  const energies = sortedReports.map(report => 
    report.clinicalIndicators?.totalEnergy || null
  );

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = dayjs(params[0].name).format('YYYY-MM-DD') + '<br/>';
        params.forEach(param => {
          let value = param.value === null ? '暂无数据' : param.value;
          let unit = '';
          if (param.seriesName === '治疗体积') unit = ' cm³';
          if (param.seriesName === '总能量') unit = ' J';
          result += `${param.marker}${param.seriesName}：${value}${unit}<br/>`;
        });
        return result;
      }
    },
    legend: {
      data: ['肌瘤个数', '治疗体积', '总能量'],
      bottom: 0
    },
    grid: {
      top: 40,
      right: 20,
      bottom: 60,
      left: 60,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 30,
        interval: 0
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '肌瘤个数',
        minInterval: 1,
        position: 'left',
        axisLine: { show: true },
        axisLabel: { formatter: '{value}' }
      },
      {
        type: 'value',
        name: '体积/能量',
        position: 'right',
        axisLine: { show: true },
        axisLabel: { formatter: '{value}' }
      }
    ],
    series: [
      {
        name: '肌瘤个数',
        type: 'line',
        data: fibroids,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#1890ff' }
      },
      {
        name: '治疗体积',
        type: 'line',
        yAxisIndex: 1,
        data: volumes,
        smooth: true,
        symbol: 'square',
        symbolSize: 8,
        itemStyle: { color: '#52c41a' }
      },
      {
        name: '总能量',
        type: 'line',
        yAxisIndex: 1,
        data: energies,
        smooth: true,
        symbol: 'triangle',
        symbolSize: 8,
        itemStyle: { color: '#faad14' }
      }
    ]
  };

  chartInstance.value.setOption(option);
};

// 修改 getStatusColor 为 computed 函数
const getStatusColor = computed(() => (result) => {
  if (!result) return 'default';
  const status = String(result);
  if (status.includes('正常')) return 'success';
  if (status.includes('异常')) return 'error';
  return 'processing';
});

// 生命周期钩子
onMounted(() => {
  console.log('组件挂载，开始初始化数据...');
  initData();
});

// 确保组件卸载时清理
onUnmounted(() => {
  if (chartInstance.value) {
    chartInstance.value.dispose();
  }
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.dashboard {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 32px;
}

.header-content h2 {
  margin: 0;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle {
  margin: 8px 0 0;
  color: #8c8c8c;
}

.info-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.doctor-info {
  padding: 16px;
}

.doctor-avatar {
  text-align: center;
  margin-bottom: 16px;
}

.doctor-details {
  text-align: center;
}

.doctor-details h3 {
  margin: 0 0 12px;
  font-size: 18px;
  color: #1f1f1f;
}

.doctor-tags {
  margin-bottom: 16px;
}

.hospital-info,
.contact-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #595959;
  margin-bottom: 8px;
}

.doctor-actions {
  margin-top: 16px;
  text-align: center;
}

.report-info {
  padding: 16px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.report-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #8c8c8c;
}

.report-content {
  background: #f8f9fc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.report-item {
  margin-bottom: 12px;
}

.report-item:last-child {
  margin-bottom: 0;
}

.report-item .label {
  display: block;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.report-item .value {
  font-size: 20px;
  font-weight: 500;
  color: #1890ff;
}

.report-actions {
  text-align: right;
}

.chart-card {
  margin-bottom: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-wrapper {
  padding: 16px;
  min-height: 450px;
}

.chart-container {
  width: 100%;
  height: 450px;
}

.quick-actions {
  margin-top: 0;
}

.action-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #1890ff;
  border-radius: 24px;
  color: white;
  font-size: 24px;
}

.action-content {
  flex: 1;
}

.action-content h4 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #1f1f1f;
}

.action-content p {
  margin: 0;
  color: #8c8c8c;
  font-size: 14px;
}

:deep(.ant-card-head) {
  border-bottom: 1px solid #f0f0f0;
  min-height: 48px;
  padding: 0 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

:deep(.ant-card-body) {
  padding: 24px;
}

@media (max-width: 768px) {
  .action-card {
    margin-bottom: 0;
  }
  
  .dashboard {
    padding: 16px;
  }
  
  .page-header {
    margin-bottom: 24px;
  }
}
</style>

