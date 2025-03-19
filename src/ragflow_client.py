"""
RAGFLOW API客户端模块，用于调用RAGFLOW API上传和解析文档
"""

import logging
import requests
from typing import Dict, Any, Optional, List

from . import config

# 设置日志
logger = logging.getLogger(__name__)


class RAGFlowClient:
    """RAGFLOW API客户端，用于上传和解析文档"""
    
    def __init__(self):
        """初始化RAGFLOW API客户端"""
        self.api_key = config.RAGFLOW_API_KEY
        self.api_url = config.RAGFLOW_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        logger.info("初始化RAGFLOW API客户端")
    
    def upload_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        上传文档到RAGFLOW
        
        Args:
            document_data: 文档数据，包含文件内容和元数据
        
        Returns:
            API响应结果
        """
        upload_endpoint = f"{self.api_url}/documents/upload"
        
        payload = {
            'content': document_data['content'],
            'metadata': {
                'filename': document_data['file_name'],
                'extension': document_data['extension'],
                'source_path': document_data['file_path']
            }
        }
        
        try:
            logger.info(f"上传文档 {document_data['file_name']} 到RAGFLOW")
            response = requests.post(upload_endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"文档 {document_data['file_name']} 上传成功，文档ID: {result.get('document_id', 'unknown')}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"上传文档 {document_data['file_name']} 失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"错误响应: {e.response.text}")
            raise
    
    def parse_document(self, document_id: str) -> Dict[str, Any]:
        """
        解析已上传的文档
        
        Args:
            document_id: 文档ID
        
        Returns:
            解析结果
        """
        parse_endpoint = f"{self.api_url}/documents/{document_id}/parse"
        
        try:
            logger.info(f"解析文档 ID: {document_id}")
            response = requests.post(parse_endpoint, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            logger.info(f"文档 ID: {document_id} 解析成功")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"解析文档 ID: {document_id} 失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"错误响应: {e.response.text}")
            raise
    
    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        获取文档处理状态
        
        Args:
            document_id: 文档ID
        
        Returns:
            文档状态信息
        """
        status_endpoint = f"{self.api_url}/documents/{document_id}/status"
        
        try:
            logger.info(f"获取文档 ID: {document_id} 的状态")
            response = requests.get(status_endpoint, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"获取文档状态失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"错误响应: {e.response.text}")
            raise 