"""
Memory 系统配置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QMessageBox, QCheckBox,
    QSpinBox, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt


class MemoryTab(QWidget):
    """Memory 系统配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # === Memory 设置组 ===
        settings_group = QGroupBox("Memory 设置")
        settings_layout = QFormLayout(settings_group)

        # 启用自动记忆
        self.auto_memory_checkbox = QCheckBox("启用自动记忆")
        self.auto_memory_checkbox.setToolTip("自动记住用户偏好和上下文信息")
        self.auto_memory_checkbox.setChecked(True)
        settings_layout.addRow(self.auto_memory_checkbox)

        # Memory 存储路径
        self.memory_path_edit = QLineEdit()
        memory_path_browse_btn = QPushButton("浏览...")
        memory_path_layout = QHBoxLayout()
        memory_path_layout.addWidget(self.memory_path_edit)
        memory_path_layout.addWidget(memory_path_browse_btn)
        settings_layout.addRow("Memory 存储路径:", memory_path_layout)

        # 最大 Memory 条目数
        self.max_entries_spin = QSpinBox()
        self.max_entries_spin.setRange(10, 10000)
        self.max_entries_spin.setValue(1000)
        settings_layout.addRow("最大 Memory 条目数:", self.max_entries_spin)

        # Memory 过期天数
        self.expiry_days_spin = QSpinBox()
        self.expiry_days_spin.setRange(7, 365)
        self.expiry_days_spin.setValue(90)
        settings_layout.addRow("Memory 过期天数:", self.expiry_days_spin)

        layout.addWidget(settings_group)

        # === Memory 类型组 ===
        types_group = QGroupBox("Memory 类型")
        types_layout = QVBoxLayout(types_group)

        # Memory 类型表格
        self.types_table = QTableWidget()
        self.types_table.setColumnCount(3)
        self.types_table.setHorizontalHeaderLabels(["Memory 类型", "状态", "描述"])
        self.types_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.types_table.setMaximumHeight(200)
        types_layout.addWidget(self.types_table)

        # 添加默认的 Memory 类型
        self.setup_default_memory_types()

        layout.addWidget(types_group)

        # === 高级设置组 ===
        advanced_group = QGroupBox("高级设置")
        advanced_layout = QFormLayout(advanced_group)

        # 自动清理过期 Memory
        self.auto_cleanup_checkbox = QCheckBox("自动清理过期 Memory")
        self.auto_cleanup_checkbox.setChecked(True)
        advanced_layout.addRow(self.auto_cleanup_checkbox)

        # Memory 压缩
        self.compression_checkbox = QCheckBox("启用 Memory 压缩")
        self.compression_checkbox.setToolTip("压缩相似的 Memory 条目以节省空间")
        advanced_layout.addRow(self.compression_checkbox)

        # 跨项目共享 Memory
        self.cross_project_checkbox = QCheckBox("跨项目共享 Memory")
        self.cross_project_checkbox.setToolTip("允许不同项目访问相同的 Memory")
        advanced_layout.addRow(self.cross_project_checkbox)

        layout.addWidget(advanced_group)

        layout.addStretch()

        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        clean_btn = QPushButton("清理过期 Memory")
        save_btn.clicked.connect(self.save_settings)
        clean_btn.clicked.connect(self.cleanup_memory)
        button_layout.addStretch()
        button_layout.addWidget(clean_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def setup_default_memory_types(self):
        """设置默认的 Memory 类型"""
        memory_types = [
            ("用户记忆", "启用", "记住用户的角色、偏好和专业知识"),
            ("项目记忆", "启用", "记住项目相关的目标和决策"),
            ("反馈记忆", "启用", "记住用户对方法的反馈和偏好"),
            ("引用记忆", "启用", "记住外部系统和文档的位置"),
        ]

        self.types_table.setRowCount(0)
        for mem_type, status, desc in memory_types:
            row = self.types_table.rowCount()
            self.types_table.insertRow(row)
            self.types_table.setItem(row, 0, QTableWidgetItem(mem_type))
            self.types_table.setItem(row, 1, QTableWidgetItem(status))
            self.types_table.setItem(row, 2, QTableWidgetItem(desc))

    def load_data(self, config_data):
        """加载数据"""
        memory_config = config_data.get("memory", {})

        self.auto_memory_checkbox.setChecked(memory_config.get("autoMemoryEnabled", True))
        self.memory_path_edit.setText(memory_config.get("memoryPath", ""))
        self.max_entries_spin.setValue(memory_config.get("maxEntries", 1000))
        self.expiry_days_spin.setValue(memory_config.get("expiryDays", 90))

        # 高级设置
        self.auto_cleanup_checkbox.setChecked(memory_config.get("autoCleanup", True))
        self.compression_checkbox.setChecked(memory_config.get("compressionEnabled", False))
        self.cross_project_checkbox.setChecked(memory_config.get("crossProjectSharing", False))

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "memory" not in config_data:
                config_data["memory"] = {}

            config_data["memory"]["autoMemoryEnabled"] = self.auto_memory_checkbox.isChecked()
            config_data["memory"]["memoryPath"] = self.memory_path_edit.text().strip()
            config_data["memory"]["maxEntries"] = self.max_entries_spin.value()
            config_data["memory"]["expiryDays"] = self.expiry_days_spin.value()
            config_data["memory"]["autoCleanup"] = self.auto_cleanup_checkbox.isChecked()
            config_data["memory"]["compressionEnabled"] = self.compression_checkbox.isChecked()
            config_data["memory"]["crossProjectSharing"] = self.cross_project_checkbox.isChecked()

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "Memory 配置已保存!")
            self.parent_window.statusBar().showMessage("Memory 配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def cleanup_memory(self):
        """清理过期 Memory"""
        QMessageBox.information(self, "清理 Memory", "Memory 清理功能开发中...")
