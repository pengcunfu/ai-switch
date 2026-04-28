"""
Claude 配置管理器主窗口
"""
import json
import shutil
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
        self.create_raw_config_tab()

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
        self.tab_widget.addTab(tab, "📊 统计信息")

    def create_basic_category_tab(self):
        """创建基础配置分类标签页"""
        from .tabs.category_basic_tab import BasicCategoryTab
        tab = BasicCategoryTab(self)
        self.basic_category_tab = tab
        self.tab_widget.addTab(tab, "⚙️ 基础配置")

    def create_model_permissions_category_tab(self):
        """创建模型与权限分类标签页"""
        from .tabs.category_model_permissions_tab import ModelPermissionsCategoryTab
        tab = ModelPermissionsCategoryTab(self)
        self.model_permissions_category_tab = tab
        self.tab_widget.addTab(tab, "🤖 模型与权限")

    def create_features_category_tab(self):
        """创建功能配置分类标签页"""
        from .tabs.category_features_tab import FeaturesCategoryTab
        tab = FeaturesCategoryTab(self)
        self.features_category_tab = tab
        self.tab_widget.addTab(tab, "⚙️ 功能配置")

    def create_appearance_category_tab(self):
        """创建外观与界面分类标签页"""
        from .tabs.category_appearance_tab import AppearanceCategoryTab
        tab = AppearanceCategoryTab(self)
        self.appearance_category_tab = tab
        self.tab_widget.addTab(tab, "🎨 外观与界面")

    def create_integration_category_tab(self):
        """创建集成与工具分类标签页"""
        from .tabs.category_integration_tab import IntegrationCategoryTab
        tab = IntegrationCategoryTab(self)
        self.integration_category_tab = tab
        self.tab_widget.addTab(tab, "🔗 集成与工具")

    def create_raw_config_tab(self):
        """创建原始 JSON 配置标签页"""
        from .tabs.raw_config_tab import RawConfigTab
        tab = RawConfigTab(self)
        self.raw_config_tab = tab
        self.tab_widget.addTab(tab, "完整配置 (JSON)")

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
            self.raw_config_tab.load_data(self.config_data)

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
        self.raw_config_tab.load_data(self.config_data)

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")

        # 关于选项
        about_action = help_menu.addAction("关于(&A)...")
        about_action.triggered.connect(self.show_about_dialog)

    def show_about_dialog(self):
        """显示关于对话框"""
        from .dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()
