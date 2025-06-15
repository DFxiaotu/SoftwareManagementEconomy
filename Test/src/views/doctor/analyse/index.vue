<template>
  <div class="image-analyse">
    <el-card v-loading="loading">
      <!-- 患者列表 -->
      <div class="patient-list">
        <el-table :data="patientList" :row-key="record => record.userId">
          <el-table-column prop="name" label="患者姓名" />
          <el-table-column label="上次上传时间">
            <template #default="{ row }">
              {{ formatDate(row.lastGenerationDate) }}
            </template>
          </el-table-column>
          <el-table-column label="上次评估结果">
            <template #default="{ row }">
              <el-tag v-if="row.lastResult" :type="row.lastResult === '0' ? 'success' : 'danger'">
                {{ row.lastResult === '0' ? '阴性' : '阳性' }}
              </el-tag>
              <span v-else class="no-result">暂无结果</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button 
                type="primary" 
                link
                @click="showPatientDetail(row.userId)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 添加患者信息弹出框 -->
    <el-dialog
      v-model="dialogVisible"
      title="患者信息"
      width="50%"
    >
      <el-descriptions :column="3" border>
        <el-descriptions-item label="姓名">{{ selectedPatient?.name }}</el-descriptions-item>
        <el-descriptions-item label="年龄">{{ selectedPatient?.age || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ selectedPatient?.gender || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="检查日期">{{ selectedPatient?.lastGenerationDate || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="初步诊断">{{ selectedPatient?.lastResult ? (selectedPatient.lastResult === '0' ? '阴性' : '阳性') : '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="主治医生">{{ selectedPatient?.doctor || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="科室">{{ selectedPatient?.department || '暂无' }}</el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button type="primary" @click="goToUpload">
            上传新的图像
          </el-button>
          <el-button type="success" @click="goToDetail">
            生成报告
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/modules/user';
import { getPatientList, getLastReportData, getDoctorInfo } from '@/api/doctor';

interface PatientDetail {
  userId: number;
  name: string;
  age?: number;
  gender?: string;
  doctor?: string;
  department?: string;
  lastGenerationDate: string;
  lastResult: string;
}

const router = useRouter();
const patientList = ref<PatientDetail[]>([]);
const userStore = useUserStore();
const userInfo = ref(userStore.userInfo);
const doctorInfo = ref();
const loading = ref(false);
const dialogVisible = ref(false);
const selectedPatient = ref<PatientDetail | null>(null);

const formatDate = (dateStr: string) => {
  if (dateStr === '暂无记录') return dateStr;
  try {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch {
    return dateStr;
  }
};

const formatToYYYYMMDD = (dateStr: string) => {
  try {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch (error) {
    console.error('日期格式化失败:', error);
    return dateStr;
  }
};

const fetchPatientList = async () => {
  loading.value = true;
  try {
    const data = await getPatientList({ doctorId: userInfo.value.userId });
    doctorInfo.value = await getDoctorInfo({ doctorId: userInfo.value.userId });
    patientList.value = [];
    
    for (const item of data) {
      let lastReportData;
      try {
        lastReportData = await getLastReportData({ patientId: item.userId });
      } catch (error) {
        console.warn(`获取患者 ${item.userId} 的上次报告数据失败:`, error);
        lastReportData = null;
      }
      console.log('lastReportData', lastReportData);
      patientList.value.push({
        userId: item.userId,
        name: item.name,
        age: item.age,
        gender: item.gender === 1 ? '男' : '女',
        doctor: doctorInfo.value.name,
        department: doctorInfo.value.department,
        lastGenerationDate: lastReportData?.generationDate ? formatToYYYYMMDD(lastReportData.generationDate) : '暂无记录',
        lastResult: lastReportData?.result || ''
      });
      console.log('patientList', patientList.value);
    }
    
  } catch (error) {
    console.error('获取患者列表失败', error);
    ElMessage.error('获取患者列表失败');
  } finally {
    loading.value = false;
  }
};

const showPatientDetail = (patientId: number) => {
  selectedPatient.value = patientList.value.find(p => p.userId === patientId) || null;
  dialogVisible.value = true;
};

const goToUpload = () => {
  if (selectedPatient.value) {
    router.push(`/doctor/analyse/upload/${selectedPatient.value.userId}`);
    dialogVisible.value = false;
  }
};

const goToDetail = () => {
  if (selectedPatient.value) {
    router.push(`/doctor/analyse/detail/${selectedPatient.value.userId}`);
    dialogVisible.value = false;
  }
};

onMounted(() => {
  fetchPatientList();
});
</script>

<style lang="less" scoped>
.image-analyse {
  padding: 24px;

  .patient-detail {
    margin-top: 24px;
  }

  .header-info {
    margin-bottom: 24px;
  }

  .mt-4 {
    margin-top: 16px;
  }

  .tumor-slices {
    display: flex;
    gap: 16px;
    overflow-x: auto;
    padding-bottom: 12px; // 为滚动条留出空间
    
    // 优化滚动条样式
    &::-webkit-scrollbar {
      height: 8px;
    }
    
    &::-webkit-scrollbar-track {
      background: #f0f0f0;
      border-radius: 4px;
    }
    
    &::-webkit-scrollbar-thumb {
      background: #ccc;
      border-radius: 4px;
      
      &:hover {
        background: #999;
      }
    }
    
    .slice-item {
      flex: 0 0 200px; // 固定宽度，不再使用百分比
      text-align: center;
      
      .slice-image {
        width: 100%;
        height: 200px; // 固定高度，保持图片比例一致
        object-fit: contain;
        border: 1px solid #d9d9d9;
        border-radius: 4px;
      }
      
      .slice-info {
        margin-top: 8px;
        font-size: 14px;
        color: #666;
      }
    }
  }

  .patient-list {
    .no-result {
      color: #909399;
      font-size: 14px;
    }
    
    :deep(.el-tag) {
      margin: 0;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
