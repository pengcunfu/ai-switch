// Package appdata 提供应用数据目录（<文档>\FNSoftware\.aiswitch）的解析与读写。
// 文档目录通过 Windows 已知文件夹 API 动态解析（不硬编码），
// 可用环境变量 AISWITCH_APPDATA 覆盖（用于测试与便携场景）。
package appdata

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

const (
	// envOverride 用于覆盖数据目录（测试/便携场景）。
	envOverride = "AISWITCH_APPDATA"
	// AppDirName 应用套件目录名。
	AppDirName = "FNSoftware"
	// DataDirName 数据目录名。
	DataDirName = ".aiswitch"
	// BackupsDirName 备份目录名。
	BackupsDirName = "backups"
	// StateFileName 应用状态文件名。
	StateFileName = "app-state.json"
	// CodexStateRel Codex 活动档案状态相对路径。
	CodexStateRel = "codex/active_profile"
)

// AppDataDir 返回应用数据目录（<文档>/FNSoftware/.aiswitch），不存在则创建。
// 设置 AISWITCH_APPDATA 时直接使用该路径（便于测试与便携）。
func AppDataDir() (string, error) {
	if v := os.Getenv(envOverride); v != "" {
		if err := os.MkdirAll(v, 0o755); err != nil {
			return "", err
		}
		return v, nil
	}
	docs, err := documentsDir()
	if err != nil {
		return "", err
	}
	dir := filepath.Join(docs, AppDirName, DataDirName)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", err
	}
	return dir, nil
}

// BackupDir 返回备份目录（AppDataDir/backups），不存在则创建。
func BackupDir() (string, error) {
	dir, err := AppDataDir()
	if err != nil {
		return "", err
	}
	bak := filepath.Join(dir, BackupsDirName)
	if err := os.MkdirAll(bak, 0o755); err != nil {
		return "", err
	}
	return bak, nil
}

// CodexStatePath 返回 Codex 活动档案状态文件路径（AppDataDir/codex/active_profile）。
func CodexStatePath() (string, error) {
	dir, err := AppDataDir()
	if err != nil {
		return "", err
	}
	p := filepath.Join(dir, filepath.FromSlash(CodexStateRel))
	if err := os.MkdirAll(filepath.Dir(p), 0o755); err != nil {
		return "", err
	}
	return p, nil
}

// LoadState 读取应用状态 app-state.json，文件不存在时返回空对象。
func LoadState() (map[string]interface{}, error) {
	dir, err := AppDataDir()
	if err != nil {
		return nil, err
	}
	path := filepath.Join(dir, StateFileName)
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return map[string]interface{}{}, nil
		}
		return nil, err
	}
	var state map[string]interface{}
	if err := json.Unmarshal(data, &state); err != nil {
		return nil, fmt.Errorf("解析应用状态失败: %w", err)
	}
	if state == nil {
		state = map[string]interface{}{}
	}
	return state, nil
}

// SaveState 保存应用状态到 app-state.json。
func SaveState(state map[string]interface{}) error {
	dir, err := AppDataDir()
	if err != nil {
		return err
	}
	if state == nil {
		state = map[string]interface{}{}
	}
	data, err := json.MarshalIndent(state, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(dir, StateFileName), data, 0o644)
}

// BackupFile 将 src 复制到备份目录，命名 <basename>.bak.<时间戳>，返回备份路径；
// 源文件不存在时返回空串且不报错。
func BackupFile(src string) (string, error) {
	dir, err := BackupDir()
	if err != nil {
		return "", err
	}
	if _, err := os.Stat(src); err != nil {
		if os.IsNotExist(err) {
			return "", nil
		}
		return "", err
	}
	bak := filepath.Join(dir, filepath.Base(src)+".bak."+time.Now().Format("20060102_150405"))
	if err := copyFile(src, bak); err != nil {
		return "", err
	}
	return bak, nil
}

// BackupFileRolling 将 src 复制到备份目录，命名 <basename>.bak（覆盖式），源缺失时 no-op。
func BackupFileRolling(src string) error {
	dir, err := BackupDir()
	if err != nil {
		return err
	}
	if _, err := os.Stat(src); err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	bak := filepath.Join(dir, filepath.Base(src)+".bak")
	return copyFile(src, bak)
}

func copyFile(src, dst string) error {
	data, err := os.ReadFile(src)
	if err != nil {
		return err
	}
	return os.WriteFile(dst, data, 0o644)
}
