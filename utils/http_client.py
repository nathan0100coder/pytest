import json
import logging
import os
from typing import Any, Dict, Optional

import requests
import yaml

logger = logging.getLogger(__name__)


class HttpClient:
    """HTTP 客户端，用于调用 Java 服务 API"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self._load_config(config_path)
        self.base_url = self.config.get("java_service", {}).get("base_url", "").rstrip("/")
        self.timeout = self.config.get("java_service", {}).get("timeout", 30)
        self.default_headers = self.config.get("java_service", {}).get("headers", {})

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载 YAML 配置文件"""
        if not os.path.isabs(config_path):
            config_path = os.path.join(self._get_project_root(), config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _get_project_root() -> str:
        """获取项目根目录（以 utils 目录所在位置为准）"""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _build_url(self, path: str, path_params: Optional[Dict[str, Any]] = None) -> str:
        """构建完整 URL，并替换 path 中的占位符"""
        if path_params:
            for key, value in path_params.items():
                path = path.replace(f"{{{key}}}", str(value))
        return f"{self.base_url}{path}"

    def request(
        self,
        path: str,
        method: str = "POST",
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求

        :param path: API 路径（如 /api/users）
        :param method: 请求方法（GET / POST / PUT / DELETE 等）
        :param path_params: URL 路径参数，用于替换 {id} 等占位符
        :param query_params: URL 查询参数
        :param body: 请求体（JSON）
        :param headers: 自定义请求头
        :return: 响应结果字典
        """
        url = self._build_url(path, path_params)
        merged_headers = {**self.default_headers, **(headers or {})}
        method = method.upper()

        logger.info(f"[{method}] {url}")
        if query_params:
            logger.info(f"Query Params: {json.dumps(query_params, ensure_ascii=False)}")
        if body:
            logger.info(f"Request Body: {json.dumps(body, ensure_ascii=False)}")

        try:
            if method == "GET":
                resp = requests.get(
                    url,
                    params=query_params,
                    headers=merged_headers,
                    timeout=self.timeout,
                )
            elif method == "POST":
                resp = requests.post(
                    url,
                    params=query_params,
                    json=body,
                    headers=merged_headers,
                    timeout=self.timeout,
                )
            elif method == "PUT":
                resp = requests.put(
                    url,
                    params=query_params,
                    json=body,
                    headers=merged_headers,
                    timeout=self.timeout,
                )
            elif method == "DELETE":
                resp = requests.delete(
                    url,
                    params=query_params,
                    headers=merged_headers,
                    timeout=self.timeout,
                )
            else:
                resp = requests.request(
                    method,
                    url,
                    params=query_params,
                    json=body,
                    headers=merged_headers,
                    timeout=self.timeout,
                )

            resp.raise_for_status()
            result = {
                "success": True,
                "status_code": resp.status_code,
                "url": resp.url,
            }
            try:
                result["data"] = resp.json()
            except ValueError:
                result["data"] = resp.text
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    def execute_from_json(self, json_path: str) -> Dict[str, Any]:
        """
        从 JSON 文件中读取请求配置并执行

        :param json_path: JSON 文件路径
        :return: 响应结果字典
        """
        with open(json_path, "r", encoding="utf-8") as f:
            req = json.load(f)

        name = req.get("name", os.path.basename(json_path))
        logger.info(f"Executing: {name}")

        return self.request(
            path=req["path"],
            method=req.get("method", "POST"),
            path_params=req.get("path_params"),
            query_params=req.get("query_params"),
            body=req.get("body"),
        )
