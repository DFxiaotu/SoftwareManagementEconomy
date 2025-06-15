<template>
  <div 
    class="analyse-detail" 
    v-loading="loading"
    element-loading-text="加载中..."
    element-loading-spinner="el-icon-loading"
    element-loading-background="rgba(255, 255, 255, 0.8)"
  >
    <!-- 左侧主要内容区域 -->
    <div class="main-content">
      <el-card>
        <div class="page-header">
            <h2>MRI 影像分析报告</h2>
            <el-button type="primary" class="back-button" @click="goBack">
              返回列表
            </el-button>
        </div>

        <!-- 患者基本信息 -->
        <el-descriptions title="患者信息" :column="3" border>
          <el-descriptions-item label="姓名">{{ patientInfo?.name }}</el-descriptions-item>
          <el-descriptions-item label="年龄">{{ patientInfo?.age }}</el-descriptions-item>
          <el-descriptions-item label="性别">{{ patientInfo?.gender }}</el-descriptions-item>
          <el-descriptions-item label="最近检查日期">{{ patientInfo?.examDate }}</el-descriptions-item>
          <el-descriptions-item label="主治医生">{{ patientInfo?.doctor }}</el-descriptions-item>
          <el-descriptions-item label="科室">{{ patientInfo?.department }}</el-descriptions-item>
        </el-descriptions>

        <!-- MRI图像展示区域 -->
        <div class="mri-viewer" v-if="mriList.length > 0">
          <div class="date-filter">
            <div class="filter-group">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
              <el-button 
                type="primary" 
                @click="handleDateRangeChange(dateRange)"
                :loading="loading"
              >
                筛选
              </el-button>
            </div>
          </div>

          <div class="viewer-header">
            <h3>MRI 影像查看</h3>
            <div class="viewer-controls">
              <div class="date-display">
                {{ formatDate(mriList[currentGroupIndex]?.imageDate) }}
              </div>
              <div class="pagination-group">
                <el-button 
                  :disabled="currentGroupIndex === 0" 
                  @click="prevGroup"
                  class="nav-button"
                >
                  <el-icon><ArrowLeft /></el-icon>
                </el-button>
                <span class="page-info">{{ currentGroupIndex + 1 }}/{{ mriList.length }}</span>
                <el-button 
                  :disabled="currentGroupIndex === mriList.length - 1" 
                  @click="nextGroup"
                  class="nav-button"
                >
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <div class="sequence-controls">
            <el-radio-group v-model="currentSequence" size="large">
              <el-radio-button label="t1">T1序列</el-radio-button>
              <el-radio-button label="t2">T2序列</el-radio-button>
            </el-radio-group>
            <span class="slice-info">切片 {{ currentSliceIndex + 1 }}/{{ currentSlices.length }}</span>
          </div>

          <div class="image-display">
            <div class="image-controls">
              <el-button 
                :disabled="currentSliceIndex === 0" 
                @click="prevSlice"
              >
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              
              <div class="images-container">
                <!-- 前一张图片 -->
                <div class="side-image prev-image" v-if="currentSliceIndex > 0">
                  <img 
                    :src="getImageUrl(currentSlices[currentSliceIndex - 1])" 
                    alt="前一张切片"
                  />
                </div>
                
                <!-- 当前图片 -->
                <div class="main-image">
                  <div class="image-wrapper">
                    <img 
                      v-if="currentSliceUrl"
                      :src="getImageUrl(currentSliceUrl)" 
                      alt="当前切片" 
                    />
                    <div v-else class="no-image">暂无图像</div>
                    <div class="button-wrapper">
                      <el-button 
                        type="primary" 
                        @click="openEditDialog"
                      >
                        编辑当前切片
                      </el-button>
                    </div>
                  </div>
                </div>
                
                <!-- 后一张图片 -->
                <div class="side-image next-image" v-if="currentSliceIndex < currentSlices.length - 1">
                  <img 
                    :src="getImageUrl(currentSlices[currentSliceIndex + 1])" 
                    alt="后一张切片"
                  />
                </div>
              </div>
              
              <el-button 
                :disabled="currentSliceIndex === currentSlices.length - 1" 
                @click="nextSlice"
              >
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </div>

        <!-- 编辑对话框 -->
        <el-dialog
          v-model="editDialogVisible"
          width="90%"
          :close-on-click-modal="false"
        >
          <EditComponent 
            :image-url="getImageUrl(currentSliceUrl)"
            :sequence-type="currentSequence"
            :slice-index="currentSliceIndex"
            @save="handleEditSave" 
            @cancel="editDialogVisible = false"
          />
        </el-dialog>
      </el-card>
    </div>

    <!-- 右侧信息栏 -->
    <div class="side-panel">
      <el-card class="report-card">
        <template #header>
          <div class="card-header">
            <span>报告结果</span>
            <!-- 添加报告详情按钮 -->
            <div class="report-actions">
              <el-button type="primary" @click="showReportDetail" v-if="currentGroup?.hasReport">
                <el-icon><Document /></el-icon>
                查看完整报告
              </el-button>
            </div>
          </div>
        </template>
        <div class="report-content">
          <template v-if="currentGroup?.hasReport">
            <div class="result-section">
              <div class="emoji-container">
                <span class="large-emoji">
                  {{ currentReport?.result === '0' ? '😊' : '💊' }}
                </span>
                <span class="result-text">
                  {{ currentReport?.result === '0' ? '阴性' : '阳性' }}
                </span>
              </div>
            </div>

            <el-divider />
            <!-- 诊断结果部分 -->
            <div class="diagnosis-section">
              <h4>诊断结果</h4>
              <p>{{ currentReport?.radiomicComment }}</p>
            </div>
          </template>
          <template v-else>
            <div class="no-report">
              <el-empty description="暂无报告">
                <el-button 
                  type="primary" 
                  @click="handleGenerateReport"
                  :loading="loading"
                >
                  生成报告
                </el-button>
              </el-empty>
            </div>
          </template>
        </div>
      </el-card>

      <!-- MRI 参数 -->
      <el-card class="params-card">
        <template #header>
          <div class="card-header">
            <span>临床数据</span>
            <span class="date">{{ formatDate(currentGroup?.imageDate) }}</span>
          </div>
        </template>
        <div class="params-list" v-if="currentGroup?.clinicalData">
          <div class="param-item">
            <span class="label">伴发肌瘤个数</span>
            <span class="value">{{ currentGroup.clinicalData.fibroids_present }}</span>
          </div>
          <div class="param-item">
            <span class="label">平均治疗功率</span>
            <span class="value">{{ currentGroup.clinicalData.avg_treatment_power }} W</span>
          </div>
          <div class="param-item">
            <span class="label">总能量</span>
            <span class="value">{{ currentGroup.clinicalData.total_energy }} J</span>
          </div>
          <div class="param-item">
            <span class="label">治疗体积</span>
            <span class="value">{{ currentGroup.clinicalData.treatment_volume }} mm³</span>
          </div>
          <div class="param-item">
            <span class="label">孕次</span>
            <span class="value">{{ currentGroup.clinicalData.parity }}</span>
          </div>
          <div class="param-item">
            <span class="label">流产次数</span>
            <span class="value">{{ currentGroup.clinicalData.miscarriage_count }}</span>
          </div>
          <div class="param-item blood-routine" v-if="bloodRoutineData">
            <div class="blood-routine-header">
              <div class="blood-routine-title">
                <span>血常规检查结果</span>
                <el-button 
                  type="primary" 
                  link
                  @click="showBloodRoutine = !showBloodRoutine"
                >
                  {{ showBloodRoutine ? '收起' : '展开' }}
                  <el-icon class="el-icon--right">
                    <component :is="showBloodRoutine ? 'ArrowUp' : 'ArrowDown'" />
                  </el-icon>
                </el-button>
              </div>
            </div>
            <div v-show="showBloodRoutine" class="value blood-routine-list">
              <template v-if="bloodRoutineData">
                <div v-if="bloodRoutineData.wbc_count" class="blood-item">
                  <span class="item-label">白细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.wbc_count }}</span>
                </div>
                <div v-if="bloodRoutineData.basophil_absolute" class="blood-item">
                  <span class="item-label">嗜碱性粒细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.basophil_absolute }}</span>
                </div>
                <div v-if="bloodRoutineData.eosinophil_absolute" class="blood-item">
                  <span class="item-label">嗜酸性粒细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.eosinophil_absolute }}</span>
                </div>
                <div v-if="bloodRoutineData.neutrophil_absolute" class="blood-item">
                  <span class="item-label">中性粒细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.neutrophil_absolute }}</span>
                </div>
                <div v-if="bloodRoutineData.lymphocyte_absolute" class="blood-item">
                  <span class="item-label">淋巴细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.lymphocyte_absolute }}</span>
                </div>
                <div v-if="bloodRoutineData.monocyte_absolute" class="blood-item">
                  <span class="item-label">单核细胞计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.monocyte_absolute }}</span>
                </div>
                <div v-if="bloodRoutineData.rbc_count" class="blood-item">
                  <span class="item-label">红细胞计数 (×10¹²/L)</span>
                  <span class="item-value">{{ bloodRoutineData.rbc_count }}</span>
                </div>
                <div v-if="bloodRoutineData.hemoglobin" class="blood-item">
                  <span class="item-label">血红蛋白 (g/L)</span>
                  <span class="item-value">{{ bloodRoutineData.hemoglobin }}</span>
                </div>
                <div v-if="bloodRoutineData.hematocrit" class="blood-item">
                  <span class="item-label">红细胞压积 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.hematocrit }}</span>
                </div>
                <div v-if="bloodRoutineData.mcv" class="blood-item">
                  <span class="item-label">平均红细胞体积 (fL)</span>
                  <span class="item-value">{{ bloodRoutineData.mcv }}</span>
                </div>
                <div v-if="bloodRoutineData.mch" class="blood-item">
                  <span class="item-label">平均血红蛋白含量 (pg)</span>
                  <span class="item-value">{{ bloodRoutineData.mch }}</span>
                </div>
                <div v-if="bloodRoutineData.mchc" class="blood-item">
                  <span class="item-label">平均血红蛋白浓度 (g/L)</span>
                  <span class="item-value">{{ bloodRoutineData.mchc }}</span>
                </div>
                <div v-if="bloodRoutineData.rdw_cv" class="blood-item">
                  <span class="item-label">红细胞分布宽度-CV (%)</span>
                  <span class="item-value">{{ bloodRoutineData.rdw_cv }}</span>
                </div>
                <div v-if="bloodRoutineData.rdw_sd" class="blood-item">
                  <span class="item-label">红细胞分布宽度-SD (fL)</span>
                  <span class="item-value">{{ bloodRoutineData.rdw_sd }}</span>
                </div>
                <div v-if="bloodRoutineData.platelet_count" class="blood-item">
                  <span class="item-label">血小板计数 (×10⁹/L)</span>
                  <span class="item-value">{{ bloodRoutineData.platelet_count }}</span>
                </div>
                <div v-if="bloodRoutineData.pdw" class="blood-item">
                  <span class="item-label">血小板分布宽度 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.pdw }}</span>
                </div>
                <div v-if="bloodRoutineData.mpv" class="blood-item">
                  <span class="item-label">平均血小板体积 (fL)</span>
                  <span class="item-value">{{ bloodRoutineData.mpv }}</span>
                </div>
                <div v-if="bloodRoutineData.neutrophil_percentage" class="blood-item">
                  <span class="item-label">中性粒细胞百分比 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.neutrophil_percentage }}</span>
                </div>
                <div v-if="bloodRoutineData.lymphocyte_percentage" class="blood-item">
                  <span class="item-label">淋巴细胞百分比 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.lymphocyte_percentage }}</span>
                </div>
                <div v-if="bloodRoutineData.monocyte_percentage" class="blood-item">
                  <span class="item-label">单核细胞百分比 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.monocyte_percentage }}</span>
                </div>
                <div v-if="bloodRoutineData.eosinophil_percentage" class="blood-item">
                  <span class="item-label">嗜酸性粒细胞百分比 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.eosinophil_percentage }}</span>
                </div>
                <div v-if="bloodRoutineData.basophil_percentage" class="blood-item">
                  <span class="item-label">嗜碱性粒细胞百分比 (%)</span>
                  <span class="item-value">{{ bloodRoutineData.basophil_percentage }}</span>
                </div>
              </template>
            </div>
          </div>
          <div v-else class="no-data">暂无血常规数据</div>
        </div>
        <div v-else class="no-data">暂无临床数据</div>
      </el-card>

      <!-- 在右侧面板最下方添加折线图卡片 -->
      <el-card class="trend-card">
        <template #header>
          <div class="card-header">
            <span>趋势</span>
            <el-select v-model="selectedMetric" placeholder="选择指标" size="small">
              <el-option label="治疗体积" value="treatment_volume" />
              <el-option label="平均治疗功率" value="avg_treatment_power" />
              <el-option label="总能量" value="total_energy" />
              <el-option label="伴发肌瘤个数" value="fibroids_present" />
            </el-select>
          </div>
        </template>
        <div ref="chartRef" style="height: 300px;"></div>
      </el-card>
    </div>

    <!-- 报告详情弹窗 -->
    <el-dialog
      v-model="reportDialogVisible"
      title="报告详情"
      width="70%"
      :close-on-click-modal="false"
    >
      <div class="report-detail" ref="reportContentRef">
        <!-- 标题部分 -->
        <div class="report-header">
          <h2>MRI 检查报告</h2>
          <div class="report-date">{{ formatDate(currentGroup?.imageDate) }}</div>
        </div>

        <!-- 基本信息和临床数据并排显示 -->
        <div class="info-section">
          <!-- 左侧基本信息 -->
          <div class="basic-info">
            <h3>基本信息</h3>
            <div class="info-content">
              <div class="info-item">
                <span class="label">患者姓名：</span>
                <span class="value">{{ patientInfo?.name }}</span>
              </div>
              <div class="info-item">
                <span class="label">主治医师：</span>
                <span class="value">{{ patientInfo?.doctor }}</span>
              </div>
              <div class="info-item">
                <span class="label">科室：</span>
                <span class="value">{{ patientInfo?.department }}</span>
              </div>
            </div>
          </div>

          <!-- 右侧临床数据 -->
          <div class="clinical-data">
            <h3>临床数据</h3>
            <div class="data-content">
              <div class="data-item">
                <span class="label">伴发肌瘤个数：</span>
                <span class="value">{{ currentGroup?.clinicalData?.fibroids_present }}</span>
              </div>
              <div class="data-item">
                <span class="label">平均治疗功率：</span>
                <span class="value">{{ currentGroup?.clinicalData?.avg_treatment_power }} W</span>
              </div>
              <div class="data-item">
                <span class="label">总能量：</span>
                <span class="value">{{ currentGroup?.clinicalData?.total_energy }} J</span>
              </div>
              <div class="data-item">
                <span class="label">治疗体积：</span>
                <span class="value">{{ currentGroup?.clinicalData?.treatment_volume }} mm³</span>
              </div>
              <div class="data-item">
                <span class="label">孕次：</span>
                <span class="value">{{ currentGroup?.clinicalData?.parity }}</span>
              </div>
              <div class="data-item">
                <span class="label">流产次数：</span>
                <span class="value">{{ currentGroup?.clinicalData?.miscarriage_count }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- MRI图像部分 -->
        <div class="image-section">
          <h3>MRI图像</h3>
          <div class="image-container">
            <img :src="getImageUrl(currentSliceUrl)" alt="MRI图像" />
          </div>
        </div>

        <!-- 诊断结果部分 -->
        <div class="diagnosis-section">
          <h3>诊断结果</h3>
          <div class="diagnosis-content">
            <p class="diagnosis-text">{{ currentReport?.radiomicComment }}</p>
          </div>
        </div>

        <!-- 医生建议部分 -->
        <div class="suggestion-section">
          <h3>医生建议</h3>
          <p>{{ currentReport?.therapyComment }}</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="reportDialogVisible = false">关闭</el-button>
          <el-button 
            type="primary" 
            @click="downloadPDF"
            :loading="downloading"
          >
            <el-icon><Download /></el-icon>
            下载 PDF
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 生成报告弹窗 -->
    <GenerateReport
      v-model="generateReportDialogVisible"
      :image-url="getImageUrl(currentSliceUrl)"
      :image-id="currentGroup?.imageId"
      :clinical-data="currentGroup?.clinicalData"
      @success="handleReportSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, watch, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage} from 'element-plus';
import { getPatientInfo, getAllMRIDetails, getDoctorInfo, getPeriodClinicalData, getReport} from '@/api/doctor';
import { useUserStore } from '@/store/modules/user';
import { ArrowLeft, ArrowRight, Download, Document} from '@element-plus/icons-vue';
import EditComponent from './edit.vue';
import { use } from 'echarts/core';
import { LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import * as echarts from 'echarts/core';
import GenerateReport from './generateReport.vue';

interface PatientDetail {
  userId: number;
  name: string;
  age?: number;
  gender?: string;
  examDate?: string;
  doctor?: string;
  department?: string;
}

interface MRIData {
  allSlicesT1: string[];
  allSlicesT2: string[];
  firstSliceT1: string;
  firstSliceT2: string;
  hasReport: boolean;
  imageDate: string;
  uploadDate: string;
  imageId: number;
  clinicalData: ClinicalData;
}

interface ClinicalData {
  fibroids_present: number;
  avg_treatment_power: number;
  total_energy: number;
  treatment_volume: number;
  blood_routine: string;
  parity: number;
  miscarriage_count: number;
}

// 添加血常规数据接口
interface BloodRoutineData {
  blood_routine_id: string;
  wbc_count: number;
  basophil_absolute: number;
  eosinophil_absolute: number;
  neutrophil_absolute: number;
  lymphocyte_absolute: number;
  monocyte_absolute: number;
  rbc_count: number;
  hemoglobin: number;
  hematocrit: number;
  mcv: number;
  mch: number;
  mchc: number;
  rdw_cv: number;
  rdw_sd: number;
  platelet_count: number;
  pdw: number;
  mpv: number;
  neutrophil_percentage: number;
  lymphocyte_percentage: number;
  monocyte_percentage: number;
  eosinophil_percentage: number;
  basophil_percentage: number;
}

interface ReportDetail {
  imageId: number;
  doctorId: string;
  radiomicComment: string;
  therapyComment: string;
  result: string;
}

const route = useRoute();
const router = useRouter();
const patientId = computed(() => route.params.id as string);
const userStore = useUserStore();
const userInfo = ref(userStore.userInfo);

const loading = ref(false);
const patientInfo = ref<PatientDetail>();
const mriList = ref<MRIData[]>([]);
const dateRange = ref<[string, string] | null>(null);

// 添加新的状态管理
const currentGroupIndex = ref(0);
const currentSequence = ref<'t1' | 't2'>('t1');
const currentSliceIndex = ref(0);
const editDialogVisible = ref(false);
const editCanvas = ref<HTMLCanvasElement | null>(null);
const editContext = ref<CanvasRenderingContext2D | null>(null);

// 计算当前显示的切片数组
const currentSlices = computed(() => {
  const currentGroup = mriList.value[currentGroupIndex.value];
  if (!currentGroup) return [];
  return currentSequence.value === 't1' ? currentGroup.allSlicesT1 : currentGroup.allSlicesT2;
});

// 计算当前显示的切片URL
const currentSliceUrl = computed(() => {
  return currentSlices.value[currentSliceIndex.value];
});

// 切换组
const prevGroup = async () => {
  if (currentGroupIndex.value > 0) {
    currentGroupIndex.value--;
    currentSliceIndex.value = 0;
    // 获取新组的血常规数据，使用 uploadDate
    const currentUploadDate = mriList.value[currentGroupIndex.value].uploadDate;
    await fetchBloodRoutineData(currentUploadDate);
  }
};

const nextGroup = async () => {
  if (currentGroupIndex.value < mriList.value.length - 1) {
    currentGroupIndex.value++;
    currentSliceIndex.value = 0;
    // 获取新组的血常规数据，使用 uploadDate
    const currentUploadDate = mriList.value[currentGroupIndex.value].uploadDate;
    await fetchBloodRoutineData(currentUploadDate);
  }
};

// 切换切片
const prevSlice = () => {
  if (currentSliceIndex.value > 0) {
    currentSliceIndex.value--;
  }
};

const nextSlice = () => {
  if (currentSliceIndex.value < currentSlices.value.length - 1) {
    currentSliceIndex.value++;
  }
};

// 编辑功能
const openEditDialog = () => {
  editDialogVisible.value = true;
  console.log('Current edit slice URL:', currentSliceUrl.value);
  console.log('Current edit slices:', currentSlices.value);
  nextTick(() => {
    if (editCanvas.value) {
      const ctx = editCanvas.value.getContext('2d');
      if (ctx) {
        editContext.value = ctx;
        // 加载当前图片到canvas
        const img = new Image();
        img.onload = () => {
          editCanvas.value!.width = img.width;
          editCanvas.value!.height = img.height;
          ctx.drawImage(img, 0, 0);
        };
        img.src = getImageUrl(currentSliceUrl.value);
      }
    }
  });
};

const handleEditSave = (editedImageData: string) => {
  const currentGroup = mriList.value[currentGroupIndex.value];
  // 更新当前切片的图像数据
  if (currentSequence.value === 't1') {
    currentGroup.allSlicesT1[currentSliceIndex.value] = editedImageData;
  } else {
    currentGroup.allSlicesT2[currentSliceIndex.value] = editedImageData;
  }
  // 关闭编辑对话框
  editDialogVisible.value = false;
  ElMessage.success('标注已保存');
};

// 获取患者信息和MRI列表
const fetchPatientData = async () => {
  loading.value = true;
  try {
    // 获取MRI列表
    const mriData = await getAllMRIDetails(Number(patientId.value));
    console.log('Raw MRI response:', mriData);

    if (Array.isArray(mriData)) {
      // 处理MRI数据，包括临床数据
      mriList.value = mriData.map(item => {
        console.log('Processing MRI item:', item);
        const processedItem = {
          allSlicesT1: item.allSlicesT1,
          allSlicesT2: item.allSlicesT2,
          firstSliceT1: item.firstSliceT1,
          firstSliceT2: item.firstSliceT2,
          hasReport: item.hasReport,
          imageDate: item.imageDate || '未知日期',
          uploadDate: item.uploadDate || '未知日期',
          imageId: item.imageId,
          clinicalData: {
            fibroids_present: item.fibroidsPresent,
            avg_treatment_power: item.avgTreatmentPower,
            total_energy: item.totalEnergy,
            treatment_volume: item.treatmentVolume,
            blood_routine: item.bloodRoutine,
            parity: item.parity,
            miscarriage_count: item.miscarriageCount
          }
        };
        console.log('Processed item:', processedItem);
        return processedItem;
      }).sort((a, b) => {
        return new Date(b.imageDate).getTime() - new Date(a.imageDate).getTime();
      });
      
      console.log('Final processed MRI list:', mriList.value);

      if (mriList.value.length > 0) {
        // 获取第一组的血常规数据，使用 uploadDate
        const firstUploadDate = mriList.value[0].uploadDate;
        await fetchBloodRoutineData(firstUploadDate);
      }
    } else {
      console.warn('Invalid MRI data format:', mriData);
      mriList.value = [];
    }

    // 获取患者基本信息
    const patientData = await getPatientInfo({ patientId: Number(patientId.value) });
    const doctorInfo = await getDoctorInfo({ doctorId: userInfo.value.userId });
    
    patientInfo.value = {
      userId: patientData.userId,
      name: patientData.name,
      age: patientData.age,
      gender: patientData.gender === 1 ? '男' : '女',
      examDate: mriList.value.length > 0 ? formatDate(mriList.value[0].imageDate) : '暂无检查记录',
      doctor: doctorInfo.name,
      department: doctorInfo.department
    }
  } catch (error: any) {
    console.error('Error details:', error);
    ElMessage.error(error.message || '获取数据失败');
  } finally {
    loading.value = false;
  }
};

// 修改日期范围处理函数
const handleDateRangeChange = async (dates: [string, string] | null) => {
  if (!dates) {
    // 清除筛选时，恢复原始排序后的数据
    mriList.value = mriList.value.sort((a, b) => {
      return new Date(b.imageDate).getTime() - new Date(a.imageDate).getTime();
    });
    return;
  }

  try {
    loading.value = true;
    const [startDate, endDate] = dates;
    const startTime = new Date(startDate).getTime();
    const endTime = new Date(endDate).getTime();

    // 直接筛选现有数据
    mriList.value = mriList.value
      .filter(item => {
        const itemTime = new Date(item.imageDate).getTime();
        return itemTime >= startTime && itemTime <= endTime;
      })
      .sort((a, b) => {
        return new Date(b.imageDate).getTime() - new Date(a.imageDate).getTime();
      });

    // 重置索引
    currentGroupIndex.value = 0;
    currentSliceIndex.value = 0;

    if (mriList.value.length === 0) {
      ElMessage.warning('所选时间范围内没有MRI数据');
    }
  } catch (error) {
    console.error('筛选数据失败:', error);
    ElMessage.error('筛选数据失败');
  } finally {
    loading.value = false;
  }
};

const goBack = () => {
  router.push('/doctor/analyse');
};  

const getImageUrl = (base64String: string) => {
  if (!base64String) return '';
  // 如果已经是data URL格式，直接返回
  if (base64String.startsWith('data:image')) {
    return base64String;
  }
  // 否则，添加base64前缀
  return `data:image/jpeg;base64,${base64String}`;
};

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return '未知日期';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch {
    return dateStr;
  }
};

// 添加 currentGroup 计算属性
const currentGroup = computed(() => {
  return mriList.value[currentGroupIndex.value];
});

// 添加新的响应式变量
const selectedMetric = ref('treatment_volume');
const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

// 导入 ECharts 组件
use([TitleComponent, TooltipComponent, GridComponent, LineChart, CanvasRenderer]);


const generateTrendData = () => {
  const dates: string[] = [];
  const values: number[] = [];
  
  mriList.value.forEach(item => {
    dates.push(formatDate(item.imageDate));
    
    switch (selectedMetric.value) {
      case 'treatment_volume':
        values.push(item.clinicalData.treatment_volume || 0);
        break;
      case 'avg_treatment_power':
        values.push(item.clinicalData.avg_treatment_power || 0);
        break;
      case 'total_energy':
        values.push(item.clinicalData.total_energy || 0);
        break;
      case 'fibroids_present':
        values.push(item.clinicalData.fibroids_present || 0);
        break;
    }
  });

  // 按日期排序
  const sortedIndices = dates.map((_, i) => i).sort((a, b) => 
    new Date(dates[a]).getTime() - new Date(dates[b]).getTime()
  );
  
  return {
    dates: sortedIndices.map(i => dates[i]),
    values: sortedIndices.map(i => values[i])
  };
};

// 修改 updateChart 函数
const updateChart = () => {
  if (!chartRef.value) return;

  try {
    // 如果图表实例不存在，创建新实例
    if (!chart) {
      chart = echarts.init(chartRef.value);
    }

    const { dates, values } = generateTrendData();

    const option = {
      title: {
        text: getMetricName(selectedMetric.value),
        left: 'center',
        top: 10
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const param = params[0];
          return `${param.name}<br/>${getMetricName(selectedMetric.value)}: ${param.value} ${getUnit(selectedMetric.value)}`;
        }
      },
      grid: {
        top: 60,
        right: 40,
        bottom: 60,
        left: 60
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 30,
          margin: 15
        }
      },
      yAxis: {
        type: 'value',
        name: getUnit(selectedMetric.value),
        nameLocation: 'middle',
        nameGap: 40,
        nameTextStyle: {
          fontWeight: 'bold'
        }
      },
      series: [{
        name: getMetricName(selectedMetric.value),
        data: values,
        type: 'line',
        smooth: true,
        symbolSize: 8,
        itemStyle: {
          color: '#409EFF'
        },
        lineStyle: {
          width: 3,
          color: '#409EFF'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{
              offset: 0,
              color: 'rgba(64,158,255,0.2)'
            }, {
              offset: 1,
              color: 'rgba(64,158,255,0)'
            }]
          }
        }
      }]
    };
    
    chart.setOption(option);
  } catch (error) {
    console.error('Chart update failed:', error);
  }
};

// 获取单位
const getUnit = (metric: string) => {
  switch (metric) {
    case 'treatment_volume':
      return 'mm³';
    case 'avg_treatment_power':
      return 'W';
    case 'total_energy':
      return 'J';
    case 'fibroids_present':
      return '个';
    default:
      return '';
  }
};

// 获取指标名称的函数
const getMetricName = (metric: string) => {
  switch (metric) {
    case 'treatment_volume':
      return '治疗体积';
    case 'avg_treatment_power':
      return '平均治疗功率';
    case 'total_energy':
      return '总能量';
    case 'fibroids_present':
      return '伴发肌瘤个数';
    default:
      return '';
  }
};

// 修改 onMounted 钩子
onMounted(async () => {
  await fetchPatientData();
  nextTick(() => {
    if (chartRef.value) {
      chart = echarts.init(chartRef.value);
      updateChart();
      
      // 添加窗口大小变化监听
      window.addEventListener('resize', () => {
        chart?.resize();
      });
    }
  });
});

// 修改 onUnmounted 钩子
onUnmounted(() => {
  // 清理图表实例和事件监听
  if (chart) {
    chart.dispose();
    chart = null;
  }
  window.removeEventListener('resize', () => {
    chart?.resize();
  });
});

// 添加对 mriList 的监听
watch(mriList, () => {
  nextTick(() => {
    updateChart();
  });
}, { deep: true });

// 添加对 selectedMetric 的监听
watch(selectedMetric, () => {
  nextTick(() => {
    updateChart();
  });
});

// 血常规数据存储
const bloodRoutineData = ref<BloodRoutineData | null>(null);

// 获取血常规数据的函数
const fetchBloodRoutineData = async (date: string) => {
  try {
    const formattedDate = formatToYYYYMMDD(date);
    console.log('Fetching blood routine data for date:', formattedDate);

    const response = await getPeriodClinicalData(
      Number(patientId.value),
      formattedDate,
      formattedDate,
      'bloodRoutine'
    );

    if (Array.isArray(response) && response.length > 0) {
      bloodRoutineData.value = {
        blood_routine_id: response[0].bloodRoutineId || '',
        wbc_count: response[0].wbcCount || 0,
        basophil_absolute: response[0].basophilAbsolute || 0,
        eosinophil_absolute: response[0].eosinophilAbsolute || 0,
        neutrophil_absolute: response[0].neutrophilAbsolute || 0,
        lymphocyte_absolute: response[0].lymphocyteAbsolute || 0,
        monocyte_absolute: response[0].monocyteAbsolute || 0,
        rbc_count: response[0].rbcCount || 0,
        hemoglobin: response[0].hemoglobin || 0,
        hematocrit: response[0].hematocrit || 0,
        mcv: response[0].mcv || 0,
        mch: response[0].mch || 0,
        mchc: response[0].mchc || 0,
        rdw_cv: response[0].rdwCv || 0,
        rdw_sd: response[0].rdwSd || 0,
        platelet_count: response[0].plateletCount || 0,
        pdw: response[0].pdw || 0,
        mpv: response[0].mpv || 0,
        neutrophil_percentage: response[0].neutrophilPercentage || 0,
        lymphocyte_percentage: response[0].lymphocytePercentage || 0,
        monocyte_percentage: response[0].monocytePercentage || 0,
        eosinophil_percentage: response[0].eosinophilPercentage || 0,
        basophil_percentage: response[0].basophilPercentage || 0
      };
      console.log('Processed blood routine data:', bloodRoutineData.value);
    } else {
      bloodRoutineData.value = null;
      console.log('No blood routine data available for this date');
    }
  } catch (error) {
    console.error('获取血常规数据失败:', error);
    ElMessage.error('获取血常规数据失败');
  }
};

// 添加日期格式化函数
const formatToYYYYMMDD = (dateStr: string) => {
  try {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  } catch (error) {
    console.error('日期格式化失败:', error);
    return dateStr; // 如果转换失败，返回原始字符串
  }
};

//添加控制血常规显示的状态
const showBloodRoutine = ref(false);

// 添加报告详情弹窗
const reportDialogVisible = ref(false);
const downloading = ref(false);

const showReportDetail = () => {
  reportDialogVisible.value = true;
};

// 添加报告数据的响应式变量
const currentReport = ref<ReportDetail | null>(null);

// 添加获取报告的方法
const fetchReportDetail = async () => {
  try {
    if (currentGroup.value?.hasReport && currentGroup.value?.imageId) {
      const reportData = await getReport({imageId: currentGroup.value.imageId});
      currentReport.value = reportData;
    } else {
      currentReport.value = null;
    }
  } catch (error) {
    console.error('获取报告失败:', error);
    ElMessage.error('获取报告失败');
  }
};

// 监听 currentGroup 的变化
watch(() => currentGroup.value?.imageId, (newId) => {
  if (newId && currentGroup.value?.hasReport) {
    fetchReportDetail();
  }
});

const generateReportDialogVisible = ref(false);

// 修改生成报告的处理函数
const handleGenerateReport = () => {
  generateReportDialogVisible.value = true;
};

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
const reportContentRef = ref<HTMLElement | null>(null);

const downloadPDF = async () => {
  // 添加日志来调试
  console.log('开始下载PDF');
  console.log('reportContentRef:', reportContentRef.value);
  
  if (!reportContentRef.value) {
    console.error('未找到报告内容元素');
    return;
  }
  
  downloading.value = true;
  
  try {
    // 等待下一个 tick，确保内容已经渲染
    await nextTick();
    
    console.log('开始生成canvas');
    const canvas = await html2canvas(reportContentRef.value, {
      scale: 2,
      useCORS: true,
      logging: true, // 开启日志以便调试
      backgroundColor: '#ffffff'
    });
    
    console.log('canvas生成成功');
    
    // 创建 PDF
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgData = canvas.toDataURL('image/jpeg', 1.0);
    
    // 设置 PDF 尺寸
    const imgWidth = 210;
    const pageHeight = 297;
    const imgHeight = canvas.height * imgWidth / canvas.width;
    
    // 添加图片到 PDF
    pdf.addImage(imgData, 'JPEG', 0, 0, imgWidth, imgHeight);
    
    // 生成文件名
    const fileName = `${patientInfo.value?.name || 'patient'}_MRI报告_${formatDate(currentGroup.value?.imageDate) || 'report'}.pdf`;
    
    console.log('准备保存PDF:', fileName);
    pdf.save(fileName);
    
    ElMessage.success('PDF 文件下载成功');
  } catch (error) {
    console.error('PDF生成失败:', error);
    ElMessage.error('下载 PDF 失败，请稍后重试');
  } finally {
    downloading.value = false;
  }
};

const handleReportSuccess = async () => {
  generateReportDialogVisible.value = false;
  // 重新获取数据
  await fetchPatientData();
};

</script>

<style lang="less" scoped>
.analyse-detail {
  padding: 24px;
  display: flex;
  gap: 24px;

  .main-content {
    flex: 1;
  }

  .side-panel {
    width: 300px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    
    .report-card, .params-card, .trend-card {
      height: fit-content;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .title {
          font-size: 18px;
          font-weight: bold;
        }

        .date {
          color: #909399;
        }
      }
    }

    .report-card {
      height: fit-content;
      margin-bottom: 20px;

      .report-content {
        text-align: left;
        padding: 16px;
        max-height: 400px;
        
        .emoji {
          font-size: 48px;
          text-align: center;
          margin-bottom: 20px;
        }

        .diagnosis {
          margin-bottom: 20px;
          padding-bottom: 16px;
          border-bottom: 1px solid #EBEEF5;
        }

        .diagnosis, .suggestion {
          h4 {
            color: #303133;
            font-size: 16px;
            margin: 0 0 12px 0;
            font-weight: 500;
          }

          p {
            color: #606266;
            margin: 0 0 16px 0;
            line-height: 1.6;
          }
        }

        .el-button {
          width: 100%;
          margin-top: 16px;
        }

        .no-report {
          text-align: center;
          padding: 20px 0;
        }
      }
    }

    .params-card {
      .params-list {
        .param-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          &.blood-routine {
            flex-direction: column;
            align-items: flex-start;
            border-top: 1px solid #EBEEF5;
            padding-top: 12px;
            margin-top: 12px;

            .blood-routine-header {
              width: 100%;
              margin-bottom: 8px;
              
              .blood-routine-title {
                display: flex;
                justify-content: space-between;
                align-items: center;
                
                span {
                  font-size: 14px;
                  color: #606266;
                }
                
                .el-button {
                  padding: 0;
                  height: auto;
                  font-size: 12px;
                  
                  .el-icon {
                    margin-left: 4px;
                    font-size: 12px;
                  }
                }
              }
            }

            .blood-routine-list {
              width: 100%;
              animation: slideDown 0.3s ease-out;
              
              .blood-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px;
                border-bottom: 1px solid #EBEEF5;
                
                &:last-child {
                  border-bottom: none;
                }
                
                .item-label {
                  color: #606266;
                  font-size: 13px;
                }
                
                .item-value {
                  color: #303133;
                  font-weight: 500;
                  font-size: 13px;
                }
              }
            }
          }
          
          .label {
            color: #606266;
          }
          
          .value {
            color: #303133;
            font-weight: 500;
          }
        }
      }
    }
  }
}

// MRI 查看器相关样式
.mri-viewer {
  margin-top: 24px;
  
  .date-filter {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;

    .filter-group {
      display: flex;
      gap: 12px;
      align-items: center;

      .el-date-picker {
        width: 400px;
      }
    }
  }

  .viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      margin: 0;
    }

    .viewer-controls {
      display: flex;
      align-items: center;
      gap: 16px;

      .date-display {
        font-size: 14px;
        color: var(--el-text-color-regular);
        padding: 0 12px;
      }

      .pagination-group {
        display: inline-flex;
        align-items: center;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 4px;
        background: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        
        .nav-button {
          height: 32px;
          padding: 0 12px;
          border: none;
          background: transparent;
          color: var(--el-text-color-regular);
          transition: all 0.3s;

          &:hover:not(:disabled) {
            background: var(--el-fill-color-light);
            color: var(--el-color-primary);
          }

          &:disabled {
            background: transparent;
            color: var(--el-text-color-placeholder);
          }

          .el-icon {
            font-size: 14px;
          }
        }

        .page-info {
          min-width: 48px;
          padding: 0 12px;
          height: 32px;
          line-height: 32px;
          text-align: center;
          font-size: 14px;
          color: var(--el-text-color-primary);
          font-weight: 500;
          border-left: 1px solid var(--el-border-color-lighter);
          border-right: 1px solid var(--el-border-color-lighter);
          background: var(--el-fill-color-blank);
        }
      }
    }
  }

  .sequence-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 20px 0;
    gap: 24px;

    .slice-info {
      font-size: 14px;
      color: #666;
    }
  }

  .image-display {
    .image-controls {
      display: flex;
      align-items: center;
      gap: 16px;

      .images-container {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        
        .side-image {
          width: 200px;
          opacity: 0.6;
          transition: all 0.3s;
          
          img {
            width: 100%;
            height: auto;
            filter: grayscale(50%);
          }
          
          &:hover {
            opacity: 0.8;
          }
        }
        
        .main-image {
          width: 400px;
          
          .image-wrapper {
            position: relative;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            
            img {
              width: 100%;
              height: auto;
              max-height: 400px;
              object-fit: contain;
              display: block;
              margin-bottom: 16px;
              border: 2px solid var(--el-color-primary-light-3);
              border-radius: 4px;
            }

            .button-wrapper {
              text-align: center;
              margin-top: 16px;
            }
          }
        }
      }
    }
  }
}

// 页面头部样式
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  h2 {
    margin: 0;
    font-size: 24px;
    font-weight: bold;
  }

  .back-button {
    margin-left: auto;
  }
}

.report-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;

  .report-header {
    text-align: center;
    margin-bottom: 20px;
    
    h2 {
      margin: 0;
      font-size: 24px;
      color: #303133;
    }
    
    .report-date {
      color: #606266;
      margin-top: 4px;
    }
  }

  .info-section {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;

    .basic-info, .clinical-data {
      flex: 1;
      
      h3 {
        font-size: 16px;
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #EBEEF5;
      }
    }

    .info-item, .data-item {
      margin-bottom: 8px;
      font-size: 14px;

      .label {
        color: #606266;
        margin-right: 8px;
      }

      .value {
        color: #303133;
        font-weight: 500;
      }
    }
  }

  .image-section {
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      margin-bottom: 12px;
    }

    .image-container {
      text-align: center;
      
      img {
        max-width: 100%;
        max-height: 300px;
        object-fit: contain;
      }
    }
  }

  .diagnosis-section {
    margin-bottom: 20px;

    h3 {
      font-size: 16px;
      margin-bottom: 12px;
    }

    .diagnosis-content {
      background: #F5F7FA;
      padding: 12px;
      border-radius: 4px;

      .result-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        background: #67C23A;
        color: white;
        margin-bottom: 8px;

        &.positive {
          background: #F56C6C;
        }
      }

      .diagnosis-text {
        margin: 0;
        font-size: 14px;
        line-height: 1.6;
      }
    }
  }

  .suggestion-section {
    h3 {
      font-size: 16px;
      margin-bottom: 12px;
    }

    p {
      margin: 0;
      font-size: 14px;
      line-height: 1.6;
      color: #303133;
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
}

:deep(.el-dialog__header) {
  margin-right: 0;
  padding: 20px 24px;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.el-dialog__body) {
  padding: 0;
}

:deep(.el-dialog__footer) {
  padding: 20px 24px;
  border-top: 1px solid #ebeef5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  
  .el-button {
    display: flex;
    align-items: center;
    gap: 4px;
    
    .el-icon {
      font-size: 16px;
    }
  }
}

.report-content {
  padding: 20px;
  height: fit-content;
  .result-section {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 0;

    .emoji-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 16px;

      .large-emoji {
        font-size: 72px;  // 更大的emoji
        line-height: 1;
      }

      .result-text {
        font-size: 24px;  // 更大的结果文字
        font-weight: 500;
        color: #303133;
      }
    }
  }

  .diagnosis-section {
    margin-top: 20px;
    
    h4 {
      font-size: 20px;  // 更大的标题
      font-weight: 500;
      margin-bottom: 16px;
      color: #303133;
    }

    p {
      font-size: 16px;  // 更大的内容文字
      color: #606266;
      line-height: 1.8;  // 增加行高
      padding: 0 20px;   // 添加内边距
    }
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
