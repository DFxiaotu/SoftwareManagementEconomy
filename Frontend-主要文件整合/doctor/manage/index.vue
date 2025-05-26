<template>
  <div class="patient-manage">
    <el-card :body-style="{ padding: '20px' }">
      <!-- 搜索区域 -->
      <div class="search-area">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入患者姓名"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">
              搜索
            </el-button>
          </template>
        </el-input>
        
        <el-button type="primary" @click="handleAdd">
          新增患者
        </el-button>
      </div>

      <!-- 表格区域 -->
      <el-table
        :data="filteredList"
        v-loading="loading"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="gender" label="性别">
          <template #default="{ row }">
            {{ row.gender === 1 ? '男' : '女' }}
          </template>
        </el-table-column>
        <el-table-column prop="age" label="年龄" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="danger" link @click="confirmDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 添加患者对话框 -->
      <el-dialog
        v-model="addDialogVisible"
        title="添加患者"
        width="400px"
      >
        <div class="dialog-content">
          <template v-if="!tempPatientInfo">
            <el-input
              v-model="searchPatientName"
              placeholder="请输入患者姓名"
              style="width: 100%"
            />
            <el-input
              v-model="searchPatientPhone"
              placeholder="请输入患者手机号"
              style="width: 100%"
            />
          </template>
          <template v-else>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ tempPatientInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="性别">{{ tempPatientInfo.gender === 1 ? '男' : '女' }}</el-descriptions-item>
              <el-descriptions-item label="年龄">{{ tempPatientInfo.age }}</el-descriptions-item>
            </el-descriptions>
          </template>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="addDialogVisible = false">取消</el-button>
            <el-button
              type="primary"
              @click="!tempPatientInfo ? searchPatient() : confirmAddPatient()"
              :loading="searching || adding"
            >
              {{ !tempPatientInfo ? '查找' : '确认添加' }}
            </el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useUserStore } from '@/store/modules/user';
import { getPatientList, addPatient, removePatient, getPatientInfoByName } from '@/api/doctor';

interface patient {
  userId: number;
  name: string;
  gender: number;
  age: number;
}

const patientList = ref<patient[]>([]);
// const patientId = ref<number | undefined>();

const userStore = useUserStore();
const userInfo = ref(userStore.userInfo);

const addDialogVisible = ref(false);
const loading = ref(false);
const searchKeyword = ref('');
const tempPatientInfo = ref<patient>();
const searchPatientName = ref('');
const searchPatientPhone = ref('');
const searching = ref(false);
const adding = ref(false);

const fetchPatientList = async () => {
  loading.value = true;
  try {
    const response = await getPatientList({ doctorId: userInfo.value.userId });
    if (response && Array.isArray(response)) {
      patientList.value = response;
    } else {
      console.log("数据格式不符合预期");
      ElMessage.error('获取患者列表失败');
    }
  } catch (error: any) {
    console.log("userId", userInfo.value.userId);
    ElMessage.error(error.response?.data?.message || '获取患者列表失败');
    patientList.value = [];
  } finally {
    loading.value = false;
  }
};

const filteredList = computed(() => {
  const keyword = searchKeyword.value.toLowerCase();
  if (!keyword) return patientList.value;
  
  return patientList.value.filter(
    item => item.name.toLowerCase().includes(keyword)
  );
});

const handleSearch = () => {
  fetchPatientList();
};

const handleAdd = () => {
  addDialogVisible.value = true;
  resetAddDialog();
};

const searchPatient = async () => {
  if (!searchPatientName.value || !searchPatientPhone.value) {
    ElMessage.warning('请输入患者信息');
    return;
  }

  searching.value = true;
  try {
    const data = await getPatientInfoByName({ patientName: searchPatientName.value, patientPhone: searchPatientPhone.value });
    tempPatientInfo.value = data;
  } catch (error) {
    console.error('查找患者失败:', error);
    ElMessage.error('未找到该患者');
  } finally {
    searching.value = false;
  }
};

const resetAddDialog = () => {
  tempPatientInfo.value = undefined;
  searchPatientName.value = '';
  searchPatientPhone.value = '';
};

const confirmAddPatient = async () => {
  if (!tempPatientInfo.value) return;

  adding.value = true;
  try {
    await addPatient({
      doctorId: userInfo.value.userId,
      patientId: tempPatientInfo.value.userId
    });
    ElMessage.success('添加成功');
    addDialogVisible.value = false;
    fetchPatientList(); // 刷新列表
  } catch (error) {
    console.error('添加患者失败:', error);
    ElMessage.error('添加患者失败');
  } finally {
    adding.value = false;
  }
};

const confirmDelete = (patient: patient) => {
  ElMessageBox.confirm(
    `确定要删除患者 ${patient.name} 吗？`,
    '确认删除',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    handleDelete(patient.userId);
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

const handleDelete = async (patient_id: number) => {
  try {
    await removePatient({ doctorId: userInfo.value.userId, patientId: patient_id });
    ElMessage.success('删除成功');
    fetchPatientList();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '删除失败');
  }
};

onMounted(() => {
  fetchPatientList();
});
</script>

<style lang="less" scoped>
.patient-manage {
  padding: 24px;
  
  .search-area {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    
    .search-input {
      width: 300px;
    }
  }

  .dialog-content {
    margin-bottom: 20px;
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: 20px;
  }
}
</style>
