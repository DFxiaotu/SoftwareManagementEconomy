<template>
  <div class="records">
    <a-card>
      <!-- 搜索表单 -->
      <a-form layout="inline" :model="searchForm">
        <a-form-item label="时间范围">
          <a-range-picker v-model:value="searchForm.dateRange" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="searchForm.type" placeholder="请选择类型">
            <a-select-option value="all">全部</a-select-option>
            <a-select-option value="mri">MRI</a-select-option>
            <a-select-option value="ct">CT</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch">搜索</a-button>
          <a-button style="margin-left: 8px" @click="handleReset">重置</a-button>
        </a-form-item>
      </a-form>

      <!-- 记录列表 -->
      <a-table :columns="columns" :data-source="records" :loading="loading">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" @click="viewRecord(record)">查看</a-button>
              <a-button type="link" @click="analyzeRecord(record)">分析</a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import type { TableColumnsType } from 'ant-design-vue';
import { getLastReport, getAllReports, getClinicalIndicators } from '@/api/modules/patient'; // 引入相关接口


defineOptions({
  name: 'PatientRecords',
});

interface Record {
  id: string;
  date: string;
  type: string;
  description: string;
  status: string;
}

const searchForm = reactive({
  dateRange: [],
  type: 'all',
});

const loading = ref(false);
const records = ref<Record[]>([]);

const columns: TableColumnsType = [
  {
    title: '记录ID',
    dataIndex: 'id',
  },
  {
    title: '检查日期',
    dataIndex: 'date',
  },
  {
    title: '检查类型',
    dataIndex: 'type',
  },
  {
    title: '描述',
    dataIndex: 'description',
  },
  {
    title: '状态',
    dataIndex: 'status',
  },
  {
    title: '操作',
    key: 'action',
    slots: { customRender: 'action' },
  },
];

// 处理搜索操作
const handleSearch = async () => {
  loading.value = true;
  try {
    const { dateRange, type } = searchForm;
    const startDate = dateRange[0]?.format('YYYY-MM-DD');
    const endDate = dateRange[1]?.format('YYYY-MM-DD');

    // 如果类型为"all"，则获取所有报告，如果为"mri"或"ct"则筛选相关类型的报告
    const params: any = {
      startDate,
      endDate,
    };

    if (type === 'mri' || type === 'ct') {
      const indicatorType = type;  // 根据类型获取临床指标
      const { data: indicators } = await getClinicalIndicators('patientId', startDate, endDate, indicatorType);
      // 这里可以把 indicators 数据填充到表格或其他地方
    }

    // 获取报告列表，默认获取所有报告
    const { data: reportData } = type === 'all'
      ? await getAllReports('patientId')  // 根据患者ID获取所有报告
      : await getLastReport('patientId'); // 获取最近报告

    records.value = reportData.map((item: any) => ({
      id: item.id,
      date: item.date,
      type: item.type,
      description: item.description,
      status: item.status,
    }));

  } catch (error) {
    console.error('搜索记录失败', error);
  } finally {
    loading.value = false;
  }
};

// 重置表单
const handleReset = () => {
  searchForm.dateRange = [];
  searchForm.type = 'all';
};

// 查看记录
const viewRecord = (record: Record) => {
  console.log('查看记录:', record);
  // 在此处添加查看记录的功能
};

// 分析记录
const analyzeRecord = (record: Record) => {
  console.log('分析记录:', record);
  // 在此处添加分析记录的功能
};

// 获取初始数据（例如加载默认报告列表）
onMounted(async () => {
  await handleSearch();
});
</script>

<style scoped>
.records {
  padding: 24px;
}
</style>
