"""
MCP 工具列表对话框
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QLabel, QGroupBox, QTextEdit, QHeaderView,
    QAbstractItemView, QProgressBar, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal


class MCPWorkerThread(QThread):
    """MCP 工作线程，用于异步执行 MCP 操作"""

    # 定义信号
    tools_loaded = Signal(list, list)  # tools, resources
    connection_failed = Signal(str)
    progress_updated = Signal(str)

    def __init__(self, server_config):
        super().__init__()
        self.server_config = server_config
        self.loop = None
        self.session = None

    def run(self):
        """在后台线程中运行 MCP 操作"""
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # 在事件循环中执行异步操作
            tools, resources = self.loop.run_until_complete(self._load_mcp_tools())

            if tools is not None:
                self.tools_loaded.emit(tools, resources)
            else:
                self.connection_failed.emit("无法加载工具列表")

        except Exception as e:
            self.connection_failed.emit(str(e))
        finally:
            if self.loop:
                self.loop.close()

    async def _load_mcp_tools(self):
        """使用 MCP SDK 加载工具列表"""
        try:
            command = self.server_config.get("command", "")
            args = self.server_config.get("args", [])
            env = self.server_config.get("env", {})

            if not command:
                return None, None

            # 创建服务器参数
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env
            )

            self.progress_updated.emit("正在连接到 MCP 服务器...")

            # 使用 MCP SDK 连接服务器，添加超时处理
            try:
                async with asyncio.timeout(10.0):  # 10秒超时
                    async with stdio_client(server_params) as (read, write):
                        async with ClientSession(read, write) as session:
                            self.progress_updated.emit("正在初始化连接...")

                            # 初始化连接，添加详细错误处理
                            try:
                                init_result = await session.initialize()
                                self.progress_updated.emit("初始化成功")
                            except Exception as init_error:
                                raise Exception(f"初始化失败: {str(init_error)}")

                            self.progress_updated.emit("正在加载工具列表...")

                            # 获取工具列表
                            try:
                                tools_result = await session.list_tools()
                                tools = tools_result.tools if tools_result else []
                            except Exception as tools_error:
                                # 即使工具列表获取失败，也尝试继续
                                tools = []
                                self.progress_updated.emit(f"工具列表获取失败，继续加载资源: {str(tools_error)}")

                            self.progress_updated.emit("正在加载资源列表...")

                            # 获取资源列表
                            try:
                                resources_result = await session.list_resources()
                                resources = resources_result.resources if resources_result else []
                            except Exception as resources_error:
                                # 即使资源列表获取失败，也返回已有的工具
                                resources = []
                                self.progress_updated.emit(f"资源列表获取失败: {str(resources_error)}")

                            return tools, resources

            except asyncio.TimeoutError:
                raise Exception("连接超时 (10秒)。MCP 服务器可能启动缓慢或无响应。")
            except Exception as client_error:
                raise Exception(f"MCP 客户端错误: {str(client_error)}")

        except FileNotFoundError:
            raise Exception(f"找不到命令: {command}")
        except PermissionError:
            raise Exception(f"权限不足，无法执行命令: {command}")
        except Exception as e:
            # 提供更详细的错误信息
            import traceback
            error_details = f"{str(e)}\n\n详细错误:\n{traceback.format_exc()}"
            raise Exception(f"MCP 通信失败: {error_details}")


class MCPToolsDialog(QDialog):
    """MCP 工具列表对话框"""

    def __init__(self, parent, server_name, server_config):
        super().__init__(parent)
        self.server_name = server_name
        self.server_config = server_config
        self.worker_thread = None
        self.progress_dialog = None
        self.init_ui()
        self.load_tools()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"MCP 工具列表 - {self.server_name}")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        layout = QVBoxLayout(self)

        # 服务器信息
        info_group = QGroupBox("服务器信息")
        info_layout = QVBoxLayout(info_group)

        command = self.server_config.get("command", "")
        args = self.server_config.get("args", [])
        info_text = f"命令: {command}\n参数: {' '.join(args)}"

        info_label = QLabel(info_text)
        info_label.setStyleSheet("background: #f5f5f5; padding: 10px; border-radius: 5px;")
        info_layout.addWidget(info_label)

        layout.addWidget(info_group)

        # 工具列表
        tools_group = QGroupBox("可用工具")
        tools_layout = QVBoxLayout(tools_group)

        # 加载进度
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("正在加载工具列表...")
        self.progress_bar.setRange(0, 0)  # 不确定进度
        tools_layout.addWidget(self.progress_bar)

        # 工具表格
        self.tools_table = QTableWidget()
        self.tools_table.setColumnCount(4)
        self.tools_table.setHorizontalHeaderLabels(["工具名称", "描述", "输入架构", "是否异步"])
        self.tools_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tools_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tools_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tools_layout.addWidget(self.tools_table)

        layout.addWidget(tools_group)

        # 资源列表
        resources_group = QGroupBox("可用资源")
        resources_layout = QVBoxLayout(resources_group)

        self.resources_table = QTableWidget()
        self.resources_table.setColumnCount(3)
        self.resources_table.setHorizontalHeaderLabels(["资源名称", "URI", "描述"])
        self.resources_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.resources_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.resources_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        resources_layout.addWidget(self.resources_table)

        layout.addWidget(resources_group)

        # 详细信息
        detail_group = QGroupBox("详细信息")
        detail_layout = QVBoxLayout(detail_group)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(150)
        detail_layout.addWidget(self.detail_text)

        layout.addWidget(detail_group)

        # 按钮
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新")
        close_btn = QPushButton("关闭")
        refresh_btn.clicked.connect(self.load_tools)
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # 连接表格选择事件
        self.tools_table.itemSelectionChanged.connect(self.on_tool_selected)
        self.resources_table.itemSelectionChanged.connect(self.on_resource_selected)

    def load_tools(self):
        """加载工具列表"""
        self.tools_table.setRowCount(0)
        self.resources_table.setRowCount(0)
        self.detail_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("正在初始化...")
        self.progress_bar.setRange(0, 0)  # 不确定进度

        # 创建并启动工作线程
        self.worker_thread = MCPWorkerThread(self.server_config)
        self.worker_thread.tools_loaded.connect(self.on_tools_loaded)
        self.worker_thread.connection_failed.connect(self.on_connection_failed)
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.start()

    def on_progress_updated(self, message):
        """进度更新"""
        self.progress_bar.setFormat(message)

    def on_tools_loaded(self, tools, resources):
        """工具加载成功"""
        try:
            # 填充工具表格
            for tool in tools:
                row = self.tools_table.rowCount()
                self.tools_table.insertRow(row)

                self.tools_table.setItem(row, 0, QTableWidgetItem(tool.name))
                self.tools_table.setItem(row, 1, QTableWidgetItem(tool.description or ""))

                # 输入架构
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    schema_str = str(tool.inputSchema)[:100] + "..." if len(str(tool.inputSchema)) > 100 else str(tool.inputSchema)
                else:
                    schema_str = "无"
                self.tools_table.setItem(row, 2, QTableWidgetItem(schema_str))

            # 填充资源表格
            for resource in resources:
                row = self.resources_table.rowCount()
                self.resources_table.insertRow(row)

                self.resources_table.setItem(row, 0, QTableWidgetItem(resource.name))
                self.resources_table.setItem(row, 1, QTableWidgetItem(resource.uri))
                self.resources_table.setItem(row, 2, QTableWidgetItem(resource.description or ""))

            self.detail_text.append(f"成功加载 {len(tools)} 个工具和 {len(resources)} 个资源")
            self.progress_bar.setFormat(f"加载完成 - {len(tools)} 个工具, {len(resources)} 个资源")

        except Exception as e:
            QMessageBox.warning(self, "警告", f"解析工具列表时发生错误:\n{str(e)}")
        finally:
            self.progress_bar.setVisible(False)

    def on_connection_failed(self, error_message):
        """连接失败"""
        # 显示详细错误对话框
        from .mcp_error_dialog import MCPErrorDialog
        error_dialog = MCPErrorDialog(self, error_message, self.server_config)
        error_dialog.exec()

        self.detail_text.append(f"连接失败: {error_message}")
        self.progress_bar.setVisible(False)

    def on_tool_selected(self):
        """工具选择改变"""
        selected_items = self.tools_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        tool_name = self.tools_table.item(row, 0).text()
        description = self.tools_table.item(row, 1).text()

        detail = f"工具名称: {tool_name}\n"
        detail += f"描述: {description}\n"

        self.detail_text.clear()
        self.detail_text.append(detail)

    def on_resource_selected(self):
        """资源选择改变"""
        selected_items = self.resources_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        resource_name = self.resources_table.item(row, 0).text()
        uri = self.resources_table.item(row, 1).text()
        description = self.resources_table.item(row, 2).text()

        detail = f"资源名称: {resource_name}\n"
        detail += f"URI: {uri}\n"
        detail += f"描述: {description}\n"

        self.detail_text.clear()
        self.detail_text.append(detail)

    def accept(self):
        """关闭对话框"""
        # 清理工作线程
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        super().accept()
