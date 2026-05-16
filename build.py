"""
Claude Configuration Manager 打包脚本
使用 PyInstaller 将应用程序编译为可执行文件
"""
import os
import re
import shutil
import sys
import subprocess
from pathlib import Path

VERSION_FILE = Path(__file__).parent / "app" / "version.py"


def read_version() -> tuple[str, int]:
    """读取当前版本号与编译版本号。"""
    text = VERSION_FILE.read_text(encoding="utf-8")
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', text)
    build_match = re.search(r"__build__\s*=\s*(\d+)", text)
    if not version_match or not build_match:
        raise ValueError(f"无法解析版本文件: {VERSION_FILE}")
    return version_match.group(1), int(build_match.group(1))


def bump_build_number() -> tuple[str, int]:
    """编译前递增编译版本号，并写回 version.py。"""
    text = VERSION_FILE.read_text(encoding="utf-8")
    version, build = read_version()
    build += 1
    text = re.sub(r"__build__\s*=\s*\d+", f"__build__ = {build}", text, count=1)
    VERSION_FILE.write_text(text, encoding="utf-8")
    return version, build


def run_command(cmd):
    """执行命令并显示输出"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=True)
    return result.returncode


def build():
    """打包应用程序"""
    project_root = Path(__file__).parent

    # PyInstaller 参数
    pyinstaller_args = [
        "pyinstaller",
        "--name=ClaudeConfigManager",
        "--icon=resources/icon.png",
        "--windowed",
        "--onefile",
        "--add-data=resources;resources",
        "--clean",
        "main.py",
    ]

    os.chdir(project_root)

    version, build = bump_build_number()
    print(f"编译版本: {version} (build {build})")

    try:
        run_command(pyinstaller_args)

        # 清理 .spec 文件
        spec_file = project_root / "ClaudeConfigManager.spec"
        if spec_file.exists():
            spec_file.unlink()
            print(f"  已删除: {spec_file.name}")

        # 清理 PyInstaller 中间产物目录
        build_dir = project_root / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
            print(f"  已删除: {build_dir}")

        print("\n打包成功!")
        print(f"  版本: {version} · 编译 {build}")
        print(f"  可执行文件位置: {project_root / 'dist' / 'ClaudeConfigManager.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"\n打包失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n未找到 PyInstaller，请先安装:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build()
