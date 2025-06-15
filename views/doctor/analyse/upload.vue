<template>
  <div class="mri-upload">
    <!-- MRI图像上传卡片 -->
    <el-card class="upload-card">
      <h2 class="upload-title">MRI 影像上传</h2>
      <el-form
        :model="formState"
        :rules="rules"
        ref="formRef"
        label-position="top"
      >
        <!-- 图像拍摄日期 -->
        <el-form-item
          label="图像拍摄日期"
          prop="imagingDate"
        >
          <el-date-picker
            v-model="formState.imagingDate"
            placeholder="选择拍摄日期"
            style="width: 100%"
            type="date"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>

        <!-- 上传图像 -->
        <div class="upload-container">
          <el-form-item
            label="T1 MRI 图像文件 (.nrrd)"
            prop="t1File"
            class="upload-item"
          >
            <el-upload
              class="upload-box"
              drag
              :before-upload="handleT1Upload"
              :file-list="fileList.t1File"
              accept=".nrrd"
              :limit="1"
              :on-remove="removeT1File"
            >
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">点击或拖拽文件上传</div>
              <div class="el-upload__tip">支持 .nrrd 格式文件</div>
            </el-upload>
          </el-form-item>

          <el-form-item
            label="T2 MRI 图像文件 (.nrrd)"
            prop="t2File"
            class="upload-item"
          >
            <el-upload
              class="upload-box"
              drag
              :before-upload="handleT2Upload"
              :file-list="fileList.t2File"
              accept=".nrrd"
              :limit="1"
              :on-remove="removeT2File"
            >
              <i class="el-icon-upload"></i>
              <div class="el-upload__text">点击或拖拽文件上传</div>
              <div class="el-upload__tip">支持 .nrrd 格式文件</div>
            </el-upload>
          </el-form-item>
        </div>

        <!-- 图像上传按钮 -->
        <div class="button-wrapper">
          <el-button type="primary" @click="handleImageSubmit">提交图像</el-button>
          <el-button @click="resetImageForm">重置</el-button>
        </div>
      </el-form>
    </el-card>

    <!-- 临床数据上传卡片 -->
    <el-card class="upload-card">
      <template #header>
        <span class="card-title">
          <el-icon><Medicine /></el-icon> 临床数据录入
        </span>
      </template>

      <el-form :model="clinicalData" ref="clinicalFormRef">
        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="拍摄医院" prop="imagingHospital">
              <el-input v-model="clinicalData.imagingHospital" placeholder="请输入拍摄医院" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="伴发肌瘤个数" prop="fibroidsPresent">
              <el-input-number v-model="clinicalData.fibroidsPresent" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平均治疗功率 (W)" prop="avgTreatmentPower">
              <el-input-number v-model="clinicalData.avgTreatmentPower" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="总能量 (J)" prop="totalEnergy">
              <el-input-number v-model="clinicalData.totalEnergy" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="治疗体积 (mm³)" prop="treatmentVolume">
              <el-input-number v-model="clinicalData.treatmentVolume" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-form-item label="孕次" prop="parity">
              <el-input-number v-model="clinicalData.parity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="流产次数" prop="miscarriageCount">
              <el-input-number v-model="clinicalData.miscarriageCount" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>血常规指标</el-divider>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="白细胞计数 (10^9/L)" prop="wbcCount">
              <el-input-number v-model="clinicalData.wbcCount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="中性粒细胞绝对值 (10^9/L)" prop="neutrophilAbsolute">
              <el-input-number v-model="clinicalData.neutrophilAbsolute" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="淋巴细胞绝对值 (10^9/L)" prop="lymphocyteAbsolute">
              <el-input-number v-model="clinicalData.lymphocyteAbsolute" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="单核细胞绝对值 (10^9/L)" prop="monocyteAbsolute">
              <el-input-number v-model="clinicalData.monocyteAbsolute" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="嗜酸性粒细胞绝对值 (10^9/L)" prop="eosinophilAbsolute">
              <el-input-number v-model="clinicalData.eosinophilAbsolute" :min="0" :precision="3" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="嗜碱性粒细胞绝对值 (10^9/L)" prop="basophilAbsolute">
              <el-input-number v-model="clinicalData.basophilAbsolute" :min="0" :precision="3" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="红细胞计数 (10^12/L)" prop="rbcCount">
              <el-input-number v-model="clinicalData.rbcCount" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="血红蛋白 (g/L)" prop="hemoglobin">
              <el-input-number v-model="clinicalData.hemoglobin" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="红细胞压积 (%)" prop="hematocrit">
              <el-input-number v-model="clinicalData.hematocrit" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="平均红细胞体积 (fL)" prop="mcv">
              <el-input-number v-model="clinicalData.mcv" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平均血红蛋白含量 (pg)" prop="mch">
              <el-input-number v-model="clinicalData.mch" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平均血红蛋白浓度 (g/L)" prop="mchc">
              <el-input-number v-model="clinicalData.mchc" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="红细胞分布宽度CV (%)" prop="rdwCv">
              <el-input-number v-model="clinicalData.rdwCv" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="红细胞分布宽度SD (fL)" prop="rdwSd">
              <el-input-number v-model="clinicalData.rdwSd" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="血小板计数 (10^9/L)" prop="plateletCount">
              <el-input-number v-model="clinicalData.plateletCount" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="血小板分布宽度 (%)" prop="pdw">
              <el-input-number v-model="clinicalData.pdw" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平均血小板体积 (fL)" prop="mpv">
              <el-input-number v-model="clinicalData.mpv" :min="0" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider>细胞百分比</el-divider>
        
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="中性粒细胞百分比 (%)" prop="neutrophilPercentage">
              <el-input-number v-model="clinicalData.neutrophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="淋巴细胞百分比 (%)" prop="lymphocytePercentage">
              <el-input-number v-model="clinicalData.lymphocytePercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单核细胞百分比 (%)" prop="monocytePercentage">
              <el-input-number v-model="clinicalData.monocytePercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="嗜酸性粒细胞百分比 (%)" prop="eosinophilPercentage">
              <el-input-number v-model="clinicalData.eosinophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="嗜碱性粒细胞百分比 (%)" prop="basophilPercentage">
              <el-input-number v-model="clinicalData.basophilPercentage" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="button-wrapper">
          <el-button type="primary" @click="handleClinicalSubmit">提交数据</el-button>
          <el-button @click="resetClinicalForm">重置</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useRoute} from 'vue-router';
import { uploadMriImage, uploadMriClinicalData } from '@/api/doctor';
import type { FormRules } from 'element-plus';

// 获取路由参数中的患者ID
const route = useRoute();
const patientId = computed(() => route.params.id as string);

// 表单状态
const formState = reactive({
  imagingDate: '',
  t1File: null as File | null,
  t2File: null as File | null,
});

// 上传文件列表
const fileList = reactive({
  t1File: [] as any[],
  t2File: [] as any[]
});

// 表单验证规则
const rules: FormRules = {
  imagingDate: [{ required: true, message: '请选择图像拍摄日期', trigger: 'change' }],
  t1File: [{ required: true, message: '请上传 T1 MRI 图像文件', trigger: 'change' }],
  t2File: [{ required: true, message: '请上传 T2 MRI 图像文件', trigger: 'change' }]
};

// 添加imageId的ref
const currentImageId = ref<number | null>(null);

// 上传 T1 文件
const handleT1Upload = (file: File) => {
  formState.t1File = file;
  fileList.t1File = [{ name: file.name, size: file.size }];
  return false;
};

// 上传 T2 文件
const handleT2Upload = (file: File) => {
  formState.t2File = file;
  fileList.t2File = [{ name: file.name, size: file.size }];
  return false;
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

// 添加临床数据状态
const clinicalData = reactive({
  imagingDate: '',
  imagingHospital: '',
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

// 修改handleImageSubmit函数
const handleImageSubmit = async () => {
  if (!formState.imagingDate || !formState.t1File || !formState.t2File) {
    ElMessage.error('请完成所有必填项');
    return;
  }

  const formData = new FormData();
  const date = new Date(formState.imagingDate);
  const formattedDate = date.toISOString().split('T')[0];
  formData.append('imagingDate', formattedDate);
  formData.append('t1File', formState.t1File as Blob);
  formData.append('t2File', formState.t2File as Blob);
  
  try {
    const response = await uploadMriImage(patientId.value, formData);
    currentImageId.value = response.imageId; // 保存返回的imageId
    ElMessage.success('图像上传成功，请继续填写临床数据');
  } catch (error) {
    console.error('上传失败:', error);
    ElMessage.error('图像上传失败，请稍后重试');
  }
};

// 修改handleClinicalSubmit函数
const handleClinicalSubmit = async () => {
  if (!currentImageId.value) {
    ElMessage.warning('请先上传MRI图像');
    return;
  }

  try {
    const clinicalDataToSubmit = {
      imagingDate: formState.imagingDate,
      imagingHospital: clinicalData.imagingHospital,
      fibroidsPresent: Number(clinicalData.fibroidsPresent) || 0,
      avgTreatmentPower: Number(clinicalData.avgTreatmentPower) || 0,
      totalEnergy: Number(clinicalData.totalEnergy) || 0,
      treatmentVolume: Number(clinicalData.treatmentVolume) || 0,
      parity: Number(clinicalData.parity) || 0,
      miscarriageCount: Number(clinicalData.miscarriageCount) || 0,
      wbcCount: Number(clinicalData.wbcCount) || 0,
      basophilAbsolute: Number(clinicalData.basophilAbsolute) || 0,
      eosinophilAbsolute: Number(clinicalData.eosinophilAbsolute) || 0,
      neutrophilAbsolute: Number(clinicalData.neutrophilAbsolute) || 0,
      lymphocyteAbsolute: Number(clinicalData.lymphocyteAbsolute) || 0,
      monocyteAbsolute: Number(clinicalData.monocyteAbsolute) || 0,
      rbcCount: Number(clinicalData.rbcCount) || 0,
      hemoglobin: Number(clinicalData.hemoglobin) || 0,
      hematocrit: Number(clinicalData.hematocrit) || 0,
      mcv: Number(clinicalData.mcv) || 0,
      mch: Number(clinicalData.mch) || 0,
      mchc: Number(clinicalData.mchc) || 0,
      rdwCv: Number(clinicalData.rdwCv) || 0,
      rdwSd: Number(clinicalData.rdwSd) || 0,
      plateletCount: Number(clinicalData.plateletCount) || 0,
      pdw: Number(clinicalData.pdw) || 0,
      mpv: Number(clinicalData.mpv) || 0,
      neutrophilPercentage: Number(clinicalData.neutrophilPercentage) || 0,
      lymphocytePercentage: Number(clinicalData.lymphocytePercentage) || 0,
      monocytePercentage: Number(clinicalData.monocytePercentage) || 0,
      eosinophilPercentage: Number(clinicalData.eosinophilPercentage) || 0,
      basophilPercentage: Number(clinicalData.basophilPercentage) || 0
    };
    console.log("clinicalDataToSubmit", clinicalDataToSubmit);
    console.log("currentImageId", currentImageId.value);

    await uploadMriClinicalData(currentImageId.value.toString(), clinicalDataToSubmit);
    ElMessage.success('临床数据提交成功');
    resetClinicalForm();
    currentImageId.value = null;
  } catch (error) {
    console.error('提交失败:', error);
    ElMessage.error('临床数据提交失败，请稍后重试');
  }
};

// 分离重置函数
const resetImageForm = () => {
  formState.imagingDate = '';
  formState.t1File = null;
  formState.t2File = null;
  fileList.t1File = [];
  fileList.t2File = [];
};

const resetClinicalForm = () => {
  Object.keys(clinicalData).forEach(key => {
    clinicalData[key] = 0;
  });
  clinicalData.imagingHospital = '';
};

// const router = useRouter();
</script>

<style scoped>
.mri-upload {
  padding: 24px;
}

.upload-card {
  margin-bottom: 24px;
}

.upload-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
}

.upload-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.upload-item {
  flex: 1;
  margin-right: 10px;
}

.upload-box {
  width: 100%;
  border: 2px dashed #d9d9d9;
  border-radius: 6px;
  text-align: center;
  padding: 40px 20px;
  background-color: #f9f9f9;
}

.el-upload__text {
  font-size: 16px;
  color: #606266;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
}

.button-wrapper {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 10px;
}

.el-button {
  min-width: 100px;
}

.clinical-data {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.el-input-number {
  width: 180px;
}

.el-textarea {
  width: 100%;
  max-width: 400px;
}

.form-row {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 18px;
}

.form-row .el-form-item {
  flex: 1;
  margin-bottom: 0;
}

.full-width {
  width: 100%;
}

.el-input-number {
  width: 100%;
}

.el-textarea {
  width: 100%;
}
</style>