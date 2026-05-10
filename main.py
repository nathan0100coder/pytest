#!/usr/bin/env python3
"""
调用 Java 服务 API 的主程序。

功能说明：
1. 从 config/config.yaml 读取 Java 服务基础地址；
2. 从 requests/ 目录下的 JSON 文件中读取 API 路径与请求参数；
3. 根据 JSON 中的 method 字段自动选择 GET 或 POST（以及 PUT/DELETE）；
4. 支持 URL 路径参数替换（如 {id}）、Query 参数、JSON Body。

JSON 文件格式示例：
{
  "name": "创建用户",
  "path": "/api/users",
  "method": "POST",
  "description": "创建新用户",
  "body": {
    "username": "zhangsan",
    "email": "zhangsan@example.com"
  }
}

使用方式：
    python main.py                           # 执行 requests/ 下所有 JSON
    python main.py requests/user_create.json # 执行单个 JSON 文件
"""

import json
import logging
import os
import sys

from utils.http_client import HttpClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def list_request_files(requests_dir: str) -> list:
    """列出 requests 目录下所有 .json 文件"""
    files = []
    for f in os.listdir(requests_dir):
        if f.endswith(".json"):
            files.append(os.path.join(requests_dir, f))
    # 按文件名排序，保证执行顺序稳定
    files.sort()
    return files


def execute_single(client: HttpClient, json_path: str) -> None:
    """执行单个 JSON 请求文件"""
    logger.info(f"Loading request config: {json_path}")
    result = client.execute_from_json(json_path)
    logger.info(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")


def main():
    project_root = get_project_root()
    config_path = os.path.join(project_root, "config", "config.yaml")
    requests_dir = os.path.join(project_root, "requests")

    client = HttpClient(config_path=config_path)

    # 如果命令行传入了指定 JSON 文件路径，则只执行该文件
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if not os.path.isabs(target):
            target = os.path.join(project_root, target)
        if not os.path.exists(target):
            logger.error(f"File not found: {target}")
            sys.exit(1)
        execute_single(client, target)
        return

    # 否则执行 requests/ 目录下所有 JSON 文件
    if not os.path.isdir(requests_dir):
        logger.error(f"Requests directory not found: {requests_dir}")
        sys.exit(1)

    request_files = list_request_files(requests_dir)
    if not request_files:
        logger.warning("No JSON request files found in requests/")
        return

    logger.info(f"Found {len(request_files)} request file(s) to execute.\n")
    for idx, json_path in enumerate(request_files, 1):
        logger.info(f"[{idx}/{len(request_files)}] {'=' * 40}")
        execute_single(client, json_path)
        print()  # 空行分隔


if __name__ == "__main__":
    main()
