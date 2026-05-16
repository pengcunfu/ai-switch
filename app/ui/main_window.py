"""
Claude 配置管理器主窗口
"""
import json
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QFileDialog,
    QMessageBox, QLabel, QHeaderView, QAbstractItemView,
    QGroupBox, QSplitter, QCheckBox, QMenuBar, QMenu
)
from PySide6.QtCore import QSize, QRect

from .widgets.json_highlighter import JsonHighlighter


class ClaudeConfigGUI(QMainWindow):
    """Claude 配置管理器主窗口"""

    def __init__(self):
        super().__init__()
        self.config_path = Path.home() / ".claude.json"
        self.config_data = {}
        self.init_ui()
        self.load_config()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Claude Configuration Manager")

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent.parent / "resources" / "icon.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        # 设置窗口大小并居中
        self.resize(1200, 750)
        self.center_window()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 5, 10, 10)

        # Config path label
        path_label = QLabel(f"配置文件: {self.config_path}")
        path_label.setStyleSheet("color: #666; font-size: 11px; padding: 2px 0;")
        main_layout.addWidget(path_label)

        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create categorized tabs
        self.create_statistics_tab()  # 第一个标签页：独立的统计信息
        self.create_basic_category_tab()
        self.create_model_permissions_category_tab()
        self.create_features_category_tab()
        self.create_appearance_category_tab()
        self.create_integration_category_tab()

        # Create menu bar
        self.create_menu_bar()

        # Status bar
        self.statusBar().showMessage("就绪")

    def center_window(self):
        """将窗口居中显示"""
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())

    def create_statistics_tab(self):
        """创建统计信息标签页 (第一个标签页)"""
        from .tabs.statistics_tab import StatisticsTab
        tab = StatisticsTab(self)
        self.statistics_tab = tab
        self.tab_widget.addTab(tab, "统计信息")

    def create_basic_category_tab(self):
        """创建基础配置分类标签页"""
        from .tabs.category_basic_tab import BasicCategoryTab
        tab = BasicCategoryTab(self)
        self.basic_category_tab = tab
        self.tab_widget.addTab(tab, "基础配置")

    def create_model_permissions_category_tab(self):
        """创建模型与权限分类标签页"""
        from .tabs.category_model_permissions_tab import ModelPermissionsCategoryTab
        tab = ModelPermissionsCategoryTab(self)
        self.model_permissions_category_tab = tab
        self.tab_widget.addTab(tab, "模型与权限")

    def create_features_category_tab(self):
        """创建功能配置分类标签页"""
        from .tabs.category_features_tab import FeaturesCategoryTab
        tab = FeaturesCategoryTab(self)
        self.features_category_tab = tab
        self.tab_widget.addTab(tab, "功能配置")

    def create_appearance_category_tab(self):
        """创建外观与界面分类标签页"""
        from .tabs.category_appearance_tab import AppearanceCategoryTab
        tab = AppearanceCategoryTab(self)
        self.appearance_category_tab = tab
        self.tab_widget.addTab(tab, "外观与界面")

    def create_integration_category_tab(self):
        """创建集成与工具分类标签页"""
        from .tabs.category_integration_tab import IntegrationCategoryTab
        tab = IntegrationCategoryTab(self)
        self.integration_category_tab = tab
        self.tab_widget.addTab(tab, "集成与工具")

    def load_config(self):
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
            else:
                self.config_data = {}

            # 更新所有分类标签页
            self.statistics_tab.load_data(self.config_data)
            self.basic_category_tab.load_data(self.config_data)
            self.model_permissions_category_tab.load_data(self.config_data)
            self.features_category_tab.load_data(self.config_data)
            self.appearance_category_tab.load_data(self.config_data)
            self.integration_category_tab.load_data(self.config_data)

            self.statusBar().showMessage(f"配置已加载: {self.config_path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败:\n{str(e)}")
            self.statusBar().showMessage("加载失败")

    def save_config_to_file(self):
        """保存配置到文件"""
        try:
            # 备份原文件
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                shutil.copy2(self.config_path, backup_path)

            # 写入新配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)

            self.statusBar().showMessage(f"配置已保存到: {self.config_path}")
        except Exception as e:
            raise Exception(f"保存到文件失败: {str(e)}")

    def get_config_data(self):
        """获取配置数据"""
        return self.config_data

    def set_config_data(self, data):
        """设置配置数据"""
        self.config_data = data

    def refresh_all_views(self):
        """刷新所有视图"""
        self.statistics_tab.load_data(self.config_data)
        self.basic_category_tab.load_data(self.config_data)
        self.model_permissions_category_tab.load_data(self.config_data)
        self.features_category_tab.load_data(self.config_data)
        self.appearance_category_tab.load_data(self.config_data)
        self.integration_category_tab.load_data(self.config_data)

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")

        # 打开配置文件位置
        open_config_action = file_menu.addAction("打开配置文件位置(&C)")
        open_config_action.triggered.connect(self.open_config_location)

        # 打开 Skills 文件夹
        open_skills_action = file_menu.addAction("打开 Skills 文件夹(&S)")
        open_skills_action.triggered.connect(self.open_skills_folder)

        # 打开 .claude 文件夹
        open_claude_action = file_menu.addAction("打开 .claude 文件夹(&L)")
        open_claude_action.triggered.connect(self.open_claude_folder)

        file_menu.addSeparator()

        # 查看完整配置 JSON
        view_config_action = file_menu.addAction("查看完整配置 JSON(&J)")
        view_config_action.triggered.connect(self.show_config_json_dialog)

        # 刷新配置
        refresh_action = file_menu.addAction("刷新配置(&R)")
        refresh_action.triggered.connect(self.refresh_config)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于选项
        about_action = help_menu.addAction("关于(&A)...")
        about_action.triggered.connect(self.show_about_dialog)

    def open_config_location(self):
        """打开配置文件位置"""
        try:
            config_file = self.config_path
            if config_file.exists():
                self.open_file_location(config_file)
                self.statusBar().showMessage(f"已打开: {config_file}")
            else:
                QMessageBox.warning(self, "警告", f"配置文件不存在:\n{config_file}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开配置文件位置失败:\n{str(e)}")

    def open_skills_folder(self):
        """打开 Skills 文件夹"""
        try:
            # 全局 Skills 文件夹
            global_skills = Path.home() / ".claude" / "skills"
            if global_skills.exists():
                self.open_file_location(global_skills)
                self.statusBar().showMessage(f"已打开: {global_skills}")
            else:
                QMessageBox.warning(self, "警告", f"Skills 文件夹不存在:\n{global_skills}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开 Skills 文件夹失败:\n{str(e)}")

    def open_claude_folder(self):
        """打开 .claude 文件夹"""
        try:
            claude_folder = Path.home() / ".claude"
            if claude_folder.exists():
                self.open_file_location(claude_folder)
                self.statusBar().showMessage(f"已打开: {claude_folder}")
            else:
                QMessageBox.warning(self, "警告", f".claude 文件夹不存在:\n{claude_folder}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开 .claude 文件夹失败:\n{str(e)}")

    def open_file_location(self, path):
        """打开文件或文件夹位置"""
        try:
            path = Path(path)
            system = platform.system()

            if system == "Windows":
                # Windows: 使用 explorer
                if path.is_file():
                    subprocess.run(['explorer', '/select,', str(path)])
                else:
                    subprocess.run(['explorer', str(path)])
            elif system == "Darwin":  # macOS
                if path.is_file():
                    subprocess.run(['open', '-R', str(path)])
                else:
                    subprocess.run(['open', str(path)])
            else:  # Linux
                if path.is_file():
                    subprocess.run(['xdg-open', str(path.parent)])
                else:
                    subprocess.run(['xdg-open', str(path)])
        except Exception as e:
            raise Exception(f"无法打开位置: {str(e)}")

    def refresh_config(self):
        """刷新配置"""
        try:
            self.load_config()
            QMessageBox.information(self, "成功", "配置已刷新!")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新配置失败:\n{str(e)}")

    def show_about_dialog(self):
        """显示关于对话框"""
        from .dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()

    def show_config_json_dialog(self):
        """显示完整配置 JSON 对话框"""
        from .dialogs.config_json_dialog import ConfigJsonDialog
        dialog = ConfigJsonDialog(self, self.config_data)
        dialog.exec()
