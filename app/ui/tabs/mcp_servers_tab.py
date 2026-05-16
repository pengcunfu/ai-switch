"""
MCP 服务器标签页
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt


class MCPServersTab(QWidget):
    """MCP 服务器标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        add_btn = QPushButton("添加服务器")
        edit_btn = QPushButton("编辑服务器")
        delete_btn = QPushButton("删除服务器")
        test_btn = QPushButton("测试连接")
        tools_btn = QPushButton("查看工具")

        add_btn.clicked.connect(self.add_server)
        edit_btn.clicked.connect(self.edit_server)
        delete_btn.clicked.connect(self.delete_server)
        test_btn.clicked.connect(self.test_connection)
        tools_btn.clicked.connect(self.view_tools)

        button_layout.addWidget(add_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(test_btn)
        button_layout.addWidget(tools_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["服务器名称", "命令", "参数", "环境变量", "状态"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemDoubleClicked.connect(self.edit_server)
        layout.addWidget(self.table)

    def load_data(self, config_data):
        """加载数据"""
        mcp_servers = config_data.get("mcpServers", {})

        self.table.setRowCount(0)
        for name, config in mcp_servers.items():
            row = self.table.rowCount()
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(config.get("command", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(config.get("args", []))))

            env = config.get("env", {})
            env_str = "; ".join([f"{k}={v}" for k, v in env.items()])
            self.table.setItem(row, 3, QTableWidgetItem(env_str))

            # 状态列 (默认显示未知状态)
            status_item = QTableWidgetItem("未测试")
            status_item.setForeground(Qt.GlobalColor.gray)
            self.table.setItem(row, 4, status_item)

    def add_server(self):
        """添加服务器"""
        from ..dialogs.mcp_server_dialog import MCPServerDialog
        dialog = MCPServerDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            config_data = self.parent_window.get_config_data()
            if "mcpServers" not in config_data:
                config_data["mcpServers"] = {}

            config_data["mcpServers"][server_data["name"]] = server_data["config"]

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已添加!")

    def edit_server(self):
        """编辑服务器"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        mcp_servers = config_data.get("mcpServers", {})
        if server_name not in mcp_servers:
            return

        server_config = mcp_servers[server_name]

        from ..dialogs.mcp_server_dialog import MCPServerDialog
        dialog = MCPServerDialog(self, server_name, server_config)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            server_data = dialog.get_server_data()

            # 如果名称改变,删除旧条目
            if server_data["name"] != server_name:
                del mcp_servers[server_name]

            mcp_servers[server_data["name"]] = server_data["config"]

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            QMessageBox.information(self, "成功", f"MCP服务器 '{server_data['name']}' 已更新!")

    def delete_server(self):
        """删除服务器"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除MCP服务器 '{server_name}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config_data = self.parent_window.get_config_data()
            mcp_servers = config_data.get("mcpServers", {})
            if server_name in mcp_servers:
                del mcp_servers[server_name]

                self.parent_window.set_config_data(config_data)
                self.parent_window.save_config_to_file()
                self.load_data(config_data)
                self.parent_window.raw_config_tab.load_data(config_data)

                QMessageBox.information(self, "成功", f"MCP服务器 '{server_name}' 已删除!")

    def test_connection(self):
        """测试 MCP 服务器连接"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        mcp_servers = config_data.get("mcpServers", {})
        if server_name not in mcp_servers:
            QMessageBox.warning(self, "警告", f"服务器 '{server_name}' 不存在")
            return

        server_config = mcp_servers[server_name]

        # 更新状态为测试中
        status_item = self.table.item(row, 4)
        status_item.setText("测试中...")
        status_item.setForeground(Qt.GlobalColor.blue)
        self.table.repaint()

        try:
            # 这里模拟测试连接的过程
            # 实际应该尝试启动 MCP 服务器并检查是否响应
            result = self._test_mcp_server(server_config)

            if result["success"]:
                status_item.setText("正常")
                status_item.setForeground(Qt.GlobalColor.green)
                QMessageBox.information(self, "连接测试", f"MCP服务器 '{server_name}' 连接正常!\n\n{result.get('message', '连接成功')}")
            else:
                status_item.setText("失败")
                status_item.setForeground(Qt.GlobalColor.red)

                # 显示详细错误对话框
                from ..dialogs.mcp_error_dialog import MCPErrorDialog
                error_dialog = MCPErrorDialog(self, result.get('error', '未知错误'), server_config)
                error_dialog.exec()

        except Exception as e:
            status_item.setText("错误")
            status_item.setForeground(Qt.GlobalColor.red)

            # 显示详细错误对话框
            from ..dialogs.mcp_error_dialog import MCPErrorDialog
            error_dialog = MCPErrorDialog(self, str(e), server_config)
            error_dialog.exec()

    def _test_mcp_server(self, server_config):
        """使用 MCP SDK 测试服务器连接"""
        async def test_connection():
            try:
                command = server_config.get("command", "")
                args = server_config.get("args", [])
                env = server_config.get("env", {})

                if not command:
                    return {"success": False, "error": "未配置命令"}

                # 创建服务器参数
                server_params = StdioServerParameters(
                    command=command,
                    args=args,
                    env=env
                )

                # 使用 MCP SDK 连接服务器，添加超时处理
                try:
                    async with asyncio.timeout(5.0):  # 5秒超时
                        async with stdio_client(server_params) as (read, write):
                            async with ClientSession(read, write) as session:
                                # 尝试初始化连接
                                try:
                                    init_result = await session.initialize()
                                    server_info = getattr(init_result, 'serverInfo', None)
                                    server_name = getattr(server_info, 'name', '未知') if server_info else '未知'
                                    server_version = getattr(server_info, 'version', '未知') if server_info else '未知'
                                    message = f"连接成功\n服务器: {server_name}\n版本: {server_version}"
                                    return {"success": True, "message": message}
                                except Exception as init_error:
                                    return {"success": False, "error": f"初始化失败: {str(init_error)}"}

                except asyncio.TimeoutError:
                    return {"success": False, "error": "连接超时 (5秒)。服务器可能启动缓慢或配置错误。"}
                except Exception as client_error:
                    return {"success": False, "error": f"MCP 客户端错误: {str(client_error)}"}

            except FileNotFoundError:
                return {"success": False, "error": f"找不到命令: {command}"}
            except PermissionError:
                return {"success": False, "error": f"权限不足，无法执行: {command}"}
            except Exception as e:
                return {"success": False, "error": str(e)}

        # 运行异步测试
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(test_connection())
                return result
            finally:
                # 确保清理所有待处理的任务
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                loop.close()
        except Exception as e:
            return {"success": False, "error": f"测试失败: {str(e)}"}

    def view_tools(self):
        """查看 MCP 服务器的工具"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个服务器")
            return

        row = selected_items[0].row()
        server_name = self.table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        mcp_servers = config_data.get("mcpServers", {})
        if server_name not in mcp_servers:
            QMessageBox.warning(self, "警告", f"服务器 '{server_name}' 不存在")
            return

        server_config = mcp_servers[server_name]

        # 显示工具列表对话框
        from ..dialogs.mcp_tools_dialog import MCPToolsDialog
        dialog = MCPToolsDialog(self, server_name, server_config)
        dialog.exec()
