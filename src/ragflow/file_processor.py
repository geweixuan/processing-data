"""
文件处理模块，用于读取和处理文件
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from . import config

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理类，用于扫描文件目录并读取文件内容"""
    
    def __init__(self, input_dir: str):
        """
        初始化文件处理器
        
        Args:
            input_dir: 输入文件目录路径
        """
        self.input_dir = Path(input_dir)
        if not self.input_dir.exists():
            raise FileNotFoundError(f"目录不存在: {input_dir}")
        
        logger.info(f"初始化文件处理器，输入目录: {input_dir}")
    
    def scan_files(self) -> List[Path]:
        """
        扫描输入目录中的文件
        
        Returns:
            符合条件的文件路径列表
        """
        files = []
        for file_path in self.input_dir.rglob("*"):
            if file_path.is_file() and self._is_valid_file(file_path):
                files.append(file_path)
        
        logger.info(f"扫描到 {len(files)} 个有效文件")
        return files
    
    def _is_valid_file(self, file_path: Path) -> bool:
        """
        检查文件是否符合处理条件
        
        Args:
            file_path: 文件路径
        
        Returns:
            是否为有效文件
        """
        # 检查文件扩展名
        if file_path.suffix.lower() not in config.SUPPORTED_EXTENSIONS:
            return False
        
        # 检查文件大小
        if file_path.stat().st_size > config.MAX_FILE_SIZE:
            logger.warning(f"文件过大: {file_path} ({file_path.stat().st_size} bytes)")
            return False
        
        return True
    
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        """
        读取文件内容并返回文件信息
        
        Args:
            file_path: 文件路径
        
        Returns:
            包含文件信息的字典
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='replace')
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'extension': file_path.suffix,
                'size': file_path.stat().st_size,
                'content': content
            }
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败: {str(e)}")
            return {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'extension': file_path.suffix,
                'size': file_path.stat().st_size,
                'content': '',
                'error': str(e)
            } 