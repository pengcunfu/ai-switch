"""
Claude Configuration Manager
Claude 配置管理器主程序
"""
import signal
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import ClaudeConfigGUI


def _install_sigint_handler(app: QApplication) -> None:
    """让 Ctrl+C 在 Qt 事件循环中也能触发退出。"""
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    # 定期唤醒 Python 解释器以处理挂起的 SIGINT
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(200)
    app._sigint_timer = timer  # 防止被 GC


def main():
    """主函数"""
    app = QApplication(sys.argv)
    _install_sigint_handler(app)

    icon_path = Path(__file__).parent / "resources" / "icon.png"
    app.setWindowIcon(QIcon(str(icon_path)))

    app.setStyle("WindowsVista")

    window = ClaudeConfigGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
