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

        # Create tabs
        self.create_general_settings_tab()
        self.create_mcp_servers_tab()
        self.create_projects_tab()
        self.create_user_info_tab()
        self.create_experimental_features_tab()
        self.create_skills_tab()
        self.create_model_config_tab()
        self.create_permissions_tab()
        self.create_statistics_tab()
        self.create_theme_tab()
        self.create_hooks_tab()
        self.create_memory_tab()
        self.create_uiux_tab()
        self.create_developer_tools_tab()
        self.create_integration_tab()
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

    def create_general_settings_tab(self):
        """创建通用设置标签页"""
        from .tabs.general_settings_tab import GeneralSettingsTab
        tab = GeneralSettingsTab(self)
        self.general_settings_tab = tab
        self.tab_widget.addTab(tab, "通用设置")

    def create_mcp_servers_tab(self):
        """创建 MCP 服务器标签页"""
        from .tabs.mcp_servers_tab import MCPServersTab
        tab = MCPServersTab(self)
        self.mcp_servers_tab = tab
        self.tab_widget.addTab(tab, "MCP 服务器")

    def create_projects_tab(self):
        """创建项目列表标签页"""
        from .tabs.projects_tab import ProjectsTab
        tab = ProjectsTab(self)
        self.projects_tab = tab
        self.tab_widget.addTab(tab, "项目列表")

    def create_user_info_tab(self):
        """创建用户信息标签页"""
        from .tabs.user_info_tab import UserInfoTab
        tab = UserInfoTab(self)
        self.user_info_tab = tab
        self.tab_widget.addTab(tab, "用户信息")

    def create_experimental_features_tab(self):
        """创建实验性功能标签页"""
        from .tabs.experimental_features_tab import ExperimentalFeaturesTab
        tab = ExperimentalFeaturesTab(self)
        self.experimental_features_tab = tab
        self.tab_widget.addTab(tab, "实验性功能")

    def create_skills_tab(self):
        """创建 Skills 标签页"""
        from .tabs.skills_tab import SkillsTab
        tab = SkillsTab(self)
        self.skills_tab = tab
        self.tab_widget.addTab(tab, "Skills")

    def create_model_config_tab(self):
        """创建 Model 配置标签页"""
        from .tabs.model_config_tab import ModelConfigTab
        tab = ModelConfigTab(self)
        self.model_config_tab = tab
        self.tab_widget.addTab(tab, "Model 配置")

    def create_permissions_tab(self):
        """创建 Permissions 管理标签页"""
        from .tabs.permissions_tab import PermissionsTab
        tab = PermissionsTab(self)
        self.permissions_tab = tab
        self.tab_widget.addTab(tab, "权限管理")

    def create_statistics_tab(self):
        """创建 Statistics 仪表板标签页"""
        from .tabs.statistics_tab import StatisticsTab
        tab = StatisticsTab(self)
        self.statistics_tab = tab
        self.tab_widget.addTab(tab, "统计信息")

    def create_theme_tab(self):
        """创建 Theme/外观配置标签页"""
        from .tabs.theme_tab import ThemeTab
        tab = ThemeTab(self)
        self.theme_tab = tab
        self.tab_widget.addTab(tab, "主题外观")

    def create_hooks_tab(self):
        """创建 Hooks 配置标签页"""
        from .tabs.hooks_tab import HooksTab
        tab = HooksTab(self)
        self.hooks_tab = tab
        self.tab_widget.addTab(tab, "Hooks 配置")

    def create_memory_tab(self):
        """创建 Memory 系统配置标签页"""
        from .tabs.memory_tab import MemoryTab
        tab = MemoryTab(self)
        self.memory_tab = tab
        self.tab_widget.addTab(tab, "Memory 系统")

    def create_uiux_tab(self):
        """创建 UI/UX 配置标签页"""
        from .tabs.uiux_tab import UIUXTab
        tab = UIUXTab(self)
        self.uiux_tab = tab
        self.tab_widget.addTab(tab, "UI/UX 设置")

    def create_developer_tools_tab(self):
        """创建 Developer Tools 标签页"""
        from .tabs.developer_tools_tab import DeveloperToolsTab
        tab = DeveloperToolsTab(self)
        self.developer_tools_tab = tab
        self.tab_widget.addTab(tab, "开发者工具")

    def create_integration_tab(self):
        """创建 Integration Settings 标签页"""
        from .tabs.integration_tab import IntegrationTab
        tab = IntegrationTab(self)
        self.integration_tab = tab
        self.tab_widget.addTab(tab, "集成设置")

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

            # 更新所有视图
            self.general_settings_tab.load_data(self.config_data)
            self.raw_config_tab.load_data(self.config_data)
            self.mcp_servers_tab.load_data(self.config_data)
            self.projects_tab.load_data(self.config_data)
            self.user_info_tab.load_data(self.config_data)
            self.experimental_features_tab.load_data(self.config_data)
            self.skills_tab.load_data(self.config_data)
            self.model_config_tab.load_data(self.config_data)
            self.permissions_tab.load_data(self.config_data)
            self.statistics_tab.load_data(self.config_data)
            self.theme_tab.load_data(self.config_data)
            self.hooks_tab.load_data(self.config_data)
            self.memory_tab.load_data(self.config_data)
            self.uiux_tab.load_data(self.config_data)
            self.developer_tools_tab.load_data(self.config_data)
            self.integration_tab.load_data(self.config_data)

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
        self.general_settings_tab.load_data(self.config_data)
        self.raw_config_tab.load_data(self.config_data)
        self.mcp_servers_tab.load_data(self.config_data)
        self.projects_tab.load_data(self.config_data)
        self.user_info_tab.load_data(self.config_data)
        self.experimental_features_tab.load_data(self.config_data)
        self.skills_tab.load_data(self.config_data)
        self.model_config_tab.load_data(self.config_data)
        self.permissions_tab.load_data(self.config_data)
        self.statistics_tab.load_data(self.config_data)
        self.theme_tab.load_data(self.config_data)
        self.hooks_tab.load_data(self.config_data)
        self.memory_tab.load_data(self.config_data)
        self.uiux_tab.load_data(self.config_data)
        self.developer_tools_tab.load_data(self.config_data)
        self.integration_tab.load_data(self.config_data)

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
