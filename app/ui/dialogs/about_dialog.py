"""
关于对话框
"""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("关于 Claude Configuration Manager")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # 标题
        title_label = QLabel("Claude Configuration Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 版本信息
        version_label = QLabel("版本 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)

        # 描述
        desc_label = QLabel("Claude Code 配置文件管理工具")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)

        # 版权信息
        copyright_label = QLabel("© 2026 pengcunfu")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet("color: #666;")
        layout.addWidget(copyright_label)

        layout.addStretch()

        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)
