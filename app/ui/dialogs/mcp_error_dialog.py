"""
MCP 错误详情对话框
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QTextEdit, QGroupBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MCPErrorDialog(QDialog):
    """MCP 错误详情对话框"""

    def __init__(self, parent, error_message, server_config):
        super().__init__(parent)
        self.error_message = error_message
        self.server_config = server_config
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("MCP 连接错误详情")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout(self)

        # 错误摘要
        error_group = QGroupBox("错误摘要")
        error_layout = QVBoxLayout(error_group)

        error_label = QLabel(self.error_message)
        error_label.setWordWrap(True)
        error_label.setStyleSheet("color: red; font-weight: bold; padding: 10px; background: #fff5f5; border-radius: 5px;")
        error_layout.addWidget(error_label)

        layout.addWidget(error_group)

        # Tab 切换
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # 详细错误 Tab
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)

        detail_label = QLabel("详细错误信息:")
        detail_layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setFont(QFont("Consolas", 10))
        detail_layout.addWidget(self.detail_text)

        # 设置详细错误信息
        self.detail_text.append(self.error_message)

        tab_widget.addTab(detail_widget, "详细错误")

        # 配置信息 Tab
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)

        config_label = QLabel("服务器配置:")
        config_layout.addWidget(config_label)

        config_text = QTextEdit()
        config_text.setReadOnly(True)
        config_text.setFont(QFont("Consolas", 10))

        # 显示配置信息
        import json
        config_str = json.dumps(self.server_config, indent=2, ensure_ascii=False)
        config_text.append(config_str)

        config_layout.addWidget(config_text)
        tab_widget.addTab(config_widget, "服务器配置")

        # 建议解决方案 Tab
        solution_widget = QWidget()
        solution_layout = QVBoxLayout(solution_widget)

        solution_label = QLabel("可能的解决方案:")
        solution_layout.addWidget(solution_label)

        self.solution_text = QTextEdit()
        self.solution_text.setReadOnly(True)
        self.solution_text.setFont(QFont("Consolas", 10))

        # 根据错误类型提供解决方案
        solutions = self._get_solutions()
        self.solution_text.append(solutions)

        solution_layout.addWidget(self.solution_text)
        tab_widget.addTab(solution_widget, "解决方案")

        # 按钮
        button_layout = QHBoxLayout()
        copy_btn = QPushButton("复制错误信息")
        close_btn = QPushButton("关闭")
        copy_btn.clicked.connect(self.copy_error)
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(copy_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def _get_solutions(self):
        """根据错误类型提供解决方案"""
        solutions = "常见问题排查步骤:\n\n"

        # 检查命令是否存在
        command = self.server_config.get("command", "")
        if command and "找不到命令" in self.error_message:
            solutions += "1. 命令路径问题:\n"
            solutions += f"   - 检查命令是否正确: {command}\n"
            solutions += "   - 确认命令已安装并在系统 PATH 中\n"
            solutions += "   - 尝试使用完整路径\n\n"

        # 检查是否是超时错误
        if "超时" in self.error_message:
            solutions += "1. 连接超时问题:\n"
            solutions += "   - MCP 服务器可能启动缓慢\n"
            solutions += "   - 检查服务器配置是否正确\n"
            solutions += "   - 尝试手动启动服务器验证配置\n\n"

        # 检查是否是权限问题
        if "权限" in self.error_message:
            solutions += "1. 权限问题:\n"
            solutions += "   - 以管理员身份运行程序\n"
            solutions += "   - 检查文件/目录访问权限\n\n"

        # 通用解决方案
        solutions += "2. 通用排查步骤:\n"
        solutions += "   - 验证 MCP 服务器配置是否正确\n"
        solutions += "   - 检查环境变量设置\n"
        solutions += "   - 查看服务器日志获取详细错误信息\n"
        solutions += "   - 确认 MCP SDK 版本兼容性\n\n"

        solutions += "3. 测试命令:\n"
        if command:
            args = self.server_config.get("args", [])
            test_cmd = f"{command} {' '.join(args)}"
            solutions += f"   手动运行: {test_cmd}\n"
            solutions += "   查看是否能正常启动\n\n"

        return solutions

    def copy_error(self):
        """复制错误信息到剪贴板"""
        from PySide6.QtGui import QClipboard
        clipboard = self.clipboard()
        clipboard.setText(self.error_message)
        QMessageBox.information(self, "复制成功", "错误信息已复制到剪贴板")
