"""
中国裁判文书解析模块，用于解析裁判文书内容
"""

import re
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

# 设置日志
logger = logging.getLogger(__name__)


class WenshuParser:
    """中国裁判文书解析器"""
    
    def __init__(self):
        """初始化文书解析器"""
        logger.info("初始化裁判文书解析器")
    
    def parse_html(self, html_content: str) -> Dict[str, Any]:
        """
        解析HTML格式的文书内容
        
        Args:
            html_content: HTML格式的文书内容
            
        Returns:
            解析后的文书数据
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 提取文书标题
            title_elem = soup.find('div', class_='ws_title') or soup.find('title')
            title = title_elem.get_text().strip() if title_elem else ""
            
            # 提取文书信息
            info = {}
            info_elem = soup.find('div', class_='ws_info')
            if info_elem:
                info_text = info_elem.get_text()
                # 提取案号
                case_number_match = re.search(r'[（(](\d+)[）)][\u4e00-\u9fa5]{1,4}第\d+号', info_text)
                if case_number_match:
                    info['case_number'] = case_number_match.group(0)
                
                # 提取法院名称
                court_match = re.search(r'[\u4e00-\u9fa5]+法院', info_text)
                if court_match:
                    info['court'] = court_match.group(0)
                
                # 提取日期
                date_match = re.search(r'\d{4}[\u4e00-\u9fa5]\d{1,2}[\u4e00-\u9fa5]\d{1,2}[\u4e00-\u9fa5]', info_text)
                if date_match:
                    info['date'] = date_match.group(0)
            
            # 提取文书正文
            content_elem = soup.find('div', class_='ws_content') or soup.find('div', class_='content')
            content = content_elem.get_text(separator='\n').strip() if content_elem else ""
            
            # 提取当事人信息
            parties = []
            party_elems = soup.find_all('div', class_='ws_party')
            for elem in party_elems:
                party_text = elem.get_text().strip()
                parties.append(party_text)
            
            # 提取审判人员
            judges = []
            judge_elems = soup.find_all('div', class_='ws_judge')
            for elem in judge_elems:
                judge_text = elem.get_text().strip()
                judges.append(judge_text)
            
            # 构造解析结果
            result = {
                'title': title,
                'info': info,
                'content': content,
                'parties': parties,
                'judges': judges
            }
            
            logger.info(f"成功解析文书，标题: {title}")
            return {"success": True, "data": result}
            
        except Exception as e:
            logger.error(f"解析HTML内容失败: {str(e)}")
            return {"success": False, "error": f"解析HTML内容失败: {str(e)}"}
    
    def parse_html_file(self, file_path: str) -> Dict[str, Any]:
        """
        解析HTML文件
        
        Args:
            file_path: HTML文件路径
            
        Returns:
            解析后的文书数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            result = self.parse_html(html_content)
            if result.get("success", False):
                result["file_path"] = file_path
            
            return result
            
        except Exception as e:
            logger.error(f"读取或解析文件 {file_path} 失败: {str(e)}")
            return {"success": False, "error": f"读取或解析文件失败: {str(e)}"}
    
    def extract_structured_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从解析后的数据中提取结构化信息
        
        Args:
            parsed_data: 解析后的文书数据
            
        Returns:
            结构化的文书数据
        """
        if not parsed_data.get("success", False):
            return parsed_data
        
        data = parsed_data.get("data", {})
        content = data.get("content", "")
        
        structured_data = {
            "title": data.get("title", ""),
            "court": data.get("info", {}).get("court", ""),
            "case_number": data.get("info", {}).get("case_number", ""),
            "date": data.get("info", {}).get("date", ""),
            "parties": data.get("parties", []),
            "judges": data.get("judges", []),
            "case_type": "",
            "cause_of_action": "",
            "keywords": [],
            "judgment_result": "",
            "laws_referenced": []
        }
        
        # 提取案件类型
        case_type_match = re.search(r'审判程序：([\u4e00-\u9fa5]+)', content)
        if case_type_match:
            structured_data["case_type"] = case_type_match.group(1)
        
        # 提取案由
        cause_match = re.search(r'案由：([\u4e00-\u9fa5]+)', content)
        if cause_match:
            structured_data["cause_of_action"] = cause_match.group(1)
        
        # 提取关键词
        keywords_match = re.search(r'关键词：([^，；。\n]+)', content)
        if keywords_match:
            keywords = keywords_match.group(1)
            structured_data["keywords"] = [k.strip() for k in re.split(r'[,，、]', keywords) if k.strip()]
        
        # 提取判决结果
        judgment_match = re.search(r'判决如下[：:]([\s\S]+?)(?:如不服本判决|本判决为终审判决|当事人如不服本判决)', content)
        if judgment_match:
            structured_data["judgment_result"] = judgment_match.group(1).strip()
        
        # 提取引用法律法规
        law_patterns = [
            r'《中华人民共和国([\u4e00-\u9fa5]+?)》(?:第[^条]+条)?',
            r'《([\u4e00-\u9fa5]+?)》(?:第[^条]+条)?'
        ]
        
        laws = []
        for pattern in law_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                law = match.group(0)
                if law not in laws:
                    laws.append(law)
        
        structured_data["laws_referenced"] = laws
        
        return {"success": True, "data": structured_data}
    
    def batch_parse_directory(self, input_dir: str, output_dir: str = None) -> Dict[str, Any]:
        """
        批量解析目录中的文书文件
        
        Args:
            input_dir: 输入目录，包含HTML文件
            output_dir: 输出目录，用于保存解析结果
            
        Returns:
            解析结果统计
        """
        input_path = Path(input_dir)
        if not input_path.exists() or not input_path.is_dir():
            return {"success": False, "error": f"输入目录不存在或不是一个目录: {input_dir}"}
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "parsed_documents": []
        }
        
        # 查找所有HTML文件
        html_files = list(input_path.glob("*.html"))
        stats["total"] = len(html_files)
        
        logger.info(f"开始批量解析目录 {input_dir} 中的 {len(html_files)} 个文件")
        
        # 解析每个文件
        for file_path in html_files:
            logger.info(f"解析文件: {file_path}")
            
            # 解析HTML文件
            parse_result = self.parse_html_file(str(file_path))
            
            if not parse_result.get("success", False):
                stats["failed"] += 1
                logger.error(f"解析文件 {file_path} 失败: {parse_result.get('error', '未知错误')}")
                continue
            
            # 提取结构化数据
            structured_result = self.extract_structured_data(parse_result)
            
            if not structured_result.get("success", False):
                stats["failed"] += 1
                logger.error(f"提取结构化数据失败: {structured_result.get('error', '未知错误')}")
                continue
            
            # 处理成功，保存结果
            stats["success"] += 1
            
            document_data = structured_result.get("data", {})
            document_data["original_file"] = str(file_path)
            stats["parsed_documents"].append(document_data)
            
            # 保存解析结果到JSON文件
            if output_dir:
                json_file = output_path / f"{file_path.stem}.json"
                try:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(document_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"解析结果已保存到 {json_file}")
                except Exception as e:
                    logger.error(f"保存解析结果到文件 {json_file} 失败: {str(e)}")
        
        # 保存汇总结果
        if output_dir:
            summary_file = output_path / "summary.json"
            try:
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, ensure_ascii=False, indent=2)
                logger.info(f"解析汇总结果已保存到 {summary_file}")
            except Exception as e:
                logger.error(f"保存汇总结果到文件 {summary_file} 失败: {str(e)}")
        
        logger.info(f"批量解析完成，总数: {stats['total']}，成功: {stats['success']}，失败: {stats['failed']}")
        return {"success": True, "stats": stats} 