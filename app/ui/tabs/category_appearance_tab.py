"""
外观与界面分类标签页 - 包含主题外观、UI/UX 设置
"""
from .base_category_tab import BaseCategoryTab


class AppearanceCategoryTab(BaseCategoryTab):
    """外观与界面分类标签页"""

    def create_sub_tabs(self):
        """创建子标签页"""
        # 主题外观
        from .theme_tab import ThemeTab
        self.add_sub_tab(ThemeTab, "主题外观", "theme")

        # UI/UX 设置
        from .uiux_tab import UIUXTab
        self.add_sub_tab(UIUXTab, "UI/UX 设置", "uiux")
