"""
权限配置对话框
"""
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox
)


class PermissionDialog(QDialog):
    """权限配置对话框"""

    def __init__(self, parent, permission_data=None):
        super().__init__(parent)
        self.permission_data = permission_data or {}
        self.init_ui()
        if self.permission_data:
            self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("工具权限配置")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        # 工具名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如: Bash, Read, Grep")
        layout.addRow("工具名称*:", self.name_edit)

        # 工具类型
        self.type_combo = QComboBox()
        self.type_combo.addItem("Bash", "bash")
        self.type_combo.addItem("文件操作", "file")
        self.type_combo.addItem("MCP 工具", "mcp")
        self.type_combo.addItem("网络请求", "network")
        self.type_combo.addItem("其他", "other")
        layout.addRow("工具类型:", self.type_combo)

        # 权限级别
        self.permission_combo = QComboBox()
        self.permission_combo.addItem("自动允许", "allow")
        self.permission_combo.addItem("需要确认", "prompt")
        self.permission_combo.addItem("拒绝", "deny")
        layout.addRow("权限级别:", self.permission_combo)

        # 按钮
        button_layout = QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        layout.addRow(button_layout)

    def load_data(self):
        """加载数据"""
        self.name_edit.setText(self.permission_data.get("name", ""))
        type_value = self.permission_data.get("type", "")
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == type_value:
                self.type_combo.setCurrentIndex(i)
                break

        permission_value = self.permission_data.get("permission", "prompt")
        for i in range(self.permission_combo.count()):
            if self.permission_combo.itemData(i) == permission_value:
                self.permission_combo.setCurrentIndex(i)
                break

    def get_permission_data(self):
        """获取权限数据"""
        return {
            "name": self.name_edit.text().strip(),
            "type": self.type_combo.currentData(),
            "permission": self.permission_combo.currentData()
        }

    def accept(self):
        """接受"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "工具名称不能为空")
            return
        super().accept()
