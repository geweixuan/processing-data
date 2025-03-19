"""
裁判文书下载和解析命令行工具
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from .wenshu_downloader import WenshuDownloader
from .wenshu_parser import WenshuParser

# 设置日志
log_file = f"wenshu_cli_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="中国裁判文书网下载和解析工具")
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 下载命令
    download_parser = subparsers.add_parser("download", help="下载裁判文书")
    download_parser.add_argument("--keywords", type=str, required=True, help="搜索关键词")
    download_parser.add_argument("--output_dir", type=str, default="./wenshu_downloads", help="输出目录")
    download_parser.add_argument("--max_pages", type=int, default=5, help="最大搜索页数")
    download_parser.add_argument("--case_type", type=str, help="案件类型")
    download_parser.add_argument("--court", type=str, help="法院名称")
    download_parser.add_argument("--date_from", type=str, help="开始日期 (YYYY-MM-DD)")
    download_parser.add_argument("--date_to", type=str, help="结束日期 (YYYY-MM-DD)")
    download_parser.add_argument("--cookie", type=str, help="用户Cookie (推荐使用，避免反爬)")
    download_parser.add_argument("--proxy", type=str, help="代理服务器地址，格式为'http://ip:port'")
    
    # 解析命令
    parse_parser = subparsers.add_parser("parse", help="解析裁判文书")
    parse_parser.add_argument("--input_dir", type=str, required=True, help="HTML文件输入目录")
    parse_parser.add_argument("--output_dir", type=str, default="./wenshu_parsed", help="解析结果输出目录")
    
    # 下载并解析命令
    download_parse_parser = subparsers.add_parser("download-parse", help="下载并解析裁判文书")
    download_parse_parser.add_argument("--keywords", type=str, required=True, help="搜索关键词")
    download_parse_parser.add_argument("--download_dir", type=str, default="./wenshu_downloads", help="下载文件目录")
    download_parse_parser.add_argument("--parse_dir", type=str, default="./wenshu_parsed", help="解析结果目录")
    download_parse_parser.add_argument("--max_pages", type=int, default=5, help="最大搜索页数")
    download_parse_parser.add_argument("--case_type", type=str, help="案件类型")
    download_parse_parser.add_argument("--court", type=str, help="法院名称")
    download_parse_parser.add_argument("--date_from", type=str, help="开始日期 (YYYY-MM-DD)")
    download_parse_parser.add_argument("--date_to", type=str, help="结束日期 (YYYY-MM-DD)")
    download_parse_parser.add_argument("--cookie", type=str, help="用户Cookie (推荐使用，避免反爬)")
    download_parse_parser.add_argument("--proxy", type=str, help="代理服务器地址，格式为'http://ip:port'")
    
    # 上传到RAGFLOW命令
    upload_parser = subparsers.add_parser("upload", help="将解析后的文书上传到RAGFLOW")
    upload_parser.add_argument("--input_dir", type=str, required=True, help="解析结果输入目录")
    
    return parser.parse_args()


def cmd_download(args):
    """执行下载命令"""
    try:
        # 初始化下载器
        downloader = WenshuDownloader(
            cookie=args.cookie,
            use_proxy=bool(args.proxy),
            proxy=args.proxy
        )
        
        # 确保输出目录存在
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 批量下载
        logger.info(f"开始下载裁判文书，关键词: {args.keywords}, 输出目录: {args.output_dir}")
        result = downloader.batch_download(
            keywords=args.keywords,
            output_dir=args.output_dir,
            max_pages=args.max_pages,
            case_type=args.case_type,
            court=args.court,
            date_from=args.date_from,
            date_to=args.date_to
        )
        
        # 保存下载结果汇总
        stats_file = output_path / "download_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"下载完成，共下载 {result['total']} 个文书，成功 {result['success']} 个，失败 {result['failed']} 个")
        logger.info(f"下载统计信息已保存到 {stats_file}")
        
        return result
        
    except Exception as e:
        logger.error(f"下载过程中发生错误: {str(e)}")
        return {"success": False, "error": str(e)}


def cmd_parse(args):
    """执行解析命令"""
    try:
        # 初始化解析器
        parser = WenshuParser()
        
        # 批量解析
        logger.info(f"开始解析裁判文书，输入目录: {args.input_dir}, 输出目录: {args.output_dir}")
        result = parser.batch_parse_directory(
            input_dir=args.input_dir,
            output_dir=args.output_dir
        )
        
        if not result.get("success", False):
            logger.error(f"解析失败: {result.get('error', '未知错误')}")
            return result
        
        stats = result.get("stats", {})
        logger.info(f"解析完成，共解析 {stats.get('total', 0)} 个文书，成功 {stats.get('success', 0)} 个，失败 {stats.get('failed', 0)} 个")
        
        return result
        
    except Exception as e:
        logger.error(f"解析过程中发生错误: {str(e)}")
        return {"success": False, "error": str(e)}


def cmd_download_parse(args):
    """执行下载并解析命令"""
    # 执行下载
    download_args = argparse.Namespace(
        keywords=args.keywords,
        output_dir=args.download_dir,
        max_pages=args.max_pages,
        case_type=args.case_type,
        court=args.court,
        date_from=args.date_from,
        date_to=args.date_to,
        cookie=args.cookie,
        proxy=args.proxy
    )
    download_result = cmd_download(download_args)
    
    if not download_result.get("success", 0):
        logger.error("下载失败，不继续执行解析")
        return download_result
    
    # 执行解析
    parse_args = argparse.Namespace(
        input_dir=args.download_dir,
        output_dir=args.parse_dir
    )
    parse_result = cmd_parse(parse_args)
    
    # 返回组合结果
    return {
        "success": parse_result.get("success", False),
        "download_stats": download_result,
        "parse_stats": parse_result.get("stats", {})
    }


def cmd_upload_ragflow(args):
    """执行上传到RAGFLOW命令"""
    try:
        # 需要导入RAGFLOW客户端
        # 这里我们修改导入路径，使用src.ragflow中的实现
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from src.ragflow.ragflow_client import RAGFlowClient
        
        # 初始化RAGFLOW客户端
        ragflow_client = RAGFlowClient()
        
        # 查找所有JSON文件
        input_path = Path(args.input_dir)
        json_files = list(input_path.glob("*.json"))
        
        if not json_files:
            logger.warning(f"目录 {args.input_dir} 中没有找到JSON文件")
            return {"success": False, "error": "没有找到JSON文件"}
        
        # 过滤出summary.json之外的文件
        json_files = [f for f in json_files if f.name != "summary.json" and f.name != "download_stats.json"]
        
        if not json_files:
            logger.warning(f"目录 {args.input_dir} 中没有找到有效的解析结果JSON文件")
            return {"success": False, "error": "没有找到有效的解析结果JSON文件"}
        
        logger.info(f"开始上传 {len(json_files)} 个文书到RAGFLOW")
        
        results = {
            "total": len(json_files),
            "success": 0,
            "failed": 0,
            "documents": []
        }
        
        # 上传每个文书
        for json_file in json_files:
            try:
                # 读取JSON文件
                with open(json_file, 'r', encoding='utf-8') as f:
                    document_data = json.load(f)
                
                # 准备上传数据
                title = document_data.get("title", "")
                content = ""
                
                # 组装文书内容
                content += f"标题: {title}\n\n"
                content += f"法院: {document_data.get('court', '')}\n"
                content += f"案号: {document_data.get('case_number', '')}\n"
                content += f"日期: {document_data.get('date', '')}\n"
                content += f"案件类型: {document_data.get('case_type', '')}\n"
                content += f"案由: {document_data.get('cause_of_action', '')}\n\n"
                
                content += "当事人:\n"
                for party in document_data.get("parties", []):
                    content += f"- {party}\n"
                content += "\n"
                
                content += "审判人员:\n"
                for judge in document_data.get("judges", []):
                    content += f"- {judge}\n"
                content += "\n"
                
                if document_data.get("judgment_result"):
                    content += f"判决结果:\n{document_data.get('judgment_result')}\n\n"
                
                if document_data.get("laws_referenced"):
                    content += "引用法律法规:\n"
                    for law in document_data.get("laws_referenced", []):
                        content += f"- {law}\n"
                
                # 准备上传数据
                upload_data = {
                    "content": content,
                    "file_name": f"{json_file.stem}.txt",
                    "extension": ".txt"
                }
                
                # 上传到RAGFLOW
                upload_result = ragflow_client.upload_document(upload_data)
                document_id = upload_result.get("document_id")
                
                if document_id:
                    # 解析文档
                    parse_result = ragflow_client.parse_document(document_id)
                    
                    results["success"] += 1
                    results["documents"].append({
                        "document_id": document_id,
                        "title": title,
                        "original_file": document_data.get("original_file", ""),
                        "json_file": str(json_file)
                    })
                    
                    logger.info(f"文书 '{title}' 上传并解析成功，文档ID: {document_id}")
                else:
                    results["failed"] += 1
                    logger.error(f"文书 '{title}' 上传失败")
                
            except Exception as e:
                results["failed"] += 1
                logger.error(f"处理文件 {json_file} 时发生错误: {str(e)}")
        
        logger.info(f"上传完成，共上传 {results['total']} 个文书，成功 {results['success']} 个，失败 {results['failed']} 个")
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"上传过程中发生错误: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """主函数"""
    args = parse_arguments()
    
    try:
        if args.command == "download":
            cmd_download(args)
        elif args.command == "parse":
            cmd_parse(args)
        elif args.command == "download-parse":
            cmd_download_parse(args)
        elif args.command == "upload":
            cmd_upload_ragflow(args)
        else:
            logger.error("未指定有效的命令")
            print("请指定有效的命令: download, parse, download-parse 或 upload")
            return 1
        
        return 0
        
    except Exception as e:
        logger.critical(f"程序执行过程中发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 