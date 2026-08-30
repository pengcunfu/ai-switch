# Claude Configuration Manager

基于 **Wails v2**（Go 后端 + Vue 3 前端）的 Claude Code 配置文件管理工具。
用于管理 `~/.claude.json`（Claude Code 全局配置）和 `~/.claude/skills/` 下的 Skills。

> 原版本使用 PySide6 构建桌面界面，现已完全迁移为 Web 界面（Vue 3 + Vite + Naive UI），后端为 Go。

## 功能

- **统计信息**：总请求数 / 成本 / Tokens、Skills 使用统计、项目活跃度、模型使用统计
- **基础配置**：自动更新、服务商档案管理（Auth Token / Base URL / Model）、环境变量写入（Windows `setx` / Unix `env.sh`）、迁移状态、用户信息、配置备份与恢复
- **模型与权限**：Model 配置（默认模型、参数、上下文、使用限制）、权限管理（全局/项目工具权限）
- **功能配置**：MCP 服务器管理（增删改、连接测试、工具/资源列表）、Skills 管理、Hooks 配置、Memory 系统
- **外观与界面**：主题外观（模式/字体/颜色/高亮）、UI/UX 设置
- **集成与工具**：项目列表（GitHub 仓库映射本地路径）、集成设置（GitHub/Slack）、开发者工具、实验性功能
- 完整配置 JSON 查看/编辑、一键导出/导入/重置

## 环境要求

- [Go](https://go.dev/dl/) >= 1.25
- [Node.js](https://nodejs.org/) >= 20（LTS，前端构建必需）
- [Wails CLI](https://wails.io/) v2（`go install github.com/wailsapp/wails/v2/cmd/wails@latest`）
- Windows：WebView2 运行时（Win11 已内置）

## 开发

```bash
# 安装前端依赖（首次）
cd frontend && npm install && cd ..

# 开发模式（热重载）
wails dev
```

## 打包

```bash
wails build
# 输出: build/bin/ClaudeConfigManager.exe
# 打包前自动递增编译号（internal/version 的 Build）
```

## 目录结构

```
├── main.go                 # Wails 入口
├── app.go                  # 暴露给前端的全部绑定方法
├── internal/
│   ├── version/            # 版本管理
│   ├── buildver/           # 打包前自动递增编译号
│   ├── config/             # ~/.claude.json 读写/备份/导出/导入/重置
│   ├── skills/             # Skills 扫描与 SKILL.md 管理
│   ├── mcp/                # MCP 连接测试与工具列表（mcp-go）
│   ├── env/                # 环境变量写入
│   ├── explorer/           # 系统文件管理器打开目录
│   └── dialog/             # 原生文件对话框封装
├── frontend/               # Vue 3 + Vite + TS + Naive UI
└── build/                  # Wails 构建资源（图标、Windows 资源）
```
