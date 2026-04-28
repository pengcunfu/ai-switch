"""
集成与工具分类标签页 - 包含项目列表、集成设置、开发者工具、实验性功能
"""
from .base_category_tab import BaseCategoryTab


class IntegrationCategoryTab(BaseCategoryTab):
    """集成与工具分类标签页"""

    def create_sub_tabs(self):
        """创建子标签页"""
        # 项目列表
        from .projects_tab import ProjectsTab
        self.add_sub_tab(ProjectsTab, "项目列表", "projects")

        # 集成设置
        from .integration_tab import IntegrationTab
        self.add_sub_tab(IntegrationTab, "集成设置", "integration")

        # 开发者工具
        from .developer_tools_tab import DeveloperToolsTab
        self.add_sub_tab(DeveloperToolsTab, "开发者工具", "devtools")

        # 实验性功能
        from .experimental_features_tab import ExperimentalFeaturesTab
        self.add_sub_tab(ExperimentalFeaturesTab, "实验性功能", "experimental")
