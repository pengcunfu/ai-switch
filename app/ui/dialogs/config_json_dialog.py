"""
完整配置 JSON 对话框
"""
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QMessageBox, QApplication
)
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

from ..widgets.json_highlighter import JsonHighlighter


class ConfigJsonDialog(QDialog):
    """完整配置 JSON 子模态对话框"""

    def __init__(self, parent, config_data):
        super().__init__(parent)
        self.parent_window = parent
        self.config_data = config_data
        self.highlighter = None
        self.init_ui()
        self.load_config()

    def init_ui(self):
        self.setWindowTitle("完整配置 (JSON)")
        self.resize(840, 560)

        icon_path = Path(__file__).parent.parent.parent.parent / "resources" / "icon.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()

        format_btn = QPushButton("格式化 JSON")
        format_btn.clicked.connect(self.format_json)

        copy_btn = QPushButton("复制全部")
        copy_btn.clicked.connect(self.copy_to_clipboard)

        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_config)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)

        button_layout.addWidget(format_btn)
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # JSON 文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.highlighter = JsonHighlighter(self.text_edit.document())

        layout.addWidget(self.text_edit)

    def load_config(self):
        json_str = json.dumps(self.config_data, indent=2, ensure_ascii=False)
        self.text_edit.setPlainText(json_str)

    def format_json(self):
        try:
            json_text = self.text_edit.toPlainText()
            data = json.loads(json_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            self.parent_window.statusBar().showMessage("JSON 已格式化")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        self.parent_window.statusBar().showMessage("配置 JSON 已复制到剪贴板")

    def save_config(self):
        try:
            json_text = self.text_edit.toPlainText()
            config_data = json.loads(json_text)

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.parent_window.refresh_all_views()

            self.config_data = config_data

            QMessageBox.information(self, "成功", "配置已保存!")
            self.parent_window.statusBar().showMessage("配置已保存")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
