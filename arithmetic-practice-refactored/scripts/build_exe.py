"""
PyInstaller 打包脚本 —— 生成独立可执行文件。

用法:
    python scripts/build_exe.py

输出:
    dist/mathpractice.exe (Windows 单文件可执行程序)
"""

import subprocess
import sys
from pathlib import Path


def build():
    """使用 PyInstaller 构建单文件可执行程序。"""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                          # 单文件输出
        "--name", "mathpractice",             # 输出名称
        "--add-data", f"{src_dir}{';' if sys.platform == 'win32' else ':'}{src_dir}",
        "--console",                          # 控制台程序
        "--clean",                            # 清理缓存
        str(project_root / "src" / "mathpractice" / "__main__.py"),
    ]

    print("=" * 50)
    print("  PyInstaller 打包中...")
    print(f"  命令: {' '.join(cmd)}")
    print("=" * 50)

    result = subprocess.run(cmd, cwd=str(project_root))
    if result.returncode == 0:
        exe = project_root / "dist" / "mathpractice.exe"
        if exe.exists():
            print(f"\n[OK] 打包成功: {exe}")
            print(f"     文件大小: {exe.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("\n[OK] 打包完成（检查 dist/ 目录）")
    else:
        print("\n[ERROR] 打包失败，请检查 PyInstaller 是否正确安装。")
        print("  安装: pip install pyinstaller")


if __name__ == "__main__":
    build()
