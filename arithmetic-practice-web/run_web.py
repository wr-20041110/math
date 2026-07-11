#!/usr/bin/env python3
"""
Web服务启动入口。

用法:
    python run_web.py                # 默认 http://127.0.0.1:5000
    python run_web.py --port 8080    # 指定端口
    python run_web.py --debug        # 调试模式
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))


def main():
    import argparse
    parser = argparse.ArgumentParser(description="口算练习Web服务")
    parser.add_argument("--host", default="127.0.0.1", help="绑定地址")
    parser.add_argument("--port", type=int, default=5000, help="端口号")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    args = parser.parse_args()

    from web import create_app
    app = create_app()

    print("=" * 50)
    print("  口算练习系统 —— Web版")
    print(f"  访问地址: http://{args.host}:{args.port}")
    print(f"  调试模式: {'开启' if args.debug else '关闭'}")
    print("=" * 50)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
