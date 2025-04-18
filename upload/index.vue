<template>
  <div class="mri-upload">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2><cloud-upload-outlined /> MRI 影像上传</h2>
    </div>

    <a-card class="upload-card">
      <template #title>
        <span class="card-title">
          <file-image-outlined /> MRI 影像上传
        </span>
      </template>
      <template #extra>
        <a-button type="link" @click="resetForm">
          <reload-outlined /> 重置表单
        </a-button>
      </template>

      <a-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        layout="vertical"
        class="upload-form"
      >
        <!-- 图像拍摄日期 -->
        <a-row :gutter="[24, 24]">
          <a-col :span="24">
            <a-form-item
              label="图像拍摄日期"
              name="imagingDate"
              :rules="rules.imagingDate"
            >
              <a-date-picker
                v-model:value="formState.imagingDate"
                @change="onDateChange"
                placeholder="选择拍摄日期"
                style="width: 100%"
                :disabled-date="disabledDate"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <!-- 上传 T1 图像 -->
          <a-col :span="12">
            <a-form-item
              label="T1 MRI 图像文件"
              name="t1File"
              :rules="rules.t1File"
              class="upload-item"
            >
              <div class="upload-box">
                <a-upload
                  :before-upload="handleT1Upload"
                  :file-list="fileList.t1File"
                  accept=".nrrd"
                  :maxCount="1"
                  :on-remove="removeT1File"
                >
                  <div class="upload-trigger">
                    <p class="upload-icon">
                      <inbox-outlined />
                    </p>
                    <p class="upload-text">点击或拖拽文件上传</p>
                    <p class="upload-hint">支持 .nrrd 格式文件</p>
                  </div>
                </a-upload>
              </div>
            </a-form-item>
          </a-col>

          <!-- 上传 T2 图像 -->
          <a-col :span="12">
            <a-form-item
              label="T2 MRI 图像文件"
              name="t2File"
              :rules="rules.t2File"
              class="upload-item"
            >
              <div class="upload-box">
                <a-upload
                  :before-upload="handleT2Upload"
                  :file-list="fileList.t2File"
                  accept=".nrrd"
                  :maxCount="1"
                  :on-remove="removeT2File"
                >
                  <div class="upload-trigger">
                    <p class="upload-icon">
                      <inbox-outlined />
                    </p>
                    <p class="upload-text">点击或拖拽文件上传</p>
                    <p class="upload-hint">支持 .nrrd 格式文件</p>
                  </div>
                </a-upload>
              </div>
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-card>

    <!-- 临床数据录入 -->
    <a-card class="clinical-data-card" style="margin-top: 24px;">
      <template #title>
        <span class="card-title">
          <medicine-box-outlined /> 临床数据录入
        </span>
      </template>

      <a-form layout="vertical" :model="clinicalData" ref="clinicalFormRef">
        <a-row :gutter="[24, 24]">
          <a-col :span="12">
            <a-form-item label="拍摄医院" name="imagingHospital">
              <a-input v-model:value="clinicalData.imagingHospital" placeholder="请输入拍摄医院" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="分析结果" name="result">
              <a-select v-model:value="clinicalData.result">
                <a-select-option :value="1">正常</a-select-option>
                <a-select-option :value="2">异常</a-select-option>
                <a-select-option :value="3">其他</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="12">
            <a-form-item label="伴发肌瘤个数" name="fibroidsPresent">
              <a-input-number v-model:value="clinicalData.fibroidsPresent" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="平均治疗功率 (W)" name="avgTreatmentPower">
              <a-input-number v-model:value="clinicalData.avgTreatmentPower" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="12">
            <a-form-item label="总能量 (J)" name="totalEnergy">
              <a-input-number v-model:value="clinicalData.totalEnergy" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="治疗体积 (mm³)" name="treatmentVolume">
              <a-input-number v-model:value="clinicalData.treatmentVolume" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="12">
            <a-form-item label="孕次" name="parity">
              <a-input-number v-model:value="clinicalData.parity" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="流产次数" name="miscarriageCount">
              <a-input-number v-model:value="clinicalData.miscarriageCount" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 血常规指标 -->
        <a-divider>血常规指标</a-divider>

        <!-- 白细胞相关指标 -->
        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="白细胞计数 (10^9/L)" name="wbcCount">
              <a-input-number v-model:value="clinicalData.wbcCount" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="中性粒细胞绝对值 (10^9/L)" name="neutrophilAbsolute">
              <a-input-number v-model:value="clinicalData.neutrophilAbsolute" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="淋巴细胞绝对值 (10^9/L)" name="lymphocyteAbsolute">
              <a-input-number v-model:value="clinicalData.lymphocyteAbsolute" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="单核细胞绝对值 (10^9/L)" name="monocyteAbsolute">
              <a-input-number v-model:value="clinicalData.monocyteAbsolute" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="嗜酸性粒细胞绝对值 (10^9/L)" name="eosinophilAbsolute">
              <a-input-number v-model:value="clinicalData.eosinophilAbsolute" :min="0" :precision="3" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="嗜碱性粒细胞绝对值 (10^9/L)" name="basophilAbsolute">
              <a-input-number v-model:value="clinicalData.basophilAbsolute" :min="0" :precision="3" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 红细胞相关指标 -->
        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="红细胞计数 (10^12/L)" name="rbcCount">
              <a-input-number v-model:value="clinicalData.rbcCount" :min="0" :precision="2" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="血红蛋白 (g/L)" name="hemoglobin">
              <a-input-number v-model:value="clinicalData.hemoglobin" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="红细胞压积 (%)" name="hematocrit">
              <a-input-number v-model:value="clinicalData.hematocrit" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="平均红细胞体积 (fL)" name="mcv">
              <a-input-number v-model:value="clinicalData.mcv" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="平均血红蛋白含量 (pg)" name="mch">
              <a-input-number v-model:value="clinicalData.mch" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="平均血红蛋白浓度 (g/L)" name="mchc">
              <a-input-number v-model:value="clinicalData.mchc" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 红细胞分布宽度和血小板相关指标 -->
        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="红细胞分布宽度CV (%)" name="rdwCv">
              <a-input-number v-model:value="clinicalData.rdwCv" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="红细胞分布宽度SD (fL)" name="rdwSd">
              <a-input-number v-model:value="clinicalData.rdwSd" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="血小板计数 (10^9/L)" name="plateletCount">
              <a-input-number v-model:value="clinicalData.plateletCount" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 血小板相关指标和细胞百分比 -->
        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="血小板分布宽度 (%)" name="pdw">
              <a-input-number v-model:value="clinicalData.pdw" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="平均血小板体积 (fL)" name="mpv">
              <a-input-number v-model:value="clinicalData.mpv" :min="0" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 细胞百分比 -->
        <a-divider>细胞百分比</a-divider>
        
        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="中性粒细胞百分比 (%)" name="neutrophilPercentage">
              <a-input-number v-model:value="clinicalData.neutrophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="淋巴细胞百分比 (%)" name="lymphocytePercentage">
              <a-input-number v-model:value="clinicalData.lymphocytePercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="单核细胞百分比 (%)" name="monocytePercentage">
              <a-input-number v-model:value="clinicalData.monocytePercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="[24, 24]">
          <a-col :span="8">
            <a-form-item label="嗜酸性粒细胞百分比 (%)" name="eosinophilPercentage">
              <a-input-number v-model:value="clinicalData.eosinophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="嗜碱性粒细胞百分比 (%)" name="basophilPercentage">
              <a-input-number v-model:value="clinicalData.basophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-card>

    <!-- 统一的提交按钮区域 -->
    <div class="form-actions-container">
      <a-card>
        <div class="form-actions">
          <a-button 
            type="primary" 
            :loading="uploading || submitting" 
            @click="handleSubmitAll"
          >
            <template #icon><cloud-upload-outlined /></template>
            提交所有数据
          </a-button>
          <a-button 
            @click="resetAll" 
            :disabled="uploading || submitting"
          >
            <template #icon><reload-outlined /></template>
            重置所有数据
          </a-button>
        </div>
      </a-card>
    </div>

    <!-- 上传说明 -->
    <a-card class="tips-card">
      <template #title>
        <span class="card-title">
          <info-circle-outlined /> 上传说明
        </span>
      </template>
      <a-alert
        type="info"
        show-icon
        :message="'注意事项'"
        :description="'1. 请确保上传的文件格式为 .nrrd\n2. 文件大小不超过 100MB\n3. 请选择正确的拍摄日期'"
        style="margin-bottom: 16px"
      />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { message } from 'ant-design-vue';
import { uploadMriImage, uploadMriClinicalData } from '@/api/modules/patient';
import dayjs from 'dayjs';
import {
  CloudUploadOutlined,
  FileImageOutlined,
  InboxOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  MedicineBoxOutlined,
  SaveOutlined
} from '@ant-design/icons-vue';

// 创建组件引用
const formRef = ref();
const uploading = ref(false);

// 禁用未来日期
const disabledDate = (current: dayjs.Dayjs) => {
  return current && current > dayjs().endOf('day');
};

// 表单状态
const formState = reactive({
  imagingDate: '',
  t1File: null,
  t2File: null
});

// 文件列表
const fileList = reactive({
  t1File: [],
  t2File: []
});

// 表单验证规则
const rules = {
  imagingDate: [{ required: true, message: '请选择图像拍摄日期', trigger: 'change' }],
  t1File: [{ required: true, message: '请上传 T1 MRI 图像文件', trigger: 'change' }],
  t2File: [{ required: true, message: '请上传 T2 MRI 图像文件', trigger: 'change' }],
};

// 重置 MRI 上传表单
const resetMriForm = () => {
  formState.imagingDate = '';
  formState.t1File = null;
  formState.t2File = null;
  fileList.t1File = [];
  fileList.t2File = [];
};

// 日期处理
const onDateChange = (date: dayjs.Dayjs | null, dateString: string) => {
  if (date) {
    formState.imagingDate = dateString;
  } else {
    formState.imagingDate = '';
  }
};

// 上传 T1 文件
const handleT1Upload = (file: File) => {
  formState.t1File = file;
  fileList.t1File = [file];
  return false; // 阻止默认上传行为
};

// 上传 T2 文件
const handleT2Upload = (file: File) => {
  formState.t2File = file;
  fileList.t2File = [file];
  return false; // 阻止默认上传行为
};

// 移除 T1 文件
const removeT1File = () => {
  formState.t1File = null;
  fileList.t1File = [];
};

// 移除 T2 文件
const removeT2File = () => {
  formState.t2File = null;
  fileList.t2File = [];
};

// 合并提交函数
const handleSubmitAll = async () => {
  try {
    await formRef.value?.validate();
    await clinicalFormRef.value?.validate();
    
    uploading.value = true;
    submitting.value = true;

    // 1. 上传 MRI 图像
    const formData = new FormData();
    formData.append('imagingDate', formState.imagingDate);
    formData.append('t1File', formState.t1File as Blob);
    formData.append('t2File', formState.t2File as Blob);

    const patientId = getLoggedInPatientId();
    if (!patientId) {
      throw new Error('无法获取患者ID');
    }
    
    // 上传图像
    const uploadResponse = await uploadMriImage(patientId, formData);
    console.log('图像上传响应:', uploadResponse);
    
    if (!uploadResponse?.imageId) {
      throw new Error('图像上传失败');
    }

    // 2. 上传所有临床数据
    const clinicalDataToSubmit = {
      imagingDate: formState.imagingDate,
      imagingHospital: clinicalData.imagingHospital,
      result: Number(clinicalData.result),
      fibroidsPresent: Number(clinicalData.fibroidsPresent),
      avgTreatmentPower: Number(clinicalData.avgTreatmentPower),
      totalEnergy: Number(clinicalData.totalEnergy),
      treatmentVolume: Number(clinicalData.treatmentVolume),
      parity: Number(clinicalData.parity),
      miscarriageCount: Number(clinicalData.miscarriageCount),
      wbcCount: Number(clinicalData.wbcCount),
      basophilAbsolute: Number(clinicalData.basophilAbsolute),
      eosinophilAbsolute: Number(clinicalData.eosinophilAbsolute),
      neutrophilAbsolute: Number(clinicalData.neutrophilAbsolute),
      lymphocyteAbsolute: Number(clinicalData.lymphocyteAbsolute),
      monocyteAbsolute: Number(clinicalData.monocyteAbsolute),
      rbcCount: Number(clinicalData.rbcCount),
      hemoglobin: Number(clinicalData.hemoglobin),
      hematocrit: Number(clinicalData.hematocrit),
      mcv: Number(clinicalData.mcv),
      mch: Number(clinicalData.mch),
      mchc: Number(clinicalData.mchc),
      rdwCv: Number(clinicalData.rdwCv),
      rdwSd: Number(clinicalData.rdwSd),
      plateletCount: Number(clinicalData.plateletCount),
      pdw: Number(clinicalData.pdw),
      mpv: Number(clinicalData.mpv),
      neutrophilPercentage: Number(clinicalData.neutrophilPercentage),
      lymphocytePercentage: Number(clinicalData.lymphocytePercentage),
      monocytePercentage: Number(clinicalData.monocytePercentage),
      eosinophilPercentage: Number(clinicalData.eosinophilPercentage),
      basophilPercentage: Number(clinicalData.basophilPercentage)
    };

    console.log('准备上传的临床数据:', clinicalDataToSubmit);
    await uploadMriClinicalData(uploadResponse.imageId, clinicalDataToSubmit);
    
    message.success('所有数据上传成功！');
    resetAll();
  } catch (error) {
    console.error('上传失败:', error);
    message.error(error instanceof Error ? error.message : '数据上传失败，请重试');
  } finally {
    uploading.value = false;
    submitting.value = false;
  }
};

// 统一的重置函数
const resetAll = () => {
  resetMriForm(); // 使用新的重置 MRI 表单函数
  resetClinicalData(); // 保持原有的临床数据重置函数
};

// 获取已登录患者 ID（示例实现）
const getLoggedInPatientId = () => {
  try {
    const user = JSON.parse(localStorage.getItem('__persisted__user') || '{}');
    const token = user.token;
    const base64Payload = token.split('.')[1];
    const payload = JSON.parse(atob(base64Payload));
    return payload.sub; // 提取患者 ID
  } catch (error) {
    console.error('无法获取患者 ID:', error);
    return null;
  }
};

// 临床数据状态
const clinicalData = reactive({
  imagingDate: '',
  imagingHospital: '',
  result: 1,
  fibroidsPresent: 0,
  avgTreatmentPower: 0,
  totalEnergy: 0,
  treatmentVolume: 0,
  parity: 0,
  miscarriageCount: 0,
  wbcCount: 0,
  basophilAbsolute: 0,
  eosinophilAbsolute: 0,
  neutrophilAbsolute: 0,
  lymphocyteAbsolute: 0,
  monocyteAbsolute: 0,
  rbcCount: 0,
  hemoglobin: 0,
  hematocrit: 0,
  mcv: 0,
  mch: 0,
  mchc: 0,
  rdwCv: 0,
  rdwSd: 0,
  plateletCount: 0,
  pdw: 0,
  mpv: 0,
  neutrophilPercentage: 0,
  lymphocytePercentage: 0,
  monocytePercentage: 0,
  eosinophilPercentage: 0,
  basophilPercentage: 0
});

const clinicalFormRef = ref();
const submitting = ref(false);

// 提交临床数据
const submitClinicalData = async () => {
  if (!currentImageId.value) {
    message.error('请先上传MRI图像');
    return;
  }

  try {
    submitting.value = true;
    // 设置拍摄日期为图像拍摄日期
    clinicalData.imagingDate = formState.imagingDate;
    
    await uploadMriClinicalData(currentImageId.value, clinicalData);
    message.success('临床数据提交成功！');
    resetClinicalData();
  } catch (error) {
    console.error('提交临床数据失败:', error);
    message.error('提交临床数据失败，请重试');
  } finally {
    submitting.value = false;
  }
};

// 重置临床数据
const resetClinicalData = () => {
  Object.keys(clinicalData).forEach(key => {
    if (typeof clinicalData[key] === 'number') {
      clinicalData[key] = 0;
    } else {
      clinicalData[key] = '';
    }
  });
};

// 添加当前图像ID的引用
const currentImageId = ref('');
</script>

<style scoped>
.mri-upload {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  padding: 16px 24px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.page-header h2 {
  margin: 0;
  color: #1890ff;
}

.upload-card {
  margin-bottom: 24px;
}

.tips-card {
  background: #fff;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
}

.upload-form {
  max-width: 100%;
}

.upload-item {
  margin-bottom: 24px;
}

.upload-box {
  background: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.upload-box:hover {
  border-color: #1890ff;
}

.upload-trigger {
  padding: 24px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #1890ff;
  margin-bottom: 16px;
}

.upload-text {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 4px;
}

.upload-hint {
  color: rgba(0, 0, 0, 0.45);
}

.form-actions-container {
  margin-top: 24px;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

:deep(.ant-upload-list) {
  margin-top: 16px;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}

:deep(.ant-alert-description) {
  white-space: pre-line;
}
</style>
