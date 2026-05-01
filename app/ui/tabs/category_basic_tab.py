"""
基础配置分类标签页 - 包含通用设置
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout

from .general_settings_tab import GeneralSettingsTab


class BasicCategoryTab(QWidget):
    """基础配置分类标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.general_settings = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.general_settings = GeneralSettingsTab(self.parent_window)
        layout.addWidget(self.general_settings)

    def load_data(self, config_data):
        self.general_settings.load_data(config_data)
