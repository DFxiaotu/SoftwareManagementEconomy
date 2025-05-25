import joblib
import torch

# 使用 joblib 加载参数
state_dict = joblib.load(".\\trainedModel\\svm_model.joblib")

# 保存为 PyTorch 的 .pth 格式
torch.save(state_dict, ".\\trainedModel\\svm_model.pth")
