"""
通用设置标签页 - 包含通用设置、服务商配置、用户信息、备份恢复
"""
import os
import json
import shutil
import platform
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QCheckBox, QLabel, QPushButton, QMessageBox,
    QFileDialog, QScrollArea, QComboBox, QLineEdit, QInputDialog
)
from PySide6.QtCore import Qt, QProcess


class GeneralSettingsTab(QWidget):
    """通用设置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.profiles = []
        self.active_profile_name = ""
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

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

        # === 服务商配置组 ===
        provider_group = QGroupBox("服务商配置")
        provider_layout = QVBoxLayout(provider_group)

        # Profile 切换栏
        profile_bar = QHBoxLayout()
        profile_bar.addWidget(QLabel("当前档案:"))

        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(180)
        self.profile_combo.currentIndexChanged.connect(self.on_profile_changed)
        profile_bar.addWidget(self.profile_combo)

        add_profile_btn = QPushButton("新增")
        add_profile_btn.clicked.connect(self.add_profile)
        profile_bar.addWidget(add_profile_btn)

        delete_profile_btn = QPushButton("删除")
        delete_profile_btn.clicked.connect(self.delete_profile)
        profile_bar.addWidget(delete_profile_btn)

        profile_bar.addStretch()
        provider_layout.addLayout(profile_bar)

        # 字段表单
        form_layout = QFormLayout()

        self.auth_token_edit = QLineEdit()
        self.auth_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.auth_token_edit.setPlaceholderText("输入 API 认证令牌")
        form_layout.addRow("Auth Token:", self.auth_token_edit)

        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("https://api.anthropic.com")
        form_layout.addRow("Base URL:", self.base_url_edit)

        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("claude-sonnet-4-6")
        form_layout.addRow("Model:", self.model_edit)

        provider_layout.addLayout(form_layout)

        # 应用环境变量按钮
        apply_env_btn = QPushButton("应用环境变量（写入系统）")
        apply_env_btn.setStyleSheet("color: #d4380d; font-weight: bold;")
        apply_env_btn.clicked.connect(self.apply_env_vars)
        provider_layout.addWidget(apply_env_btn)

        layout.addWidget(provider_group)

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

    # ========== 服务商档案管理 ==========

    def _default_profiles(self):
        return [
            {"name": "Anthropic 默认", "authToken": "", "baseUrl": "https://api.anthropic.com", "model": "claude-sonnet-4-6"}
        ]

    def _save_current_fields_to_profile(self):
        """将当前字段值存入当前档案"""
        if not self.active_profile_name:
            return
        for p in self.profiles:
            if p["name"] == self.active_profile_name:
                p["authToken"] = self.auth_token_edit.text().strip()
                p["baseUrl"] = self.base_url_edit.text().strip()
                p["model"] = self.model_edit.text().strip()
                break

    def _load_profile_to_fields(self, profile):
        """将档案数据加载到字段"""
        self.auth_token_edit.setText(profile.get("authToken", ""))
        self.base_url_edit.setText(profile.get("baseUrl", ""))
        self.model_edit.setText(profile.get("model", ""))

    def _rebuild_combo(self, select_name=None):
        """重建下拉框"""
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for p in self.profiles:
            self.profile_combo.addItem(p["name"])
        if select_name:
            idx = self.profile_combo.findText(select_name)
            if idx >= 0:
                self.profile_combo.setCurrentIndex(idx)
        self.profile_combo.blockSignals(False)

    def on_profile_changed(self, index):
        """切换档案"""
        if index < 0:
            return
        # 保存当前编辑内容
        if self.active_profile_name:
            self._save_current_fields_to_profile()
        # 加载新档案
        new_name = self.profile_combo.currentText()
        self.active_profile_name = new_name
        for p in self.profiles:
            if p["name"] == new_name:
                self._load_profile_to_fields(p)
                break

    def add_profile(self):
        """新增档案"""
        name, ok = QInputDialog.getText(self, "新增服务商档案", "请输入档案名称:")
        if not ok or not name.strip():
            return
        name = name.strip()
        if any(p["name"] == name for p in self.profiles):
            QMessageBox.warning(self, "警告", f"档案 '{name}' 已存在!")
            return
        self._save_current_fields_to_profile()
        self.profiles.append({"name": name, "authToken": "", "baseUrl": "", "model": ""})
        self._rebuild_combo(select_name=name)
        self.active_profile_name = name
        self._load_profile_to_fields({"authToken": "", "baseUrl": "", "model": ""})

    def delete_profile(self):
        """删除当前档案"""
        if len(self.profiles) <= 1:
            QMessageBox.warning(self, "警告", "至少保留一个服务商档案!")
            return
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除档案 '{self.active_profile_name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.profiles = [p for p in self.profiles if p["name"] != self.active_profile_name]
        first_name = self.profiles[0]["name"]
        self._rebuild_combo(select_name=first_name)
        self.active_profile_name = first_name
        self._load_profile_to_fields(self.profiles[0])

    def apply_env_vars(self):
        """将当前激活档案的环境变量写入系统（异步，不阻塞UI）"""
        self._save_current_fields_to_profile()

        # 立即持久化到配置文件
        config_data = self.parent_window.get_config_data()
        config_data["providerProfiles"] = self.profiles
        config_data["activeProviderProfile"] = self.active_profile_name
        self.parent_window.set_config_data(config_data)
        try:
            self.parent_window.save_config_to_file()
        except Exception:
            pass  # 保存失败不阻塞环境变量设置

        active = None
        for p in self.profiles:
            if p["name"] == self.active_profile_name:
                active = p
                break

        if not active:
            QMessageBox.warning(self, "警告", "没有选中的服务商档案!")
            return

        token = active.get("authToken", "")
        base_url = active.get("baseUrl", "")
        model = active.get("model", "")

        if not token and not base_url and not model:
            QMessageBox.warning(self, "警告", "当前档案所有字段为空，无需设置!")
            return

        # 立即设置当前进程的环境变量
        if token:
            os.environ["ANTHROPIC_AUTH_TOKEN"] = token
        if base_url:
            os.environ["ANTHROPIC_BASE_URL"] = base_url
        if model:
            os.environ["ANTHROPIC_MODEL"] = model

        system = platform.system()

        if system == "Windows":
            # 使用 QProcess 异步执行 setx，避免阻塞 UI
            self._pending_setx = []
            if token:
                self._pending_setx.append(("ANTHROPIC_AUTH_TOKEN", token))
            if base_url:
                self._pending_setx.append(("ANTHROPIC_BASE_URL", base_url))
            if model:
                self._pending_setx.append(("ANTHROPIC_MODEL", model))

            self._run_next_setx()
        else:
            # Unix: 写入 ~/.claude/env.sh
            env_file = Path.home() / ".claude" / "env.sh"
            env_file.parent.mkdir(parents=True, exist_ok=True)
            lines = ["# Claude Code 服务商环境变量 (由 ClaudeConfigManager 生成)\n"]
            if token:
                lines.append(f'export ANTHROPIC_AUTH_TOKEN="{token}"\n')
            if base_url:
                lines.append(f'export ANTHROPIC_BASE_URL="{base_url}"\n')
            if model:
                lines.append(f'export ANTHROPIC_MODEL="{model}"\n')
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            QMessageBox.information(
                self, "成功",
                f"环境变量已生效，并写入 ~/.claude/env.sh\n"
                f"请在 shell 配置中 source 此文件以持久化:\n  source ~/.claude/env.sh"
            )
            self.parent_window.statusBar().showMessage("环境变量已应用: " + self.active_profile_name)

    def _run_next_setx(self):
        """异步执行下一个 setx 命令"""
        if not self._pending_setx:
            QMessageBox.information(
                self, "成功",
                "环境变量已设置!\n\n请重新打开终端以使环境变量在新终端中生效。"
            )
            self.parent_window.statusBar().showMessage("环境变量已应用: " + self.active_profile_name)
            return

        name, value = self._pending_setx.pop(0)
        proc = QProcess(self)
        proc.setProgram("setx")
        proc.setArguments([name, value])
        proc.finished.connect(lambda exit_code, exit_status, _name=name: self._on_setx_finished(exit_code, exit_status, _name))
        proc.errorOccurred.connect(lambda err, _name=name: self._on_setx_error(err, _name))
        self.parent_window.statusBar().showMessage(f"正在设置环境变量 {name}...")

    def _on_setx_finished(self, exit_code, exit_status, name):
        """setx 完成回调"""
        if exit_code == 0:
            self.parent_window.statusBar().showMessage(f"已设置 {name}")
            self._run_next_setx()
        else:
            err_msg = f"setx {name} 返回错误码: {exit_code}"
            QMessageBox.critical(self, "错误", err_msg)

    def _on_setx_error(self, err, name):
        """setx 错误回调"""
        QMessageBox.critical(
            self, "错误",
            f"执行 setx {name} 失败:\n{err}\n\n"
            f"当前进程环境变量已生效，但持久化失败。"
        )
        self._run_next_setx()

    # ========== 数据加载与保存 ==========

    def load_data(self, config_data):
        """加载数据"""
        # 通用设置
        self.auto_updates_checkbox.setChecked(config_data.get("autoUpdates", False))
        self.install_method_label.setText(config_data.get("installMethod", "未知"))

        # 服务商档案
        self.profiles = config_data.get("providerProfiles", self._default_profiles())
        self.active_profile_name = config_data.get("activeProviderProfile", self.profiles[0]["name"] if self.profiles else "")

        self._rebuild_combo(select_name=self.active_profile_name)
        active = next((p for p in self.profiles if p["name"] == self.active_profile_name), self.profiles[0] if self.profiles else None)
        if active:
            self._load_profile_to_fields(active)

        # 迁移状态
        sonnet = config_data.get("sonnet45MigrationComplete", False)
        opus = config_data.get("opus45MigrationComplete", False)
        thinking = config_data.get("thinkingMigrationComplete", False)

        self.sonnet_migration_label.setText("已完成" if sonnet else "未完成")
        self.sonnet_migration_label.setStyleSheet("color: green;" if sonnet else "color: red;")

        self.opus_migration_label.setText("已完成" if opus else "未完成")
        self.opus_migration_label.setStyleSheet("color: green;" if opus else "color: red;")

        self.thinking_migration_label.setText("已完成" if thinking else "未完成")
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

            # 通用设置
            config_data["autoUpdates"] = self.auto_updates_checkbox.isChecked()

            # 服务商档案
            self._save_current_fields_to_profile()
            config_data["providerProfiles"] = self.profiles
            config_data["activeProviderProfile"] = self.active_profile_name

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
                    "githubRepoPaths": {},
                    "providerProfiles": self._default_profiles(),
                    "activeProviderProfile": "Anthropic 默认"
                }

                self.parent_window.set_config_data(default_config)
                self.parent_window.save_config_to_file()
                self.parent_window.refresh_all_views()

                QMessageBox.information(self, "成功", "配置已重置为默认值!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"重置失败:\n{str(e)}")
