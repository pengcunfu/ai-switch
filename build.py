"""
Claude Configuration Manager 打包脚本
使用 PyInstaller 将应用程序编译为可执行文件
"""
import os
import sys
import subprocess
from pathlib import Path


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

    # 切换到项目根目录
    os.chdir(project_root)

    # 执行打包
    try:
        run_command(pyinstaller_args)

        # 清理 .spec 文件
        spec_file = project_root / "ClaudeConfigManager.spec"
        if spec_file.exists():
            spec_file.unlink()
            print(f"  已删除: {spec_file.name}")

        print("\n✓ 打包成功!")
        print(f"  可执行文件位置: {project_root / 'dist' / 'ClaudeConfigManager.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 打包失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("\n✗ 未找到 PyInstaller，请先安装:")
        print("  pip install pyinstaller")
        sys.exit(1)


if __name__ == "__main__":
    build()
