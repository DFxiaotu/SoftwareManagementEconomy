<template>
  <div class="patient-report">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><file-text-outlined /> 检查报告</h2>
      <p class="subtitle">查看和管理您的所有检查报告</p>
    </div>

    <!-- 最近一份报告 -->
    <a-card class="report-card">
      <template #title>
        <div class="card-title">
          <clock-circle-outlined />
          <span>最新检查报告</span>
        </div>
      </template>
      <div v-if="latestReport" class="report-summary">
        <div class="report-header">
          <div class="date-info">
            <calendar-outlined />
            <span>{{ formatDate(latestReport.generationDate) }}</span>
          </div>
          <a-tag :color="getStatusColor(latestReport.result)">
            {{ latestReport.result || '未知' }}
          </a-tag>
        </div>
        <a-divider />
        <div class="report-indicators">
          <div class="indicator">
            <span class="label">子宫肌瘤个数</span>
            <span class="value">{{
              latestReport.clinicalIndicators?.fibroidsPresent ??
              latestReport.clinicalIndicators?.bloodRoutine?.fibroidsPresent ??
              '未知'
            }}</span>
          </div>
          <div class="indicator">
            <span class="label">治疗体积</span>
            <span class="value">{{
              (latestReport.clinicalIndicators?.treatmentVolume ??
              latestReport.clinicalIndicators?.bloodRoutine?.treatmentVolume ??
              '未知') + ' cm³'
            }}</span>
          </div>
          <div class="indicator">
            <span class="label">总能量</span>
            <span class="value">{{
              (latestReport.clinicalIndicators?.totalEnergy ??
              latestReport.clinicalIndicators?.bloodRoutine?.totalEnergy ??
              '未知') + ' J'
            }}</span>
          </div>
        </div>
        <div class="action-buttons">
          <a-button type="primary" @click="viewReportDetail(latestReport.reportId)">
            查看详细报告
          </a-button>
        </div>
      </div>
      <a-empty v-else description="未找到最近的报告" />
    </a-card>

    <!-- 历史报告列表 -->
    <a-card class="report-card">
      <template #title>
        <div class="card-title">
          <unordered-list-outlined />
          <span>历史报告记录</span>
        </div>
      </template>
      <a-empty v-if="!reportList.length" description="暂无报告记录" />
      <a-list v-else bordered :data-source="reportList" :pagination="pagination">
        <template #renderItem="{ item: report }">
          <a-list-item>
            <a-list-item-meta>
              <template #title>
                <div class="report-list-title">
                  <span>{{ formatDate(report.generationDate) }}</span>
                  <a-tag :color="getStatusColor(report.result)">
                    {{ report.result || '未知' }}
                  </a-tag>
                </div>
              </template>
              <template #description>
                <div class="report-list-desc">
                  <span>肌瘤个数: {{ report.clinicalIndicators?.fibroidsPresent ?? '未知' }}</span>
                  <span>治疗体积: {{ report.clinicalIndicators?.treatmentVolume ?? '未知' }} cm³</span>
                  <span>总能量: {{ report.clinicalIndicators?.totalEnergy ?? '未知' }} J</span>
                </div>
              </template>
            </a-list-item-meta>
            <template #extra>
              <a-button type="link" @click="viewReportDetail(report.reportId)">
                查看详情
              </a-button>
            </template>
          </a-list-item>
        </template>
      </a-list>
    </a-card>

    <!-- 报告详情弹窗 -->
    <a-modal v-model:open="detailModalVisible" title="报告详情" width="800px" :footer="null">
      <div v-if="reportDetail" class="report-detail">
        <div class="detail-header">
          <div class="detail-date">
            <calendar-outlined />
            <span>{{ formatDate(reportDetail.generationDate) }}</span>
          </div>
          <a-tag :color="getStatusColor(reportDetail.result)">
            {{ reportDetail.result || '未知' }}
          </a-tag>
        </div>
        <a-divider />
        <a-descriptions bordered>
          <a-descriptions-item label="生成医生" :span="3">
            {{ reportDetail.doctorName || '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="MRI分析结果" :span="3">
            {{ reportDetail.result || '未知' }}
          </a-descriptions-item>
          <a-descriptions-item label="治疗备注" :span="3">
            {{ reportDetail.therapyComment || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="放射组学备注" :span="3">
            {{ reportDetail.radiomicComment || '无' }}
          </a-descriptions-item>
        </a-descriptions>

        <div class="clinical-indicators">
          <h3>临床指标</h3>
          <a-row :gutter="[16, 16]">
            <a-col :span="8">
              <div class="indicator-card">
                <medicine-box-outlined />
                <div class="indicator-content">
                  <span class="label">子宫肌瘤个数</span>
                  <span class="value">{{ 
                    reportDetail.clinicalIndicators?.fibroidsPresent ?? 
                    reportDetail.clinicalIndicators?.bloodRoutine?.fibroidsPresent ?? 
                    '未知' 
                  }}</span>
                </div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="indicator-card">
                <column-height-outlined />
                <div class="indicator-content">
                  <span class="label">治疗体积</span>
                  <span class="value">{{ 
                    reportDetail.clinicalIndicators?.treatmentVolume ?? 
                    reportDetail.clinicalIndicators?.bloodRoutine?.treatmentVolume ?? 
                    '未知' 
                  }} cm³</span>
                </div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="indicator-card">
                <thunderbolt-outlined />
                <div class="indicator-content">
                  <span class="label">总能量</span>
                  <span class="value">{{ 
                    reportDetail.clinicalIndicators?.totalEnergy ?? 
                    reportDetail.clinicalIndicators?.bloodRoutine?.totalEnergy ?? 
                    '未知' 
                  }} J</span>
                </div>
              </div>
            </a-col>
          </a-row>
        </div>
      </div>
      <a-spin v-else />
    </a-modal>

    <!-- 在历史报告列表后添加 -->
    <a-card class="report-card">
      <template #title>
        <div class="card-title">
          <line-chart-outlined />
          <span>病情趋势分析</span>
        </div>
      </template>
      <a-row :gutter="[16, 16]">
        <a-col :span="24">
          <div class="chart-container">
            <h4>治疗指标趋势</h4>
            <div :ref="el => bindChartRef(el, 'treatmentTrend')" style="width: 100%; height: 400px;"></div>
          </div>
        </a-col>
        <a-col :span="24">
          <div class="chart-container">
            <h4>血常规指标趋势</h4>
            <div :ref="el => bindChartRef(el, 'bloodTrend')" style="width: 100%; height: 400px;"></div>
          </div>
        </a-col>
      </a-row>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue';
import { message } from 'ant-design-vue';
import {
  FileTextOutlined,
  UnorderedListOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  MedicineBoxOutlined,
  ThunderboltOutlined,
  ColumnHeightOutlined,
  LineChartOutlined
} from '@ant-design/icons-vue';
import { getLastReport, getAllReports, getReportDetail } from '@/api/modules/patient';
import dayjs from 'dayjs';
import * as echarts from 'echarts';

// 数据状态
const latestReport = ref(null);
const reportList = ref<Report[]>([]);
const reportDetail = ref(null);
const detailModalVisible = ref(false);

// 分页配置
const pagination = {
  pageSize: 10,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条记录`
};

// 获取状态颜色
const getStatusColor = computed(() => (result) => {
  if (!result) return 'default';
  const status = String(result);
  if (status.includes('正常')) return 'success';
  if (status.includes('异常')) return 'error';
  return 'processing';
});

// 获取患者ID
const getPatientId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('__persisted__user') || '{}');
    const token = user.token || '';
    const payload = JSON.parse(atob(token.split('.')[1] || ''));
    return payload.sub || null;
  } catch (error) {
    console.error('获取患者ID失败:', error);
    message.error('无法获取患者ID，请重新登录');
    return null;
  }
};

// 日期格式化函数
const formatDate = (dateStr: string) => {
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm');
};

// 获取最近一份报告
const fetchLatestReport = async () => {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const res = await getLastReport(patientId);
    if (res && res.generationDate) {
      latestReport.value = res;
    } else {
      message.warning('未找到最近报告');
    }
  } catch (error) {
    console.error('获取最近报告失败:', error);
    message.error('获取最近报告失败');
  }
};

// 获取所有报告
const fetchAllReports = async () => {
  const patientId = getPatientId();
  if (!patientId) return;

  try {
    const res = await getAllReports(patientId);
    if (Array.isArray(res)) {
      reportList.value = res;
    } else {
      message.warning('未找到任何报告');
    }
  } catch (error) {
    console.error('获取所有报告失败:', error);
    message.error('获取所有报告失败');
  }
};

// 查看报告详情
const viewReportDetail = async (reportId: number) => {
  detailModalVisible.value = true;
  reportDetail.value = null;

  try {
    const res = await getReportDetail(reportId);
    if (res && res.generationDate) {
      reportDetail.value = res;
    } else {
      message.warning('未找到报告详情');
    }
  } catch (error) {
    console.error('获取报告详情失败:', error);
    message.error('获取报告详情失败');
  }
};

// 修改图表相关的代码

// 1. 修改图表 ref 声明
const chartRefs = {
  bloodTrend: ref(null),
  treatmentTrend: ref(null)
};

const chartInstances = {
  bloodTrend: ref(null),
  treatmentTrend: ref(null)
};

// 2. 修改初始化和清理方法
const initCharts = () => {
  console.log('开始初始化图表...');
  console.log('chartRefs:', chartRefs);
  Object.keys(chartRefs).forEach(key => {
    console.log(`正在初始化 ${key} 图表...`);
    console.log(`DOM元素:`, chartRefs[key].value);
    if (chartRefs[key].value && !chartInstances[key].value) {
      try {
        chartInstances[key].value = echarts.init(chartRefs[key].value);
        console.log(`${key} 图表初始化成功`);
      } catch (error) {
        console.error(`${key} 图表初始化失败:`, error);
      }
    }
  });
};

const disposeCharts = () => {
  Object.values(chartInstances).forEach(instance => {
    if (instance.value) {
      instance.value.dispose();
      instance.value = null;
    }
  });
};

const handleResize = () => {
  Object.values(chartInstances).forEach(instance => {
    instance.value?.resize();
  });
};

// 3. 修改生命周期钩子
onMounted(async () => {
  console.log('组件挂载...');
  await fetchLatestReport();
  const reports = await fetchAllReports();
  console.log('数据获取完成:', reports);
  
  // 确保 DOM 已更新
  await nextTick();
  console.log('DOM 已更新，开始初始化图表...');
  initCharts();
  updateCharts();
  
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  disposeCharts();
  window.removeEventListener('resize', handleResize);
});

// 4. 更新所有图表的方法
const updateCharts = () => {
  console.log('开始更新图表...');
  console.log('reportList:', reportList.value);
  console.log('chartInstances:', chartInstances);
  updateTreatmentTrendChart();
  updateBloodTrendChart();
};

// 5. 修改图表更新方法
const updateTreatmentTrendChart = () => {
  console.log('更新治疗趋势图表...');
  if (!chartInstances.treatmentTrend.value || !reportList.value.length) {
    console.log('无法更新治疗趋势图表:', {
      hasInstance: !!chartInstances.treatmentTrend.value,
      dataLength: reportList.value.length
    });
    return;
  }

  const sortedReports = [...reportList.value].sort((a, b) => 
    new Date(a.generationDate).getTime() - new Date(b.generationDate).getTime()
  );

  const dates = sortedReports.map(report => dayjs(report.generationDate).format('MM-DD'));
  const treatmentData = sortedReports.map(report => ({
    fibroids: report.clinicalIndicators?.fibroidsPresent,
    volume: report.clinicalIndicators?.treatmentVolume,
    energy: report.clinicalIndicators?.totalEnergy,
    power: report.clinicalIndicators?.avgTreatmentPower
  }));

  const option = {
    title: {
      text: '治疗指标趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['肌瘤个数', '治疗体积', '总能量', '平均功率'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 30 }
    },
    yAxis: [
      {
        type: 'value',
        name: '肌瘤个数',
        position: 'left'
      },
      {
        type: 'value',
        name: '其他指标',
        position: 'right'
      }
    ],
    series: [
      {
        name: '肌瘤个数',
        type: 'bar',
        data: treatmentData.map(d => d.fibroids)
      },
      {
        name: '治疗体积',
        type: 'line',
        yAxisIndex: 1,
        data: treatmentData.map(d => d.volume)
      },
      {
        name: '总能量',
        type: 'line',
        yAxisIndex: 1,
        data: treatmentData.map(d => d.energy)
      },
      {
        name: '平均功率',
        type: 'line',
        yAxisIndex: 1,
        data: treatmentData.map(d => d.power)
      }
    ]
  };

  chartInstances.treatmentTrend.value.setOption(option);
};

const updateBloodTrendChart = () => {
  console.log('更新血常规趋势图表...');
  if (!chartInstances.bloodTrend.value || !reportList.value.length) {
    console.log('无法更新血常规趋势图表:', {
      hasInstance: !!chartInstances.bloodTrend.value,
      dataLength: reportList.value.length
    });
    return;
  }

  const sortedReports = [...reportList.value].sort((a, b) => 
    new Date(a.generationDate).getTime() - new Date(b.generationDate).getTime()
  );

  const dates = sortedReports.map(report => dayjs(report.generationDate).format('MM-DD'));
  const bloodData = sortedReports.map(report => report.clinicalIndicators?.bloodRoutine);

  const option = {
    title: {
      text: '血常规指标趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['WBC', 'RBC', 'HGB', 'PLT'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '60px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 30 }
    },
    yAxis: {
      type: 'value',
      name: '指标值'
    },
    series: [
      {
        name: 'WBC',
        type: 'line',
        data: bloodData.map(d => d?.wbcCount)
      },
      {
        name: 'RBC',
        type: 'line',
        data: bloodData.map(d => d?.rbcCount)
      },
      {
        name: 'HGB',
        type: 'line',
        data: bloodData.map(d => d?.hemoglobin)
      },
      {
        name: 'PLT',
        type: 'line',
        data: bloodData.map(d => d?.plateletCount)
      }
    ]
  };

  chartInstances.bloodTrend.value.setOption(option);
};

// 6. 修改 watch
watch(reportList, (newVal) => {
  console.log('reportList 更新:', newVal);
  if (newVal.length) {
    nextTick(() => {
      console.log('数据更新后重新初始化图表...');
      initCharts();
      updateCharts();
    });
  }
}, { deep: true });

// 页面加载时初始化数据
onMounted(() => {
  fetchLatestReport();
  fetchAllReports().then(() => {
    nextTick(() => {
      initCharts();
      updateCharts();
    });
  });
});

// 修改 ref 的绑定方式
const bindChartRef = (el, key) => {
  console.log(`绑定 ${key} 图表 ref:`, el);
  chartRefs[key].value = el;
};
</script>

<style scoped>
.patient-report {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle {
  margin: 8px 0 0;
  color: rgba(0, 0, 0, 0.45);
}

.report-card {
  margin-bottom: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.65);
}

.report-indicators {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 16px 0;
}

.indicator {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  text-align: center;
}

.indicator .label {
  display: block;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 8px;
}

.indicator .value {
  font-size: 24px;
  font-weight: 500;
  color: #1890ff;
}

.action-buttons {
  text-align: right;
  margin-top: 16px;
}

.report-list-title {
  display: flex;
  align-items: center;
  gap: 16px;
}

.report-list-desc {
  display: flex;
  gap: 24px;
  color: rgba(0, 0, 0, 0.45);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-date {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.clinical-indicators {
  margin-top: 24px;
}

.clinical-indicators h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.indicator-card {
  background: #fafafa;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.indicator-content {
  flex: 1;
}

.indicator-content .label {
  display: block;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 4px;
}

.indicator-content .value {
  font-size: 20px;
  font-weight: 500;
  color: #1890ff;
}

:deep(.ant-descriptions-bordered .ant-descriptions-item-label) {
  background: #fafafa;
  width: 120px;
}

:deep(.ant-list-item) {
  padding: 16px;
}

:deep(.ant-modal-body) {
  padding: 24px;
}

@media (max-width: 768px) {
  .report-list-desc {
    flex-direction: column;
    gap: 8px;
  }
}

.analysis-charts {
  margin-top: 24px;
}

.analysis-charts h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

.chart-container {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.chart-container h4 {
  margin: 0 0 16px;
  text-align: center;
  color: rgba(0, 0, 0, 0.85);
}
</style>

