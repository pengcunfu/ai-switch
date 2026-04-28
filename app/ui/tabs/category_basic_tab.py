"""
基础配置分类标签页 - 包含通用设置、用户信息
"""
from .base_category_tab import BaseCategoryTab


class BasicCategoryTab(BaseCategoryTab):
    """基础配置分类标签页"""

    def create_sub_tabs(self):
        """创建子标签页"""
        # 通用设置
        from .general_settings_tab import GeneralSettingsTab
        self.add_sub_tab(GeneralSettingsTab, "通用设置", "general")

        # 用户信息
        from .user_info_tab import UserInfoTab
        self.add_sub_tab(UserInfoTab, "用户信息", "user")
