import torch
import torch.nn as nn
from torchvision import models
import SimpleITK as sitk
import numpy as np
from PIL import Image
from torchvision import transforms

# 测试集只需要基本预处理
test_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485], std=[0.229])
])

def process_slice(image_slice):
    """处理单个切片"""
    # 归一化到0-255范围
    if image_slice.dtype != np.uint8:
        image_slice = ((image_slice - image_slice.min()) / (image_slice.max() - image_slice.min()) * 255).astype(np.uint8)
    
    # 转换为PIL图像并调整大小
    img_pil = Image.fromarray(image_slice, mode='L')
    img_pil = img_pil.resize((224, 224), Image.Resampling.LANCZOS)
    
    # 应用预处理
    img_tensor = test_transforms(img_pil)
    return img_tensor

def predict_single_case(model, t1_path, t2_path, device):
    """预测单个病例"""
    # 读取nrrd文件
    t1_image = sitk.ReadImage(t1_path)
    t2_image = sitk.ReadImage(t2_path)
    
    # 转换为numpy数组
    t1_array = sitk.GetArrayFromImage(t1_image)
    t2_array = sitk.GetArrayFromImage(t2_image)
    
    # 使用中间切片
    center_idx = t1_array.shape[0] // 2
    
    # 组合切片
    slices = []
    for seq_array in [t1_array, t2_array]:
        for offset in [-4, -2, 0, 2, 4]:
            slice_idx = center_idx + offset
            if 0 <= slice_idx < seq_array.shape[0]:
                slice_tensor = process_slice(seq_array[slice_idx])
            else:
                slice_tensor = torch.zeros(1, 224, 224)
            slices.append(slice_tensor)
    
    # 堆叠为一个批次
    input_tensor = torch.stack(slices).unsqueeze(0)  # [1, 10, 1, 224, 224]
    
    # 预测
    model.eval()
    with torch.no_grad():
        input_tensor = input_tensor.to(device)
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        _, prediction = torch.max(outputs, 1)
    
    return prediction.item(), probabilities[0, 1].item()

class ResNet18_Feature(nn.Module):
    def __init__(self, num_classes=2):
        super(ResNet18_Feature, self).__init__()
        # 加载预训练的ResNet18
        resnet = models.resnet18(pretrained=True)
        
        # 移除最后的全连接层
        self.features = nn.Sequential(*list(resnet.children())[:-1])
        
        # 添加最大池化层，用于合并10个切片的特征
        self.max_pool = nn.AdaptiveMaxPool1d(1)
        
        # 添加分类头
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
        
    def forward(self, x, return_features=False, return_predictions=False):
        # x的形状为 [batch_size, 10, 1, 224, 224]
        batch_size = x.size(0)
        num_slices = x.size(1)
        
        # 重塑输入以单独处理每个切片
        x = x.view(-1, 1, 224, 224)  # [batch_size*10, 1, 224, 224]
        x = x.repeat(1, 3, 1, 1)  # [batch_size*10, 3, 224, 224]
        
        # 提取特征
        features = self.features(x)  # [batch_size*10, 512, 1, 1]
        features = features.view(batch_size, num_slices, -1)  # [batch_size, 10, 512]
        features = features.transpose(1, 2)  # [batch_size, 512, 10]
        features = self.max_pool(features)  # [batch_size, 512, 1]
        features = features.squeeze(-1)  # [batch_size, 512]
        
        if return_features:
            return features
            
        # 分类
        logits = self.classifier(features)
        
        if return_predictions:
            probs = torch.softmax(logits, dim=1)
            preds = torch.argmax(logits, dim=1)
            return features, logits, probs, preds
            
        return logits



def main():
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载模型
    model = ResNet18_Feature().to(device)
    model.load_state_dict(torch.load("dl_output/best_model.pth"))
    
    # 示例：预测单个病例
    t1_path = "path/to/your/t1.nrrd"
    t2_path = "path/to/your/t2.nrrd"
    
    prediction, probability = predict_single_case(model, t1_path, t2_path, device)
    print(f"预测标签: {prediction}")
    print(f"预测概率: {probability:.4f}")

if __name__ == '__main__':
    main() 