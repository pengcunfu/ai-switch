"""
UI/UX 配置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QMessageBox, QCheckBox,
    QSpinBox, QComboBox, QDoubleSpinBox
)


class UIUXTab(QWidget):
    """UI/UX 配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # === 界面显示组 ===
        display_group = QGroupBox("界面显示")
        display_layout = QFormLayout(display_group)

        # 状态栏
        self.status_bar_checkbox = QCheckBox("显示状态栏")
        self.status_bar_checkbox.setChecked(True)
        display_layout.addRow(self.status_bar_checkbox)

        # 工具栏
        self.toolbar_checkbox = QCheckBox("显示工具栏")
        self.toolbar_checkbox.setChecked(True)
        display_layout.addRow(self.toolbar_checkbox)

        # 配置文件路径
        self.config_path_checkbox = QCheckBox("显示配置文件路径")
        self.config_path_checkbox.setChecked(True)
        display_layout.addRow(self.config_path_checkbox)

        # 标签页位置
        self.tab_position_combo = QComboBox()
        self.tab_position_combo.addItem("顶部", "top")
        self.tab_position_combo.addItem("底部", "bottom")
        self.tab_position_combo.addItem("左侧", "left")
        self.tab_position_combo.addItem("右侧", "right")
        display_layout.addRow("标签页位置:", self.tab_position_combo)

        layout.addWidget(display_group)

        # === 交互设置组 ===
        interaction_group = QGroupBox("交互设置")
        interaction_layout = QFormLayout(interaction_group)

        # 双击编辑
        self.double_click_edit_checkbox = QCheckBox("双击编辑项目")
        self.double_click_edit_checkbox.setChecked(True)
        interaction_layout.addRow(self.double_click_edit_checkbox)

        # 确认删除
        self.confirm_delete_checkbox = QCheckBox("删除前确认")
        self.confirm_delete_checkbox.setChecked(True)
        interaction_layout.addRow(self.confirm_delete_checkbox)

        # 自动保存
        self.auto_save_checkbox = QCheckBox("自动保存配置")
        self.auto_save_checkbox.setChecked(False)
        interaction_layout.addRow(self.auto_save_checkbox)

        # 自动保存间隔
        self.auto_save_interval_spin = QSpinBox()
        self.auto_save_interval_spin.setRange(1, 60)
        self.auto_save_interval_spin.setValue(5)
        self.auto_save_interval_spin.setSuffix(" 分钟")
        interaction_layout.addRow("自动保存间隔:", self.auto_save_interval_spin)

        layout.addWidget(interaction_group)

        # === 性能设置组 ===
        performance_group = QGroupBox("性能设置")
        performance_layout = QFormLayout(performance_group)

        # Spinner 显示
        self.spinner_tree_checkbox = QCheckBox("显示 Spinner 树")
        self.spinner_tree_checkbox.setChecked(False)
        performance_layout.addRow(self.spinner_tree_checkbox)

        # 动画效果
        self.animations_checkbox = QCheckBox("启用界面动画")
        self.animations_checkbox.setChecked(True)
        performance_layout.addRow(self.animations_checkbox)

        # 刷新频率
        self.refresh_rate_spin = QSpinBox()
        self.refresh_rate_spin.setRange(10, 1000)
        self.refresh_rate_spin.setValue(100)
        self.refresh_rate_spin.setSuffix(" ms")
        performance_layout.addRow("界面刷新频率:", self.refresh_rate_spin)

        layout.addWidget(performance_group)

        # === 通知设置组 ===
        notification_group = QGroupBox("通知设置")
        notification_layout = QFormLayout(notification_group)

        # 成功通知
        self.success_notify_checkbox = QCheckBox("显示成功通知")
        self.success_notify_checkbox.setChecked(True)
        notification_layout.addRow(self.success_notify_checkbox)

        # 错误通知
        self.error_notify_checkbox = QCheckBox("显示错误通知")
        self.error_notify_checkbox.setChecked(True)
        notification_layout.addRow(self.error_notify_checkbox)

        # 警告通知
        self.warning_notify_checkbox = QCheckBox("显示警告通知")
        self.warning_notify_checkbox.setChecked(True)
        notification_layout.addRow(self.warning_notify_checkbox)

        # 通知持续时间
        self.notify_duration_spin = QSpinBox()
        self.notify_duration_spin.setRange(1, 10)
        self.notify_duration_spin.setValue(3)
        self.notify_duration_spin.setSuffix(" 秒")
        notification_layout.addRow("通知持续时间:", self.notify_duration_spin)

        layout.addWidget(notification_group)

        layout.addStretch()

        # 按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        reset_btn = QPushButton("重置默认")
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        uiux_config = config_data.get("uiux", {})

        # 界面显示
        self.status_bar_checkbox.setChecked(uiux_config.get("showStatusBar", True))
        self.toolbar_checkbox.setChecked(uiux_config.get("showToolbar", True))
        self.config_path_checkbox.setChecked(uiux_config.get("showConfigPath", True))

        tab_position = uiux_config.get("tabPosition", "top")
        for i in range(self.tab_position_combo.count()):
            if self.tab_position_combo.itemData(i) == tab_position:
                self.tab_position_combo.setCurrentIndex(i)
                break

        # 交互设置
        self.double_click_edit_checkbox.setChecked(uiux_config.get("doubleClickToEdit", True))
        self.confirm_delete_checkbox.setChecked(uiux_config.get("confirmBeforeDelete", True))
        self.auto_save_checkbox.setChecked(uiux_config.get("autoSave", False))
        self.auto_save_interval_spin.setValue(uiux_config.get("autoSaveInterval", 5))

        # 性能设置
        self.spinner_tree_checkbox.setChecked(uiux_config.get("showSpinnerTree", False))
        self.animations_checkbox.setChecked(uiux_config.get("animationsEnabled", True))
        self.refresh_rate_spin.setValue(uiux_config.get("refreshRate", 100))

        # 通知设置
        notifications = uiux_config.get("notifications", {})
        self.success_notify_checkbox.setChecked(notifications.get("showSuccess", True))
        self.error_notify_checkbox.setChecked(notifications.get("showError", True))
        self.warning_notify_checkbox.setChecked(notifications.get("showWarning", True))
        self.notify_duration_spin.setValue(notifications.get("duration", 3))

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "uiux" not in config_data:
                config_data["uiux"] = {}

            # 界面显示
            config_data["uiux"]["showStatusBar"] = self.status_bar_checkbox.isChecked()
            config_data["uiux"]["showToolbar"] = self.toolbar_checkbox.isChecked()
            config_data["uiux"]["showConfigPath"] = self.config_path_checkbox.isChecked()
            config_data["uiux"]["tabPosition"] = self.tab_position_combo.currentData()

            # 交互设置
            config_data["uiux"]["doubleClickToEdit"] = self.double_click_edit_checkbox.isChecked()
            config_data["uiux"]["confirmBeforeDelete"] = self.confirm_delete_checkbox.isChecked()
            config_data["uiux"]["autoSave"] = self.auto_save_checkbox.isChecked()
            config_data["uiux"]["autoSaveInterval"] = self.auto_save_interval_spin.value()

            # 性能设置
            config_data["uiux"]["showSpinnerTree"] = self.spinner_tree_checkbox.isChecked()
            config_data["uiux"]["animationsEnabled"] = self.animations_checkbox.isChecked()
            config_data["uiux"]["refreshRate"] = self.refresh_rate_spin.value()

            # 通知设置
            config_data["uiux"]["notifications"] = {
                "showSuccess": self.success_notify_checkbox.isChecked(),
                "showError": self.error_notify_checkbox.isChecked(),
                "showWarning": self.warning_notify_checkbox.isChecked(),
                "duration": self.notify_duration_spin.value()
            }

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "UI/UX 配置已保存! 部分设置可能需要重启应用后生效。")
            self.parent_window.statusBar().showMessage("UI/UX 配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def reset_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置为默认值吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.status_bar_checkbox.setChecked(True)
            self.toolbar_checkbox.setChecked(True)
            self.config_path_checkbox.setChecked(True)
            self.tab_position_combo.setCurrentIndex(0)
            self.double_click_edit_checkbox.setChecked(True)
            self.confirm_delete_checkbox.setChecked(True)
            self.auto_save_checkbox.setChecked(False)
            self.auto_save_interval_spin.setValue(5)
            self.spinner_tree_checkbox.setChecked(False)
            self.animations_checkbox.setChecked(True)
            self.refresh_rate_spin.setValue(100)
            self.success_notify_checkbox.setChecked(True)
            self.error_notify_checkbox.setChecked(True)
            self.warning_notify_checkbox.setChecked(True)
            self.notify_duration_spin.setValue(3)
