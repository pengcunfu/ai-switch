"""
Integration Settings 标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QMessageBox, QCheckBox,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget
)
from PySide6.QtCore import Qt


class IntegrationTab(QWidget):
    """Integration Settings 标签页"""

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

        # === GitHub App Tab ===
        github_widget = QWidget()
        github_layout = QVBoxLayout(github_widget)

        # GitHub App 配置
        github_group = QGroupBox("GitHub App 配置")
        github_form = QFormLayout(github_group)

        # 启用 GitHub App
        self.github_enabled_checkbox = QCheckBox("启用 GitHub App 集成")
        github_form.addRow(self.github_enabled_checkbox)

        # Personal Access Token
        self.github_token_edit = QLineEdit()
        self.github_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token_edit.setPlaceholderText("ghp_xxxxxxxxxxxx")
        github_form.addRow("Personal Access Token:", self.github_token_edit)

        # 默认用户名
        self.github_username_edit = QLineEdit()
        self.github_username_edit.setPlaceholderText("GitHub 用户名")
        github_form.addRow("用户名:", self.github_username_edit)

        # 默认仓库
        self.github_repo_edit = QLineEdit()
        self.github_repo_edit.setPlaceholderText("username/repo-name")
        github_form.addRow("默认仓库:", self.github_repo_edit)

        github_layout.addWidget(github_group)

        # GitHub 集成功能
        github_features_group = QGroupBox("GitHub 集成功能")
        github_features_layout = QVBoxLayout(github_features_group)

        self.github_pr_checkbox = QCheckBox("自动创建 Pull Request")
        self.github_issues_checkbox = QCheckBox("创建 GitHub Issues")
        self.github_repo_sync_checkbox = QCheckBox("自动同步仓库配置")

        github_features_layout.addWidget(self.github_pr_checkbox)
        github_features_layout.addWidget(self.github_issues_checkbox)
        github_features_layout.addWidget(self.github_repo_sync_checkbox)

        github_layout.addWidget(github_features_group)

        self.tab_widget.addTab(github_widget, "GitHub")

        # === Slack App Tab ===
        slack_widget = QWidget()
        slack_layout = QVBoxLayout(slack_widget)

        # Slack App 配置
        slack_group = QGroupBox("Slack App 配置")
        slack_form = QFormLayout(slack_group)

        # 启用 Slack App
        self.slack_enabled_checkbox = QCheckBox("启用 Slack App 集成")
        slack_form.addRow(self.slack_enabled_checkbox)

        # Webhook URL
        self.slack_webhook_edit = QLineEdit()
        self.slack_webhook_edit.setPlaceholderText("https://hooks.slack.com/services/...")
        slack_form.addRow("Webhook URL:", self.slack_webhook_edit)

        # 默认频道
        self.slack_channel_edit = QLineEdit()
        self.slack_channel_edit.setPlaceholderText("#general")
        slack_form.addRow("默认频道:", self.slack_channel_edit)

        # Bot Token
        self.slack_bot_token_edit = QLineEdit()
        self.slack_bot_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.slack_bot_token_edit.setPlaceholderText("xoxb-...")
        slack_form.addRow("Bot Token:", self.slack_bot_token_edit)

        slack_layout.addWidget(slack_group)

        # Slack 通知设置
        slack_notifications_group = QGroupBox("Slack 通知设置")
        slack_notifications_layout = QVBoxLayout(slack_notifications_group)

        self.slack_error_checkbox = QCheckBox("发送错误通知")
        self.slack_completion_checkbox = QCheckBox("发送任务完成通知")
        self.slack_daily_summary_checkbox = QCheckBox("发送每日汇总")

        slack_notifications_layout.addWidget(self.slack_error_checkbox)
        slack_notifications_layout.addWidget(self.slack_completion_checkbox)
        slack_notifications_layout.addWidget(self.slack_daily_summary_checkbox)

        slack_layout.addWidget(slack_notifications_group)

        self.tab_widget.addTab(slack_widget, "Slack")

        # === 自定义命令 Tab ===
        custom_widget = QWidget()
        custom_layout = QVBoxLayout(custom_widget)

        # 自定义命令说明
        custom_hint = QLabel("自定义命令允许你为常用的操作序列创建快捷方式。")
        custom_hint.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        custom_hint.setWordWrap(True)
        custom_layout.addWidget(custom_hint)

        # 自定义命令表格
        custom_commands_group = QGroupBox("自定义命令")
        custom_commands_table_layout = QVBoxLayout(custom_commands_group)

        self.custom_commands_table = QTableWidget()
        self.custom_commands_table.setColumnCount(4)
        self.custom_commands_table.setHorizontalHeaderLabels(["命令名称", "触发词", "操作", "启用"])
        self.custom_commands_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.custom_commands_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        custom_commands_table_layout.addWidget(self.custom_commands_table)

        # 按钮
        custom_btn_layout = QHBoxLayout()
        add_custom_btn = QPushButton("添加命令")
        edit_custom_btn = QPushButton("编辑")
        remove_custom_btn = QPushButton("删除")
        add_custom_btn.clicked.connect(self.add_custom_command)
        edit_custom_btn.clicked.connect(self.edit_custom_command)
        remove_custom_btn.clicked.connect(self.remove_custom_command)
        custom_btn_layout.addWidget(add_custom_btn)
        custom_btn_layout.addWidget(edit_custom_btn)
        custom_btn_layout.addWidget(remove_custom_btn)
        custom_btn_layout.addStretch()
        custom_commands_table_layout.addLayout(custom_btn_layout)

        custom_layout.addWidget(custom_commands_group)
        self.tab_widget.addTab(custom_widget, "自定义命令")

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        test_github_btn = QPushButton("测试 GitHub")
        test_slack_btn = QPushButton("测试 Slack")
        save_btn.clicked.connect(self.save_settings)
        test_github_btn.clicked.connect(self.test_github)
        test_slack_btn.clicked.connect(self.test_slack)
        button_layout.addStretch()
        button_layout.addWidget(test_github_btn)
        button_layout.addWidget(test_slack_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        integrations = config_data.get("integrations", {})

        # GitHub 配置
        github = integrations.get("github", {})
        self.github_enabled_checkbox.setChecked(github.get("enabled", False))
        self.github_token_edit.setText(github.get("token", ""))
        self.github_username_edit.setText(github.get("username", ""))
        self.github_repo_edit.setText(github.get("defaultRepo", ""))

        github_features = github.get("features", {})
        self.github_pr_checkbox.setChecked(github_features.get("autoCreatePR", False))
        self.github_issues_checkbox.setChecked(github_features.get("createIssues", False))
        self.github_repo_sync_checkbox.setChecked(github_features.get("autoSyncRepo", False))

        # Slack 配置
        slack = integrations.get("slack", {})
        self.slack_enabled_checkbox.setChecked(slack.get("enabled", False))
        self.slack_webhook_edit.setText(slack.get("webhookUrl", ""))
        self.slack_channel_edit.setText(slack.get("defaultChannel", "#general"))
        self.slack_bot_token_edit.setText(slack.get("botToken", ""))

        slack_notifications = slack.get("notifications", {})
        self.slack_error_checkbox.setChecked(slack_notifications.get("sendErrors", False))
        self.slack_completion_checkbox.setChecked(slack_notifications.get("sendCompletion", False))
        self.slack_daily_summary_checkbox.setChecked(slack_notifications.get("sendDailySummary", False))

        # 自定义命令
        custom_commands = integrations.get("customCommands", [])
        self.load_custom_commands(custom_commands)

    def load_custom_commands(self, commands):
        """加载自定义命令"""
        self.custom_commands_table.setRowCount(0)
        for cmd in commands:
            row = self.custom_commands_table.rowCount()
            self.custom_commands_table.insertRow(row)
            self.custom_commands_table.setItem(row, 0, QTableWidgetItem(cmd.get("name", "")))
            self.custom_commands_table.setItem(row, 1, QTableWidgetItem(cmd.get("trigger", "")))
            self.custom_commands_table.setItem(row, 2, QTableWidgetItem(cmd.get("action", "")))
            self.custom_commands_table.setItem(row, 3, QTableWidgetItem("是" if cmd.get("enabled", True) else "否"))

    def add_custom_command(self):
        """添加自定义命令"""
        QMessageBox.information(self, "添加命令", "自定义命令添加功能开发中...")

    def edit_custom_command(self):
        """编辑自定义命令"""
        QMessageBox.information(self, "编辑命令", "自定义命令编辑功能开发中...")

    def remove_custom_command(self):
        """删除自定义命令"""
        selected_items = self.custom_commands_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个命令")
            return

        row = selected_items[0].row()
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除此自定义命令吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.custom_commands_table.removeRow(row)

    def test_github(self):
        """测试 GitHub 连接"""
        QMessageBox.information(self, "测试 GitHub", "GitHub 连接测试功能开发中...")

    def test_slack(self):
        """测试 Slack 连接"""
        QMessageBox.information(self, "测试 Slack", "Slack 连接测试功能开发中...")

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "integrations" not in config_data:
                config_data["integrations"] = {}

            # GitHub 配置
            config_data["integrations"]["github"] = {
                "enabled": self.github_enabled_checkbox.isChecked(),
                "token": self.github_token_edit.text().strip(),
                "username": self.github_username_edit.text().strip(),
                "defaultRepo": self.github_repo_edit.text().strip(),
                "features": {
                    "autoCreatePR": self.github_pr_checkbox.isChecked(),
                    "createIssues": self.github_issues_checkbox.isChecked(),
                    "autoSyncRepo": self.github_repo_sync_checkbox.isChecked()
                }
            }

            # Slack 配置
            config_data["integrations"]["slack"] = {
                "enabled": self.slack_enabled_checkbox.isChecked(),
                "webhookUrl": self.slack_webhook_edit.text().strip(),
                "defaultChannel": self.slack_channel_edit.text().strip(),
                "botToken": self.slack_bot_token_edit.text().strip(),
                "notifications": {
                    "sendErrors": self.slack_error_checkbox.isChecked(),
                    "sendCompletion": self.slack_completion_checkbox.isChecked(),
                    "sendDailySummary": self.slack_daily_summary_checkbox.isChecked()
                }
            }

            # 自定义命令
            custom_commands = []
            for row in range(self.custom_commands_table.rowCount()):
                custom_commands.append({
                    "name": self.custom_commands_table.item(row, 0).text(),
                    "trigger": self.custom_commands_table.item(row, 1).text(),
                    "action": self.custom_commands_table.item(row, 2).text(),
                    "enabled": self.custom_commands_table.item(row, 3).text() == "是"
                })
            config_data["integrations"]["customCommands"] = custom_commands

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "集成配置已保存!")
            self.parent_window.statusBar().showMessage("集成配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")
