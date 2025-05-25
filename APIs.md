# **后端接口文档**

## **认证管理**

### **1. 用户注册接口**

- **接口**：`POST /auth/register`
- **功能**：用户注册，支持注册医生或患者账号。
- **请求参数**（JSON）：
    ```json
    {
      "phoneNumber": "手机号",
      "password": "密码",
      "userType": "用户类型 ('doctor' 或 'patient')"
    }
    ```
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 201,
      "message": "注册成功"
    }
    ```
    - 失败（字段未填）：
    ```json
    {
      "code": 400,
      "message": "所有字段均为必填"
    }
    ```
    - 失败（手机号已注册）：
    ```json
    {
      "code": 400,
      "message": "手机号已被注册"
    }
    ```

### **2. 用户登录接口**

- **接口**：`POST /auth/login`
- **功能**：用户登录，验证手机号和密码，成功后返回 JWT 令牌。
- **请求参数**（JSON）：
    ```json
    {
      "phoneNumber": "手机号",
      "password": "密码"
    }
    ```
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "登录成功",
      "token": "JWT令牌",
      "data": {
        "userId": "用户ID",
        "name": "真实姓名",
        "phoneNumber": "手机号",
        "userType": "用户类型 ('doctor' 或 'patient')",
        "isAuthenticated": "是否已认证"
      }
    }
    ```
    - 失败（手机号或密码错误）：
    ```json
    {
      "code": 404,
      "message": "用户不存在"
    }
    ```
    ```json
    {
      "code": 401,
      "message": "密码错误"
    }
    ```

### **3. 医生认证接口**

- **接口**：`POST /auth/authenticate/doctor`
- **功能**：进行医生认证，更新医生的真实姓名、所属医院、部门、职称并标记为已认证。
- **请求参数**（JSON）：
    ```json
    {
      "userId": "用户ID",
      "realName": "真实姓名",
      "hospital": "医院",
      "department": "部门",
      "title": "职称"
    }
    ```
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "认证成功"
    }
    ```
    - 失败（字段未填）：
    ```json
    {
      "code": 400,
      "message": "用户ID和真实姓名为必填"
    }
    ```
    - 失败（用户已认证）：
    ```json
    {
      "code": 403,
      "message": "医生已认证，无需重复认证"
    }
    ```
    - 失败（用户不存在）：
    ```json
    {
      "code": 404,
      "message": "医生不存在"
    }
    ```

### **4. 患者认证接口**

- **接口**：`POST /auth/authenticate/patient`
- **功能**：进行患者认证，更新患者的真实姓名、性别、年龄并标记为已认证。
- **请求参数**（JSON）：
    ```json
    {
      "userId": "用户ID",
      "realName": "真实姓名",
      "age": "年龄",
      "gender": "性别 (1/0 分别代表 男/女)"
    }
    ```
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "认证成功"
    }
    ```
    - 失败（字段未填）：
    ```json
    {
      "code": 400,
      "message": "用户ID和真实姓名为必填"
    }
    ```
    - 失败（用户已认证）：
    ```json
    {
      "code": 403,
      "message": "患者已认证，无需重复认证"
    }
    ```
    - 失败（用户不存在）：
    ```json
    {
      "code": 404,
      "message": "患者不存在"
    }
    ```

### **5. 认证状态重置接口**

- **接口**：`PATCH /auth/resetAuth`
- **功能**：重置认证状态，以便重新认证。
- **路径参数**：
  - `user_id`：用户的唯一标识符。
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "认证状态已重置"
    }
    ```
    - 失败（用户不存在）：
    ```json
    {
      "code": 404,
      "message": "用户不存在"
    }
    ```
    - 失败（用户未认证）：
    ```json
    {
      "code": 403,
      "message": "用户未认证，不可重置认证状态"
    }
    ```
    - 失败（数据库操作失败）：
    ```json
    {
      "code": 500,
      "message": "认证状态重置失败: <错误信息>"
    }
    ```
  
---

### **请求和响应状态码说明**：
- **200 OK**：请求成功。
- **201 Created**：资源创建成功（如注册成功）。
- **400 Bad Request**：请求参数不正确。
- **401 Unauthorized**：认证失败（如密码错误）。
- **403 Forbidden**：操作被禁止（如用户已认证）。
- **404 Not Found**：找不到用户或资源。
- **500 Internal Server Error**：服务器错误，操作失败。

---

## **患者管理**

### **1. 获取患者列表接口**

- **接口**：`GET /manage/<doctor_id>/all`
- **功能**：获取指定医生管理的所有患者的基本信息。
- **路径参数**：
  - `doctor_id`：医生的唯一标识符。
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "data": [
        {
          "userId": "患者ID",
          "name": "患者姓名",
          "age": "患者年龄",
          "gender": "患者性别"
        }
      ]
    }
    ```
    - 失败（医生不存在）：
    ```json
    {
      "code": 404,
      "message": "医生不存在"
    }
    ```

### **2. 添加患者接口**

- **接口**：`PATCH /manage/<doctor_id>/add`
- **功能**：将指定患者添加到指定医生的患者列表。
- **路径参数**：
  - `doctor_id`：医生的唯一标识符。
- **查询参数**：
  - `patient_id`：患者的唯一标识符。
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "添加患者成功"
    }
    ```
    - 失败（缺失患者ID）：
    ```json
    {
      "code": 400,
      "message": "缺失患者ID"
    }
    ```
    - 失败（医生不存在）：
    ```json
    {
      "code": 404,
      "message": "医生不存在"
    }
    ```
    - 失败（患者不存在）：
    ```json
    {
      "code": 404,
      "message": "患者不存在"
    }
    ```
    - 失败（数据库操作失败）：
    ```json
    {
      "code": 500,
      "message": "添加患者失败: <错误信息>"
    }
    ```

### **3. 移除患者接口**

- **接口**：`PATCH /manage/<doctor_id>/remove`
- **功能**：将指定患者从指定医生的患者列表中移除。
- **路径参数**：
  - `doctor_id`：医生的唯一标识符。
- **查询参数**：
  - `patient_id`：患者的唯一标识符。
- **响应**（JSON）：
    - 成功：
    ```json
    {
      "code": 200,
      "message": "移除患者成功"
    }
    ```
    - 失败（缺失患者ID）：
    ```json
    {
      "code": 400,
      "message": "缺失患者ID"
    }
    ```
    - 失败（医生不存在）：
    ```json
    {
      "code": 404,
      "message": "医生不存在"
    }
    ```
    - 失败（患者不存在）：
    ```json
    {
      "code": 404,
      "message": "患者不存在"
    }
    ```
    - 失败（数据库操作失败）：
    ```json
    {
      "code": 500,
      "message": "移除患者失败: <错误信息>"
    }
    ```

---

### **请求和响应状态码说明**：
- **200 OK**：请求成功。
- **400 Bad Request**：请求参数不正确（如缺失患者ID）。
- **404 Not Found**：找不到指定的医生或患者。
- **500 Internal Server Error**：服务器错误，操作失败（如数据库操作失败）。

---

## **MRI图像管理**

---

### **1. MRI图像上传接口**

- **接口**：`POST /mri/upload/<patient_id>`
- **功能**：上传患者的 MRI 图像（T1 和 T2）。
- **路径参数**：
  - `patient_id`：患者的唯一标识符。
- **请求参数**：
  - **表单字段**：
    - `imagingDate`：图像拍摄日期，格式为 `YYYY-MM-DD`。
  - **文件字段**：
    - `t1File`：T1 MRI 图像文件（格式：`.nrrd`）。
    - `t2File`：T2 MRI 图像文件（格式：`.nrrd`）。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 201,
      "message": "文件上传成功"
    }
    ```
  - 失败：（缺少必要文件：）
    ```json
    {
      "code": 400,
      "message": "需要上传t1和t2文件"
    }
    ```
  - 失败（缺少拍摄日期）：
    ```json
      {
        "code": 400,
        "message": "缺少图像拍摄日期"
      }
    ```
  - 失败（文件上传失败）：
    ```json
    {
      "code": 500,
      "message": "文件上传失败: <错误信息>"
    }
      ```

---

### **2. 全部 MRI 图像获取接口**

- **接口**：`GET /mri/all/<patient_id>`
- **功能**：获取患者的全部 MRI 图像。
- **路径参数**：
  - `patient_id`：患者的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    [
      {
        "imageId": "MRI图像ID",
        "allSlicesT1": ["T1序列所有切片的base64编码数组"],
        "firstSliceT1": "T1序列第一张切片的base64编码",
        "allSlicesT2": ["T2序列所有切片的base64编码数组"],
        "firstSliceT2": "T2序列第一张切片的base64编码",
        "hasReport": "是否已生成报告",
        "imageDate": "图像拍摄日期"
      }
    ]
    ```
  - 失败：
    ```json
    {
      "code": 404,
      "message": "没有找到相关MRI图像"
    }
    ```

---

### **3. MRI 图像按时间段获取接口**

- **接口**：`GET /mri/period/<patient_id>`
- **功能**：按时间范围获取患者的 MRI 图像。
- **路径参数**：
  - `patient_id`：患者的唯一标识符。
- **查询参数**：
  - `startDate`：起始日期，格式为 `YYYY-MM-DD`。
  - `endDate`：结束日期，格式为 `YYYY-MM-DD`。
- **响应**（JSON）：
  - 成功：
    ```json
    [
      {
        "imageId": "MRI图像ID",
        "allSlicesT1": ["T1序列所有切片的base64编码数组"],
        "firstSliceT1": "T1序列第一张切片的base64编码",
        "allSlicesT2": ["T2序列所有切片的base64编码数组"],
        "firstSliceT2": "T2序列第一张切片的base64编码",
        "hasReport": "是否已生成报告",
        "imageDate": "图像拍摄日期"
      }
    ]
    ```
  - 失败（参数缺失）：
    ```json
    {
      "code": 400,
      "message": "缺少患者ID或时间范围"
    }
      ```
  - 失败（日期格式错误）：
    ```json
    {
      "code": 400,
      "message": "日期格式错误，应为YYYY-MM-DD"
    }
      ```
  - 失败（未找到图像）：
    ```json
    {
      "code": 404,
      "message": "没有找到相关MRI图像"
    }
      ```

---

### **4. 获取 MRI 图像详情接口**

- **接口**：`GET /mri/details`
- **功能**：获取某个 MRI 图像的详细信息（T1 和 T2 文件及临床指标）。
- **查询参数**：
  - `imageId`：MRI 图像的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": {
        "clinicalIndicators": { ... },
        "file": "<下载文件的URL>"
      }
    }
    ```
  - 失败（缺少 MRI 图像 ID）：
    ```json
      {
        "code": 400,
        "message": "缺少MRI图像ID"
      }
      ```
  - 失败（找不到图像）：
    ```json
      {
        "code": 404,
        "message": "没有找到相关MRI图像"
      }
      ```

---

### **5. 获取某时间段内的临床指标接口**

- **接口**：`GET /mri/clinical/<patient_id>`
- **功能**：获取患者一段时间内的某个临床指标。
- **路径参数**：
  - `patient_id`：患者的唯一标识符。
- **查询参数**：
  - `startDate`：起始日期，格式为 `YYYY-MM-DD`。
  - `endDate`：结束日期，格式为 `YYYY-MM-DD`。
  - `indicatorType`：临床指标的类型。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": [ ... ]  // 指标值列表
    }
    ```
  - 失败（缺少参数）：
    ```json
    {
      "code": 400,
      "message": "时间范围或临床指标类型缺失"
    }
      ```
  - 失败（日期格式错误）：
    ```json
    {
      "code": 400,
      "message": "日期格式错误，应为YYYY-MM-DD"
    }
      ```
  - 失败（无相关图像）：
    ```json
    {
      "code": 404,
      "message": "没有找到相关MRI图像"
    }
      ```

---

### **6. MRI 影像分析接口**

- **接口**：`POST /mri/analyse/<image_id>`
- **功能**：分析 MRI 图像并返回预测结果。
- **路径参数**：
  - `image_id`：MRI图像的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": {
        "prediction": "预测结果（0或1）",
        "probability": "预测概率"
      }
    }
    ```
  - 失败：
    ```json
    {
      "code": 500,
      "message": "模型预测失败"
    }
    ```

---

### **7. 上传临床数据接口**

- **接口**：`POST /mri/upload/all/<image_id>`
- **功能**：上传 MRI 图像相关的所有临床数据。
- **路径参数**：
  - `image_id`：MRI图像的唯一标识符。
- **请求参数**（JSON）：
    ```json
    {
      "imagingDate": "图像拍摄日期",
      "imagingHospital": "拍摄医院",
      "result": "分析结果",
      "fibroidsPresent": "肌瘤数量",
      "avgTreatmentPower": "平均治疗功率",
      "totalEnergy": "总能量",
      "treatmentVolume": "治疗体积",
      "parity": "生育次数",
      "miscarriageCount": "流产次数",
      "wbcCount": "白细胞计数",
      "basophilAbsolute": "嗜碱性粒细胞绝对值",
      "eosinophilAbsolute": "嗜酸性粒细胞绝对值",
      "neutrophilAbsolute": "中性粒细胞绝对值",
      "lymphocyteAbsolute": "淋巴细胞绝对值",
      "monocyteAbsolute": "单核细胞绝对值",
      "rbcCount": "红细胞计数",
      "hemoglobin": "血红蛋白",
      "hematocrit": "红细胞压积",
      "mcv": "平均红细胞体积",
      "mch": "平均红细胞血红蛋白含量",
      "mchc": "平均红细胞血红蛋白浓度",
      "rdwCv": "红细胞分布宽度变异系数",
      "rdwSd": "红细胞分布宽度标准差",
      "plateletCount": "血小板计数",
      "pdw": "血小板分布宽度",
      "mpv": "平均血小板体积",
      "neutrophilPercentage": "中性粒细胞百分比",
      "lymphocytePercentage": "淋巴细胞百分比",
      "monocytePercentage": "单核细胞百分比",
      "eosinophilPercentage": "嗜酸性粒细胞百分比",
      "basophilPercentage": "嗜碱性粒细胞百分比"
    }
    ```
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "message": "临床数据上传成功"
    }
    ```
  - 失败：
    ```json
    {
      "code": 404,
      "message": "没有找到相关MRI图像"
    }
    ```

---

### **状态码说明**
- **200 OK**：请求成功。
- **201 Created**：资源创建成功。
- **400 Bad Request**：请求参数缺失或格式错误。
- **404 Not Found**：找不到相关资源。
- **500 Internal Server Error**：服务器错误。

---

以下是 `personController` 的接口文档：

---

## **人员管理**

---

### **1. 全部医生基本信息获取接口**

- **接口**：`GET /person/doctor/all`
- **功能**：获取所有医生的基本信息。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": [ ... ]  // 医生信息列表
    }
    ```
  - 失败：
    ```json
    {
      "code": 500,
      "message": "获取医生信息失败: <错误信息>"
    }
    ```

---

### **2. 指定ID医生基本信息获取接口**

- **接口**：`GET /person/doctor/select/<doctor_id>`
- **功能**：根据医生 ID 获取该医生的基本信息。
- **路径参数**：
  - `doctor_id`：医生的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 医生信息
    }
    ```
  - 失败：
    - 医生不存在：
      ```json
      {
        "error": "医生不存在"
      }
      ```
    - 其他错误：
      ```json
      {
        "code": 500,
        "message": "获取医生信息失败: <错误信息>"
      }
      ```

---

### **3. 患者主管医生基本信息获取接口**

- **接口**：`GET /person/doctor/charge`
- **功能**：根据患者 ID 获取该患者的主管医生信息。
- **查询参数**：
  - `patient_id`：患者的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 医生信息
    }
    ```
  - 失败：
    - 缺少参数：
      ```json
      {
        "code": 400,
        "message": "患者ID为必填参数"
      }
      ```
    - 患者不存在：
      ```json
      {
        "code": 404,
        "message": "患者不存在"
      }
      ```
    - 无主管医生：
      ```json
      {
        "code": 404,
        "message": "该患者没有主管医生"
      }
      ```
    - 其他错误：
      ```json
      {
        "code": 500,
        "message": "获取主管医生信息失败: <错误信息>"
      }
      ```

---

### **4. 全部患者基本信息获取接口**

- **接口**：`GET /person/patient/all`
- **功能**：获取所有患者的基本信息。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": [ ... ]  // 患者信息列表
    }
    ```
  - 失败：
    ```json
    {
      "code": 500,
      "message": "获取患者信息失败: <错误信息>"
    }
    ```

---

### **5. 指定ID患者基本信息获取接口**

- **接口**：`GET /person/patient/select/<patient_id>`
- **功能**：根据患者 ID 获取该患者的基本信息。
- **路径参数**：
  - `patient_id`：患者的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 患者信息
    }
    ```
  - 失败：
    - 患者不存在：
      ```json
      {
        "code": 404,
        "message": "患者不存在"
      }
      ```
    - 其他错误：
      ```json
      {
        "code": 500,
        "message": "获取患者信息失败: <错误信息>"
      }
      ```

---

### **6. 医生负责患者列表获取接口**

- **接口**：`GET /person/patient/charge`
- **功能**：根据医生 ID 获取该医生负责的患者列表。
- **查询参数**：
  - `doctor_id`：医生的唯一标识符。
- **响应**（JSON）：
  - 成功：
    ```json
    {
      "code": 200,
      "data": [ ... ]  // 患者信息列表
    }
    ```
  - 失败：
    - 缺少参数：
      ```json
      {
        "code": 400,
        "message": "医生ID为必填参数"
      }
      ```
    - 医生不存在：
      ```json
      {
        "error": "医生不存在"
      }
      ```
    - 其他错误：
      ```json
      {
        "error": "获取患者列表失败: <错误信息>"
      }
      ```

---

### **状态码说明**
- **200 OK**：请求成功。
- **400 Bad Request**：请求参数缺失或格式错误。
- **404 Not Found**：找不到相关资源。
- **500 Internal Server Error**：服务器错误。

---

## **报告管理**

---

### **1. 报告生成接口**

- **接口**：`POST /report/generate`
- **功能**：根据上传的 MRI 图像生成分析报告。
- **请求参数**：
  - **JSON**：
    - `imageId` (必填)：MRI 图像 ID。
    - `doctorId` (必填)：医生 ID。
    - `radiomicComment` (选填)：放射组学注释。
    - `therapyComment` (选填)：治疗建议注释。
  - **文件**：
    - `roi_t1` (必填)：T1 ROI 图像文件。
    - `roi_t2` (必填)：T2 ROI 图像文件。
- **响应**：
  - 成功：
    ```json
    {
      "code": 201,
      "message": "报告生成成功",
      "data": { ... }  // 报告详细内容
    }
    ```
  - 失败：
    - 参数缺失：
      ```json
      {
        "code": 400,
        "message": "缺少MRI图像ID或医生ID"
      }
      ```
    - 文件缺失：
      ```json
      {
        "code": 400,
        "message": "缺少ROI图像文件 (T1 或 T2)"
      }
      ```
    - 数据库错误：
      ```json
      {
        "code": 500,
        "message": "报告生成失败: <错误信息>"
      }
      ```

---

### **2. 获取患者最近一份报告的粗略信息**

- **接口**：`GET /report/last`
- **功能**：获取指定患者最近生成的报告的摘要信息。
- **查询参数**：
  - `patientId` (必填)：患者 ID。
- **响应**：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 报告摘要信息
    }
    ```
  - 失败：
    - 参数缺失：
      ```json
      {
        "code": 400,
        "message": "缺少患者ID"
      }
      ```
    - 报告不存在：
      ```json
      {
        "code": 404,
        "message": "未找到任何报告"
      }
      ```

---

### **3. 获取患者所有报告的粗略信息**

- **接口**：`GET /report/all`
- **功能**：获取指定患者所有报告的摘要信息。
- **查询参数**：
  - `patientId` (必填)：患者 ID。
- **响应**：
  - 成功：
    ```json
    {
      "code": 200,
      "data": [ ... ]  // 报告摘要信息列表
    }
    ```
  - 失败：
    - 参数缺失：
      ```json
      {
        "code": 400,
        "message": "缺少患者ID"
      }
      ```

---

### **4. 获取某一份报告的详细内容**

- **接口**：`GET /report/detail/<report_id>`
- **功能**：根据报告 ID 获取详细内容。
- **路径参数**：
  - `report_id`：报告 ID。
- **响应**：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 报告详细内容
    }
    ```
  - 失败：
    ```json
    {
      "code": 404,
      "message": "报告不存在"
    }
    ```

---

### **5. 获取某个 MRI 图像对应的分析报告**

- **接口**：`GET /report/ofImage`
- **功能**：根据 MRI 图像 ID 获取对应的分析报告。
- **查询参数**：
  - `imageId` (必填)：MRI 图像 ID。
- **响应**：
  - 成功：
    ```json
    {
      "code": 200,
      "data": { ... }  // 报告详细内容
    }
    ```
  - 失败：
    - 参数缺失：
      ```json
      {
        "code": 400,
        "message": "缺少MRI图像ID"
      }
      ```
    - 报告不存在：
      ```json
      {
        "code": 404,
        "message": "该MRI图像尚未生成分析报告"
      }
      ```

---

### **6. 编辑报告**

- **接口**：`POST /report/edit/<report_id>`
- **功能**：编辑指定报告的放射组学和治疗注释。
- **路径参数**：
  - `report_id`：报告 ID。
- **请求参数**：
  - **JSON**：
    - `radiomicComment` (选填)：放射组学注释。
    - `therapyComment` (选填)：治疗建议注释。
- **响应**：
  - 成功：
    ```json
    {
      "code": 200,
      "message": "报告编辑成功",
      "data": { ... }  // 报告详细内容
    }
    ```
  - 失败：
    - 报告不存在：
      ```json
      {
        "code": 404,
        "message": "未找到相关报告"
      }
      ```
    - 数据库错误：
      ```json
      {
        "code": 500,
        "message": "报告编辑失败: <错误信息>"
      }
      ```

---

### **状态码说明**
- **200 OK**：请求成功。
- **201 Created**：资源创建成功。
- **400 Bad Request**：请求参数缺失或错误。
- **404 Not Found**：资源不存在。
- **500 Internal Server Error**：服务器错误。

---

## DTO文档

---

### 1. **患者信息**  
从患者记录中提取，字段如下：
- **`userId`** (int): 患者的唯一标识符。
- **`name`** (string): 患者姓名。
- **`age`** (int): 患者年龄。
- **`gender`** (string): 患者性别。

---

### 2. **医生信息**  
从医生记录中提取，字段如下：
- **`userId`** (int): 医生的唯一标识符。
- **`name`** (string): 医生姓名。
- **`hospital`** (string): 医生所属医院。
- **`department`** (string): 医生所属科室。
- **`title`** (string): 医生的职称。

---

### 3. **临床指标**  
从MRI图像记录中提取，字段如下：
- **`fibroidsPresent`** (int): 子宫肌瘤个数。
- **`avgTreatmentPower`** (float): 平均治疗功率 (单位: W)。
- **`totalEnergy`** (float): 总能量 (单位: J)。
- **`treatmentVolume`** (float): 治疗体积 (单位: cm³)。
- **`parity`** (int): 生育次数。
- **`miscarriageCount`** (int): 流产次数。
- **`bloodRoutine`** (object): 血常规对象，包含除 `bloodRoutineId` 外的其他字段。

---

### 4. **MRI图像简略信息**  
从MRI图像记录中提取，字段如下：
- **`imageId`** (int): MRI图像的唯一标识符。
- **`result`** (string): MRI分析结果。

---

### 5. **报告详细内容**  
从报告记录中提取，字段如下：
- **`imageId`** (int): MRI图像的唯一标识符。
- **`doctorId`** (int): 报告生成医生的唯一标识符。
- **`radiomicComment`** (string): 放射组学备注。
- **`therapyComment`** (string): 治疗备注。
- **`generationDate`** (string): 报告生成日期 (ISO 8601 格式)。
- **`doctorName`** (string): 生成报告的医生姓名。
- **`result`** (string): MRI图像分析结果。
- **`clinicalIndicators`** (object): 包含临床指标字段的对象。

---

### 6. **报告简略信息**  
从报告记录中提取，字段如下：
- **`reportId`** (int): 报告的唯一标识符。
- **`generationDate`** (string): 报告生成日期 (ISO 8601 格式)。
- **`result`** (string): MRI图像分析结果。
- **`clinicalIndicators`** (object): 包含临床指标字段的对象。
