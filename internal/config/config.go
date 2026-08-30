// Package config 负责 ~/.claude.json 的读写、备份、导出、导入与重置，
// 替代原 PySide6 主窗口中的 load_config / save_config_to_file 等逻辑。
package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// ConfigPath 返回 Claude Code 全局配置文件路径。
func ConfigPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".claude.json"), nil
}

// Load 读取配置文件，文件不存在时返回空对象。
func Load() (map[string]interface{}, error) {
	path, err := ConfigPath()
	if err != nil {
		return nil, err
	}
	return LoadFrom(path)
}

// LoadFrom 从指定路径读取 JSON 配置。
func LoadFrom(path string) (map[string]interface{}, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return map[string]interface{}{}, nil
		}
		return nil, err
	}
	var cfg map[string]interface{}
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("解析配置文件失败: %w", err)
	}
	if cfg == nil {
		cfg = map[string]interface{}{}
	}
	return cfg, nil
}

// Save 保存配置：先备份原文件为 .bak，再写入新内容（UTF-8、2 空格缩进、不转义非 ASCII）。
func Save(cfg map[string]interface{}) error {
	path, err := ConfigPath()
	if err != nil {
		return err
	}
	return SaveTo(path, cfg)
}

// SaveTo 保存配置到指定路径，写入前自动备份。
func SaveTo(path string, cfg map[string]interface{}) error {
	if err := backup(path); err != nil {
		return err
	}
	return WriteJSON(path, cfg)
}

// WriteJSON 将配置对象序列化并写入路径（无备份）。
func WriteJSON(path string, cfg map[string]interface{}) error {
	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0o644)
}

// ReadJSONString 以字符串形式读取指定路径的 JSON 文件。
func ReadJSONString(path string) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(data), nil
}

// WriteJSONString 将 JSON 字符串写入配置文件（含 .bak 备份），返回解析后的配置对象。
func WriteJSONString(path, text string) (map[string]interface{}, error) {
	var cfg map[string]interface{}
	if err := json.Unmarshal([]byte(text), &cfg); err != nil {
		return nil, fmt.Errorf("JSON 格式错误: %w", err)
	}
	if cfg == nil {
		cfg = map[string]interface{}{}
	}
	if err := SaveTo(path, cfg); err != nil {
		return nil, err
	}
	return cfg, nil
}

// DefaultProfiles 返回默认服务商档案。
func DefaultProfiles() []interface{} {
	return []interface{}{
		map[string]interface{}{
			"name":     "Anthropic 默认",
			"authToken": "",
			"baseUrl":   "https://api.anthropic.com",
			"model":     "claude-sonnet-4-6",
		},
	}
}

// DefaultConfig 返回重置后的默认配置。
func DefaultConfig() map[string]interface{} {
	return map[string]interface{}{
		"installMethod":          "native",
		"autoUpdates":            false,
		"mcpServers":             map[string]interface{}{},
		"githubRepoPaths":        map[string]interface{}{},
		"providerProfiles":       DefaultProfiles(),
		"activeProviderProfile":  "Anthropic 默认",
	}
}

// Reset 将配置重置为默认值，重置前备份原文件（带时间戳）。
func Reset() (map[string]interface{}, error) {
	path, err := ConfigPath()
	if err != nil {
		return nil, err
	}
	// 带时间戳备份
	if _, err := os.Stat(path); err == nil {
		stamp := time.Now().Format("20060102_150405")
		bak := path + ".bak." + stamp
		data, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}
		if err := os.WriteFile(bak, data, 0o644); err != nil {
			return nil, err
		}
	}
	cfg := DefaultConfig()
	if err := WriteJSON(path, cfg); err != nil {
		return nil, err
	}
	return cfg, nil
}

// ImportFromPath 从指定路径导入配置，导入前备份当前配置。
func ImportFromPath(sourcePath string) (map[string]interface{}, error) {
	cfg, err := LoadFrom(sourcePath)
	if err != nil {
		return nil, err
	}
	path, err := ConfigPath()
	if err != nil {
		return nil, err
	}
	if err := SaveTo(path, cfg); err != nil {
		return nil, err
	}
	return cfg, nil
}

// backup 将现有配置文件复制为 .bak。
func backup(path string) error {
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return os.WriteFile(path+".bak", data, 0o644)
}
