<template>
  <div class="slice-edit">
    <a-card :bordered="false">
      <div class="page-title">
        编辑切片
      </div>
      <div class="edit-area">
        <div class="tools-panel">
          <div class="tool-section">
            <h4>序列信息</h4>
            <div class="info-display">
              <div class="info-item">
                序列类型：{{ props.sequenceType === 't1' ? 'T1' : 'T2' }}
              </div>
              <div class="info-item">
                坐标：({{ coordinates.x }}, {{ coordinates.y }}, {{ coordinates.z }})
              </div>
            </div>
          </div>

          <div class="tool-section">
            <h4>缩放</h4>
            <a-slider v-model:value="zoom" :min="50" :max="200" :step="10" />
          </div>

          <div class="tool-section">
            <h4>绘制</h4>
            <div class="drawing-tools">
              <div class="tool-buttons">
                <a-button-group>
                  <a-button :type="tool === 'pen' ? 'primary' : 'default'" @click="tool = 'pen'">
                    <template #icon><edit-outlined /></template>
                  </a-button>
                  <a-button :type="tool === 'eraser' ? 'primary' : 'default'" @click="tool = 'eraser'">
                    <template #icon><delete-outlined /></template>
                  </a-button>
                </a-button-group>
              </div>
              <div class="color-picker">
                <div 
                  v-for="color in colors" 
                  :key="color"
                  class="color-box"
                  :style="{ backgroundColor: color }"
                  :class="{ active: currentColor === color }"
                  @click="currentColor = color"
                ></div>
              </div>
              <div class="brush-size">
                <span>笔刷大小:</span>
                <a-slider v-model:value="brushSize" :min="1" :max="20" style="width: 100px" />
              </div>
            </div>
          </div>

          <div class="tool-section">
            <a-button 
              type="primary" 
              block
              :loading="saving"
              @click="handleSave"
            >
              保存标注
            </a-button>
          </div>
        </div>

        <div class="canvas-container">
          <div class="canvas-wrapper" :style="{
            transform: `scale(${zoom / 100})`,
            transformOrigin: 'center center'
          }">
            <canvas ref="baseCanvas" class="base-canvas"></canvas>
            <canvas 
              ref="drawCanvas" 
              class="draw-canvas"
              @mousedown="startDrawing"
              @mousemove="draw"
              @mouseup="stopDrawing"
              @mouseleave="stopDrawing"
            ></canvas>
          </div>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { EditOutlined, DeleteOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';

// 定义props和emit
interface Props {
  imageUrl: string;
  sequenceType: 't1' | 't2';
  sliceIndex: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  (e: 'save', imageData: string): void
}>();

// 模拟坐标计算
const calculateCoordinates = (sliceIndex: number) => {
  // 假设每个切片在y轴上间隔2mm
  return {
    x: 0,  // 同一序列x坐标相同
    y: sliceIndex * 2,  // y坐标随切片索引变化
    z: 0   // 同一序列z坐标相同
  };
};

// 基础状态
const coordinates = ref(calculateCoordinates(props.sliceIndex));
const zoom = ref(100);
const tool = ref<'pen' | 'eraser'>('pen');
const brushSize = ref(5);
const currentColor = ref('#FF0000');
const colors = ['#FF0000', '#FFFF00', '#0000FF'];

// 绘画状态
const isDrawing = ref(false);
let ctx: CanvasRenderingContext2D | null = null;

// 修改画布引用
const baseCanvas = ref<HTMLCanvasElement | null>(null);
const drawCanvas = ref<HTMLCanvasElement | null>(null);
let baseCtx: CanvasRenderingContext2D | null = null;
let drawCtx: CanvasRenderingContext2D | null = null;

// 添加路径记录
interface StrokePath {
  id: number;
  points: { x: number; y: number }[];
  color: string;
  width: number;
}

const paths = ref<StrokePath[]>([]);
let currentPath: StrokePath | null = null;
let pathId = 0;

// 修改获取坐标的函数
const getCanvasCoordinates = (event: MouseEvent) => {
  const rect = drawCanvas.value!.getBoundingClientRect();
  const scale = zoom.value / 100;
  
  // 计算相对于缩放后画布的坐标
  return {
    x: (event.clientX - rect.left) / scale,
    y: (event.clientY - rect.top) / scale
  };
};

// 修改绘画函数
const startDrawing = (event: MouseEvent) => {
  isDrawing.value = true;
  const { x, y } = getCanvasCoordinates(event);
  
  if (drawCtx) {
    drawCtx.beginPath();
    drawCtx.moveTo(x, y);
    drawCtx.strokeStyle = currentColor.value;
    drawCtx.lineWidth = brushSize.value;
    drawCtx.lineCap = 'round';
    
    currentPath = {
      id: pathId++,
      points: [{ x, y }],
      color: currentColor.value,
      width: brushSize.value
    };
  }
};

const draw = (event: MouseEvent) => {
  if (!isDrawing.value || !drawCtx) return;
  
  const { x, y } = getCanvasCoordinates(event);
  
  if (tool.value === 'pen') {
    currentPath?.points.push({ x, y });
    drawCtx.lineTo(x, y);
    drawCtx.stroke();
  } else {
    const hitPath = findPathAtPoint(x, y);
    if (hitPath) {
      erasePath(hitPath);
    }
  }
};

const stopDrawing = () => {
  isDrawing.value = false;
  if (drawCtx) {
    drawCtx.closePath();
    if (currentPath) {
      paths.value.push(currentPath);
      currentPath = null;
    }
  }
};

// 查找点击位置的路径
const findPathAtPoint = (x: number, y: number): StrokePath | null => {
  // 设置一个容差范围，使得更容易选中路径
  const tolerance = brushSize.value / 2;
  
  for (const path of paths.value) {
    for (let i = 1; i < path.points.length; i++) {
      const p1 = path.points[i - 1];
      const p2 = path.points[i];
      
      // 检查点是否在线段附近
      if (isPointNearLine(x, y, p1.x, p1.y, p2.x, p2.y, tolerance)) {
        return path;
      }
    }
  }
  return null;
};

// 检查点是否在线段附近
const isPointNearLine = (
  px: number, py: number,
  x1: number, y1: number,
  x2: number, y2: number,
  tolerance: number
): boolean => {
  const A = px - x1;
  const B = py - y1;
  const C = x2 - x1;
  const D = y2 - y1;

  const dot = A * C + B * D;
  const len_sq = C * C + D * D;
  let param = -1;

  if (len_sq !== 0) {
    param = dot / len_sq;
  }

  let xx, yy;

  if (param < 0) {
    xx = x1;
    yy = y1;
  } else if (param > 1) {
    xx = x2;
    yy = y2;
  } else {
    xx = x1 + param * C;
    yy = y1 + param * D;
  }

  const dx = px - xx;
  const dy = py - yy;
  const distance = Math.sqrt(dx * dx + dy * dy);

  return distance <= tolerance;
};

// 擦除整条路径
const erasePath = (path: StrokePath) => {
  // 从路径列表中移除
  paths.value = paths.value.filter(p => p.id !== path.id);
  
  // 重绘所有剩余路径
  redrawPaths();
};

// 重绘所有路径
const redrawPaths = () => {
  if (!drawCtx || !drawCanvas.value) return;
  
  // 清空绘制层
  drawCtx.clearRect(0, 0, drawCanvas.value.width, drawCanvas.value.height);
  
  // 重绘所有路径
  for (const path of paths.value) {
    drawCtx.beginPath();
    drawCtx.strokeStyle = path.color;
    drawCtx.lineWidth = path.width;
    drawCtx.lineCap = 'round';
    
    const [first, ...rest] = path.points;
    drawCtx.moveTo(first.x, first.y);
    
    for (const point of rest) {
      drawCtx.lineTo(point.x, point.y);
    }
    
    drawCtx.stroke();
  }
};

// 添加保存相关状态和函数
const saving = ref(false);

const handleSave = async () => {
  saving.value = true;
  try {
    if (!baseCanvas.value || !drawCanvas.value) return;

    // 创建一个临时画布来合并图层
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = baseCanvas.value.width;
    tempCanvas.height = baseCanvas.value.height;
    const tempCtx = tempCanvas.getContext('2d');

    if (!tempCtx) return;

    // 首先绘制基础图层
    tempCtx.drawImage(baseCanvas.value, 0, 0);
    // 然后绘制标注图层
    tempCtx.drawImage(drawCanvas.value, 0, 0);

    // 将画布转换为数据URL
    const dataUrl = tempCanvas.toDataURL('image/png');
    
    // 发送更新事件到父组件
    emit('save', dataUrl);
    
    message.success('保存成功');
  } catch (error) {
    console.error('保存失败:', error);
    message.error('保存失败，请重试');
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  if (baseCanvas.value && drawCanvas.value) {
    baseCtx = baseCanvas.value.getContext('2d')!;
    drawCtx = drawCanvas.value.getContext('2d', { willReadFrequently: true })!;
    
    if (baseCtx && drawCtx) {
      // 加载图片
      const img = new Image();
      img.src = props.imageUrl;
      img.onload = () => {
        // 设置两个画布的尺寸为图片实际尺寸
        const width = img.width;
        const height = img.height;
        baseCanvas.value!.width = width;
        baseCanvas.value!.height = height;
        drawCanvas.value!.width = width;
        drawCanvas.value!.height = height;
        
        // 在底层画布绘制原始图片
        baseCtx!.drawImage(img, 0, 0);
        
        // 设置画布容器的尺寸
        const wrapper = baseCanvas.value!.parentElement;
        if (wrapper) {
          wrapper.style.width = `${width}px`;
          wrapper.style.height = `${height}px`;
        }
      };
    }
  }
});
</script>

<style lang="less" scoped>
.slice-edit {
  padding: 24px;

  .page-title {
    font-size: 18px;
    font-weight: 500;
    color: #333;
    margin: 16px 24px 24px;  // 调整标题位置
  }

  .edit-area {
    display: flex;
    gap: 24px;

    .tools-panel {
      width: 300px;
      flex-shrink: 0;
      background: #f5f5f5;
      padding: 16px;
      border-radius: 4px;

      .tool-section {
        margin-bottom: 20px;

        h4 {
          margin-bottom: 12px;
          color: #333;
        }

        .info-display {
          background: #fff;
          padding: 12px;
          border-radius: 4px;
          
          .info-item {
            margin-bottom: 8px;
            color: #666;
            font-size: 14px;
            
            &:last-child {
              margin-bottom: 0;
            }
          }
        }

        .drawing-tools {
          .tool-buttons {
            margin-bottom: 12px;
          }

          .color-picker {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;

            .color-box {
              width: 24px;
              height: 24px;
              border-radius: 4px;
              cursor: pointer;
              border: 2px solid transparent;

              &.active {
                border-color: #1890ff;
              }
            }
          }

          .brush-size {
            display: flex;
            align-items: center;
            gap: 8px;
          }
        }

        // 为保存按钮添加样式
        &:last-child {
          margin-top: auto;  // 将保存按钮推到底部
          padding-top: 20px;
          border-top: 1px solid #e8e8e8;
        }
      }
    }

    .canvas-container {
      flex-grow: 1;
      overflow: hidden; // 改为 hidden
      border: 1px solid #d9d9d9;
      border-radius: 4px;
      height: 80vh;
      display: flex;
      justify-content: center;
      align-items: center;
      background: #f0f0f0;

      .canvas-wrapper {
        position: relative;
        transition: transform 0.2s ease; // 添加平滑过渡
        
        .base-canvas,
        .draw-canvas {
          position: absolute;
          top: 0;
          left: 0;
          pointer-events: auto; // 确保画布可以接收鼠标事件
        }
        
        .draw-canvas {
          z-index: 1;
        }
      }
    }
  }
}
</style> 