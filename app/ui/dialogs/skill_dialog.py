"""
Skill 配置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox,
    QGroupBox, QVBoxLayout, QTextEdit, QComboBox, QCheckBox,
    QHBoxLayout, QLabel
)
from PySide6.QtGui import QFont


class SkillDialog(QDialog):
    """Skill 配置对话框"""

    def __init__(self, parent, skill_data=None, scope="global"):
        super().__init__(parent)
        self.skill_data = skill_data or {}
        self.scope = scope
        self.init_ui()
        if self.skill_data:
            self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Skill 配置")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # === Frontmatter 组 ===
        fm_group = QGroupBox("Frontmatter 配置")
        fm_layout = QFormLayout(fm_group)

        # 名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("skill 名称 (同时作为目录名和斜杠命令名)")
        fm_layout.addRow("名称*:", self.name_edit)

        # 描述
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("简要描述此 skill 的功能和使用场景")
        fm_layout.addRow("描述:", self.description_edit)

        # Context
        self.context_combo = QComboBox()
        self.context_combo.setEditable(True)
        self.context_combo.addItem("")  # 默认空
        self.context_combo.addItem("fork")
        self.context_combo.addItem("agent")
        self.context_combo.setPlaceholderText("默认: 无 (当前上下文)")
        fm_layout.addRow("Context:", self.context_combo)

        # Agent
        self.agent_combo = QComboBox()
        self.agent_combo.setEditable(True)
        self.agent_combo.addItem("")  # 默认空
        self.agent_combo.addItem("Explore")
        self.agent_combo.addItem("Plan")
        self.agent_combo.addItem("general-purpose")
        self.agent_combo.setPlaceholderText("默认: 无")
        fm_layout.addRow("Agent:", self.agent_combo)

        # 允许工具
        self.allowed_tools_edit = QLineEdit()
        self.allowed_tools_edit.setPlaceholderText("例如: Read Grep Bash (空格分隔)")
        fm_layout.addRow("允许工具:", self.allowed_tools_edit)

        # 参数提示
        self.argument_hint_edit = QLineEdit()
        self.argument_hint_edit.setPlaceholderText("例如: [issue-number] 或 [filename] [format]")
        fm_layout.addRow("参数提示:", self.argument_hint_edit)

        # 复选框行
        check_layout = QHBoxLayout()
        self.user_invocable_check = QCheckBox("用户可调用 (斜杠命令)")
        self.user_invocable_check.setChecked(True)
        self.disable_model_check = QCheckBox("禁用模型自动调用")
        self.disable_model_check.setChecked(False)
        check_layout.addWidget(self.user_invocable_check)
        check_layout.addWidget(self.disable_model_check)
        check_layout.addStretch()
        fm_layout.addRow(check_layout)

        layout.addWidget(fm_group)

        # === Skill 内容组 ===
        content_group = QGroupBox("Skill 内容 (SKILL.md 正文)")
        content_layout = QVBoxLayout(content_group)

        content_hint = QLabel("提示: 这是 Claude 在触发此 skill 时收到的指令内容。Frontmatter 已在上方配置，无需在此重复。")
        content_hint.setStyleSheet("color: #666; font-size: 10px;")
        content_hint.setWordWrap(True)
        content_layout.addWidget(content_hint)

        self.content_edit = QTextEdit()
        self.content_edit.setFont(QFont("Consolas", 10))
        self.content_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.content_edit.setPlaceholderText(
            "输入 skill 的指令内容...\n\n"
            "例如:\n"
            "当审查代码时，请遵循以下步骤:\n"
            "1. 检查代码风格和一致性\n"
            "2. 查找潜在的 bug 和安全问题\n"
            "3. 验证错误处理是否完善\n"
            "4. 检查性能优化机会"
        )
        content_layout.addWidget(self.content_edit)

        layout.addWidget(content_group)

        # === 按钮 ===
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def load_data(self):
        """加载已有 skill 数据"""
        self.name_edit.setText(self.skill_data.get("name", ""))
        self.description_edit.setText(self.skill_data.get("description", ""))

        context = self.skill_data.get("context", "")
        idx = self.context_combo.findText(context)
        if idx >= 0:
            self.context_combo.setCurrentIndex(idx)
        else:
            self.context_combo.setCurrentText(context)

        agent = self.skill_data.get("agent", "")
        idx = self.agent_combo.findText(agent)
        if idx >= 0:
            self.agent_combo.setCurrentIndex(idx)
        else:
            self.agent_combo.setCurrentText(agent)

        self.allowed_tools_edit.setText(self.skill_data.get("allowed_tools", ""))
        self.argument_hint_edit.setText(self.skill_data.get("argument_hint", ""))
        self.user_invocable_check.setChecked(self.skill_data.get("user_invocable", True))
        self.disable_model_check.setChecked(self.skill_data.get("disable_model_invocation", False))
        self.content_edit.setPlainText(self.skill_data.get("content", ""))

    def validate_and_accept(self):
        """验证并接受"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "Skill 名称不能为空")
            return

        # 名称只能包含字母、数字、连字符
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            QMessageBox.warning(self, "警告", "Skill 名称只能包含字母、数字、连字符和下划线")
            return

        self.accept()

    def get_skill_data(self):
        """获取 skill 数据"""
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.text().strip(),
            "context": self.context_combo.currentText().strip(),
            "agent": self.agent_combo.currentText().strip(),
            "allowed_tools": self.allowed_tools_edit.text().strip(),
            "argument_hint": self.argument_hint_edit.text().strip(),
            "user_invocable": self.user_invocable_check.isChecked(),
            "disable_model_invocation": self.disable_model_check.isChecked(),
            "content": self.content_edit.toPlainText(),
        }
