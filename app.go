package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"

	"claude-config-manager/internal/config"
	"claude-config-manager/internal/dialog"
	"claude-config-manager/internal/env"
	"claude-config-manager/internal/explorer"
	"claude-config-manager/internal/mcp"
	"claude-config-manager/internal/skills"
	"claude-config-manager/internal/version"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// App 是暴露给前端（Wails 绑定）的应用程序结构体。
// 每个导出的方法都会自动绑定到前端 window 调用，返回 error 时 Promise 会 reject。
type App struct {
	ctx context.Context
}

// NewApp 创建 App 实例。
func NewApp() *App {
	return &App{}
}

// startup 在应用启动时保存上下文，供运行时 API 使用。
func (a *App) startup(ctx context.Context) {
	a.ctx = ctx
}

// ==================== 配置管理 ====================

// GetConfig 读取 ~/.claude.json。
func (a *App) GetConfig() (map[string]interface{}, error) {
	return config.Load()
}

// SaveConfig 保存配置到 ~/.claude.json（自动备份 .bak）。
func (a *App) SaveConfig(cfg map[string]interface{}) error {
	return config.Save(cfg)
}

// GetConfigPath 返回配置文件路径。
func (a *App) GetConfigPath() (string, error) {
	return config.ConfigPath()
}

// ExportConfig 将配置导出到指定路径。
func (a *App) ExportConfig(cfg map[string]interface{}, targetPath string) error {
	if targetPath == "" {
		return errors.New("未选择导出路径")
	}
	return config.WriteJSON(targetPath, cfg)
}

// ImportConfig 从指定路径导入配置（导入前备份当前配置）。
func (a *App) ImportConfig(sourcePath string) (map[string]interface{}, error) {
	if sourcePath == "" {
		return nil, errors.New("未选择导入文件")
	}
	return config.ImportFromPath(sourcePath)
}

// ResetConfig 重置配置为默认值（重置前带时间戳备份）。
func (a *App) ResetConfig() (map[string]interface{}, error) {
	return config.Reset()
}

// ReadConfigFile 以字符串形式读取任意 JSON 文件。
func (a *App) ReadConfigFile(path string) (string, error) {
	return config.ReadJSONString(path)
}

// WriteConfigFile 将 JSON 字符串保存到配置文件，返回解析后的配置。
func (a *App) WriteConfigFile(path, text string) (map[string]interface{}, error) {
	return config.WriteJSONString(path, text)
}

// ==================== 版本信息 ====================

// GetVersion 返回版本信息对象。
func (a *App) GetVersion() map[string]interface{} {
	return version.Map()
}

// ==================== 打开目录 ====================

// OpenInExplorer 在系统文件管理器中打开文件或目录。
func (a *App) OpenInExplorer(path string) error {
	return explorer.Open(path)
}

// OpenSkillsFolder 打开全局 Skills 文件夹。
func (a *App) OpenSkillsFolder() error {
	home, err := os.UserHomeDir()
	if err != nil {
		return err
	}
	return explorer.OpenDir(filepath.Join(home, ".claude", "skills"))
}

// OpenClaudeFolder 打开 .claude 文件夹。
func (a *App) OpenClaudeFolder() error {
	home, err := os.UserHomeDir()
	if err != nil {
		return err
	}
	return explorer.OpenDir(filepath.Join(home, ".claude"))
}

// ==================== 原生对话框 ====================

// PickDirectory 打开目录选择对话框。
func (a *App) PickDirectory(title string) (string, error) {
	return dialog.OpenDirectory(a.ctx, title)
}

// PickFile 打开文件选择对话框。
func (a *App) PickFile(title, filter string) (string, error) {
	return dialog.OpenFile(a.ctx, title, filter)
}

// SaveFile 打开保存文件对话框。
func (a *App) SaveFile(title, defaultName string) (string, error) {
	return dialog.SaveFile(a.ctx, title, defaultName)
}

// ==================== 环境变量 ====================

// ApplyEnvVars 将服务商档案写入系统环境变量（Windows setx / Unix env.sh）。
func (a *App) ApplyEnvVars(profile map[string]interface{}) (*env.ApplyResult, error) {
	p := env.Profile{}
	if v, ok := profile["authToken"].(string); ok {
		p.AuthToken = v
	}
	if v, ok := profile["baseUrl"].(string); ok {
		p.BaseURL = v
	}
	if v, ok := profile["model"].(string); ok {
		p.Model = v
	}
	return env.Apply(p)
}

// ==================== MCP 服务器 ====================

// TestMCPConnection 测试 MCP 服务器连接。
func (a *App) TestMCPConnection(cfg map[string]interface{}) (*mcp.TestResult, error) {
	return mcp.TestConnection(toMCPServerConfig(cfg)), nil
}

// ListMCPToolsAndResources 列出 MCP 服务器的工具与资源。
func (a *App) ListMCPToolsAndResources(cfg map[string]interface{}) (*mcp.ListResult, error) {
	return mcp.ListToolsAndResources(toMCPServerConfig(cfg))
}

// toMCPServerConfig 将前端传来的 map 转为 mcp.ServerConfig。
func toMCPServerConfig(cfg map[string]interface{}) mcp.ServerConfig {
	c := mcp.ServerConfig{Env: map[string]string{}}
	if v, ok := cfg["command"].(string); ok {
		c.Command = v
	}
	if v, ok := cfg["args"].([]interface{}); ok {
		for _, a := range v {
			c.Args = append(c.Args, fmt.Sprintf("%v", a))
		}
	}
	if v, ok := cfg["env"].(map[string]interface{}); ok {
		for k, val := range v {
			c.Env[k] = fmt.Sprintf("%v", val)
		}
	}
	return c
}

// ==================== Skills ====================

// ListSkills 列出指定作用域下的 Skills。
func (a *App) ListSkills(scope, projectDir string) ([]skills.Skill, error) {
	return skills.List(scope, projectDir)
}

// SaveSkill 创建或更新 Skill（支持重命名）。
func (a *App) SaveSkill(scope, projectDir string, data map[string]interface{}) error {
	return skills.Save(scope, projectDir, data)
}

// DeleteSkill 删除指定名称的 Skill 目录。
func (a *App) DeleteSkill(scope, projectDir, name string) error {
	return skills.Delete(scope, projectDir, name)
}

// ==================== 剪贴板 ====================

// CopyToClipboard 复制文本到系统剪贴板。
func (a *App) CopyToClipboard(text string) error {
	return runtime.ClipboardSetText(a.ctx, text)
}
