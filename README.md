# 数据处理与文书解析工具

这个Python项目包含两个功能模块：
1. RAGFLOW文档上传和解析功能
2. 中国裁判文书网文书下载和解析功能

## 功能

### RAGFLOW模块
- 从指定文件夹读取文本文件
- 调用RAGFLOW API上传文档并解析
- 支持多种文本格式处理

### 裁判文书网模块
- 通过关键词搜索裁判文书
- 批量下载文书内容
- 解析文书为结构化数据
- 上传解析后的文书到RAGFLOW平台

## 目录结构

```
processing-data/
├── src/
│   ├── ragflow/            # RAGFLOW上传解析功能
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── utils.py
│   │   ├── file_processor.py
│   │   ├── ragflow_client.py
│   │   └── main.py
│   │
│   ├── wenshu/             # 裁判文书网功能
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── utils.py
│   │   ├── wenshu_downloader.py
│   │   ├── wenshu_parser.py
│   │   └── wenshu_cli.py
│   │
│   └── __init__.py
│
├── data/                   # RAGFLOW输入文件目录
├── wenshu_downloads/       # 裁判文书下载目录
├── wenshu_parsed/          # 裁判文书解析结果目录
├── ragflow_app.py          # RAGFLOW功能入口
├── wenshu_app.py           # 裁判文书网功能入口
├── requirements.txt
└── README.md
```

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

### RAGFLOW模块

运行RAGFLOW处理程序:

```
python ragflow_app.py --input_dir ./data --output_dir ./results
```

参数说明:
- `--input_dir`: 输入文件目录
- `--output_dir`: 输出结果保存目录

### 裁判文书网模块

使用命令行工具下载裁判文书:

```
python wenshu_app.py download --keywords "民间借贷" --output_dir ./wenshu_downloads
```

更多参数选项:
- `--keywords`: 搜索关键词（必需）
- `--output_dir`: 输出目录，默认为 "./wenshu_downloads"
- `--max_pages`: 最大搜索页数，默认为 5
- `--case_type`: 案件类型，如"民事案件"、"刑事案件"等
- `--court`: 法院名称
- `--date_from`: 开始日期，格式为 YYYY-MM-DD
- `--date_to`: 结束日期，格式为 YYYY-MM-DD
- `--cookie`: 用户Cookie（推荐使用，避免被反爬）
- `--proxy`: 代理服务器地址，格式为"http://ip:port"

解析已下载的裁判文书:

```
python wenshu_app.py parse --input_dir ./wenshu_downloads --output_dir ./wenshu_parsed
```

一键下载并解析:

```
python wenshu_app.py download-parse --keywords "民间借贷" --download_dir ./wenshu_downloads --parse_dir ./wenshu_parsed
```

上传解析后的文书到RAGFLOW:

```
python wenshu_app.py upload --input_dir ./wenshu_parsed
```

## 注意事项

### RAGFLOW模块
- 确保有有效的RAGFLOW API密钥
- 支持的文件格式有：.txt、.md、.pdf、.docx（可在.env文件中自定义）

### 裁判文书网模块
- 中国裁判文书网有反爬虫机制，建议使用Cookie和代理
- 获取Cookie的方法：在浏览器中登录裁判文书网后，复制Cookie信息
- 下载过程设置了随机延时，避免频繁请求被封IP
- 裁判文书解析功能基于页面结构，如果官网结构变化可能需要调整解析逻辑