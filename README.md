# 数据处理与RAGFLOW上传工具

这个Python项目用于自动化处理文本文件并将其上传到RAGFLOW平台进行文档解析。

## 功能

- 从指定文件夹读取文本文件
- 调用RAGFLOW API上传文档并解析
- 支持多种文本格式处理

## 安装

1. 克隆此仓库
2. 安装依赖包:
   ```
   pip install -r requirements.txt
   ```
3. 创建`.env`文件并设置RAGFLOW API密钥:
   ```
   RAGFLOW_API_KEY=your_api_key_here
   RAGFLOW_API_URL=your_api_url_here
   ```

## 使用方法

运行主程序:

```
python src/main.py --input_dir ./data --output_dir ./results
```

参数说明:
- `--input_dir`: 输入文件目录
- `--output_dir`: 输出结果保存目录