package appdata

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestAppDataDirOverride(t *testing.T) {
	dir := t.TempDir()
	t.Setenv(envOverride, dir)
	got, err := AppDataDir()
	if err != nil {
		t.Fatal(err)
	}
	if got != dir {
		t.Fatalf("override 未生效: %s != %s", got, dir)
	}
	if _, err := os.Stat(dir); err != nil {
		t.Fatalf("目录应已创建: %v", err)
	}
}

func TestBackupAndRolling(t *testing.T) {
	t.Setenv(envOverride, t.TempDir())
	src := filepath.Join(t.TempDir(), "config.toml")
	if err := os.WriteFile(src, []byte("model = \"x\""), 0o644); err != nil {
		t.Fatal(err)
	}
	// 时间戳备份
	bak, err := BackupFile(src)
	if err != nil {
		t.Fatal(err)
	}
	if bak == "" || !strings.Contains(bak, ".bak.") {
		t.Fatalf("时间戳备份路径异常: %q", bak)
	}
	if _, err := os.Stat(bak); err != nil {
		t.Fatalf("时间戳备份文件不存在: %v", err)
	}
	// 滚动备份（覆盖式）
	if err := BackupFileRolling(src); err != nil {
		t.Fatal(err)
	}
	rolling := filepath.Join(filepath.Dir(bak), "config.toml.bak")
	if _, err := os.Stat(rolling); err != nil {
		t.Fatalf("滚动备份不存在: %v", err)
	}
	// 源缺失 no-op
	if err := BackupFileRolling(filepath.Join(t.TempDir(), "missing")); err != nil {
		t.Fatal(err)
	}
}

func TestStateRoundTrip(t *testing.T) {
	t.Setenv(envOverride, t.TempDir())
	empty, err := LoadState()
	if err != nil {
		t.Fatal(err)
	}
	if len(empty) != 0 {
		t.Fatalf("无状态时应为空: %v", empty)
	}
	st := map[string]interface{}{
		"activeTool": "codex",
		"uiux":       map[string]interface{}{"showStatusBar": true},
	}
	if err := SaveState(st); err != nil {
		t.Fatal(err)
	}
	got, err := LoadState()
	if err != nil {
		t.Fatal(err)
	}
	if got["activeTool"] != "codex" {
		t.Fatalf("状态未正确往返: %v", got)
	}
}

func TestCodexStatePathCreatesParent(t *testing.T) {
	t.Setenv(envOverride, t.TempDir())
	p, err := CodexStatePath()
	if err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Dir(p)); err != nil {
		t.Fatalf("父目录应已创建: %v", err)
	}
	if filepath.Base(p) != "active_profile" {
		t.Fatalf("状态文件命名异常: %s", p)
	}
}
