"""
项目列表标签页
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QAbstractItemView,
    QSplitter, QLabel, QFileDialog, QGroupBox, QSizePolicy
)
from PySide6.QtCore import Qt


class ProjectsTab(QWidget):
    """项目列表标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self._selected_repo = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        hint = QLabel("将 GitHub 仓库映射到本地项目路径，便于 Claude 识别工作区。")
        hint.setWordWrap(True)
        hint.setStyleSheet("color: palette(mid);")
        layout.addWidget(hint)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # 左侧: 仓库列表
        repo_group = QGroupBox("仓库列表")
        repo_layout = QVBoxLayout(repo_group)
        repo_layout.setSpacing(6)

        repo_btn_layout = QHBoxLayout()
        add_repo_btn = QPushButton("添加仓库")
        delete_repo_btn = QPushButton("删除仓库")
        add_repo_btn.clicked.connect(self.add_repo)
        delete_repo_btn.clicked.connect(self.delete_repo)
        repo_btn_layout.addWidget(add_repo_btn)
        repo_btn_layout.addWidget(delete_repo_btn)
        repo_btn_layout.addStretch()
        repo_layout.addLayout(repo_btn_layout)

        self.repo_table = QTableWidget()
        self.repo_table.setColumnCount(2)
        self.repo_table.setHorizontalHeaderLabels(["仓库", "路径数"])
        self.repo_table.verticalHeader().setVisible(False)
        self.repo_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.repo_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.repo_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.repo_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.repo_table.setAlternatingRowColors(True)
        self.repo_table.itemSelectionChanged.connect(self.on_repo_selected)
        repo_layout.addWidget(self.repo_table)

        repo_group.setMinimumWidth(280)
        splitter.addWidget(repo_group)

        # 右侧: 路径详情
        self.path_group = QGroupBox("本地路径")
        path_layout = QVBoxLayout(self.path_group)
        path_layout.setSpacing(6)

        path_btn_layout = QHBoxLayout()
        self.add_path_btn = QPushButton("添加路径")
        self.remove_path_btn = QPushButton("删除路径")
        self.add_path_btn.clicked.connect(self.add_path)
        self.remove_path_btn.clicked.connect(self.remove_path)
        path_btn_layout.addWidget(self.add_path_btn)
        path_btn_layout.addWidget(self.remove_path_btn)
        path_btn_layout.addStretch()
        path_layout.addLayout(path_btn_layout)

        self.path_placeholder = QLabel("请在左侧选择一个仓库")
        self.path_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.path_placeholder.setStyleSheet("color: palette(mid); padding: 24px;")
        self.path_placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.path_table = QTableWidget()
        self.path_table.setColumnCount(1)
        self.path_table.setHorizontalHeaderLabels(["路径"])
        self.path_table.verticalHeader().setVisible(False)
        self.path_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.path_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.path_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.path_table.setAlternatingRowColors(True)
        self.path_table.hide()

        path_layout.addWidget(self.path_placeholder)
        path_layout.addWidget(self.path_table)

        self.path_group.setMinimumWidth(360)
        splitter.addWidget(self.path_group)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        splitter.setSizes([320, 480])

        layout.addWidget(splitter, 1)
        self._update_path_panel_state()

    def _update_path_panel_state(self):
        """根据是否选中仓库更新右侧面板"""
        has_repo = bool(self._selected_repo)
        self.add_path_btn.setEnabled(has_repo)
        self.remove_path_btn.setEnabled(has_repo)
        self.path_table.setVisible(has_repo)
        self.path_placeholder.setVisible(not has_repo)
        if has_repo:
            self.path_group.setTitle(f"本地路径 — {self._selected_repo}")
        else:
            self.path_group.setTitle("本地路径")

    def load_data(self, config_data):
        """加载数据"""
        github_repos = config_data.get("githubRepoPaths", {})

        self.repo_table.setRowCount(0)
        for repo_name, paths in github_repos.items():
            row = self.repo_table.rowCount()
            self.repo_table.insertRow(row)

            self.repo_table.setItem(row, 0, QTableWidgetItem(repo_name))
            self.repo_table.setItem(row, 1, QTableWidgetItem(str(len(paths))))

        self._selected_repo = None
        self.path_table.setRowCount(0)
        self._update_path_panel_state()

        if self.repo_table.rowCount() > 0:
            self.repo_table.selectRow(0)

    def on_repo_selected(self):
        """仓库选择改变事件"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            self._selected_repo = None
            self.path_table.setRowCount(0)
            self._update_path_panel_state()
            return

        row = selected_items[0].row()
        self._selected_repo = self.repo_table.item(row, 0).text()

        config_data = self.parent_window.get_config_data()
        github_repos = config_data.get("githubRepoPaths", {})
        paths = github_repos.get(self._selected_repo, [])

        self.path_table.setRowCount(0)
        for path in paths:
            path_row = self.path_table.rowCount()
            self.path_table.insertRow(path_row)
            self.path_table.setItem(path_row, 0, QTableWidgetItem(path))

        self._update_path_panel_state()

    def add_repo(self):
        """添加仓库"""
        from ..dialogs.repo_dialog import RepoDialog
        dialog = RepoDialog(self)
        if dialog.exec() == QMessageBox.DialogCode.Accepted:
            repo_name = dialog.get_repo_name()

            config_data = self.parent_window.get_config_data()
            if "githubRepoPaths" not in config_data:
                config_data["githubRepoPaths"] = {}

            config_data["githubRepoPaths"][repo_name] = []

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()
            self.load_data(config_data)
            self.parent_window.raw_config_tab.load_data(config_data)

            for row in range(self.repo_table.rowCount()):
                if self.repo_table.item(row, 0).text() == repo_name:
                    self.repo_table.selectRow(row)
                    break

            QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已添加!")

    def delete_repo(self):
        """删除仓库"""
        selected_items = self.repo_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        row = selected_items[0].row()
        repo_name = self.repo_table.item(row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除仓库 '{repo_name}' 吗?\n这将删除该仓库的所有路径配置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if repo_name in github_repos:
                del github_repos[repo_name]

                self.parent_window.set_config_data(config_data)
                self.parent_window.save_config_to_file()
                self.load_data(config_data)
                self.parent_window.raw_config_tab.load_data(config_data)

                QMessageBox.information(self, "成功", f"仓库 '{repo_name}' 已删除!")

    def add_path(self):
        """添加路径"""
        if not self._selected_repo:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        folder_path = QFileDialog.getExistingDirectory(self, "选择项目文件夹")
        if folder_path:
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if self._selected_repo in github_repos:
                paths = github_repos[self._selected_repo]
                if folder_path not in paths:
                    paths.append(folder_path)

                    self.parent_window.set_config_data(config_data)
                    self.parent_window.save_config_to_file()
                    self.load_data(config_data)
                    self.on_repo_selected()
                    self.parent_window.raw_config_tab.load_data(config_data)

                    QMessageBox.information(self, "成功", f"路径已添加到 '{self._selected_repo}'!")
                else:
                    QMessageBox.warning(self, "警告", "该路径已存在")

    def remove_path(self):
        """删除路径"""
        if not self._selected_repo:
            QMessageBox.warning(self, "警告", "请先选择一个仓库")
            return

        selected_path_items = self.path_table.selectedItems()
        if not selected_path_items:
            QMessageBox.warning(self, "警告", "请先选择要删除的路径")
            return

        path_row = selected_path_items[0].row()
        path = self.path_table.item(path_row, 0).text()

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除路径 '{path}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            config_data = self.parent_window.get_config_data()
            github_repos = config_data.get("githubRepoPaths", {})
            if self._selected_repo in github_repos:
                paths = github_repos[self._selected_repo]
                if path in paths:
                    paths.remove(path)

                    self.parent_window.set_config_data(config_data)
                    self.parent_window.save_config_to_file()
                    self.load_data(config_data)
                    self.on_repo_selected()
                    self.parent_window.raw_config_tab.load_data(config_data)

                    QMessageBox.information(self, "成功", "路径已删除!")
