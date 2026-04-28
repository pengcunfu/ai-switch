"""
Hooks 配置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QTextEdit, QTabWidget, QLabel
)
from PySide6.QtCore import Qt


class HooksTab(QWidget):
    """Hooks 配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # Tab 切换
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # === Pre-Hooks Tab ===
        pre_hooks_widget = QWidget()
        pre_hooks_layout = QVBoxLayout(pre_hooks_widget)

        # Pre-Hooks 说明
        pre_hint = QLabel("Pre-Hooks 在操作执行前运行，可以用于验证、修改输入或阻止操作。")
        pre_hint.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        pre_hint.setWordWrap(True)
        pre_hooks_layout.addWidget(pre_hint)

        # Pre-Hooks 表格
        pre_hooks_group = QGroupBox("Pre-Hooks 配置")
        pre_hooks_table_layout = QVBoxLayout(pre_hooks_group)

        self.pre_hooks_table = QTableWidget()
        self.pre_hooks_table.setColumnCount(4)
        self.pre_hooks_table.setHorizontalHeaderLabels(["触发时机", "命令/脚本", "启用", "描述"])
        self.pre_hooks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.pre_hooks_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        pre_hooks_table_layout.addWidget(self.pre_hooks_table)

        # Pre-Hooks 按钮
        pre_btn_layout = QHBoxLayout()
        add_pre_btn = QPushButton("添加 Pre-Hook")
        edit_pre_btn = QPushButton("编辑")
        remove_pre_btn = QPushButton("删除")
        add_pre_btn.clicked.connect(lambda: self.add_hook("pre"))
        edit_pre_btn.clicked.connect(lambda: self.edit_hook("pre"))
        remove_pre_btn.clicked.connect(lambda: self.remove_hook("pre"))
        pre_btn_layout.addWidget(add_pre_btn)
        pre_btn_layout.addWidget(edit_pre_btn)
        pre_btn_layout.addWidget(remove_pre_btn)
        pre_btn_layout.addStretch()
        pre_hooks_table_layout.addLayout(pre_btn_layout)

        pre_hooks_layout.addWidget(pre_hooks_group)
        self.tab_widget.addTab(pre_hooks_widget, "Pre-Hooks")

        # === Post-Hooks Tab ===
        post_hooks_widget = QWidget()
        post_hooks_layout = QVBoxLayout(post_hooks_widget)

        # Post-Hooks 说明
        post_hint = QLabel("Post-Hooks 在操作执行后运行，可以用于通知、清理或触发后续操作。")
        post_hint.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        post_hint.setWordWrap(True)
        post_hooks_layout.addWidget(post_hint)

        # Post-Hooks 表格
        post_hooks_group = QGroupBox("Post-Hooks 配置")
        post_hooks_table_layout = QVBoxLayout(post_hooks_group)

        self.post_hooks_table = QTableWidget()
        self.post_hooks_table.setColumnCount(4)
        self.post_hooks_table.setHorizontalHeaderLabels(["触发时机", "命令/脚本", "启用", "描述"])
        self.post_hooks_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.post_hooks_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        post_hooks_table_layout.addWidget(self.post_hooks_table)

        # Post-Hooks 按钮
        post_btn_layout = QHBoxLayout()
        add_post_btn = QPushButton("添加 Post-Hook")
        edit_post_btn = QPushButton("编辑")
        remove_post_btn = QPushButton("删除")
        add_post_btn.clicked.connect(lambda: self.add_hook("post"))
        edit_post_btn.clicked.connect(lambda: self.edit_hook("post"))
        remove_post_btn.clicked.connect(lambda: self.remove_hook("post"))
        post_btn_layout.addWidget(add_post_btn)
        post_btn_layout.addWidget(edit_post_btn)
        post_btn_layout.addWidget(remove_post_btn)
        post_btn_layout.addStretch()
        post_hooks_table_layout.addLayout(post_btn_layout)

        post_hooks_layout.addWidget(post_hooks_group)
        self.tab_widget.addTab(post_hooks_widget, "Post-Hooks")

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存配置")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        hooks_config = config_data.get("hooks", {})

        # 加载 Pre-Hooks
        pre_hooks = hooks_config.get("preHooks", [])
        self.load_hooks_to_table(pre_hooks, self.pre_hooks_table)

        # 加载 Post-Hooks
        post_hooks = hooks_config.get("postHooks", [])
        self.load_hooks_to_table(post_hooks, self.post_hooks_table)

    def load_hooks_to_table(self, hooks, table):
        """加载 hooks 到表格"""
        table.setRowCount(0)
        for hook in hooks:
            row = table.rowCount()
            table.insertRow(row)

            trigger_event = hook.get("trigger", "")
            command = hook.get("command", "")
            enabled = "是" if hook.get("enabled", True) else "否"
            description = hook.get("description", "")

            table.setItem(row, 0, QTableWidgetItem(trigger_event))
            table.setItem(row, 1, QTableWidgetItem(command))
            table.setItem(row, 2, QTableWidgetItem(enabled))
            table.setItem(row, 3, QTableWidgetItem(description))

    def add_hook(self, hook_type):
        """添加 Hook"""
        from ..dialogs.hook_dialog import HookDialog
        dialog = HookDialog(self, hook_type)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            hook_data = dialog.get_hook_data()
            table = self.pre_hooks_table if hook_type == "pre" else self.post_hooks_table
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(hook_data["trigger"]))
            table.setItem(row, 1, QTableWidgetItem(hook_data["command"]))
            table.setItem(row, 2, QTableWidgetItem("是" if hook_data["enabled"] else "否"))
            table.setItem(row, 3, QTableWidgetItem(hook_data["description"]))

    def edit_hook(self, hook_type):
        """编辑 Hook"""
        table = self.pre_hooks_table if hook_type == "pre" else self.post_hooks_table
        selected_items = table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个 Hook")
            return

        row = selected_items[0].row()
        hook_data = {
            "trigger": table.item(row, 0).text(),
            "command": table.item(row, 1).text(),
            "enabled": table.item(row, 2).text() == "是",
            "description": table.item(row, 3).text()
        }

        from ..dialogs.hook_dialog import HookDialog
        dialog = HookDialog(self, hook_type, hook_data)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            new_data = dialog.get_hook_data()
            table.setItem(row, 0, QTableWidgetItem(new_data["trigger"]))
            table.setItem(row, 1, QTableWidgetItem(new_data["command"]))
            table.setItem(row, 2, QTableWidgetItem("是" if new_data["enabled"] else "否"))
            table.setItem(row, 3, QTableWidgetItem(new_data["description"]))

    def remove_hook(self, hook_type):
        """删除 Hook"""
        table = self.pre_hooks_table if hook_type == "pre" else self.post_hooks_table
        selected_items = table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个 Hook")
            return

        row = selected_items[0].row()
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此 Hook 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            table.removeRow(row)

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "hooks" not in config_data:
                config_data["hooks"] = {}

            # 保存 Pre-Hooks
            pre_hooks = []
            for row in range(self.pre_hooks_table.rowCount()):
                pre_hooks.append({
                    "trigger": self.pre_hooks_table.item(row, 0).text(),
                    "command": self.pre_hooks_table.item(row, 1).text(),
                    "enabled": self.pre_hooks_table.item(row, 2).text() == "是",
                    "description": self.pre_hooks_table.item(row, 3).text()
                })
            config_data["hooks"]["preHooks"] = pre_hooks

            # 保存 Post-Hooks
            post_hooks = []
            for row in range(self.post_hooks_table.rowCount()):
                post_hooks.append({
                    "trigger": self.post_hooks_table.item(row, 0).text(),
                    "command": self.post_hooks_table.item(row, 1).text(),
                    "enabled": self.post_hooks_table.item(row, 2).text() == "是",
                    "description": self.post_hooks_table.item(row, 3).text()
                })
            config_data["hooks"]["postHooks"] = post_hooks

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "Hooks 配置已保存!")
            self.parent_window.statusBar().showMessage("Hooks 配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
