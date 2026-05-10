#!/usr/bin/env python3
from utils.runner import run


def main(json_name: str = None):
    """入口函数：执行指定 JSON 请求或全部请求"""
    run(json_name)


if __name__ == "__main__":
    main()
