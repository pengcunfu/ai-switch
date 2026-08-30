package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadMissingReturnsEmpty(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, ".claude.json")
	cfg, err := LoadFrom(path)
	if err != nil {
		t.Fatalf("LoadFrom on missing file should not error: %v", err)
	}
	if len(cfg) != 0 {
		t.Fatalf("expected empty config, got %v", cfg)
	}
}

func TestSaveBackupAndRoundTrip(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, ".claude.json")

	// 首次写入无备份
	first := map[string]interface{}{"autoUpdates": true, "name": "测试"}
	if err := SaveTo(path, first); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(path + ".bak"); !os.IsNotExist(err) {
		t.Fatal("不应生成 .bak 当原文件不存在")
	}

	// 第二次写入应生成 .bak 且内容为首次
	second := map[string]interface{}{"autoUpdates": false}
	if err := SaveTo(path, second); err != nil {
		t.Fatal(err)
	}
	bak, err := os.ReadFile(path + ".bak")
	if err != nil {
		t.Fatalf("应生成 .bak 备份: %v", err)
	}
	got, err := LoadFrom(path)
	if err != nil {
		t.Fatal(err)
	}
	if got["autoUpdates"] != false {
		t.Fatalf("配置未正确保存: %v", got)
	}
	if string(bak) == "" {
		t.Fatal(".bak 备份内容为空")
	}
}

func TestWriteJSONStringValidation(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, ".claude.json")
	if _, err := WriteJSONString(path, "{invalid json"); err == nil {
		t.Fatal("非法 JSON 应报错")
	}
	cfg, err := WriteJSONString(path, `{"a": 1, "b": "中文"}`)
	if err != nil {
		t.Fatal(err)
	}
	if cfg["a"] != float64(1) {
		t.Fatalf("解析结果错误: %v", cfg)
	}
}

func TestResetWritesDefault(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, ".claude.json")
	if err := os.WriteFile(path, []byte(`{"old": true}`), 0o644); err != nil {
		t.Fatal(err)
	}
	cfg := DefaultConfig()
	if err := WriteJSON(path, cfg); err != nil {
		t.Fatal(err)
	}
	if cfg["installMethod"] != "native" {
		t.Fatalf("默认配置错误: %v", cfg)
	}
	if cfg["activeProviderProfile"] != "Anthropic 默认" {
		t.Fatalf("默认档案错误: %v", cfg)
	}
}
