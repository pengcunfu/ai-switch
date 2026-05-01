"""
通用设置标签页 - 包含通用设置、用户信息、备份恢复
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QCheckBox, QLabel, QPushButton, QMessageBox,
    QFileDialog, QScrollArea
)
from PySide6.QtCore import Qt


class GeneralSettingsTab(QWidget):
    """通用设置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # === 通用设置组 ===
        settings_group = QGroupBox("通用设置")
        settings_layout = QFormLayout(settings_group)

        self.auto_updates_checkbox = QCheckBox("启用自动更新")
        settings_layout.addRow(self.auto_updates_checkbox)

        self.install_method_label = QLabel()
        settings_layout.addRow("安装方式:", self.install_method_label)

        layout.addWidget(settings_group)

        # === 迁移状态组 ===
        migration_group = QGroupBox("迁移状态")
        migration_layout = QFormLayout(migration_group)

        self.sonnet_migration_label = QLabel()
        self.opus_migration_label = QLabel()
        self.thinking_migration_label = QLabel()

        migration_layout.addRow("Sonnet 4.5:", self.sonnet_migration_label)
        migration_layout.addRow("Opus 4.5:", self.opus_migration_label)
        migration_layout.addRow("Thinking:", self.thinking_migration_label)

        self.marketplace_attempted_label = QLabel()
        self.marketplace_installed_label = QLabel()
        migration_layout.addRow("市场插件尝试安装:", self.marketplace_attempted_label)
        migration_layout.addRow("市场插件已安装:", self.marketplace_installed_label)

        layout.addWidget(migration_group)

        # === 用户信息组 ===
        user_group = QGroupBox("用户信息")
        user_layout = QFormLayout(user_group)

        self.user_id_label = QLabel()
        self.user_id_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.user_id_label.setWordWrap(True)
        user_layout.addRow("用户ID:", self.user_id_label)

        self.first_start_label = QLabel()
        user_layout.addRow("首次使用时间:", self.first_start_label)

        self.usage_time_label = QLabel()
        user_layout.addRow("使用时长:", self.usage_time_label)

        layout.addWidget(user_group)

        # === 配置备份与恢复组 ===
        backup_group = QGroupBox("配置备份与恢复")
        backup_layout = QVBoxLayout(backup_group)

        export_btn = QPushButton("导出配置")
        import_btn = QPushButton("导入配置")
        reset_btn = QPushButton("重置为默认")

        export_btn.clicked.connect(self.export_config)
        import_btn.clicked.connect(self.import_config)
        reset_btn.clicked.connect(self.reset_config)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(reset_btn)
        backup_layout.addLayout(btn_layout)

        backup_info = QLabel("提示: 保存配置时会自动创建 .bak 备份文件")
        backup_info.setStyleSheet("color: #666; font-size: 10px;")
        backup_layout.addWidget(backup_info)

        layout.addWidget(backup_group)

        # === 保存按钮 ===
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

        layout.addStretch()

        scroll_area.setWidget(scroll_content)
        outer_layout.addWidget(scroll_area)

    def load_data(self, config_data):
        """加载数据"""
        # 通用设置
        self.auto_updates_checkbox.setChecked(config_data.get("autoUpdates", False))
        self.install_method_label.setText(config_data.get("installMethod", "未知"))

        # 迁移状态
        sonnet = config_data.get("sonnet45MigrationComplete", False)
        opus = config_data.get("opus45MigrationComplete", False)
        thinking = config_data.get("thinkingMigrationComplete", False)

        self.sonnet_migration_label.setText("✓ 已完成" if sonnet else "✗ 未完成")
        self.sonnet_migration_label.setStyleSheet("color: green;" if sonnet else "color: red;")

        self.opus_migration_label.setText("✓ 已完成" if opus else "✗ 未完成")
        self.opus_migration_label.setStyleSheet("color: green;" if opus else "color: red;")

        self.thinking_migration_label.setText("✓ 已完成" if thinking else "✗ 未完成")
        self.thinking_migration_label.setStyleSheet("color: green;" if thinking else "color: red;")

        attempted = config_data.get("officialMarketplaceAutoInstallAttempted", False)
        installed = config_data.get("officialMarketplaceAutoInstalled", False)

        self.marketplace_attempted_label.setText("是" if attempted else "否")
        self.marketplace_installed_label.setText("是" if installed else "否")

        # 用户信息
        user_id = config_data.get("userID", "未知")
        self.user_id_label.setText(user_id)

        first_start = config_data.get("firstStartTime", "")
        if first_start:
            try:
                start_time = datetime.fromisoformat(first_start.replace('Z', '+00:00'))
                local_time = start_time.astimezone()
                formatted = local_time.strftime("%Y-%m-%d %H:%M:%S")
                self.first_start_label.setText(formatted)

                now = datetime.now(local_time.tzinfo)
                duration = now - local_time
                days = duration.days
                hours = duration.seconds // 3600
                self.usage_time_label.setText(f"{days} 天 {hours} 小时")
            except:
                self.first_start_label.setText(first_start)
                self.usage_time_label.setText("未知")
        else:
            self.first_start_label.setText("未知")
            self.usage_time_label.setText("未知")

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()
            config_data["autoUpdates"] = self.auto_updates_checkbox.isChecked()
            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "通用设置已保存!")
            self.parent_window.statusBar().showMessage("设置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败:\n{str(e)}")

    def export_config(self):
        """导出配置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出配置",
            str(Path.home() / "claude_config_backup.json"),
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            try:
                config_data = self.parent_window.get_config_data()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"配置已导出到:\n{file_path}")
                self.parent_window.statusBar().showMessage(f"配置已导出: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")

    def import_config(self):
        """导入配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入配置",
            str(Path.home()),
            "JSON 文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            reply = QMessageBox.question(
                self, "确认导入",
                "导入配置将覆盖当前配置,确定要继续吗?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        imported_data = json.load(f)

                    config_path = self.parent_window.config_path
                    if config_path.exists():
                        backup_path = config_path.with_suffix('.json.bak')
                        shutil.copy2(config_path, backup_path)

                    self.parent_window.set_config_data(imported_data)
                    self.parent_window.save_config_to_file()
                    self.parent_window.refresh_all_views()

                    QMessageBox.information(self, "成功", "配置已导入!")
                    self.parent_window.statusBar().showMessage(f"配置已导入: {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"导入失败:\n{str(e)}")

    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self, "确认重置",
            "重置配置将删除所有自定义设置!\n此操作不可撤销。\n\n确定要继续吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                config_path = self.parent_window.config_path
                if config_path.exists():
                    backup_path = config_path.with_suffix(f'.json.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
                    shutil.copy2(config_path, backup_path)

                default_config = {
                    "installMethod": "native",
                    "autoUpdates": False,
                    "mcpServers": {},
                    "githubRepoPaths": {}
                }

                self.parent_window.set_config_data(default_config)
                self.parent_window.save_config_to_file()
                self.parent_window.refresh_all_views()

                QMessageBox.information(self, "成功", "配置已重置为默认值!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置失败:\n{str(e)}")
