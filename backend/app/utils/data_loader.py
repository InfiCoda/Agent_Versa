"""数据加载器"""

import json
import csv
import os
from typing import List, Dict, Any
import aiohttp
import pandas as pd


class DataLoader:
    """数据加载器，支持多种数据源"""
    
    @staticmethod
    async def load_json(file_path: str) -> List[Dict[str, Any]]:
        """从JSON文件加载数据"""
        # 处理相对路径：如果路径不是绝对路径，尝试从项目根目录或backend目录查找
        if not os.path.isabs(file_path):
            # 获取当前工作目录（通常是backend目录）
            current_dir = os.getcwd()
            # 尝试多个可能的路径
            possible_paths = [
                file_path,  # 原始路径（相对于当前目录）
                os.path.join(current_dir, file_path),  # 当前目录下
                os.path.join("backend", file_path),  # backend目录下
                os.path.join("app", file_path),  # app目录下
                os.path.join("backend", "app", file_path),  # backend/app目录下
                os.path.join(current_dir, "app", file_path),  # 当前目录/app下
                os.path.join(current_dir, "backend", "app", file_path),  # 当前目录/backend/app下
            ]
            # 去重
            possible_paths = list(dict.fromkeys(possible_paths))
            
            found = False
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = os.path.abspath(path)  # 转换为绝对路径
                    found = True
                    break
            if not found:
                raise FileNotFoundError(
                    f"数据集文件不存在: {file_path}\n"
                    f"已尝试路径: {', '.join(possible_paths)}\n"
                    f"提示: 请使用相对路径（如 'app/data/samples.json'）或绝对路径\n"
                    f"当前工作目录: {current_dir}"
                )
        elif not os.path.exists(file_path):
            raise FileNotFoundError(f"数据集文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return [data]
        else:
            raise ValueError("JSON文件格式不正确，应为对象或数组")
    
    @staticmethod
    async def load_csv(file_path: str) -> List[Dict[str, Any]]:
        """从CSV文件加载数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        df = pd.read_csv(file_path)
        return df.to_dict('records')
    
    @staticmethod
    async def load_from_api(api_url: str, headers: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """从API加载数据"""
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"API请求失败: {response.status}")
                data = await response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data]
                else:
                    return []
    
    @staticmethod
    async def load_data(dataset_type: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """统一的数据加载接口"""
        if dataset_type == "json":
            file_path = config.get("file_path")
            if not file_path:
                raise ValueError("JSON数据源需要提供file_path")
            return await DataLoader.load_json(file_path)
        
        elif dataset_type == "csv":
            file_path = config.get("file_path")
            if not file_path:
                raise ValueError("CSV数据源需要提供file_path")
            return await DataLoader.load_csv(file_path)
        
        elif dataset_type == "api":
            api_url = config.get("url")
            if not api_url:
                raise ValueError("API数据源需要提供url")
            headers = config.get("headers", {})
            return await DataLoader.load_from_api(api_url, headers)
        
        else:
            raise ValueError(f"不支持的数据源类型: {dataset_type}")

