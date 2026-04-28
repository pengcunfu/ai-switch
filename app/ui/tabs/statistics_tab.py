"""
Statistics 仪表板标签页
"""
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QTableWidget, QTableWidgetItem, QLabel,
    QHeaderView, QAbstractItemView, QTabWidget, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatisticsTab(QWidget):
    """Statistics 仪表板标签页"""

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

        # === 概览 Tab ===
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)

        # 总体统计
        overview_group = QGroupBox("总体统计")
        overview_form = QFormLayout(overview_group)

        self.total_requests_label = QLabel("0")
        self.total_cost_label = QLabel("$0.00")
        self.total_tokens_label = QLabel("0")
        self.active_projects_label = QLabel("0")
        self.active_skills_label = QLabel("0")

        overview_form.addRow("总请求数:", self.total_requests_label)
        overview_form.addRow("总成本:", self.total_cost_label)
        overview_form.addRow("总 Tokens:", self.total_tokens_label)
        overview_form.addRow("活跃项目:", self.active_projects_label)
        overview_form.addRow("活跃 Skills:", self.active_skills_label)

        overview_layout.addWidget(overview_group)
        self.tab_widget.addTab(overview_widget, "概览")

        # === Skills 使用统计 Tab ===
        skills_widget = QWidget()
        skills_layout = QVBoxLayout(skills_widget)

        skills_group = QGroupBox("Skills 使用统计")
        skills_table_layout = QVBoxLayout(skills_group)

        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(4)
        self.skills_table.setHorizontalHeaderLabels(["Skill 名称", "使用次数", "最后使用时间", "频率"])
        self.skills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.skills_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        skills_table_layout.addWidget(self.skills_table)

        skills_layout.addWidget(skills_group)
        self.tab_widget.addTab(skills_widget, "Skills 统计")

        # === 项目统计 Tab ===
        projects_widget = QWidget()
        projects_layout = QVBoxLayout(projects_widget)

        projects_group = QGroupBox("项目活跃度统计")
        projects_table_layout = QVBoxLayout(projects_group)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(5)
        self.projects_table.setHorizontalHeaderLabels(["项目路径", "最后成本", "API 持续时间", "总 Tokens", "活跃度"])
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.projects_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        projects_table_layout.addWidget(self.projects_table)

        projects_layout.addWidget(projects_group)
        self.tab_widget.addTab(projects_widget, "项目统计")

        # === 模型使用统计 Tab ===
        model_widget = QWidget()
        model_layout = QVBoxLayout(model_widget)

        model_group = QGroupBox("模型使用统计")
        model_table_layout = QVBoxLayout(model_group)

        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels(["模型", "输入 Tokens", "输出 Tokens", "缓存读取", "成本 (USD)"])
        self.model_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.model_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        model_table_layout.addWidget(self.model_table)

        model_layout.addWidget(model_group)
        self.tab_widget.addTab(model_widget, "模型统计")

        # === 刷新按钮 ===
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新统计")
        refresh_btn.clicked.connect(self.refresh_statistics)
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        self.config_data = config_data
        self.refresh_statistics()

    def refresh_statistics(self):
        """刷新统计数据"""
        # 加载概览数据
        self.load_overview()

        # 加载 Skills 统计
        self.load_skills_statistics()

        # 加载项目统计
        self.load_projects_statistics()

        # 加载模型统计
        self.load_model_statistics()

    def load_overview(self):
        """加载总体统计"""
        skill_usage = self.config_data.get("skillUsage", {})
        projects = self.config_data.get("projects", {})

        # 计算总数据
        total_requests = 0
        total_cost = 0.0
        total_tokens = 0
        active_skills = len([s for s in skill_usage.values() if s.get("usageCount", 0) > 0])

        # 从项目数据中汇总
        for project_config in projects.values():
            if "lastCost" in project_config:
                total_cost += project_config.get("lastCost", 0.0)
            if "lastTotalInputTokens" in project_config:
                total_tokens += project_config.get("lastTotalInputTokens", 0) + \
                               project_config.get("lastTotalOutputTokens", 0)

        # 从 skill usage 计算请求数
        for skill_data in skill_usage.values():
            total_requests += skill_data.get("usageCount", 0)

        self.total_requests_label.setText(str(total_requests))
        self.total_cost_label.setText(f"${total_cost:.4f}")
        self.total_tokens_label.setText(f"{total_tokens:,}")
        self.active_projects_label.setText(str(len(projects)))
        self.active_skills_label.setText(str(active_skills))

    def load_skills_statistics(self):
        """加载 Skills 使用统计"""
        self.skills_table.setRowCount(0)

        skill_usage = self.config_data.get("skillUsage", {})

        # 按使用次数排序
        sorted_skills = sorted(
            skill_usage.items(),
            key=lambda x: x[1].get("usageCount", 0),
            reverse=True
        )

        for skill_name, skill_data in sorted_skills:
            row = self.skills_table.rowCount()
            self.skills_table.insertRow(row)

            usage_count = skill_data.get("usageCount", 0)
            last_used = skill_data.get("lastUsedAt", 0)

            if last_used > 0:
                last_used_date = datetime.fromtimestamp(last_used / 1000).strftime("%Y-%m-%d %H:%M")
            else:
                last_used_date = "从未使用"

            # 计算频率
            if usage_count > 10:
                frequency = "高频"
            elif usage_count > 5:
                frequency = "中频"
            elif usage_count > 0:
                frequency = "低频"
            else:
                frequency = "未使用"

            self.skills_table.setItem(row, 0, QTableWidgetItem(skill_name))
            self.skills_table.setItem(row, 1, QTableWidgetItem(str(usage_count)))
            self.skills_table.setItem(row, 2, QTableWidgetItem(last_used_date))
            self.skills_table.setItem(row, 3, QTableWidgetItem(frequency))

    def load_projects_statistics(self):
        """加载项目统计"""
        self.projects_table.setRowCount(0)

        projects = self.config_data.get("projects", {})

        for project_path, project_config in projects.items():
            row = self.projects_table.rowCount()
            self.projects_table.insertRow(row)

            last_cost = project_config.get("lastCost", 0.0)
            api_duration = project_config.get("lastAPIDuration", 0)
            input_tokens = project_config.get("lastTotalInputTokens", 0)
            output_tokens = project_config.get("lastTotalOutputTokens", 0)
            total_tokens = input_tokens + output_tokens

            # 计算活跃度
            if last_cost > 0.5:
                activity = "高活跃"
            elif last_cost > 0.1:
                activity = "中活跃"
            elif last_cost > 0:
                activity = "低活跃"
            else:
                activity = "未活跃"

            self.projects_table.setItem(row, 0, QTableWidgetItem(project_path))
            self.projects_table.setItem(row, 1, QTableWidgetItem(f"${last_cost:.4f}"))
            self.projects_table.setItem(row, 2, QTableWidgetItem(f"{api_duration}ms"))
            self.projects_table.setItem(row, 3, QTableWidgetItem(f"{total_tokens:,}"))
            self.projects_table.setItem(row, 4, QTableWidgetItem(activity))

    def load_model_statistics(self):
        """加载模型使用统计"""
        self.model_table.setRowCount(0)

        # 汇总所有项目的模型使用情况
        model_stats = {}

        projects = self.config_data.get("projects", {})
        for project_config in projects.values():
            last_model_usage = project_config.get("lastModelUsage", {})
            for model_name, usage_data in last_model_usage.items():
                if model_name not in model_stats:
                    model_stats[model_name] = {
                        "inputTokens": 0,
                        "outputTokens": 0,
                        "cacheReadInputTokens": 0,
                        "costUSD": 0.0
                    }

                model_stats[model_name]["inputTokens"] += usage_data.get("inputTokens", 0)
                model_stats[model_name]["outputTokens"] += usage_data.get("outputTokens", 0)
                model_stats[model_name]["cacheReadInputTokens"] += usage_data.get("cacheReadInputTokens", 0)
                model_stats[model_name]["costUSD"] += usage_data.get("costUSD", 0.0)

        # 填充表格
        for model_name, stats in model_stats.items():
            row = self.model_table.rowCount()
            self.model_table.insertRow(row)

            self.model_table.setItem(row, 0, QTableWidgetItem(model_name))
            self.model_table.setItem(row, 1, QTableWidgetItem(f"{stats['inputTokens']:,}"))
            self.model_table.setItem(row, 2, QTableWidgetItem(f"{stats['outputTokens']:,}"))
            self.model_table.setItem(row, 3, QTableWidgetItem(f"{stats['cacheReadInputTokens']:,}"))
            self.model_table.setItem(row, 4, QTableWidgetItem(f"${stats['costUSD']:.4f}"))
