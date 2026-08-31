package config

import (
	"os"
	"path/filepath"
	"testing"
)

// withFakeHome 将 USERPROFILE/HOME/AISWITCH_APPDATA 指向临时目录，避免测试改动真实配置。
func withFakeHome(t *testing.T) {
	t.Helper()
	dir := t.TempDir()
	t.Setenv("USERPROFILE", dir)
	t.Setenv("HOME", dir)
	t.Setenv("AISWITCH_APPDATA", filepath.Join(dir, "appdata"))
}

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
	withFakeHome(t)
	dir := t.TempDir()
	path := filepath.Join(dir, ".claude.json")
	bakPath := filepath.Join(os.Getenv("AISWITCH_APPDATA"), "backups", ".claude.json.bak")

	// 首次写入无备份（原文件不存在）
	first := map[string]interface{}{"autoUpdates": true, "name": "测试"}
	if err := SaveTo(path, first); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(bakPath); !os.IsNotExist(err) {
		t.Fatal("不应生成备份当原文件不存在")
	}

	// 第二次写入应在应用数据目录生成备份且内容为首次
	second := map[string]interface{}{"autoUpdates": false}
	if err := SaveTo(path, second); err != nil {
		t.Fatal(err)
	}
	bak, err := os.ReadFile(bakPath)
	if err != nil {
		t.Fatalf("应生成备份: %v", err)
	}
	got, err := LoadFrom(path)
	if err != nil {
		t.Fatal(err)
	}
	if got["autoUpdates"] != false {
		t.Fatalf("配置未正确保存: %v", got)
	}
	if string(bak) == "" {
		t.Fatal("备份内容为空")
	}
}

func TestWriteJSONStringValidation(t *testing.T) {
	withFakeHome(t)
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

func TestApplyProviderProfileWritesSettingsEnv(t *testing.T) {
	withFakeHome(t)

	// 预置 settings.json（含旧 env 与无关字段），验证合并而非覆盖
	path, err := SettingsPath()
	if err != nil {
		t.Fatal(err)
	}
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(`{"theme":"dark","env":{"API_TIMEOUT_MS":"1000"}}`), 0o644); err != nil {
		t.Fatal(err)
	}

	res, err := ApplyProviderProfile(Profile{AuthToken: "tok-1", BaseURL: "https://example.com", Model: "m1"})
	if err != nil {
		t.Fatal(err)
	}
	if len(res.Applied) != 3 {
		t.Fatalf("应写入 3 项, 实际 %v", res.Applied)
	}

	cfg, err := LoadSettings()
	if err != nil {
		t.Fatal(err)
	}
	env, _ := cfg["env"].(map[string]interface{})
	if env["ANTHROPIC_AUTH_TOKEN"] != "tok-1" ||
		env["ANTHROPIC_BASE_URL"] != "https://example.com" ||
		env["ANTHROPIC_MODEL"] != "m1" {
		t.Fatalf("env 字段写入错误: %v", env)
	}
	if env["API_TIMEOUT_MS"] != "1000" {
		t.Fatalf("不应覆盖无关的 env 键: %v", env)
	}
	if cfg["theme"] != "dark" {
		t.Fatalf("不应覆盖无关配置: %v", cfg)
	}

	// 空字段应删除对应键
	res, err = ApplyProviderProfile(Profile{AuthToken: "tok-2"})
	if err != nil {
		t.Fatal(err)
	}
	if len(res.Applied) != 1 {
		t.Fatalf("只应写入 1 项, 实际 %v", res.Applied)
	}
	cfg, _ = LoadSettings()
	env, _ = cfg["env"].(map[string]interface{})
	if _, ok := env["ANTHROPIC_MODEL"]; ok {
		t.Fatalf("空 Model 应删除 ANTHROPIC_MODEL 键: %v", env)
	}
	if env["ANTHROPIC_AUTH_TOKEN"] != "tok-2" {
		t.Fatalf("authToken 未更新: %v", env)
	}
}

func TestApplyProviderProfileEmptyFails(t *testing.T) {
	withFakeHome(t)
	if _, err := ApplyProviderProfile(Profile{}); err == nil {
		t.Fatal("全空档案应报错")
	}
}

func TestResetWritesDefault(t *testing.T) {
	withFakeHome(t)
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
