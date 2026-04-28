"""
模型与权限分类标签页 - 包含 Model 配置、权限管理
"""
from .base_category_tab import BaseCategoryTab


class ModelPermissionsCategoryTab(BaseCategoryTab):
    """模型与权限分类标签页"""

    def create_sub_tabs(self):
        """创建子标签页"""
        # Model 配置
        from .model_config_tab import ModelConfigTab
        self.add_sub_tab(ModelConfigTab, "Model 配置", "model")

        # 权限管理
        from .permissions_tab import PermissionsTab
        self.add_sub_tab(PermissionsTab, "权限管理", "permissions")
