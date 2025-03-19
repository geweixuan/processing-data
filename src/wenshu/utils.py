"""
工具函数模块，提供辅助功能
"""

import os
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_file_hash(file_path: str or Path) -> str:
    """
    计算文件的SHA-256哈希值
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件的SHA-256哈希值
    """
    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"文件不存在或不是一个文件: {file_path}")
    
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


def ensure_directory(directory_path: str or Path) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
    
    Returns:
        Path对象
    """
    directory_path = Path(directory_path)
    directory_path.mkdir(parents=True, exist_ok=True)
    return directory_path


def format_file_size(size_in_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_in_bytes: 文件大小（字节数）
    
    Returns:
        格式化后的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0 or unit == 'TB':
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0


def extract_file_metadata(file_path: str or Path) -> Dict[str, Any]:
    """
    提取文件元数据
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件元数据字典
    """
    file_path = Path(file_path)
    stats = file_path.stat()
    
    return {
        'file_name': file_path.name,
        'extension': file_path.suffix,
        'size': stats.st_size,
        'formatted_size': format_file_size(stats.st_size),
        'created_time': stats.st_ctime,
        'modified_time': stats.st_mtime,
        'is_hidden': file_path.name.startswith('.'),
        'absolute_path': str(file_path.absolute()),
        'parent_directory': str(file_path.parent)
    } 