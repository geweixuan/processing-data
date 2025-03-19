"""
数据处理与RAGFLOW上传工具的主程序
"""

import os
import sys
import argparse
import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from tqdm import tqdm

from .file_processor import FileProcessor
from .ragflow_client import RAGFlowClient

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("processing.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="数据处理与RAGFLOW上传工具")
    parser.add_argument("--input_dir", type=str, required=True, help="输入文件目录路径")
    parser.add_argument("--output_dir", type=str, default="./results", help="输出结果保存目录")
    return parser.parse_args()


def save_results(results: List[Dict[str, Any]], output_dir: str):
    """
    保存处理结果到文件
    
    Args:
        results: 处理结果列表
        output_dir: 输出目录
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存完整结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    result_file = output_path / f"results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    logger.info(f"处理结果已保存到 {result_file}")
    
    # 保存摘要
    summary_file = output_path / f"summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"处理时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件总数: {len(results)}\n")
        
        success_count = sum(1 for r in results if r.get('success', False))
        f.write(f"成功数量: {success_count}\n")
        f.write(f"失败数量: {len(results) - success_count}\n\n")
        
        if len(results) - success_count > 0:
            f.write("失败文件列表:\n")
            for r in results:
                if not r.get('success', False):
                    f.write(f"- {r.get('file_name', 'unknown')}: {r.get('error', '未知错误')}\n")
    
    logger.info(f"处理摘要已保存到 {summary_file}")


def main():
    """主函数"""
    args = parse_arguments()
    
    try:
        # 初始化文件处理器
        file_processor = FileProcessor(args.input_dir)
        
        # 初始化RAGFLOW客户端
        ragflow_client = RAGFlowClient()
        
        # 扫描文件
        files = file_processor.scan_files()
        if not files:
            logger.warning("未找到符合条件的文件")
            return
        
        # 处理结果列表
        results = []
        
        # 处理每个文件
        for file_path in tqdm(files, desc="处理文件"):
            logger.info(f"处理文件: {file_path}")
            result = {
                'file_name': file_path.name,
                'file_path': str(file_path),
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                'success': False
            }
            
            try:
                # 读取文件
                document_data = file_processor.read_file(file_path)
                if 'error' in document_data:
                    result['error'] = f"读取文件失败: {document_data['error']}"
                    results.append(result)
                    continue
                
                # 上传文档
                upload_result = ragflow_client.upload_document(document_data)
                document_id = upload_result.get('document_id')
                if not document_id:
                    result['error'] = "上传文档失败: 未获取到文档ID"
                    results.append(result)
                    continue
                
                result['document_id'] = document_id
                
                # 解析文档
                parse_result = ragflow_client.parse_document(document_id)
                result['parse_result'] = parse_result
                
                # 检查文档状态
                status_result = ragflow_client.get_document_status(document_id)
                result['status'] = status_result.get('status', 'unknown')
                
                result['success'] = True
                logger.info(f"文件 {file_path.name} 处理成功，文档ID: {document_id}")
            
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时发生错误: {str(e)}")
                result['error'] = str(e)
            
            finally:
                results.append(result)
        
        # 保存结果
        save_results(results, args.output_dir)
        
        logger.info(f"所有文件处理完成，共 {len(files)} 个文件")
    
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 