"""允许通过 python -m mathpractice 启动。"""
import sys
from .cli import build_parser, run


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command:
        run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
