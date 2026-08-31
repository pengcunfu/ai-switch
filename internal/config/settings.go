package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Profile 服务商档案，用于写入 settings.json 的 env 字段。
type Profile struct {
	AuthToken string `json:"authToken"`
	BaseURL   string `json:"baseUrl"`
	Model     string `json:"model"`
}

// ApplyResult 返回给前端的应用结果。
type ApplyResult struct {
	Applied []string `json:"applied"`
	Message string   `json:"message"`
	Path    string   `json:"path"` // settings.json 路径
}

// SettingsPath 返回 Claude Code 用户级 settings.json 路径。
func SettingsPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".claude", "settings.json"), nil
}

// LoadSettings 读取 settings.json，文件不存在时返回空对象。
func LoadSettings() (map[string]interface{}, error) {
	path, err := SettingsPath()
	if err != nil {
		return nil, err
	}
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return map[string]interface{}{}, nil
		}
		return nil, err
	}
	var cfg map[string]interface{}
	if err := json.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("解析 settings.json 失败: %w", err)
	}
	if cfg == nil {
		cfg = map[string]interface{}{}
	}
	return cfg, nil
}

// SaveSettings 保存 settings.json（写入前自动备份 .bak）。
func SaveSettings(cfg map[string]interface{}) error {
	path, err := SettingsPath()
	if err != nil {
		return err
	}
	return SaveTo(path, cfg)
}

// ApplyProviderProfile 将服务商档案写入 settings.json 的 env 字段，
// 取代向系统环境变量（setx / env.sh）写值的方式，只对 Claude Code 生效。
// 档案中为空的字段会删除对应键，避免残留旧值。
func ApplyProviderProfile(p Profile) (*ApplyResult, error) {
	items := []struct {
		Name  string
		Value string
	}{
		{"ANTHROPIC_AUTH_TOKEN", p.AuthToken},
		{"ANTHROPIC_BASE_URL", p.BaseURL},
		{"ANTHROPIC_MODEL", p.Model},
	}
	var applied []string
	for _, it := range items {
		if it.Value != "" {
			applied = append(applied, it.Name)
		}
	}
	if len(applied) == 0 {
		return nil, fmt.Errorf("当前档案所有字段为空，无需设置")
	}

	cfg, err := LoadSettings()
	if err != nil {
		return nil, err
	}
	env, ok := cfg["env"].(map[string]interface{})
	if !ok || env == nil {
		env = map[string]interface{}{}
	}
	for _, it := range items {
		if it.Value != "" {
			env[it.Name] = it.Value
		} else {
			delete(env, it.Name)
		}
	}
	if len(env) == 0 {
		delete(cfg, "env")
	} else {
		cfg["env"] = env
	}

	path, err := SettingsPath()
	if err != nil {
		return nil, err
	}
	if err := SaveSettings(cfg); err != nil {
		return nil, err
	}
	return &ApplyResult{
		Applied: applied,
		Path:    path,
		Message: fmt.Sprintf("已写入 %s 的 env 字段（%d 项），新启动的 Claude Code 会话将生效。", path, len(applied)),
	}, nil
}
