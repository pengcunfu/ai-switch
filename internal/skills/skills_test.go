package skills

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestSplitFrontmatter(t *testing.T) {
	content := "---\nname: demo\nuser-invocable: false\n---\n正文内容"
	fm, body := splitFrontmatter(content)
	if fm["name"] != "demo" {
		t.Fatalf("name 解析错误: %v", fm)
	}
	if fm["user-invocable"] != false {
		t.Fatalf("bool 解析错误: %v", fm["user-invocable"])
	}
	if body != "正文内容" {
		t.Fatalf("正文解析错误: %q", body)
	}
}

func TestSaveListDeleteProjectScope(t *testing.T) {
	dir := t.TempDir()
	data := map[string]interface{}{
		"name":                  "my-skill",
		"description":           "测试技能",
		"user_invocable":        true,
		"disable_model_invocation": false,
		"content":               "技能内容第1行\n技能内容第2行",
	}
	if err := Save("project", dir, data); err != nil {
		t.Fatal(err)
	}

	// 校验文件存在
	md := filepath.Join(dir, ".claude", "skills", "my-skill", "SKILL.md")
	raw, err := os.ReadFile(md)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasPrefix(string(raw), "---\nname: my-skill") {
		t.Fatalf("frontmatter 生成错误:\n%s", raw)
	}

	list, err := List("project", dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(list) != 1 {
		t.Fatalf("期望 1 个 skill，实际 %d", len(list))
	}
	if list[0].Name != "my-skill" || list[0].Description != "测试技能" {
		t.Fatalf("skill 信息错误: %+v", list[0])
	}
	if !strings.Contains(list[0].Content, "技能内容第2行") {
		t.Fatalf("正文未正确保留: %q", list[0].Content)
	}

	if err := Delete("project", dir, "my-skill"); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(dir, ".claude", "skills", "my-skill")); !os.IsNotExist(err) {
		t.Fatal("skill 目录未删除")
	}
}

func TestRenameSkill(t *testing.T) {
	dir := t.TempDir()
	if err := Save("project", dir, map[string]interface{}{"name": "old-name", "content": "x"}); err != nil {
		t.Fatal(err)
	}
	// 重命名：带 oldName
	if err := Save("project", dir, map[string]interface{}{
		"name": "new-name", "oldName": "old-name", "content": "y",
	}); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(dir, ".claude", "skills", "old-name")); !os.IsNotExist(err) {
		t.Fatal("旧目录应已重命名")
	}
	if _, err := os.Stat(filepath.Join(dir, ".claude", "skills", "new-name", "SKILL.md")); err != nil {
		t.Fatalf("新目录应存在: %v", err)
	}
}

func TestListMissingDirReturnsEmpty(t *testing.T) {
	dir := t.TempDir() // 不创建 skills 目录
	list, err := List("project", dir)
	if err != nil {
		t.Fatal(err)
	}
	if len(list) != 0 {
		t.Fatalf("期望空列表，实际 %d", len(list))
	}
}
