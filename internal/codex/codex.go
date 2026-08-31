// Package codex 负责 Codex CLI（~/.codex）的配置档案管理与模型切换。
// 每个服务商一套配置文件：活动集为 config.toml + models.json，
// 档案集为 config-<name>.toml + models-<name>.json，切换即整体替换活动文件。
// 所有档案的 model_catalog_json 均指向活动 models.json，因此切换仅需纯文件拷贝，
// 无需解析/重写 TOML 结构。
package codex

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"claude-config-manager/internal/appdata"
)

const (
	// customProfile 是活动配置未匹配任何档案时的显示名。
	customProfile = "自定义"

	activeConfig = "config.toml"
	activeModels = "models.json"
	stateFile    = ".active_profile"
)

var (
	profileConfigGlob = "config-*.toml"
	keyValueRegexp    = regexp.MustCompile(`^\s*([a-zA-Z0-9_]+)\s*=\s*"([^"]*)"`)
)

// Profile 一个 Codex 配置档案。
type Profile struct {
	Name      string `json:"name"`
	Model     string `json:"model"`
	Provider  string `json:"provider"`
	HasConfig bool   `json:"hasConfig"`
	HasModels bool   `json:"hasModels"`
	Active    bool   `json:"active"`
}

// ListResult 返回给前端的档案列表。
type ListResult struct {
	Dir         string    `json:"dir"`
	Exists      bool      `json:"exists"`
	Profiles    []Profile `json:"profiles"`
	Active      string    `json:"active"`
	ActiveModel string    `json:"activeModel"`
	CatalogPath string    `json:"catalogPath"`
}

// SwitchResult 切换档案的结果。
type SwitchResult struct {
	Active     string   `json:"active"`
	Message    string   `json:"message"`
	SyncedFrom string   `json:"syncedFrom"`
	BackedUp   []string `json:"backedUp"`
	Warning    string   `json:"warning,omitempty"`
}

// CodexDir 返回 Codex 配置目录。
func CodexDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".codex"), nil
}

// LoadProfiles 扫描 ~/.codex 下的档案，并判定当前活动档案。
func LoadProfiles() (*ListResult, error) {
	dir, err := CodexDir()
	if err != nil {
		return nil, err
	}
	res := &ListResult{Dir: dir}
	if !fileExists(dir) {
		return res, nil // Exists=false
	}
	res.Exists = true

	// 扫描 config-*.toml 生成档案
	matches, err := filepath.Glob(filepath.Join(dir, profileConfigGlob))
	if err != nil {
		return nil, err
	}
	for _, cfgPath := range matches {
		vals, err := topLevelValues(cfgPath)
		if err != nil {
			return nil, err
		}
		name := strings.TrimSuffix(strings.TrimPrefix(filepath.Base(cfgPath), "config-"), ".toml")
		res.Profiles = append(res.Profiles, Profile{
			Name:      name,
			Model:     vals["model"],
			Provider:  vals["model_provider"],
			HasConfig: true,
			HasModels: fileExists(filepath.Join(dir, "models-"+name+".json")),
		})
	}
	sort.Slice(res.Profiles, func(i, j int) bool { return res.Profiles[i].Name < res.Profiles[j].Name })

	// 活动配置信息
	activeCfgPath := filepath.Join(dir, activeConfig)
	activeVals, err := topLevelValues(activeCfgPath)
	if err != nil {
		return nil, err
	}
	res.ActiveModel = activeVals["model"]
	res.CatalogPath = activeVals["model_catalog_json"]
	res.Active = resolveActive(dir, res.Profiles, activeCfgPath, activeVals["model"], activeVals["model_provider"])
	for i := range res.Profiles {
		res.Profiles[i].Active = res.Profiles[i].Name == res.Active
	}
	return res, nil
}

// SwitchProfile 切换到指定档案，整体替换 config.toml 与 models.json。
func SwitchProfile(name string) (*SwitchResult, error) {
	profiles, err := LoadProfiles()
	if err != nil {
		return nil, err
	}
	if !profiles.Exists {
		return nil, fmt.Errorf("未找到 Codex 配置目录: %s", profiles.Dir)
	}
	target := findProfile(profiles.Profiles, name)
	if target == nil {
		return nil, fmt.Errorf("档案 '%s' 不存在", name)
	}

	dir := profiles.Dir
	// 先把活动文件读入内存，避免后续写入影响同步
	activeCfgData, _ := os.ReadFile(filepath.Join(dir, activeConfig))
	activeModelsData, _ := os.ReadFile(filepath.Join(dir, activeModels))

	res := &SwitchResult{SyncedFrom: profiles.Active}
	if profiles.Active == name {
		res.Active = name
		res.Message = fmt.Sprintf("当前已是档案 '%s'", name)
		return res, nil
	}

	// 若当前活动是已知档案，把活动文件同步回对应档案文件
	if profiles.Active != customProfile && findProfile(profiles.Profiles, profiles.Active) != nil {
		if len(activeCfgData) > 0 {
			if err := os.WriteFile(filepath.Join(dir, "config-"+profiles.Active+".toml"), activeCfgData, 0o644); err != nil {
				return nil, err
			}
		}
		if len(activeModelsData) > 0 {
			if err := os.WriteFile(filepath.Join(dir, "models-"+profiles.Active+".json"), activeModelsData, 0o644); err != nil {
				return nil, err
			}
		}
	}

	// 时间戳备份活动文件
	for _, f := range []string{activeConfig, activeModels} {
		p := filepath.Join(dir, f)
		if fileExists(p) {
			bak, err := timestampedBackup(p)
			if err != nil {
				return nil, err
			}
			res.BackedUp = append(res.BackedUp, bak)
		}
	}

	// 拷贝目标档案 → 活动文件
	if err := atomicCopy(filepath.Join(dir, "config-"+name+".toml"), filepath.Join(dir, activeConfig)); err != nil {
		return nil, err
	}
	if target.HasModels {
		if err := atomicCopy(filepath.Join(dir, "models-"+name+".json"), filepath.Join(dir, activeModels)); err != nil {
			return nil, err
		}
	} else {
		res.Warning = fmt.Sprintf("档案 '%s' 没有 models 文件，未替换模型目录", name)
	}

	// 记录活动档案
	if err := writeState(dir, name); err != nil {
		return nil, err
	}

	res.Active = name
	res.Message = fmt.Sprintf("已切换到档案 '%s'（model=%s）\n新启动的 Codex 会话将生效。", name, target.Model)
	return res, nil
}

// resolveActive 判定活动档案：状态文件 → 字节相等 → (model, provider) 匹配 → 自定义。
func resolveActive(dir string, profiles []Profile, activeCfgPath, activeModel, activeProvider string) string {
	// 1. 状态文件（档案已不存在时视为过期，落入后续推断）
	if name, err := readState(dir); err == nil && name != "" && findProfile(profiles, name) != nil {
		return name
	}
	// 2. 字节相等
	if activeData, err := os.ReadFile(activeCfgPath); err == nil {
		for _, p := range profiles {
			pdata, err := os.ReadFile(filepath.Join(dir, "config-"+p.Name+".toml"))
			if err == nil && bytes.Equal(activeData, pdata) {
				return p.Name
			}
		}
	}
	// 3. model + provider 匹配
	if activeModel != "" {
		for _, p := range profiles {
			if p.Model == activeModel && p.Provider == activeProvider {
				return p.Name
			}
		}
	}
	// 4. 自定义
	return customProfile
}

// topLevelValues 解析 TOML 顶层的双引号字符串键值对，遇到首个 [section] 行停止。
func topLevelValues(path string) (map[string]string, error) {
	vals := map[string]string{}
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return vals, nil
		}
		return nil, err
	}
	for _, line := range strings.Split(string(data), "\n") {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "[") {
			break
		}
		m := keyValueRegexp.FindStringSubmatch(trimmed)
		if m == nil {
			continue
		}
		vals[m[1]] = m[2]
	}
	return vals, nil
}

func findProfile(profiles []Profile, name string) *Profile {
	for i := range profiles {
		if profiles[i].Name == name {
			return &profiles[i]
		}
	}
	return nil
}

// readState 读取活动档案状态：优先应用数据目录，缺失时回退旧位置 ~/.codex/.active_profile。
func readState(dir string) (string, error) {
	if p, err := appdata.CodexStatePath(); err == nil {
		if data, err := os.ReadFile(p); err == nil {
			return strings.TrimSpace(string(data)), nil
		}
	}
	data, err := os.ReadFile(filepath.Join(dir, stateFile))
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(data)), nil
}

// writeState 写入活动档案状态到应用数据目录，并清理旧位置文件。
func writeState(dir, name string) error {
	p, err := appdata.CodexStatePath()
	if err != nil {
		return err
	}
	if err := os.WriteFile(p, []byte(name), 0o644); err != nil {
		return err
	}
	_ = os.Remove(filepath.Join(dir, stateFile))
	return nil
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// timestampedBackup 复制文件为时间戳备份（存入应用数据目录 backups），返回备份路径。
func timestampedBackup(path string) (string, error) {
	return appdata.BackupFile(path)
}

// atomicCopy 写临时文件后重命名，避免目标文件被写坏。
func atomicCopy(src, dst string) error {
	data, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	tmp := dst + ".new"
	if err := os.WriteFile(tmp, data, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, dst)
}
