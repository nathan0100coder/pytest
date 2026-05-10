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
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def list_request_files(requests_dir: str) -> list:
    """列出 requests 目录下所有 .json 文件"""
    files = []
    for f in os.listdir(requests_dir):
        if f.endswith(".json"):
            files.append(os.path.join(requests_dir, f))
    files.sort()
    return files


def execute_single(client: HttpClient, json_path: str) -> None:
    """执行单个 JSON 请求文件"""
    logger.info(f"Loading request config: {json_path}")
    result = client.execute_from_json(json_path)
    logger.info(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")


def _resolve_json_path(project_root: str, requests_dir: str, target: str) -> str:
    """将用户传入的名称/路径解析为绝对 JSON 文件路径"""
    if not target.endswith(".json"):
        target += ".json"
    if not os.path.dirname(target):
        target = os.path.join(requests_dir, target)
    elif not os.path.isabs(target):
        target = os.path.join(project_root, target)
    return target


def run(json_name: str = None):
    """
    执行 runner 逻辑。

    :param json_name: 显式传入 requests/ 目录下的 JSON 文件名称（如 "org_list"）。
                      为 None 时，优先读取命令行参数；命令行也无参数则执行全部。
    """
    project_root = get_project_root()
    config_path = os.path.join(project_root, "config", "config.yaml")
    requests_dir = os.path.join(project_root, "requests")

    client = HttpClient(config_path=config_path)

    # 1) 若显式传入了 json_name，直接解析并使用
    if json_name is not None:
        target = _resolve_json_path(project_root, requests_dir, json_name)
        if not os.path.exists(target):
            logger.error(f"File not found: {target}")
            sys.exit(1)
        execute_single(client, target)
        return

    # 2) 否则检查命令行参数
    if len(sys.argv) > 1:
        target = _resolve_json_path(project_root, requests_dir, sys.argv[1])
        if not os.path.exists(target):
            logger.error(f"File not found: {target}")
            sys.exit(1)
        execute_single(client, target)
        return

    # 3) 否则执行 requests/ 目录下所有 JSON 文件
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
