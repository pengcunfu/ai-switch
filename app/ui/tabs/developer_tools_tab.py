"""
Developer Tools 标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QPushButton, QMessageBox, QCheckBox,
    QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt


class DeveloperToolsTab(QWidget):
    """Developer Tools 标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # === 开发模式组 ===
        dev_mode_group = QGroupBox("开发模式")
        dev_mode_layout = QFormLayout(dev_mode_group)

        # 启用开发者工具
        self.dev_tools_checkbox = QCheckBox("启用开发者工具")
        self.dev_tools_checkbox.setToolTip("显示额外的调试信息和工具")
        dev_mode_layout.addRow(self.dev_tools_checkbox)

        # 详细日志
        self.verbose_logging_checkbox = QCheckBox("启用详细日志")
        self.verbose_logging_checkbox.setToolTip("在日志中显示更详细的信息")
        dev_mode_layout.addRow(self.verbose_logging_checkbox)

        # 调试模式
        self.debug_mode_checkbox = QCheckBox("调试模式")
        self.debug_mode_checkbox.setToolTip("启用调试功能，如断点、单步执行等")
        dev_mode_layout.addRow(self.debug_mode_checkbox)

        layout.addWidget(dev_mode_group)

        # === 性能监控组 ===
        perf_monitor_group = QGroupBox("性能监控")
        perf_monitor_layout = QVBoxLayout(perf_monitor_group)

        # 性能指标表格
        self.perf_table = QTableWidget()
        self.perf_table.setColumnCount(4)
        self.perf_table.setHorizontalHeaderLabels(["指标", "当前值", "峰值", "平均"])
        self.perf_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.perf_table.setMaximumHeight(200)
        perf_monitor_layout.addWidget(self.perf_table)

        # 设置默认的性能指标
        self.setup_performance_metrics()

        layout.addWidget(perf_monitor_group)

        # === 成本跟踪组 ===
        cost_tracking_group = QGroupBox("成本跟踪")
        cost_tracking_layout = QFormLayout(cost_tracking_group)

        # 启用成本跟踪
        self.cost_tracking_checkbox = QCheckBox("启用成本跟踪")
        self.cost_tracking_checkbox.setChecked(True)
        cost_tracking_layout.addRow(self.cost_tracking_checkbox)

        # 成本警告阈值
        self.cost_warning_spin = QSpinBox()
        self.cost_warning_spin.setRange(1, 1000)
        self.cost_warning_spin.setValue(50)
        self.cost_warning_spin.setSuffix(" USD")
        cost_tracking_layout.addRow("成本警告阈值:", self.cost_warning_spin)

        # 每日预算限制
        self.daily_budget_spin = QSpinBox()
        self.daily_budget_spin.setRange(1, 10000)
        self.daily_budget_spin.setValue(100)
        self.daily_budget_spin.setSuffix(" USD")
        cost_tracking_layout.addRow("每日预算限制:", self.daily_budget_spin)

        # 显示成本统计
        self.cost_stats_label = QLabel("总成本: $0.00 | 今日: $0.00")
        self.cost_stats_label.setStyleSheet("background: #f0f0f0; padding: 10px; border-radius: 5px;")
        cost_tracking_layout.addRow(self.cost_stats_label)

        layout.addWidget(cost_tracking_group)

        # === API 监控组 ===
        api_monitor_group = QGroupBox("API 监控")
        api_monitor_layout = QFormLayout(api_monitor_group)

        # 启用 API 监控
        self.api_monitor_checkbox = QCheckBox("启用 API 调用监控")
        self.api_monitor_checkbox.setChecked(True)
        api_monitor_layout.addRow(self.api_monitor_checkbox)

        # 记录 API 响应时间
        self.api_response_time_checkbox = QCheckBox("记录 API 响应时间")
        self.api_response_time_checkbox.setChecked(True)
        api_monitor_layout.addRow(self.api_response_time_checkbox)

        # 缓存命中率监控
        self.cache_hit_checkbox = QCheckBox("监控缓存命中率")
        self.cache_hit_checkbox.setChecked(True)
        api_monitor_layout.addRow(self.cache_hit_checkbox)

        layout.addWidget(api_monitor_group)

        # === 高级工具组 ===
        advanced_tools_group = QGroupBox("高级工具")
        advanced_tools_layout = QVBoxLayout(advanced_tools_group)

        # 工具按钮
        tools_btn_layout = QHBoxLayout()
        export_logs_btn = QPushButton("导出日志")
        clear_cache_btn = QPushButton("清除缓存")
        diagnose_btn = QPushButton("诊断问题")
        benchmark_btn = QPushButton("性能测试")

        export_logs_btn.clicked.connect(self.export_logs)
        clear_cache_btn.clicked.connect(self.clear_cache)
        diagnose_btn.clicked.connect(self.diagnose_issues)
        benchmark_btn.clicked.connect(self.run_benchmark)

        tools_btn_layout.addWidget(export_logs_btn)
        tools_btn_layout.addWidget(clear_cache_btn)
        tools_btn_layout.addWidget(diagnose_btn)
        tools_btn_layout.addWidget(benchmark_btn)
        tools_btn_layout.addStretch()

        advanced_tools_layout.addLayout(tools_btn_layout)
        layout.addWidget(advanced_tools_group)

        layout.addStretch()

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def setup_performance_metrics(self):
        """设置性能指标"""
        metrics = [
            ("API 响应时间", "0ms", "0ms", "0ms"),
            ("内存使用", "0MB", "0MB", "0MB"),
            ("CPU 使用率", "0%", "0%", "0%"),
            ("缓存命中率", "0%", "0%", "0%"),
        ]

        self.perf_table.setRowCount(0)
        for metric_name, current, peak, avg in metrics:
            row = self.perf_table.rowCount()
            self.perf_table.insertRow(row)
            self.perf_table.setItem(row, 0, QTableWidgetItem(metric_name))
            self.perf_table.setItem(row, 1, QTableWidgetItem(current))
            self.perf_table.setItem(row, 2, QTableWidgetItem(peak))
            self.perf_table.setItem(row, 3, QTableWidgetItem(avg))

    def load_data(self, config_data):
        """加载数据"""
        dev_tools = config_data.get("developerTools", {})

        # 开发模式
        self.dev_tools_checkbox.setChecked(dev_tools.get("enabled", False))
        self.verbose_logging_checkbox.setChecked(dev_tools.get("verboseLogging", False))
        self.debug_mode_checkbox.setChecked(dev_tools.get("debugMode", False))

        # 成本跟踪
        cost_tracking = dev_tools.get("costTracking", {})
        self.cost_tracking_checkbox.setChecked(cost_tracking.get("enabled", True))
        self.cost_warning_spin.setValue(cost_tracking.get("warningThreshold", 50))
        self.daily_budget_spin.setValue(cost_tracking.get("dailyBudget", 100))

        # 更新成本统计显示
        total_cost = cost_tracking.get("totalCost", 0.0)
        today_cost = cost_tracking.get("todayCost", 0.0)
        self.cost_stats_label.setText(f"总成本: ${total_cost:.2f} | 今日: ${today_cost:.2f}")

        # API 监控
        api_monitoring = dev_tools.get("apiMonitoring", {})
        self.api_monitor_checkbox.setChecked(api_monitoring.get("enabled", True))
        self.api_response_time_checkbox.setChecked(api_monitoring.get("logResponseTime", True))
        self.cache_hit_checkbox.setChecked(api_monitoring.get("monitorCacheHitRate", True))

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "developerTools" not in config_data:
                config_data["developerTools"] = {}

            # 开发模式
            config_data["developerTools"]["enabled"] = self.dev_tools_checkbox.isChecked()
            config_data["developerTools"]["verboseLogging"] = self.verbose_logging_checkbox.isChecked()
            config_data["developerTools"]["debugMode"] = self.debug_mode_checkbox.isChecked()

            # 成本跟踪
            config_data["developerTools"]["costTracking"] = {
                "enabled": self.cost_tracking_checkbox.isChecked(),
                "warningThreshold": self.cost_warning_spin.value(),
                "dailyBudget": self.daily_budget_spin.value()
            }

            # API 监控
            config_data["developerTools"]["apiMonitoring"] = {
                "enabled": self.api_monitor_checkbox.isChecked(),
                "logResponseTime": self.api_response_time_checkbox.isChecked(),
                "monitorCacheHitRate": self.cache_hit_checkbox.isChecked()
            }

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "开发者工具配置已保存!")
            self.parent_window.statusBar().showMessage("开发者工具配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def export_logs(self):
        """导出日志"""
        QMessageBox.information(self, "导出日志", "日志导出功能开发中...")

    def clear_cache(self):
        """清除缓存"""
        reply = QMessageBox.question(
            self, "确认清除",
            "确定要清除所有缓存吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "清除缓存", "缓存已清除!")

    def diagnose_issues(self):
        """诊断问题"""
        QMessageBox.information(self, "诊断", "系统诊断功能开发中...")

    def run_benchmark(self):
        """运行性能测试"""
        QMessageBox.information(self, "性能测试", "性能测试功能开发中...")
