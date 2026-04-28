"""
Theme/外观配置标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QComboBox, QLabel, QPushButton, QMessageBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QColorDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ThemeTab(QWidget):
    """Theme/外观配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # === 主题选择组 ===
        theme_group = QGroupBox("主题设置")
        theme_layout = QFormLayout(theme_group)

        # 主题模式
        self.theme_mode_combo = QComboBox()
        self.theme_mode_combo.addItem("跟随系统", "system")
        self.theme_mode_combo.addItem("浅色主题", "light")
        self.theme_mode_combo.addItem("深色主题", "dark")
        theme_layout.addRow("主题模式:", self.theme_mode_combo)

        # 配色方案
        self.color_scheme_combo = QComboBox()
        self.color_scheme_combo.addItem("默认", "default")
        self.color_scheme_combo.addItem("蓝色", "blue")
        self.color_scheme_combo.addItem("绿色", "green")
        self.color_scheme_combo.addItem("紫色", "purple")
        self.color_scheme_combo.addItem("自定义", "custom")
        theme_layout.addRow("配色方案:", self.color_scheme_combo)

        layout.addWidget(theme_group)

        # === 字体设置组 ===
        font_group = QGroupBox("字体设置")
        font_layout = QFormLayout(font_group)

        # 界面字体
        self.ui_font_combo = QComboBox()
        self.ui_font_combo.addItem("默认", "default")
        self.ui_font_combo.addItem("微软雅黑", "microsoft_yahei")
        self.ui_font_combo.addItem("宋体", "simsun")
        self.ui_font_combo.addItem("黑体", "simhei")
        self.ui_font_combo.addItem("Arial", "arial")
        font_layout.addRow("界面字体:", self.ui_font_combo)

        # 代码字体
        self.code_font_combo = QComboBox()
        self.code_font_combo.addItem("Consolas", "consolas")
        self.code_font_combo.addItem("Courier New", "courier_new")
        self.code_font_combo.addItem("Monaco", "monaco")
        self.code_font_combo.addItem("默认", "default")
        font_layout.addRow("代码字体:", self.code_font_combo)

        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_layout.addRow("基础字体大小:", self.font_size_spin)

        # 代码字体大小
        self.code_font_size_spin = QSpinBox()
        self.code_font_size_spin.setRange(8, 24)
        self.code_font_size_spin.setValue(11)
        font_layout.addRow("代码字体大小:", self.code_font_size_spin)

        layout.addWidget(font_group)

        # === 自定义颜色组 ===
        custom_color_group = QGroupBox("自定义颜色")
        custom_color_layout = QFormLayout(custom_color_group)

        # 主要颜色
        self.primary_color_label = QLabel("#0066cc")
        self.primary_color_label.setStyleSheet("background-color: #0066cc; color: white; padding: 5px;")
        primary_color_btn = QPushButton("选择...")
        primary_color_btn.clicked.connect(lambda: self.choose_color("primary"))
        primary_color_layout = QHBoxLayout()
        primary_color_layout.addWidget(self.primary_color_label)
        primary_color_layout.addWidget(primary_color_btn)
        custom_color_layout.addRow("主要颜色:", primary_color_layout)

        # 强调颜色
        self.accent_color_label = QLabel("#0099ff")
        self.accent_color_label.setStyleSheet("background-color: #0099ff; color: white; padding: 5px;")
        accent_color_btn = QPushButton("选择...")
        accent_color_btn.clicked.connect(lambda: self.choose_color("accent"))
        accent_color_layout = QHBoxLayout()
        accent_color_layout.addWidget(self.accent_color_label)
        accent_color_layout.addWidget(accent_color_btn)
        custom_color_layout.addRow("强调颜色:", accent_color_layout)

        # 背景颜色
        self.bg_color_label = QLabel("#ffffff")
        self.bg_color_label.setStyleSheet("background-color: #ffffff; color: black; padding: 5px;")
        bg_color_btn = QPushButton("选择...")
        bg_color_btn.clicked.connect(lambda: self.choose_color("background"))
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(self.bg_color_label)
        bg_color_layout.addWidget(bg_color_btn)
        custom_color_layout.addRow("背景颜色:", bg_color_layout)

        # 文本颜色
        self.text_color_label = QLabel("#333333")
        self.text_color_label.setStyleSheet("background-color: #333333; color: white; padding: 5px;")
        text_color_btn = QPushButton("选择...")
        text_color_btn.clicked.connect(lambda: self.choose_color("text"))
        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(self.text_color_label)
        text_color_layout.addWidget(text_color_btn)
        custom_color_layout.addRow("文本颜色:", text_color_layout)

        layout.addWidget(custom_color_group)

        # === 高亮设置组 ===
        highlight_group = QGroupBox("代码高亮设置")
        highlight_layout = QFormLayout(highlight_group)

        # 启用语法高亮
        self.syntax_highlight_checkbox = QCheckBox("启用语法高亮")
        self.syntax_highlight_checkbox.setChecked(True)
        highlight_layout.addRow(self.syntax_highlight_checkbox)

        # JSON 高亮颜色预设
        self.json_highlight_preset_combo = QComboBox()
        self.json_highlight_preset_combo.addItem("默认 (VS Code)", "vscode")
        self.json_highlight_preset_combo.addItem("Monokai", "monokai")
        self.json_highlight_preset_combo.addItem("Solarized", "solarized")
        self.json_highlight_preset_combo.addItem("GitHub", "github")
        highlight_layout.addRow("JSON 高亮方案:", self.json_highlight_preset_combo)

        layout.addWidget(highlight_group)

        # === 界面布局组 ===
        layout_group = QGroupBox("界面布局")
        layout_form = QFormLayout(layout_group)

        # 窗口透明度
        self.window_opacity_spin = QDoubleSpinBox()
        self.window_opacity_spin.setRange(0.5, 1.0)
        self.window_opacity_spin.setSingleStep(0.05)
        self.window_opacity_spin.setValue(1.0)
        layout_form.addRow("窗口透明度:", self.window_opacity_spin)

        # 动画效果
        self.animation_checkbox = QCheckBox("启用界面动画")
        self.animation_checkbox.setChecked(True)
        layout_form.addRow(self.animation_checkbox)

        # 显示窗口阴影
        self.shadow_checkbox = QCheckBox("显示窗口阴影")
        self.shadow_checkbox.setChecked(True)
        layout_form.addRow(self.shadow_checkbox)

        layout.addWidget(layout_group)

        layout.addStretch()

        # 按钮栏
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存设置")
        preview_btn = QPushButton("预览效果")
        reset_btn = QPushButton("重置默认")
        save_btn.clicked.connect(self.save_settings)
        preview_btn.clicked.connect(self.preview_theme)
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addStretch()
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(preview_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)

    def choose_color(self, color_type):
        """选择颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            if color_type == "primary":
                self.primary_color_label.setText(color_hex)
                self.primary_color_label.setStyleSheet(f"background-color: {color_hex}; color: white; padding: 5px;")
            elif color_type == "accent":
                self.accent_color_label.setText(color_hex)
                self.accent_color_label.setStyleSheet(f"background-color: {color_hex}; color: white; padding: 5px;")
            elif color_type == "background":
                self.bg_color_label.setText(color_hex)
                self.bg_color_label.setStyleSheet(f"background-color: {color_hex}; color: black; padding: 5px;")
            elif color_type == "text":
                self.text_color_label.setText(color_hex)
                self.text_color_label.setStyleSheet(f"background-color: {color_hex}; color: white; padding: 5px;")

    def load_data(self, config_data):
        """加载数据"""
        theme_config = config_data.get("theme", {})

        # 主题设置
        theme_mode = theme_config.get("mode", "system")
        for i in range(self.theme_mode_combo.count()):
            if self.theme_mode_combo.itemData(i) == theme_mode:
                self.theme_mode_combo.setCurrentIndex(i)
                break

        color_scheme = theme_config.get("colorScheme", "default")
        for i in range(self.color_scheme_combo.count()):
            if self.color_scheme_combo.itemData(i) == color_scheme:
                self.color_scheme_combo.setCurrentIndex(i)
                break

        # 字体设置
        self.ui_font_combo.setCurrentText(theme_config.get("uiFont", "默认"))
        self.code_font_combo.setCurrentText(theme_config.get("codeFont", "Consolas"))
        self.font_size_spin.setValue(theme_config.get("fontSize", 12))
        self.code_font_size_spin.setValue(theme_config.get("codeFontSize", 11))

        # 自定义颜色
        custom_colors = theme_config.get("customColors", {})
        if custom_colors.get("primary"):
            self.primary_color_label.setText(custom_colors["primary"])
            self.primary_color_label.setStyleSheet(f"background-color: {custom_colors['primary']}; color: white; padding: 5px;")
        if custom_colors.get("accent"):
            self.accent_color_label.setText(custom_colors["accent"])
            self.accent_color_label.setStyleSheet(f"background-color: {custom_colors['accent']}; color: white; padding: 5px;")
        if custom_colors.get("background"):
            self.bg_color_label.setText(custom_colors["background"])
            self.bg_color_label.setStyleSheet(f"background-color: {custom_colors['background']}; color: black; padding: 5px;")
        if custom_colors.get("text"):
            self.text_color_label.setText(custom_colors["text"])
            self.text_color_label.setStyleSheet(f"background-color: {custom_colors['text']}; color: white; padding: 5px;")

        # 高亮设置
        self.syntax_highlight_checkbox.setChecked(theme_config.get("syntaxHighlight", True))
        json_preset = theme_config.get("jsonHighlightPreset", "vscode")
        for i in range(self.json_highlight_preset_combo.count()):
            if self.json_highlight_preset_combo.itemData(i) == json_preset:
                self.json_highlight_preset_combo.setCurrentIndex(i)
                break

        # 界面布局
        self.window_opacity_spin.setValue(theme_config.get("windowOpacity", 1.0))
        self.animation_checkbox.setChecked(theme_config.get("animationEnabled", True))
        self.shadow_checkbox.setChecked(theme_config.get("shadowEnabled", True))

    def save_settings(self):
        """保存设置"""
        try:
            config_data = self.parent_window.get_config_data()

            if "theme" not in config_data:
                config_data["theme"] = {}

            # 主题设置
            config_data["theme"]["mode"] = self.theme_mode_combo.currentData()
            config_data["theme"]["colorScheme"] = self.color_scheme_combo.currentData()

            # 字体设置
            config_data["theme"]["uiFont"] = self.ui_font_combo.currentText()
            config_data["theme"]["codeFont"] = self.code_font_combo.currentText()
            config_data["theme"]["fontSize"] = self.font_size_spin.value()
            config_data["theme"]["codeFontSize"] = self.code_font_size_spin.value()

            # 自定义颜色
            config_data["theme"]["customColors"] = {
                "primary": self.primary_color_label.text(),
                "accent": self.accent_color_label.text(),
                "background": self.bg_color_label.text(),
                "text": self.text_color_label.text()
            }

            # 高亮设置
            config_data["theme"]["syntaxHighlight"] = self.syntax_highlight_checkbox.isChecked()
            config_data["theme"]["jsonHighlightPreset"] = self.json_highlight_preset_combo.currentData()

            # 界面布局
            config_data["theme"]["windowOpacity"] = self.window_opacity_spin.value()
            config_data["theme"]["animationEnabled"] = self.animation_checkbox.isChecked()
            config_data["theme"]["shadowEnabled"] = self.shadow_checkbox.isChecked()

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            QMessageBox.information(self, "成功", "主题配置已保存! 部分设置可能需要重启应用后生效。")
            self.parent_window.statusBar().showMessage("主题配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def preview_theme(self):
        """预览主题效果"""
        QMessageBox.information(self, "预览", "主题预览功能开发中...\n请保存设置后查看效果。")

    def reset_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置为默认主题吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.theme_mode_combo.setCurrentIndex(0)
            self.color_scheme_combo.setCurrentIndex(0)
            self.ui_font_combo.setCurrentIndex(0)
            self.code_font_combo.setCurrentIndex(0)
            self.font_size_spin.setValue(12)
            self.code_font_size_spin.setValue(11)
            self.window_opacity_spin.setValue(1.0)
            self.syntax_highlight_checkbox.setChecked(True)
            self.animation_checkbox.setChecked(True)
            self.shadow_checkbox.setChecked(True)
