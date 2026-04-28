"""
功能配置分类标签页 - 包含 MCP 服务器、Skills、Hooks、Memory
"""
from .base_category_tab import BaseCategoryTab


class FeaturesCategoryTab(BaseCategoryTab):
    """功能配置分类标签页"""

    def create_sub_tabs(self):
        """创建子标签页"""
        # MCP 服务器
        from .mcp_servers_tab import MCPServersTab
        self.add_sub_tab(MCPServersTab, "MCP 服务器", "mcp")

        # Skills
        from .skills_tab import SkillsTab
        self.add_sub_tab(SkillsTab, "Skills", "skills")

        # Hooks 配置
        from .hooks_tab import HooksTab
        self.add_sub_tab(HooksTab, "Hooks 配置", "hooks")

        # Memory 系统
        from .memory_tab import MemoryTab
        self.add_sub_tab(MemoryTab, "Memory 系统", "memory")
