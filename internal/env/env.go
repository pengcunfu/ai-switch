// Package env 负责将服务商档案写入系统环境变量，
// 替代原 PySide6 general_settings_tab 的 apply_env_vars。
// Windows 使用 setx 持久化；其他系统写入 ~/.claude/env.sh。
package env

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

// EnvVar 待设置的环境变量项。
type EnvVar struct {
	Name  string
	Value string
}

// ApplyResult 返回给前端的应用结果。
type ApplyResult struct {
	Applied []string `json:"applied"`
	Message string   `json:"message"`
	Method  string   `json:"method"` // "setx" 或 "env.sh"
}

// Profile 服务商档案。
type Profile struct {
	AuthToken string `json:"authToken"`
	BaseURL   string `json:"baseUrl"`
	Model     string `json:"model"`
}

// Apply 根据当前平台应用环境变量。
func Apply(p Profile) (*ApplyResult, error) {
	var vars []EnvVar
	if p.AuthToken != "" {
		vars = append(vars, EnvVar{Name: "ANTHROPIC_AUTH_TOKEN", Value: p.AuthToken})
	}
	if p.BaseURL != "" {
		vars = append(vars, EnvVar{Name: "ANTHROPIC_BASE_URL", Value: p.BaseURL})
	}
	if p.Model != "" {
		vars = append(vars, EnvVar{Name: "ANTHROPIC_MODEL", Value: p.Model})
	}
	if len(vars) == 0 {
		return nil, fmt.Errorf("当前档案所有字段为空，无需设置")
	}

	// 立即设置当前进程环境变量
	for _, v := range vars {
		_ = os.Setenv(v.Name, v.Value)
	}

	if runtime.GOOS == "windows" {
		if err := applySetx(vars); err != nil {
			return nil, err
		}
		names := make([]string, 0, len(vars))
		for _, v := range vars {
			names = append(names, v.Name)
		}
		return &ApplyResult{
			Applied: names,
			Method:  "setx",
			Message: "环境变量已设置! 请重新打开终端以使环境变量在新终端中生效。",
		}, nil
	}

	// Unix: 写入 ~/.claude/env.sh
	if err := writeEnvSh(vars); err != nil {
		return nil, err
	}
	names := make([]string, 0, len(vars))
	for _, v := range vars {
		names = append(names, v.Name)
	}
	return &ApplyResult{
		Applied: names,
		Method:  "env.sh",
		Message: "环境变量已生效，并写入 ~/.claude/env.sh\n请在 shell 配置中 source 此文件以持久化:\n  source ~/.claude/env.sh",
	}, nil
}

// applySetx 顺序执行 setx 命令（Windows）。
func applySetx(vars []EnvVar) error {
	for _, v := range vars {
		cmd := exec.Command("setx", v.Name, v.Value)
		out, err := cmd.CombinedOutput()
		if err != nil {
			return fmt.Errorf("执行 setx %s 失败: %s %s", v.Name, err, string(out))
		}
	}
	return nil
}

// writeEnvSh 写入 ~/.claude/env.sh（Unix）。
func writeEnvSh(vars []EnvVar) error {
	home, err := os.UserHomeDir()
	if err != nil {
		return err
	}
	dir := filepath.Join(home, ".claude")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	var lines []string
	lines = append(lines, "# Claude Code 服务商环境变量 (由 ClaudeConfigManager 生成)")
	for _, v := range vars {
		lines = append(lines, fmt.Sprintf("export %s=%q", v.Name, v.Value))
	}
	content := strings.Join(lines, "\n") + "\n"
	return os.WriteFile(filepath.Join(dir, "env.sh"), []byte(content), 0o644)
}
