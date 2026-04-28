"""
Hook 配置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QPushButton, QMessageBox, QCheckBox
)


class HookDialog(QDialog):
    """Hook 配置对话框"""

    def __init__(self, parent, hook_type, hook_data=None):
        super().__init__(parent)
        self.hook_type = hook_type
        self.hook_data = hook_data or {}
        self.init_ui()
        if self.hook_data:
            self.load_data()

    def init_ui(self):
        """初始化UI"""
        hook_name = "Pre-Hook" if self.hook_type == "pre" else "Post-Hook"
        self.setWindowTitle(f"{hook_name} 配置")
        self.setMinimumWidth(500)

        layout = QFormLayout(self)

        # 触发时机
        self.trigger_combo = QComboBox()
        if self.hook_type == "pre":
            self.trigger_combo.addItem("Bash 命令执行前", "before-bash")
            self.trigger_combo.addItem("文件写入前", "before-write")
            self.trigger_combo.addItem("工具调用前", "before-tool")
            self.trigger_combo.addItem("Git 提交前", "before-git-commit")
        else:
            self.trigger_combo.addItem("Bash 命令执行后", "after-bash")
            self.trigger_combo.addItem("文件写入后", "after-write")
            self.trigger_combo.addItem("工具调用后", "after-tool")
            self.trigger_combo.addItem("Git 提交后", "after-git-commit")
            self.trigger_combo.addItem("配置保存后", "after-config-save")
        layout.addRow("触发时机:", self.trigger_combo)

        # 命令
        self.command_edit = QLineEdit()
        self.command_edit.setPlaceholderText("例如: python /path/to/script.py")
        layout.addRow("命令/脚本*:", self.command_edit)

        # 工作目录
        self.working_dir_edit = QLineEdit()
        self.working_dir_edit.setPlaceholderText("留空使用当前目录")
        layout.addRow("工作目录:", self.working_dir_edit)

        # 描述
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("简要描述此 Hook 的用途")
        layout.addRow("描述:", self.description_edit)

        # 是否启用
        self.enabled_checkbox = QCheckBox("启用此 Hook")
        self.enabled_checkbox.setChecked(True)
        layout.addRow(self.enabled_checkbox)

        # 环境变量说明
        env_hint = QLabel(
            "可用环境变量:\n"
            "$CLAUDE_TOOL - 被调用的工具名称\n"
            "$CLAUDE_ARGS - 工具参数\n"
            "$CLAUDE_EXIT_CODE - 退出码 (仅 post-hook)\n"
            "$CLAUDE_CONFIG - 配置文件路径"
        )
        env_hint.setStyleSheet("color: #666; font-size: 10px; background: #f5f5f5; padding: 10px;")
        layout.addRow(env_hint)

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def load_data(self):
        """加载数据"""
        trigger = self.hook_data.get("trigger", "")
        for i in range(self.trigger_combo.count()):
            if self.trigger_combo.itemData(i) == trigger:
                self.trigger_combo.setCurrentIndex(i)
                break

        self.command_edit.setText(self.hook_data.get("command", ""))
        self.working_dir_edit.setText(self.hook_data.get("workingDir", ""))
        self.description_edit.setText(self.hook_data.get("description", ""))
        self.enabled_checkbox.setChecked(self.hook_data.get("enabled", True))

    def validate_and_accept(self):
        """验证并接受"""
        command = self.command_edit.text().strip()
        if not command:
            QMessageBox.warning(self, "警告", "命令不能为空")
            return
        self.accept()

    def get_hook_data(self):
        """获取 Hook 数据"""
        return {
            "trigger": self.trigger_combo.currentData(),
            "command": self.command_edit.text().strip(),
            "workingDir": self.working_dir_edit.text().strip(),
            "description": self.description_edit.text().strip(),
            "enabled": self.enabled_checkbox.isChecked()
        }
