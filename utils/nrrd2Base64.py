import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

def find_largest_tumor_slice(mask_array):
    """
    找到肿瘤最大截面所在的层面
    参数:
        mask_array: mask的numpy数组
    返回:
        max_slice_idx: 最大截面所在层面索引
        max_area: 最大面积
    """
    areas = []
    for i in range(mask_array.shape[0]):
        area = np.sum(mask_array[i])
        areas.append(area)
    
    max_slice_idx = np.argmax(areas)
    max_area = areas[max_slice_idx]
    
    return max_slice_idx, max_area

def normalize_slice(image_slice):
    """
    将图像切片归一化到0-255范围
    """
    normalized = ((image_slice - image_slice.min()) / 
                 (image_slice.max() - image_slice.min()) * 255).astype(np.uint8)
    return normalized

def slice_to_base64(image_slice):
    """
    将单个切片转换为base64字符串
    """
    # 创建一个内存中的字节流
    buf = io.BytesIO()
    # 将图像保存到字节流
    plt.imsave(buf, image_slice, format='png', cmap='gray')
    # 获取字节流的内容并转换为base64
    buf.seek(0)
    base64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return base64_str

def nrrd2base64(image_path):
    """
    将nrrd文件转换为base64编码的图像数据
    
    参数:
        image_path: nrrd图像路径
    返回:
        tuple: (all_slices, first_slice)
            - all_slices: 所有切片的base64编码列表
            - first_slice: 第一张切片的base64编码
    """
    # 读取图像和mask
    image = sitk.ReadImage(image_path)

    # 转换为numpy数组
    image_array = sitk.GetArrayFromImage(image)
    
    # # 找到最大肿瘤截面
    # max_slice_idx, _ = find_largest_tumor_slice(mask_array)
    
    # 存储所有切片的base64编码
    all_slices = []
    first_slice = None
    
    # 处理所有切片
    for idx in range(image_array.shape[0]):
        # 获取并归一化切片
        image_slice = normalize_slice(image_array[idx])
        
        # 转换为base64
        slice_base64 = slice_to_base64(image_slice)
        all_slices.append(slice_base64)
        
        # 如果是最大面积切片，单独保存
        if idx == 0:
            first_slice = slice_base64
    
    return all_slices, first_slice

if __name__ == "__main__":
    image_path = r"C:\Users\fangyi\Desktop\desktop foders\SITP\SITP DATA\allDatasetInNrrd\002\t1.nrrd"
    
    all_slices, first_slice = nrrd2base64(image_path)
    print(f"总切片数: {len(all_slices)}")
    print(f"第一张切片base64长度: {len(first_slice)}")


