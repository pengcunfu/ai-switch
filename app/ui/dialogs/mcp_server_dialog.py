"""
MCP 服务器配置对话框
支持表单模式和 JSON 模式编辑
"""
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QHBoxLayout, QTextEdit, QTabWidget,
    QWidget, QLabel
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from ..widgets.json_highlighter import JsonHighlighter


class MCPServerDialog(QDialog):
    """MCP 服务器配置对话框"""

    def __init__(self, parent, name="", config=None):
        super().__init__(parent)
        self.name = name
        self.config = config or {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("MCP 服务器配置")
        self.setMinimumWidth(700)
        self.setMinimumHeight(550)

        layout = QVBoxLayout(self)

        # 服务器名称 (始终显示)
        name_layout = QHBoxLayout()
        name_label = QLabel("服务器名称:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Tab 切换: 表单模式 / JSON 模式
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # === 表单模式 Tab ===
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)

        # 命令
        self.command_edit = QLineEdit()
        command_btn = QPushButton("浏览...")
        command_btn.clicked.connect(self.browse_command)
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(self.command_edit)
        cmd_layout.addWidget(command_btn)
        form_layout.addRow("命令:", cmd_layout)

        # 参数
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText('用空格分隔参数,例如: --host localhost --port 3306')
        form_layout.addRow("参数:", self.args_edit)

        # 环境变量
        env_group = QGroupBox("环境变量 (可选)")
        env_layout = QVBoxLayout(env_group)

        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["变量名", "值"])
        self.env_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        env_layout.addWidget(self.env_table)

        env_btn_layout = QHBoxLayout()
        add_env_btn = QPushButton("添加变量")
        remove_env_btn = QPushButton("删除变量")
        add_env_btn.clicked.connect(self.add_env_var)
        remove_env_btn.clicked.connect(self.remove_env_var)
        env_btn_layout.addWidget(add_env_btn)
        env_btn_layout.addWidget(remove_env_btn)
        env_btn_layout.addStretch()
        env_layout.addLayout(env_btn_layout)

        form_layout.addRow(env_group)

        self.tab_widget.addTab(form_widget, "表单模式")

        # === JSON 模式 Tab ===
        json_widget = QWidget()
        json_layout = QVBoxLayout(json_widget)

        json_hint = QLabel("提示: 直接编辑 JSON 配置，支持所有 MCP 服务器属性 (如 url, headers, type 等)")
        json_hint.setStyleSheet("color: #666; font-size: 10px;")
        json_hint.setWordWrap(True)
        json_layout.addWidget(json_hint)

        self.json_edit = QTextEdit()
        self.json_edit.setFont(QFont("Consolas", 10))
        self.json_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.json_highlighter = JsonHighlighter(self.json_edit.document())
        json_layout.addWidget(self.json_edit)

        # JSON 操作按钮
        json_btn_layout = QHBoxLayout()
        format_btn = QPushButton("格式化 JSON")
        validate_btn = QPushButton("验证 JSON")
        format_btn.clicked.connect(self.format_json)
        validate_btn.clicked.connect(self.validate_json)
        json_btn_layout.addWidget(format_btn)
        json_btn_layout.addWidget(validate_btn)
        json_btn_layout.addStretch()
        json_layout.addLayout(json_btn_layout)

        self.tab_widget.addTab(json_widget, "JSON 模式")

        # Tab 切换时同步数据
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # === 底部按钮 ===
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def on_tab_changed(self, index):
        """Tab 切换时同步数据"""
        if index == 1:
            # 切换到 JSON 模式: 从表单同步到 JSON
            self._sync_form_to_json()
        elif index == 0:
            # 切换到表单模式: 从 JSON 同步到表单
            self._sync_json_to_form()

    def _sync_form_to_json(self):
        """将表单数据同步到 JSON 编辑器"""
        config = self._get_config_from_form()
        json_str = json.dumps(config, indent=2, ensure_ascii=False)
        self.json_edit.setPlainText(json_str)

    def _sync_json_to_form(self):
        """将 JSON 编辑器数据同步到表单"""
        try:
            json_text = self.json_edit.toPlainText().strip()
            if not json_text:
                return
            config = json.loads(json_text)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "警告", "JSON 格式无效，无法同步到表单模式。请先修正 JSON 格式。")
            # 切回 JSON 模式
            self.tab_widget.blockSignals(True)
            self.tab_widget.setCurrentIndex(1)
            self.tab_widget.blockSignals(False)
            return

        # 同步 command
        self.command_edit.setText(config.get("command", ""))

        # 同步 args
        args = config.get("args", [])
        if isinstance(args, list):
            self.args_edit.setText(" ".join(str(a) for a in args))
        else:
            self.args_edit.setText(str(args))

        # 同步 env
        self.env_table.setRowCount(0)
        env = config.get("env", {})
        if isinstance(env, dict):
            for key, value in env.items():
                self.add_env_row(str(key), str(value))

    def load_data(self):
        """加载数据"""
        if self.config:
            self.name_edit.setText(self.name)

            # 加载到表单
            self.command_edit.setText(self.config.get("command", ""))

            args = self.config.get("args", [])
            if isinstance(args, list):
                self.args_edit.setText(" ".join(str(a) for a in args))
            else:
                self.args_edit.setText(str(args))

            env = self.config.get("env", {})
            if isinstance(env, dict):
                for key, value in env.items():
                    self.add_env_row(str(key), str(value))

            # 加载到 JSON 编辑器 (保留完整配置)
            json_str = json.dumps(self.config, indent=2, ensure_ascii=False)
            self.json_edit.setPlainText(json_str)

    def browse_command(self):
        """浏览可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择可执行文件",
            str(Path.home()),
            "可执行文件 (*.exe *.bat *.cmd);;所有文件 (*.*)"
        )
        if file_path:
            self.command_edit.setText(file_path)

    def add_env_var(self):
        """添加环境变量行"""
        self.add_env_row("", "")
        row = self.env_table.rowCount() - 1
        self.env_table.selectRow(row)

    def add_env_row(self, key, value):
        """添加环境变量行"""
        row = self.env_table.rowCount()
        self.env_table.insertRow(row)
        self.env_table.setItem(row, 0, QTableWidgetItem(key))
        self.env_table.setItem(row, 1, QTableWidgetItem(value))

    def remove_env_var(self):
        """删除环境变量"""
        selected_items = self.env_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.env_table.removeRow(row)

    def _get_config_from_form(self):
        """从表单获取配置对象"""
        command = self.command_edit.text().strip()

        # 解析参数
        args_text = self.args_edit.text().strip()
        args = []
        if args_text:
            import shlex
            try:
                args = shlex.split(args_text)
            except Exception:
                args = args_text.split()

        # 获取环境变量
        env_vars = {}
        for row in range(self.env_table.rowCount()):
            key_item = self.env_table.item(row, 0)
            value_item = self.env_table.item(row, 1)
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key:
                    env_vars[key] = value

        config = {}
        if command:
            config["command"] = command
        if args:
            config["args"] = args
        if env_vars:
            config["env"] = env_vars

        return config

    def _get_config_from_json(self):
        """从 JSON 编辑器获取配置对象"""
        json_text = self.json_edit.toPlainText().strip()
        if not json_text:
            return {}
        return json.loads(json_text)

    def format_json(self):
        """格式化 JSON"""
        try:
            json_text = self.json_edit.toPlainText()
            data = json.loads(json_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.json_edit.setPlainText(formatted)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")

    def validate_json(self):
        """验证 JSON"""
        try:
            json_text = self.json_edit.toPlainText().strip()
            if not json_text:
                QMessageBox.information(self, "验证结果", "JSON 为空")
                return
            json.loads(json_text)
            QMessageBox.information(self, "验证结果", "JSON 格式正确!")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "验证结果", f"JSON 格式错误:\n{str(e)}")

    def validate_and_accept(self):
        """验证并接受"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "服务器名称不能为空")
            return

        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:
            # 表单模式: command 必填
            command = self.command_edit.text().strip()
            if not command:
                QMessageBox.warning(self, "警告", "命令不能为空")
                return
        else:
            # JSON 模式: 验证 JSON 格式
            try:
                self._get_config_from_json()
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")
                return

        self.accept()

    def get_server_data(self):
        """获取服务器数据"""
        name = self.name_edit.text().strip()
        current_tab = self.tab_widget.currentIndex()

        if current_tab == 0:
            # 表单模式
            config = self._get_config_from_form()
        else:
            # JSON 模式
            config = self._get_config_from_json()

        return {
            "name": name,
            "config": config
        }
