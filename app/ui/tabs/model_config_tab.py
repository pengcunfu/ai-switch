"""
Model 配置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
    QLabel, QPushButton, QMessageBox, QCheckBox, QSlider
)
from PySide6.QtCore import Qt


class ModelConfigTab(QWidget):
    """Model 配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # === Model 选择组 ===
        model_group = QGroupBox("Model 选择")
        model_layout = QFormLayout(model_group)

        # 默认模型选择
        self.default_model_combo = QComboBox()
        self.default_model_combo.addItem("Claude Sonnet 4.6 (推荐)", "claude-sonnet-4-6")
        self.default_model_combo.addItem("Claude Opus 4.7", "claude-opus-4-7")
        self.default_model_combo.addItem("Claude Haiku 4.5", "claude-haiku-4-5-20251001")
        model_layout.addRow("默认模型:", self.default_model_combo)

        # Fast 模式模型
        self.fast_model_combo = QComboBox()
        self.fast_model_combo.addItem("Claude Sonnet 4.6", "claude-sonnet-4-6")
        self.fast_model_combo.addItem("Claude Haiku 4.5", "claude-haiku-4-5-20251001")
        self.fast_model_combo.addItem("Claude Opus 4.6", "claude-opus-4-6")
        model_layout.addRow("Fast 模式模型:", self.fast_model_combo)

        layout.addWidget(model_group)

        # === 模型参数组 ===
        params_group = QGroupBox("模型参数")
        params_layout = QFormLayout(params_group)

        # Temperature
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 1.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setValue(0.7)
        self.temperature_spin.setToolTip("控制输出的随机性，值越高越随机")
        params_layout.addRow("Temperature:", self.temperature_spin)

        # Max Tokens
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 200000)
        self.max_tokens_spin.setValue(8192)
        self.max_tokens_spin.setToolTip("最大生成 token 数")
        params_layout.addRow("Max Tokens:", self.max_tokens_spin)

        # Top P
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.1)
        self.top_p_spin.setValue(1.0)
        self.top_p_spin.setToolTip("核采样参数")
        params_layout.addRow("Top P:", self.top_p_spin)

        layout.addWidget(params_group)

        # === 上下文配置组 ===
        context_group = QGroupBox("上下文配置")
        context_layout = QFormLayout(context_group)

        # 上下文窗口大小
        self.context_window_spin = QSpinBox()
        self.context_window_spin.setRange(1000, 200000)
        self.context_window_spin.setValue(200000)
        self.context_window_spin.setToolTip("模型上下文窗口大小")
        context_layout.addRow("上下文窗口大小:", self.context_window_spin)

        # 启用 Thinking
        self.thinking_checkbox = QCheckBox("启用 Thinking 模式")
        self.thinking_checkbox.setToolTip("启用模型思考过程显示")
        context_layout.addRow(self.thinking_checkbox)

        # 启用 Compaction
        self.compaction_checkbox = QCheckBox("启用上下文压缩")
        self.compaction_checkbox.setToolTip("在上下文接近限制时自动压缩历史消息")
        context_layout.addRow(self.compaction_checkbox)

        layout.addWidget(context_group)

        # === 高级配置组 ===
        advanced_group = QGroupBox("高级配置")
        advanced_layout = QFormLayout(advanced_group)

        # Prompt Caching
        self.prompt_caching_checkbox = QCheckBox("启用提示缓存")
        self.prompt_caching_checkbox.setToolTip("缓存重复的提示内容以降低成本")
        self.prompt_caching_checkbox.setChecked(True)
        advanced_layout.addRow(self.prompt_caching_checkbox)

        # 流式输出
        self.stream_checkbox = QCheckBox("启用流式输出")
        self.stream_checkbox.setToolTip("实时显示生成内容")
        self.stream_checkbox.setChecked(True)
        advanced_layout.addRow(self.stream_checkbox)

        layout.addWidget(advanced_group)

        # === 模型限制组 ===
        limits_group = QGroupBox("使用限制")
        limits_layout = QFormLayout(limits_group)

        # 每日最大请求数
        self.daily_requests_spin = QSpinBox()
        self.daily_requests_spin.setRange(0, 10000)
        self.daily_requests_spin.setValue(0)
        self.daily_requests_spin.setToolTip("0 表示无限制")
        limits_layout.addRow("每日最大请求数:", self.daily_requests_spin)

        # 单次最大成本 (USD)
        self.max_cost_spin = QDoubleSpinBox()
        self.max_cost_spin.setRange(0.0, 1000.0)
        self.max_cost_spin.setSingleStep(0.1)
        self.max_cost_spin.setValue(0.0)
        self.max_cost_spin.setToolTip("0 表示无限制")
        limits_layout.addRow("单次最大成本 (USD):", self.max_cost_spin)

        layout.addWidget(limits_group)

        layout.addStretch()

        # 保存按钮
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        reset_btn = QPushButton("重置默认")
        save_btn.clicked.connect(self.save_settings)
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def load_data(self, config_data):
        """加载数据"""
        # Model 选择
        model_config = config_data.get("modelConfiguration", {})

        default_model = model_config.get("defaultModel", "claude-sonnet-4-6")
        for i in range(self.default_model_combo.count()):
            if self.default_model_combo.itemData(i) == default_model:
                self.default_model_combo.setCurrentIndex(i)
                break

        fast_model = model_config.get("fastModel", "claude-sonnet-4-6")
        for i in range(self.fast_model_combo.count()):
            if self.fast_model_combo.itemData(i) == fast_model:
                self.fast_model_combo.setCurrentIndex(i)
                break

        # 模型参数
        self.temperature_spin.setValue(model_config.get("temperature", 0.7))
        self.max_tokens_spin.setValue(model_config.get("maxTokens", 8192))
        self.top_p_spin.setValue(model_config.get("topP", 1.0))

        # 上下文配置
        context_config = config_data.get("contextConfiguration", {})
        self.context_window_spin.setValue(context_config.get("contextWindowSize", 200000))
        self.thinking_checkbox.setChecked(context_config.get("thinkingEnabled", False))
        self.compaction_checkbox.setChecked(context_config.get("compactionEnabled", False))

        # 高级配置
        self.prompt_caching_checkbox.setChecked(config_data.get("promptCachingEnabled", True))
        self.stream_checkbox.setChecked(config_data.get("streamEnabled", True))

        # 使用限制
        limits = config_data.get("usageLimits", {})
        self.daily_requests_spin.setValue(limits.get("dailyMaxRequests", 0))
        self.max_cost_spin.setValue(limits.get("maxCostPerRequest", 0.0))

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            # Model 配置
            if "modelConfiguration" not in config_data:
                config_data["modelConfiguration"] = {}

            config_data["modelConfiguration"]["defaultModel"] = self.default_model_combo.currentData()
            config_data["modelConfiguration"]["fastModel"] = self.fast_model_combo.currentData()
            config_data["modelConfiguration"]["temperature"] = self.temperature_spin.value()
            config_data["modelConfiguration"]["maxTokens"] = self.max_tokens_spin.value()
            config_data["modelConfiguration"]["topP"] = self.top_p_spin.value()

            # 上下文配置
            if "contextConfiguration" not in config_data:
                config_data["contextConfiguration"] = {}

            config_data["contextConfiguration"]["contextWindowSize"] = self.context_window_spin.value()
            config_data["contextConfiguration"]["thinkingEnabled"] = self.thinking_checkbox.isChecked()
            config_data["contextConfiguration"]["compactionEnabled"] = self.compaction_checkbox.isChecked()

            # 高级配置
            config_data["promptCachingEnabled"] = self.prompt_caching_checkbox.isChecked()
            config_data["streamEnabled"] = self.stream_checkbox.isChecked()

            # 使用限制
            if "usageLimits" not in config_data:
                config_data["usageLimits"] = {}

            config_data["usageLimits"]["dailyMaxRequests"] = self.daily_requests_spin.value()
            config_data["usageLimits"]["maxCostPerRequest"] = self.max_cost_spin.value()

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "Model 配置已保存!")
            self.parent_window.statusBar().showMessage("Model 配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def reset_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置为默认值吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 重置为默认值
            self.temperature_spin.setValue(0.7)
            self.max_tokens_spin.setValue(8192)
            self.top_p_spin.setValue(1.0)
            self.context_window_spin.setValue(200000)
            self.thinking_checkbox.setChecked(False)
            self.compaction_checkbox.setChecked(False)
            self.prompt_caching_checkbox.setChecked(True)
            self.stream_checkbox.setChecked(True)
            self.daily_requests_spin.setValue(0)
            self.max_cost_spin.setValue(0.0)
