#!/usr/bin/env python3
from utils.runner import run


def main(json_name: str = None, enable_token: bool = False):
    """
    入口函数：执行指定 JSON 请求或全部请求。

    :param json_name: requests/ 目录下的 JSON 文件名称（如 "org_list"），None 则执行全部。
    :param enable_token: 是否启用 Authorization token，默认 False，token 从 config.yaml 读取。
    """
    run(json_name, enable_token)


if __name__ == "__main__":
    main()
