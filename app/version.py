"""应用版本信息"""

__version__ = "1.0.0"
__build__ = 1


def version_label() -> str:
    """用于界面显示的完整版本字符串。"""
    return f"版本 {__version__} · 编译 {__build__}"
