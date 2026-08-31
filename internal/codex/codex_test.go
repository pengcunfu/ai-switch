package codex

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"claude-config-manager/internal/appdata"
)

// withFakeCodex 将 USERPROFILE/HOME/AISWITCH_APPDATA 指向临时目录并创建 ~/.codex，返回其路径。
func withFakeCodex(t *testing.T) string {
	t.Helper()
	home := t.TempDir()
	t.Setenv("USERPROFILE", home)
	t.Setenv("HOME", home)
	t.Setenv("AISWITCH_APPDATA", filepath.Join(home, "appdata"))
	dir := filepath.Join(home, ".codex")
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	return dir
}

// statePath 返回应用数据目录中的活动档案状态路径。
func statePath(t *testing.T) string {
	t.Helper()
	p, err := appdata.CodexStatePath()
	if err != nil {
		t.Fatal(err)
	}
	return p
}

// writeProfile 生成 config-<name>.toml（及可选 models-<name>.json）。
func writeProfile(t *testing.T, dir, name, model, provider string, withModels bool) {
	t.Helper()
	cfg := fmt.Sprintf("model = %q\nmodel_provider = %q\nmodel_catalog_json = \"C:/Users/pcf/.codex/models.json\"\n[model_providers.%s]\nname = %q\n", model, provider, provider, model)
	if err := os.WriteFile(filepath.Join(dir, "config-"+name+".toml"), []byte(cfg), 0o644); err != nil {
		t.Fatal(err)
	}
	if withModels {
		models := fmt.Sprintf(`{"models":[{"slug":%q}]}`, model)
		if err := os.WriteFile(filepath.Join(dir, "models-"+name+".json"), []byte(models), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}

// writeActive 写入活动 config.toml 与 models.json。
func writeActive(t *testing.T, dir, cfg, models string) {
	t.Helper()
	if err := os.WriteFile(filepath.Join(dir, activeConfig), []byte(cfg), 0o644); err != nil {
		t.Fatal(err)
	}
	if models != "" {
		if err := os.WriteFile(filepath.Join(dir, activeModels), []byte(models), 0o644); err != nil {
			t.Fatal(err)
		}
	}
}

func readFile(t *testing.T, path string) string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("读取 %s 失败: %v", path, err)
	}
	return string(data)
}

func TestParseTopLevelValues(t *testing.T) {
	dir := withFakeCodex(t)
	path := filepath.Join(dir, "config.toml")
	content := "# 注释\nmodel = \"deepseek-v4-flash-ga-260731\"   # 行尾注释\nmodel_provider = \"ark\"\nmodel_catalog_json = \"C:/path/models.json\"\n\n[model_providers.ark]\nname = \"should-not-parse\"\n"
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	vals, err := topLevelValues(path)
	if err != nil {
		t.Fatal(err)
	}
	if vals["model"] != "deepseek-v4-flash-ga-260731" || vals["model_provider"] != "ark" || vals["model_catalog_json"] != "C:/path/models.json" {
		t.Fatalf("顶层键解析错误: %v", vals)
	}
	if _, ok := vals["name"]; ok {
		t.Fatalf("不应解析 [section] 内键: %v", vals)
	}
}

func TestLoadProfilesMissingDir(t *testing.T) {
	home := t.TempDir()
	t.Setenv("USERPROFILE", home)
	t.Setenv("HOME", home)
	t.Setenv("AISWITCH_APPDATA", filepath.Join(home, "appdata"))
	res, err := LoadProfiles()
	if err != nil {
		t.Fatal(err)
	}
	if res.Exists {
		t.Fatal("目录不存在时 Exists 应为 false")
	}
}

func TestResolveActivePriority(t *testing.T) {
	dir := withFakeCodex(t)
	deepCfg := "model = \"deepseek-v4-flash-ga-260731\"\nmodel_provider = \"ark\"\n"
	writeProfile(t, dir, "deepseek", "deepseek-v4-flash-ga-260731", "ark", true)
	writeProfile(t, dir, "mimo", "mimo-v2.5-pro", "mimo", true)

	// 字节相等 → deepseek
	writeActive(t, dir, deepCfg, `{"models":[]}`)
	res, err := LoadProfiles()
	if err != nil {
		t.Fatal(err)
	}
	if res.Active != "deepseek" {
		t.Fatalf("字节相等应判定为 deepseek, 实际 %q", res.Active)
	}

	// 状态文件优先
	if err := writeState(dir, "mimo"); err != nil {
		t.Fatal(err)
	}
	res, _ = LoadProfiles()
	if res.Active != "mimo" {
		t.Fatalf("状态文件应优先为 mimo, 实际 %q", res.Active)
	}

	// 过期状态文件 → 回退到字节相等
	if err := writeState(dir, "ghost"); err != nil {
		t.Fatal(err)
	}
	res, _ = LoadProfiles()
	if res.Active != "deepseek" {
		t.Fatalf("过期状态应回退为 deepseek, 实际 %q", res.Active)
	}

	// 自定义：内容不匹配任何档案
	if err := os.Remove(statePath(t)); err != nil {
		t.Fatal(err)
	}
	writeActive(t, dir, "model = \"custom-model\"\nmodel_provider = \"other\"\n", "")
	res, _ = LoadProfiles()
	if res.Active != customProfile {
		t.Fatalf("无匹配应判定为自定义, 实际 %q", res.Active)
	}
}

func TestSwitchRoundTrip(t *testing.T) {
	dir := withFakeCodex(t)
	deepCfg := "model = \"deepseek-v4-flash-ga-260731\"\nmodel_provider = \"ark\"\n"
	deepModels := `{"models":[{"slug":"deepseek-v4-flash-ga-260731"}]}`

	writeProfile(t, dir, "deepseek", "deepseek-v4-flash-ga-260731", "ark", true)
	writeProfile(t, dir, "mimo", "mimo-v2.5-pro", "mimo", true)
	writeActive(t, dir, deepCfg, deepModels)

	// 切到 mimo
	res, err := SwitchProfile("mimo")
	if err != nil {
		t.Fatal(err)
	}
	if res.Active != "mimo" || res.SyncedFrom != "deepseek" {
		t.Fatalf("切换结果错误: %+v", res)
	}
	// config.toml 应与 config-mimo.toml 完全一致（整体替换）
	if got := readFile(t, filepath.Join(dir, activeConfig)); got != readFile(t, filepath.Join(dir, "config-mimo.toml")) {
		t.Fatalf("config.toml 未整体替换为 mimo: %q", got)
	}
	if got := readFile(t, filepath.Join(dir, activeModels)); got != readFile(t, filepath.Join(dir, "models-mimo.json")) {
		t.Fatalf("models.json 未整体替换为 mimo: %q", got)
	}
	// 首次切离 deepseek 应补建 models-deepseek.json
	if got := readFile(t, filepath.Join(dir, "models-deepseek.json")); got != deepModels {
		t.Fatalf("未补建 models-deepseek.json: %q", got)
	}
	if got := readFile(t, statePath(t)); got != "mimo" {
		t.Fatalf(".active_profile 应为 mimo, 实际 %q", got)
	}
	if len(res.BackedUp) != 2 {
		t.Fatalf("应备份 2 个活动文件, 实际 %v", res.BackedUp)
	}

	// 切回 deepseek（config-deepseek.toml 未变，models-deepseek.json 为切离时补建）
	res, err = SwitchProfile("deepseek")
	if err != nil {
		t.Fatal(err)
	}
	if got := readFile(t, filepath.Join(dir, activeConfig)); got != readFile(t, filepath.Join(dir, "config-deepseek.toml")) {
		t.Fatalf("config.toml 未还原为 deepseek: %q", got)
	}
	if got := readFile(t, filepath.Join(dir, activeModels)); got != readFile(t, filepath.Join(dir, "models-deepseek.json")) {
		t.Fatalf("models.json 未还原为 deepseek: %q", got)
	}
	if got := readFile(t, statePath(t)); got != "deepseek" {
		t.Fatalf(".active_profile 应为 deepseek, 实际 %q", got)
	}

	// 切到当前活动应为 no-op
	res, err = SwitchProfile("deepseek")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(res.Message, "当前已是") {
		t.Fatalf("切到当前档案应提示已是, 实际 %q", res.Message)
	}
}

func TestSwitchTargetMissingModels(t *testing.T) {
	dir := withFakeCodex(t)
	deepCfg := "model = \"deepseek-v4-flash-ga-260731\"\nmodel_provider = \"ark\"\n"
	deepModels := `{"models":[{"slug":"deepseek-v4-flash-ga-260731"}]}`

	writeProfile(t, dir, "deepseek", "deepseek-v4-flash-ga-260731", "ark", true)
	writeProfile(t, dir, "b", "model-b", "b", false) // b 无 models 文件
	writeActive(t, dir, deepCfg, deepModels)

	res, err := SwitchProfile("b")
	if err != nil {
		t.Fatalf("目标缺 models 文件不应报错: %v", err)
	}
	if res.Warning == "" {
		t.Fatal("缺 models 文件应返回 Warning")
	}
	if got := readFile(t, filepath.Join(dir, activeConfig)); got != readFile(t, filepath.Join(dir, "config-b.toml")) {
		t.Fatalf("config.toml 应替换为 b: %q", got)
	}
	// models.json 应保持不变（不删除旧 catalog）
	if got := readFile(t, filepath.Join(dir, activeModels)); got != deepModels {
		t.Fatalf("缺 models 时不应改动 models.json: %q", got)
	}
}

func TestSwitchCustomActiveBacksUp(t *testing.T) {
	dir := withFakeCodex(t)
	writeProfile(t, dir, "mimo", "mimo-v2.5-pro", "mimo", true)
	customCfg := "model = \"custom-model\"\nmodel_provider = \"custom\"\n"
	writeActive(t, dir, customCfg, "") // 只有 config.toml

	res, err := SwitchProfile("mimo")
	if err != nil {
		t.Fatal(err)
	}
	if res.SyncedFrom != customProfile {
		t.Fatalf("SyncedFrom 应为自定义, 实际 %q", res.SyncedFrom)
	}
	// 自定义活动态不应生成 config-自定义.toml
	if _, err := os.Stat(filepath.Join(dir, "config-自定义.toml")); !os.IsNotExist(err) {
		t.Fatal("自定义活动态不应生成档案文件")
	}
	// 只备份了 config.toml（无活动 models.json）
	if len(res.BackedUp) != 1 {
		t.Fatalf("应备份 1 个文件, 实际 %v", res.BackedUp)
	}
	if got := readFile(t, filepath.Join(dir, activeConfig)); got == customCfg {
		t.Fatal("config.toml 应已替换为 mimo")
	}
}

func TestSwitchUnknownProfile(t *testing.T) {
	dir := withFakeCodex(t)
	writeProfile(t, dir, "mimo", "mimo-v2.5-pro", "mimo", true)
	writeActive(t, dir, "model = \"mimo-v2.5-pro\"\nmodel_provider = \"mimo\"\n", "")
	if _, err := SwitchProfile("ghost"); err == nil {
		t.Fatal("未知档案应报错")
	}
}
