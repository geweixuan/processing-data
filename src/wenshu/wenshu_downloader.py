"""
中国裁判文书网下载模块，用于搜索和下载裁判文书
"""

import logging
import time
import json
import random
import base64
import hashlib
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 设置日志
logger = logging.getLogger(__name__)


class WenshuDownloader:
    """中国裁判文书网文书下载器"""
    
    def __init__(self, cookie: str = None, use_proxy: bool = False, proxy: str = None):
        """
        初始化文书下载器
        
        Args:
            cookie: 用户登录后的Cookie字符串
            use_proxy: 是否使用代理
            proxy: 代理服务器地址，格式为"http://ip:port"
        """
        self.base_url = "https://wenshu.court.gov.cn"
        self.search_url = f"{self.base_url}/website/parse/rest.q4w"
        self.document_url = f"{self.base_url}/website/parse/detail"
        
        # 设置请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/website/wenshu/181029CAIRB5JXZA/index.html",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive"
        }
        
        if cookie:
            self.headers["Cookie"] = cookie
        
        # 设置代理
        self.proxies = None
        if use_proxy and proxy:
            self.proxies = {
                "http": proxy,
                "https": proxy
            }
        
        # 初始化会话
        self.session = requests.Session()
        for key, value in self.headers.items():
            self.session.headers[key] = value
        
        logger.info("初始化裁判文书网下载器")
    
    def _generate_request_id(self) -> str:
        """
        生成请求ID
        
        Returns:
            请求ID字符串
        """
        guid = ""
        for i in range(1, 32):
            n = str(hex(int(random.random() * 16.0))[2:]).upper()
            guid += n
            if i in [8, 12, 16, 20]:
                guid += "-"
        return guid
    
    def _encrypt_param(self, param: Dict) -> str:
        """
        加密请求参数
        
        Args:
            param: 请求参数字典
        
        Returns:
            加密后的参数字符串
        """
        # 这里简化处理，实际上裁判文书网有更复杂的加密机制
        param_str = json.dumps(param)
        return base64.b64encode(param_str.encode()).decode()
    
    def search_documents(self, 
                        keywords: str, 
                        case_type: str = None, 
                        court: str = None, 
                        date_from: str = None, 
                        date_to: str = None, 
                        page: int = 1, 
                        page_size: int = 10) -> Dict[str, Any]:
        """
        搜索文书
        
        Args:
            keywords: 搜索关键词
            case_type: 案件类型
            court: 法院名称
            date_from: 开始日期，格式为YYYY-MM-DD
            date_to: 结束日期，格式为YYYY-MM-DD
            page: 页码
            page_size: 每页结果数
            
        Returns:
            搜索结果
        """
        # 构造查询参数
        search_param = {
            "sortFields": "s50:desc",
            "ciphertext": self._generate_request_id(),
            "pageNum": page,
            "pageSize": page_size,
            "queryCondition": []
        }
        
        # 添加关键词
        if keywords:
            search_param["queryCondition"].append({"key": "s8", "value": keywords})
        
        # 添加案件类型
        if case_type:
            search_param["queryCondition"].append({"key": "s9", "value": case_type})
        
        # 添加法院
        if court:
            search_param["queryCondition"].append({"key": "s2", "value": court})
        
        # 添加日期范围
        if date_from or date_to:
            date_range = []
            if date_from:
                date_range.append(date_from)
            else:
                date_range.append("1900-01-01")
            
            if date_to:
                date_range.append(date_to)
            else:
                date_range.append(datetime.now().strftime("%Y-%m-%d"))
            
            search_param["queryCondition"].append({"key": "cprq", "value": ",".join(date_range)})
        
        try:
            # 加密参数
            encrypted_param = self._encrypt_param(search_param)
            
            # 构造请求表单
            form_data = {
                "pageId": self._generate_request_id(),
                "s8": keywords,
                "sortFields": "s50:desc",
                "ciphertext": search_param["ciphertext"],
                "pageNum": page,
                "pageSize": page_size,
                "queryCondition": json.dumps(search_param["queryCondition"]),
                "cfg": "com.lawyee.judge.dc.parse.dto.SearchDataDsoDTO@queryDoc"
            }
            
            # 添加延时，避免请求过于频繁
            time.sleep(random.uniform(1, 3))
            
            logger.info(f"搜索文书，关键词: {keywords}, 页码: {page}")
            response = self.session.post(
                self.search_url, 
                data=form_data,
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"搜索请求失败，状态码: {response.status_code}")
                return {"success": False, "error": f"搜索请求失败，状态码: {response.status_code}"}
            
            try:
                result = response.json()
                return {"success": True, "data": result}
            except json.JSONDecodeError:
                logger.error("解析搜索结果失败，响应不是有效的JSON格式")
                return {"success": False, "error": "解析搜索结果失败，响应不是有效的JSON格式"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"搜索请求异常: {str(e)}")
            return {"success": False, "error": f"搜索请求异常: {str(e)}"}
    
    def get_document_detail(self, doc_id: str) -> Dict[str, Any]:
        """
        获取文书详情
        
        Args:
            doc_id: 文书ID
            
        Returns:
            文书详情
        """
        try:
            # 构造详情页URL
            detail_url = f"{self.document_url}/{doc_id}"
            
            # 添加延时，避免请求过于频繁
            time.sleep(random.uniform(2, 5))
            
            logger.info(f"获取文书详情，文书ID: {doc_id}")
            response = self.session.get(
                detail_url,
                proxies=self.proxies,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"获取文书详情请求失败，状态码: {response.status_code}")
                return {"success": False, "error": f"获取文书详情请求失败，状态码: {response.status_code}"}
            
            # 从响应中提取文书内容
            # 注意：实际情况中可能需要更复杂的解析过程
            try:
                # 这里简化处理，实际上需要对页面进行解析
                content = response.text
                return {"success": True, "content": content, "doc_id": doc_id}
            except Exception as e:
                logger.error(f"解析文书详情失败: {str(e)}")
                return {"success": False, "error": f"解析文书详情失败: {str(e)}"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取文书详情请求异常: {str(e)}")
            return {"success": False, "error": f"获取文书详情请求异常: {str(e)}"}
    
    def download_document(self, doc_id: str, output_dir: str) -> Dict[str, Any]:
        """
        下载文书并保存
        
        Args:
            doc_id: 文书ID
            output_dir: 输出目录
            
        Returns:
            下载结果
        """
        # 获取文书详情
        detail_result = self.get_document_detail(doc_id)
        if not detail_result.get("success", False):
            return detail_result
        
        content = detail_result.get("content", "")
        
        try:
            # 确保输出目录存在
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 保存文书内容
            file_path = output_path / f"{doc_id}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info(f"文书已保存到 {file_path}")
            return {
                "success": True, 
                "file_path": str(file_path), 
                "doc_id": doc_id
            }
            
        except Exception as e:
            logger.error(f"保存文书失败: {str(e)}")
            return {"success": False, "error": f"保存文书失败: {str(e)}"}
    
    def batch_download(self, 
                       keywords: str, 
                       output_dir: str, 
                       max_pages: int = 5, 
                       case_type: str = None, 
                       court: str = None, 
                       date_from: str = None, 
                       date_to: str = None) -> Dict[str, Any]:
        """
        批量下载文书
        
        Args:
            keywords: 搜索关键词
            output_dir: 输出目录
            max_pages: 最大页数
            case_type: 案件类型
            court: 法院名称
            date_from: 开始日期，格式为YYYY-MM-DD
            date_to: 结束日期，格式为YYYY-MM-DD
            
        Returns:
            下载结果统计
        """
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "documents": []
        }
        
        for page in range(1, max_pages + 1):
            # 搜索文书
            search_result = self.search_documents(
                keywords=keywords,
                case_type=case_type,
                court=court,
                date_from=date_from,
                date_to=date_to,
                page=page
            )
            
            if not search_result.get("success", False):
                logger.error(f"第 {page} 页搜索失败: {search_result.get('error', '未知错误')}")
                continue
            
            # 解析搜索结果
            search_data = search_result.get("data", {})
            result_list = search_data.get("queryResult", {}).get("resultList", [])
            
            if not result_list:
                logger.info(f"第 {page} 页没有搜索结果，停止搜索")
                break
            
            logger.info(f"第 {page} 页找到 {len(result_list)} 条结果")
            stats["total"] += len(result_list)
            
            # 下载每个文书
            for doc in result_list:
                doc_id = doc.get("rowkey", "")
                if not doc_id:
                    logger.warning("文书ID为空，跳过")
                    stats["failed"] += 1
                    continue
                
                # 下载文书
                download_result = self.download_document(doc_id, output_dir)
                
                if download_result.get("success", False):
                    stats["success"] += 1
                    stats["documents"].append({
                        "doc_id": doc_id,
                        "file_path": download_result.get("file_path", ""),
                        "title": doc.get("s1", ""),
                        "court": doc.get("s2", ""),
                        "case_number": doc.get("s7", ""),
                        "publish_date": doc.get("s41", "")
                    })
                else:
                    stats["failed"] += 1
                
                # 添加随机延时，避免请求过于频繁
                time.sleep(random.uniform(3, 8))
        
        logger.info(f"批量下载完成，总数: {stats['total']}，成功: {stats['success']}，失败: {stats['failed']}")
        return stats 