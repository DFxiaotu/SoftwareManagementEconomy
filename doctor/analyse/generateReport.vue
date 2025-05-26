<template>
  <el-dialog
    v-model="dialogVisible"
    title="生成报告"
    width="60%"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div class="report-generate">
      <div class="report-section">
        <h3>MRI 影像</h3>
        <div class="image-preview">
          <img :src="imageUrl" alt="MRI影像" />
        </div>
      </div>

      <div class="report-section">
        <h3>临床数据</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="伴发肌瘤个数">{{ clinicalData?.fibroids_present }}</el-descriptions-item>
          <el-descriptions-item label="平均治疗功率">{{ clinicalData?.avg_treatment_power }} W</el-descriptions-item>
          <el-descriptions-item label="总能量">{{ clinicalData?.total_energy }} J</el-descriptions-item>
          <el-descriptions-item label="治疗体积">{{ clinicalData?.treatment_volume }} mm³</el-descriptions-item>
          <el-descriptions-item label="孕次">{{ clinicalData?.parity }}</el-descriptions-item>
          <el-descriptions-item label="流产次数">{{ clinicalData?.miscarriage_count }}</el-descriptions-item>
        </el-descriptions>
      </div>

      <div class="report-section">
        <h3>AI 辅助诊断</h3>
        <div v-if="!aiDiagnosisResult" class="ai-diagnosis-actions">
          <el-button 
            type="primary" 
            @click="handleAIDiagnosis"
            :loading="aiDiagnosisLoading"
            size="large"
          >
            {{ aiDiagnosisLoading ? '正在分析中...' : '开始AI辅助诊断' }}
          </el-button>
        </div>
        <div v-else class="ai-diagnosis">
          <p class="diagnosis-result">
            诊断结果：{{ aiDiagnosisResult.prediction === 1 ? '建议进行治疗' : '建议继续观察' }}
          </p>
          <p class="diagnosis-probability">
            置信度：{{ (aiDiagnosisResult.probability * 100).toFixed(2) }}%
          </p>
        </div>
      </div>

      <div class="report-section">
        <h3>医生诊断结果</h3>
        <el-input
          v-model="doctorDiagnosis"
          type="textarea"
          :rows="3"
          placeholder="请输入您的诊断结果..."
          :disabled="!aiDiagnosisResult"
        />
        <div class="comment-tip" v-if="!aiDiagnosisResult">
          请先完成AI辅助诊断后再输入诊断结果
        </div>
      </div>

      <div class="report-section">
        <h3>医生建议</h3>
        <el-input
          v-model="doctorComment"
          type="textarea"
          :rows="4"
          placeholder="请输入您的治疗建议..."
          :disabled="!aiDiagnosisResult"
        />
        <div class="comment-tip" v-if="!aiDiagnosisResult">
          请先完成AI辅助诊断后再添加建议
        </div>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="submitReport"
          :loading="loading"
          :disabled="!canConfirmReport"
        >
          确认生成报告
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { analyseReport, generateReport } from '@/api/doctor';
import { useUserStore } from '@/store/modules/user';

interface Props {
  modelValue: boolean;
  imageUrl: string;
  imageId: number;
  clinicalData: {
    fibroids_present: number;
    avg_treatment_power: number;
    total_energy: number;
    treatment_volume: number;
    parity: number;
    miscarriage_count: number;
  };
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue', 'success']);
const userStore = useUserStore();

const aiDiagnosisLoading = ref(false);
const aiDiagnosisResult = ref<{ prediction: number; probability: number } | null>(null);
const doctorDiagnosis = ref('');
const doctorComment = ref('');
const loading = ref(false);

const canConfirmReport = computed(() => {
  return aiDiagnosisResult.value && 
         doctorDiagnosis.value.trim().length > 0 && 
         doctorComment.value.trim().length > 0;
});

// AI辅助诊断
const handleAIDiagnosis = async () => {
  try {
    aiDiagnosisLoading.value = true;
    const response = await analyseReport({ imageId: props.imageId });
    console.log('AI response', response);
    aiDiagnosisResult.value = {
      prediction: response.prediction,
      probability: response.probability
    };
    ElMessage.success('AI诊断完成');
  } catch (error) {
    console.error('AI诊断失败:', error);
    ElMessage.error('AI诊断失败，请稍后重试');
  } finally {
    aiDiagnosisLoading.value = false;
  }
};

// 获取报告数据
const getReportData = () => {
  if (!canConfirmReport.value) {
    return null;
  }
  
  return {
    aiDiagnosis: aiDiagnosisResult.value,
    doctorDiagnosis: doctorDiagnosis.value,
    doctorComment: doctorComment.value,
    imageId: props.imageId
  };
};

// 提交报告
const submitReport = async () => {
  if (!canConfirmReport.value) {
    ElMessage.warning('请先完成AI辅助诊断并填写诊断结果和建议');
    return;
  }

  try {
    loading.value = true;
    const formData = new FormData();
    formData.append('imageId', props.imageId.toString());
    formData.append('doctorId', userStore.userInfo.userId.toString());
    formData.append('radiomicComment', doctorDiagnosis.value);
    formData.append('therapyComment', doctorComment.value);
    // 从本地读取两个ROI文件
    try {
      // 通过 fetch 获取文件
      const roi1Response = await fetch('/Z1.nrrd');
      const roi2Response = await fetch('/Z2.nrrd');

      const roi1File = new File([await roi1Response.blob()], 'roi_t1.nrrd');
      const roi2File = new File([await roi2Response.blob()], 'roi_t2.nrrd');
      // 将文件添加到 FormData
      formData.append('roi_t1', new Blob([roi1File], {type: 'application/octet-stream'}), 'roi_t1.nrrd');
      formData.append('roi_t2', new Blob([roi2File], {type: 'application/octet-stream'}), 'roi_t2.nrrd');

    } catch (error) {
      console.error('读取ROI文件失败:', error);
      ElMessage.error('读取ROI文件失败');
      throw error;
    }

    for (let pair of formData.entries()) {
        console.log(pair[0], pair[1]); // key, value
    }
    await generateReport(formData);
    ElMessage.success('报告生成成功');
    emit('success');
  } catch (error) {
    console.error('生成报告失败:', error);
    ElMessage.error('生成报告失败，请稍后重试');
  } finally {
    loading.value = false;
  }
};

// 弹窗可见性
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 关闭处理
const handleClose = () => {
  dialogVisible.value = false;
};

// 暴露方法给父组件
defineExpose({
  getReportData,
  canConfirmReport,
  submitReport
});
</script>

<style lang="less" scoped>
.report-generate {
  .report-section {
    margin-bottom: 24px;

    h3 {
      font-size: 16px;
      font-weight: 500;
      margin: 0 0 16px 0;
      color: #303133;
    }

    .image-preview {
      text-align: center;
      margin: 20px 0;
      
      img {
        max-width: 80%;
        max-height: 400px;
        object-fit: contain;
        border: 2px solid var(--el-border-color);
        border-radius: 8px;
        box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
      }
    }

    .ai-diagnosis {
      background: #f5f7fa;
      border-radius: 8px;
      padding: 20px;
      text-align: center;
      margin: 20px 0;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
      
      .diagnosis-result {
        font-size: 18px;
        color: #303133;
        margin-bottom: 12px;
        font-weight: 500;
      }
      
      .diagnosis-probability {
        font-size: 14px;
        color: #606266;
      }
    }
    
    .ai-diagnosis-actions {
      display: flex;
      justify-content: center;
      padding: 40px;
      background: #f5f7fa;
      border-radius: 8px;
      margin: 20px 0;

      .el-button {
        padding: 12px 24px;
        font-size: 16px;
      }
    }

    .comment-tip {
      margin-top: 8px;
      color: #909399;
      font-size: 12px;
      text-align: center;
    }
  }
}
</style> 