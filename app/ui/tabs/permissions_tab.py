"""
Permissions 管理标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QCheckBox, QComboBox, QLabel, QLineEdit,
    QHeaderView, QAbstractItemView, QTabWidget
)
from PySide6.QtCore import Qt


class PermissionsTab(QWidget):
    """Permissions 管理标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # Tab 切换: 全局权限 / 工具权限
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # === 全局权限 Tab ===
        global_widget = QWidget()
        global_layout = QVBoxLayout(global_widget)

        # 自动权限设置
        auto_group = QGroupBox("自动权限设置")
        auto_layout = QFormLayout(auto_group)

        self.auto_allow_read_checkbox = QCheckBox("自动允许只读操作")
        self.auto_allow_read_checkbox.setToolTip("自动允许 Bash 只读命令和 MCP 只读工具")
        auto_layout.addRow(self.auto_allow_read_checkbox)

        self.prompt_on_write_checkbox = QCheckBox("写入操作需要确认")
        self.prompt_on_write_checkbox.setToolTip("执行可能修改系统的操作前提示确认")
        self.prompt_on_write_checkbox.setChecked(True)
        auto_layout.addRow(self.prompt_on_write_checkbox)

        self.allow_dangerous_checkbox = QCheckBox("允许危险操作")
        self.allow_dangerous_checkbox.setToolTip("允许删除文件、强制推送等危险操作")
        auto_layout.addRow(self.allow_dangerous_checkbox)

        global_layout.addWidget(auto_group)

        # 权限级别
        level_group = QGroupBox("默认权限级别")
        level_layout = QFormLayout(level_group)

        self.permission_level_combo = QComboBox()
        self.permission_level_combo.addItem("严格 (所有操作需确认)", "strict")
        self.permission_level_combo.addItem("平衡 (只读自动，写入确认)", "balanced")
        self.permission_level_combo.addItem("宽松 (仅危险操作确认)", "permissive")
        level_layout.addRow("权限级别:", self.permission_level_combo)

        global_layout.addWidget(level_group)

        # 全局工具权限
        global_tools_group = QGroupBox("全局工具权限")
        global_tools_layout = QVBoxLayout(global_tools_group)

        # 工具权限表
        self.global_tools_table = QTableWidget()
        self.global_tools_table.setColumnCount(3)
        self.global_tools_table.setHorizontalHeaderLabels(["工具名称", "类型", "权限"])
        self.global_tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.global_tools_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        global_tools_layout.addWidget(self.global_tools_table)

        # 按钮栏
        tools_btn_layout = QHBoxLayout()
        add_tool_btn = QPushButton("添加工具")
        edit_tool_btn = QPushButton("编辑工具")
        remove_tool_btn = QPushButton("移除工具")
        add_tool_btn.clicked.connect(self.add_global_tool)
        edit_tool_btn.clicked.connect(self.edit_global_tool)
        remove_tool_btn.clicked.connect(self.remove_global_tool)
        tools_btn_layout.addWidget(add_tool_btn)
        tools_btn_layout.addWidget(edit_tool_btn)
        tools_btn_layout.addWidget(remove_tool_btn)
        tools_btn_layout.addStretch()
        global_tools_layout.addLayout(tools_btn_layout)

        global_layout.addWidget(global_tools_group)

        self.tab_widget.addTab(global_widget, "全局权限")

        # === 项目权限 Tab ===
        project_widget = QWidget()
        project_layout = QVBoxLayout(project_widget)

        # 项目选择
        project_select_group = QGroupBox("项目权限覆盖")
        project_select_layout = QFormLayout(project_select_group)

        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.on_project_changed)
        project_select_layout.addRow("选择项目:", self.project_combo)

        project_layout.addWidget(project_select_group)

        # 项目工具权限
        project_tools_group = QGroupBox("项目工具权限")
        project_tools_layout = QVBoxLayout(project_tools_group)

        self.project_tools_table = QTableWidget()
        self.project_tools_table.setColumnCount(3)
        self.project_tools_table.setHorizontalHeaderLabels(["工具名称", "类型", "权限"])
        self.project_tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.project_tools_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        project_tools_layout.addWidget(self.project_tools_table)

        project_layout.addWidget(project_tools_group)

        self.tab_widget.addTab(project_widget, "项目权限")

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        # 自动权限设置
        permissions = config_data.get("permissions", {})
        self.auto_allow_read_checkbox.setChecked(permissions.get("autoAllowRead", False))
        self.prompt_on_write_checkbox.setChecked(permissions.get("promptOnWrite", True))
        self.allow_dangerous_checkbox.setChecked(permissions.get("allowDangerous", False))

        # 权限级别
        level = permissions.get("defaultLevel", "balanced")
        for i in range(self.permission_level_combo.count()):
            if self.permission_level_combo.itemData(i) == level:
                self.permission_level_combo.setCurrentIndex(i)
                break

        # 全局工具权限
        self.load_global_tools(config_data)

        # 项目列表
        self.load_projects(config_data)

    def load_global_tools(self, config_data):
        """加载全局工具权限"""
        self.global_tools_table.setRowCount(0)

        global_permissions = config_data.get("globalToolPermissions", {})

        for tool_name, perm_config in global_permissions.items():
            row = self.global_tools_table.rowCount()
            self.global_tools_table.insertRow(row)

            self.global_tools_table.setItem(row, 0, QTableWidgetItem(tool_name))
            self.global_tools_table.setItem(row, 1, QTableWidgetItem(perm_config.get("type", "unknown")))
            self.global_tools_table.setItem(row, 2, QTableWidgetItem(perm_config.get("permission", "prompt")))

    def load_projects(self, config_data):
        """加载项目列表"""
        self.project_combo.clear()

        projects = config_data.get("projects", {})
        for project_path in projects.keys():
            self.project_combo.addItem(project_path)

        if self.project_combo.count() > 0:
            self.load_project_tools(config_data, self.project_combo.currentText())

    def on_project_changed(self):
        """项目选择改变"""
        config_data = self.parent_window.get_config_data()
        selected_project = self.project_combo.currentText()
        if selected_project:
            self.load_project_tools(config_data, selected_project)

    def load_project_tools(self, config_data, project_path):
        """加载项目工具权限"""
        self.project_tools_table.setRowCount(0)

        projects = config_data.get("projects", {})
        project_config = projects.get(project_path, {})

        allowed_tools = project_config.get("allowedTools", [])
        for tool_name in allowed_tools:
            row = self.project_tools_table.rowCount()
            self.project_tools_table.insertRow(row)

            self.project_tools_table.setItem(row, 0, QTableWidgetItem(tool_name))
            self.project_tools_table.setItem(row, 1, QTableWidgetItem("allowed"))
            self.project_tools_table.setItem(row, 2, QTableWidgetItem("allowed"))

    def add_global_tool(self):
        """添加全局工具权限"""
        from ..dialogs.permission_dialog import PermissionDialog
        dialog = PermissionDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            tool_data = dialog.get_permission_data()
            row = self.global_tools_table.rowCount()
            self.global_tools_table.insertRow(row)
            self.global_tools_table.setItem(row, 0, QTableWidgetItem(tool_data["name"]))
            self.global_tools_table.setItem(row, 1, QTableWidgetItem(tool_data["type"]))
            self.global_tools_table.setItem(row, 2, QTableWidgetItem(tool_data["permission"]))

    def edit_global_tool(self):
        """编辑全局工具权限"""
        selected_items = self.global_tools_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个工具")
            return

        row = selected_items[0].row()
        tool_name = self.global_tools_table.item(row, 0).text()

        from ..dialogs.permission_dialog import PermissionDialog
        dialog = PermissionDialog(self, {
            "name": tool_name,
            "type": self.global_tools_table.item(row, 1).text(),
            "permission": self.global_tools_table.item(row, 2).text()
        })
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            tool_data = dialog.get_permission_data()
            self.global_tools_table.setItem(row, 0, QTableWidgetItem(tool_data["name"]))
            self.global_tools_table.setItem(row, 1, QTableWidgetItem(tool_data["type"]))
            self.global_tools_table.setItem(row, 2, QTableWidgetItem(tool_data["permission"]))

    def remove_global_tool(self):
        """移除全局工具权限"""
        selected_items = self.global_tools_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个工具")
            return

        row = selected_items[0].row()
        tool_name = self.global_tools_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要移除工具 '{tool_name}' 的权限设置吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.global_tools_table.removeRow(row)

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            # 保存权限配置
            if "permissions" not in config_data:
                config_data["permissions"] = {}

            config_data["permissions"]["autoAllowRead"] = self.auto_allow_read_checkbox.isChecked()
            config_data["permissions"]["promptOnWrite"] = self.prompt_on_write_checkbox.isChecked()
            config_data["permissions"]["allowDangerous"] = self.allow_dangerous_checkbox.isChecked()
            config_data["permissions"]["defaultLevel"] = self.permission_level_combo.currentData()

            # 保存全局工具权限
            global_permissions = {}
            for row in range(self.global_tools_table.rowCount()):
                tool_name = self.global_tools_table.item(row, 0).text()
                tool_type = self.global_tools_table.item(row, 1).text()
                permission = self.global_tools_table.item(row, 2).text()
                global_permissions[tool_name] = {
                    "type": tool_type,
                    "permission": permission
                }
            config_data["globalToolPermissions"] = global_permissions

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "权限配置已保存!")
            self.parent_window.statusBar().showMessage("权限配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
