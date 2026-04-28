"""
Skills 标签页 - 查看和管理 Claude Code Skills
"""
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter, QLabel, QComboBox, QTextEdit, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor


class SkillsTab(QWidget):
    """Skills 标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.skills_data = []  # [{name, description, scope, path, frontmatter, content}]
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 作用域选择
        scope_layout = QHBoxLayout()
        scope_label = QLabel("作用域:")
        self.scope_combo = QComboBox()
        self.scope_combo.addItem("全局 (~/.claude/skills/)", "global")
        self.scope_combo.addItem("项目 (.claude/skills/)", "project")
        self.scope_combo.currentIndexChanged.connect(self.on_scope_changed)
        scope_layout.addWidget(scope_label)
        scope_layout.addWidget(self.scope_combo)
        scope_layout.addStretch()
        layout.addLayout(scope_layout)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧: Skills 列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 按钮栏
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加 Skill")
        edit_btn = QPushButton("编辑 Skill")
        delete_btn = QPushButton("删除 Skill")
        refresh_btn = QPushButton("刷新")

        add_btn.clicked.connect(self.add_skill)
        edit_btn.clicked.connect(self.edit_skill)
        delete_btn.clicked.connect(self.delete_skill)
        refresh_btn.clicked.connect(self.refresh_skills)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        left_layout.addLayout(btn_layout)

        # Skills 表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["名称", "描述", "斜杠命令", "作用域"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.itemSelectionChanged.connect(self.on_skill_selected)
        self.table.itemDoubleClicked.connect(self.edit_skill)
        left_layout.addWidget(self.table)

        splitter.addWidget(left_widget)

        # 右侧: Skill 详情
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        detail_label = QLabel("Skill 详情:")
        right_layout.addWidget(detail_label)

        # Frontmatter 信息
        self.detail_group = QGroupBox("Frontmatter")
        detail_form = QFormLayout(self.detail_group)

        self.detail_name = QLabel()
        self.detail_description = QLabel()
        self.detail_description.setWordWrap(True)
        self.detail_context = QLabel()
        self.detail_agent = QLabel()
        self.detail_allowed_tools = QLabel()
        self.detail_allowed_tools.setWordWrap(True)
        self.detail_user_invocable = QLabel()
        self.detail_disable_model = QLabel()
        self.detail_path = QLabel()
        self.detail_path.setWordWrap(True)

        detail_form.addRow("名称:", self.detail_name)
        detail_form.addRow("描述:", self.detail_description)
        detail_form.addRow("Context:", self.detail_context)
        detail_form.addRow("Agent:", self.detail_agent)
        detail_form.addRow("允许工具:", self.detail_allowed_tools)
        detail_form.addRow("用户可调用:", self.detail_user_invocable)
        detail_form.addRow("禁用模型调用:", self.detail_disable_model)
        detail_form.addRow("路径:", self.detail_path)

        right_layout.addWidget(self.detail_group)

        # Skill 内容
        content_label = QLabel("Skill 内容:")
        right_layout.addWidget(content_label)

        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setFont(QFont("Consolas", 10))
        self.content_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        right_layout.addWidget(self.content_edit)

        splitter.addWidget(right_widget)

        # 设置分割比例
        splitter.setSizes([400, 500])

        layout.addWidget(splitter)

    def get_skills_base_dir(self):
        """获取当前作用域的 skills 目录"""
        scope = self.scope_combo.currentData()
        if scope == "global":
            return Path.home() / ".claude" / "skills"
        else:
            return Path.cwd() / ".claude" / "skills"

    def on_scope_changed(self):
        """作用域切换"""
        self.refresh_skills()

    def load_data(self, config_data):
        """加载数据 (从配置文件调用, 但 skills 数据来自文件系统)"""
        self.refresh_skills()

    def refresh_skills(self):
        """刷新 skills 列表"""
        self.skills_data = []
        self.table.setRowCount(0)

        skills_dir = self.get_skills_base_dir()
        if not skills_dir.exists():
            self._clear_detail()
            return

        # 扫描 skills 目录
        for item in sorted(skills_dir.iterdir()):
            if not item.is_dir():
                continue
            skill_md = item / "SKILL.md"
            if not skill_md.exists():
                continue

            skill_info = self._parse_skill(skill_md)
            if skill_info:
                self.skills_data.append(skill_info)

        # 填充表格
        scope = self.scope_combo.currentData()
        scope_label = "全局" if scope == "global" else "项目"
        for skill in self.skills_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(skill["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(skill["description"]))
            slash_cmd = f"/{skill['name']}" if skill.get("user_invocable", True) else "—"
            self.table.setItem(row, 2, QTableWidgetItem(slash_cmd))
            self.table.setItem(row, 3, QTableWidgetItem(scope_label))

        self._clear_detail()

    def _parse_skill(self, skill_md_path):
        """解析 SKILL.md 文件"""
        try:
            content = skill_md_path.read_text(encoding="utf-8")
        except Exception:
            return None

        frontmatter = {}
        body = content

        # 解析 YAML frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()
                for line in fm_text.split("\n"):
                    line = line.strip()
                    if not line or ":" not in line:
                        continue
                    key, _, value = line.partition(":")
                    key = key.strip()
                    value = value.strip()
                    # 处理布尔值
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False
                    frontmatter[key] = value

        name = frontmatter.get("name", skill_md_path.parent.name)
        description = frontmatter.get("description", "")

        return {
            "name": name,
            "description": description,
            "frontmatter": frontmatter,
            "content": body,
            "path": str(skill_md_path),
            "user_invocable": frontmatter.get("user-invocable", True),
            "context": frontmatter.get("context", ""),
            "agent": frontmatter.get("agent", ""),
            "allowed_tools": frontmatter.get("allowed-tools", ""),
            "disable_model_invocation": frontmatter.get("disable-model-invocation", False),
        }

    def on_skill_selected(self):
        """Skill 选择改变"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self._clear_detail()
            return

        row = selected_items[0].row()
        if row < len(self.skills_data):
            skill = self.skills_data[row]
            self._show_detail(skill)

    def _show_detail(self, skill):
        """显示 skill 详情"""
        self.detail_name.setText(skill["name"])
        self.detail_description.setText(skill["description"] or "—")
        self.detail_context.setText(skill.get("context") or "—")
        self.detail_agent.setText(skill.get("agent") or "—")
        self.detail_allowed_tools.setText(skill.get("allowed_tools") or "—")
        self.detail_user_invocable.setText("是" if skill.get("user_invocable", True) else "否")
        self.detail_disable_model.setText("是" if skill.get("disable_model_invocation", False) else "否")
        self.detail_path.setText(skill["path"])

        self.content_edit.setPlainText(skill["content"])

    def _clear_detail(self):
        """清空详情"""
        self.detail_name.setText("—")
        self.detail_description.setText("—")
        self.detail_context.setText("—")
        self.detail_agent.setText("—")
        self.detail_allowed_tools.setText("—")
        self.detail_user_invocable.setText("—")
        self.detail_disable_model.setText("—")
        self.detail_path.setText("—")
        self.content_edit.setPlainText("")

    def add_skill(self):
        """添加 Skill"""
        from ..dialogs.skill_dialog import SkillDialog
        dialog = SkillDialog(self, scope=self.scope_combo.currentData())
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            skill_data = dialog.get_skill_data()
            try:
                self._save_skill(skill_data)
                self.refresh_skills()
                QMessageBox.information(self, "成功", f"Skill '{skill_data['name']}' 已创建!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"创建 Skill 失败:\n{str(e)}")

    def edit_skill(self):
        """编辑 Skill"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个 Skill")
            return

        row = selected_items[0].row()
        if row >= len(self.skills_data):
            return

        skill = self.skills_data[row]

        from ..dialogs.skill_dialog import SkillDialog
        dialog = SkillDialog(self, skill_data=skill, scope=self.scope_combo.currentData())
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            new_data = dialog.get_skill_data()
            try:
                # 如果名称改变，删除旧目录
                old_name = Path(skill["path"]).parent.name
                new_name = new_data["name"]
                if old_name != new_name:
                    old_dir = Path(skill["path"]).parent
                    new_dir = old_dir.parent / new_name
                    if old_dir.exists():
                        old_dir.rename(new_dir)

                self._save_skill(new_data)
                self.refresh_skills()
                QMessageBox.information(self, "成功", f"Skill '{new_data['name']}' 已更新!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"更新 Skill 失败:\n{str(e)}")

    def delete_skill(self):
        """删除 Skill"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个 Skill")
            return

        row = selected_items[0].row()
        if row >= len(self.skills_data):
            return

        skill = self.skills_data[row]

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 Skill '{skill['name']}' 吗?\n这将删除整个 skill 目录。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                skill_dir = Path(skill["path"]).parent
                if skill_dir.exists():
                    shutil.rmtree(skill_dir)
                self.refresh_skills()
                QMessageBox.information(self, "成功", f"Skill '{skill['name']}' 已删除!")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除 Skill 失败:\n{str(e)}")

    def _save_skill(self, skill_data):
        """保存 skill 到文件"""
        skills_dir = self.get_skills_base_dir()
        skill_dir = skills_dir / skill_data["name"]
        skill_dir.mkdir(parents=True, exist_ok=True)

        skill_md = skill_dir / "SKILL.md"

        # 构建 frontmatter
        fm_lines = ["---"]
        fm_lines.append(f"name: {skill_data['name']}")
        if skill_data.get("description"):
            fm_lines.append(f"description: {skill_data['description']}")
        if skill_data.get("context"):
            fm_lines.append(f"context: {skill_data['context']}")
        if skill_data.get("agent"):
            fm_lines.append(f"agent: {skill_data['agent']}")
        if skill_data.get("allowed_tools"):
            fm_lines.append(f"allowed-tools: {skill_data['allowed_tools']}")
        if skill_data.get("user_invocable") is False:
            fm_lines.append("user-invocable: false")
        if skill_data.get("disable_model_invocation"):
            fm_lines.append("disable-model-invocation: true")
        if skill_data.get("argument_hint"):
            fm_lines.append(f"argument-hint: {skill_data['argument_hint']}")
        fm_lines.append("---")

        # 组合内容
        content = skill_data.get("content", "")
        full_content = "\n".join(fm_lines) + "\n" + content

        skill_md.write_text(full_content.strip() + "\n", encoding="utf-8")
