"""
基础分类标签页模板
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget


class BaseCategoryTab(QWidget):
    """基础分类标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.sub_tabs = {}
        self.init_ui()

    def init_ui(self):
        """初始化UI - 子类需要实现"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建子标签页
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # 子类需要调用 create_sub_tabs 来添加子标签页
        self.create_sub_tabs()

    def create_sub_tabs(self):
        """创建子标签页 - 子类需要实现"""
        pass

    def add_sub_tab(self, tab_class, tab_name, tab_key):
        """添加子标签页"""
        tab = tab_class(self.parent_window)
        self.tab_widget.addTab(tab, tab_name)
        self.sub_tabs[tab_key] = tab
        return tab

    def load_data(self, config_data):
        """加载数据到所有子标签页"""
        for tab in self.sub_tabs.values():
            if hasattr(tab, 'load_data'):
                tab.load_data(config_data)
