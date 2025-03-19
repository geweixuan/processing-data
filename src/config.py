"""
配置模块，用于加载环境变量和配置项
"""

import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# RAGFLOW API配置
RAGFLOW_API_KEY = os.getenv("RAGFLOW_API_KEY")
RAGFLOW_API_URL = os.getenv("RAGFLOW_API_URL")

# 文件处理配置
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 默认10MB
SUPPORTED_EXTENSIONS = os.getenv("SUPPORTED_EXTENSIONS", ".txt,.md,.pdf,.docx").split(",")

# 验证必要的配置
if not RAGFLOW_API_KEY:
    raise ValueError("缺少RAGFLOW_API_KEY环境变量配置")

if not RAGFLOW_API_URL:
    raise ValueError("缺少RAGFLOW_API_URL环境变量配置") 