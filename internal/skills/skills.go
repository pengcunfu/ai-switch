// Package skills 负责扫描与管理 ~/.claude/skills 及项目 .claude/skills 下的
// Skills（SKILL.md 的解析、创建、编辑、删除），替代原 PySide6 skills_tab。
package skills

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

// Skill 表示一个 Skill 目录下的 SKILL.md 信息。
type Skill struct {
	Name                  string                 `json:"name"`
	Description           string                 `json:"description"`
	Context               string                 `json:"context"`
	Agent                 string                 `json:"agent"`
	AllowedTools          string                 `json:"allowed_tools"`
	ArgumentHint          string                 `json:"argument_hint"`
	UserInvocable         bool                   `json:"user_invocable"`
	DisableModelInvocation bool                  `json:"disable_model_invocation"`
	Path                  string                 `json:"path"`
	Scope                 string                 `json:"scope"`
	Content               string                 `json:"content"`
	Frontmatter           map[string]interface{} `json:"frontmatter"`
}

// baseDir 返回指定作用域的 skills 目录。
// global -> ~/.claude/skills；project -> <projectDir>/.claude/skills（未指定则取当前目录）。
func baseDir(scope, projectDir string) (string, error) {
	if scope == "project" {
		base := projectDir
		if base == "" {
			cwd, err := os.Getwd()
			if err != nil {
				return "", err
			}
			base = cwd
		}
		return filepath.Join(base, ".claude", "skills"), nil
	}
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, ".claude", "skills"), nil
}

// List 扫描指定作用域下的所有 Skills。
func List(scope, projectDir string) ([]Skill, error) {
	dir, err := baseDir(scope, projectDir)
	if err != nil {
		return nil, err
	}
	var result []Skill
	entries, err := os.ReadDir(dir)
	if err != nil {
		if os.IsNotExist(err) {
			return result, nil
		}
		return nil, err
	}
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		mdPath := filepath.Join(dir, entry.Name(), "SKILL.md")
		info, err := parseFile(mdPath, scope)
		if err != nil {
			continue
		}
		result = append(result, info)
	}
	sort.Slice(result, func(i, j int) bool { return result[i].Name < result[j].Name })
	return result, nil
}

// parseFile 解析单个 SKILL.md 文件。
func parseFile(path, scope string) (Skill, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return Skill{}, err
	}
	text := string(content)
	frontmatter, body := splitFrontmatter(text)

	name, _ := frontmatter["name"].(string)
	if name == "" {
		name = filepath.Base(filepath.Dir(path))
	}
	desc, _ := frontmatter["description"].(string)
	userInvocable := true
	if v, ok := frontmatter["user-invocable"].(bool); ok {
		userInvocable = v
	}
	disableModel := false
	if v, ok := frontmatter["disable-model-invocation"].(bool); ok {
		disableModel = v
	}

	return Skill{
		Name:                   name,
		Description:            desc,
		Context:                asString(frontmatter["context"]),
		Agent:                  asString(frontmatter["agent"]),
		AllowedTools:           asString(frontmatter["allowed-tools"]),
		ArgumentHint:           asString(frontmatter["argument-hint"]),
		UserInvocable:          userInvocable,
		DisableModelInvocation: disableModel,
		Path:                   path,
		Scope:                  scope,
		Content:                body,
		Frontmatter:            frontmatter,
	}, nil
}

// splitFrontmatter 解析 SKILL.md 的 YAML frontmatter（--- 包裹的头部）与正文。
func splitFrontmatter(text string) (map[string]interface{}, string) {
	if !strings.HasPrefix(text, "---") {
		return map[string]interface{}{}, strings.TrimSpace(text)
	}
	parts := strings.SplitN(text, "---", 3)
	if len(parts) < 3 {
		return map[string]interface{}{}, strings.TrimSpace(text)
	}
	fm := map[string]interface{}{}
	if err := yaml.Unmarshal([]byte(parts[1]), &fm); err != nil || fm == nil {
		fm = map[string]interface{}{}
	}
	return fm, strings.TrimSpace(parts[2])
}

// Save 创建或更新一个 Skill。若名称变更（重命名），先移动旧目录。
func Save(scope, projectDir string, data map[string]interface{}) error {
	dir, err := baseDir(scope, projectDir)
	if err != nil {
		return err
	}
	name := asString(data["name"])
	if name == "" {
		return fmt.Errorf("Skill 名称不能为空")
	}
	// 重命名支持：oldName 存在且不等于新名称时移动目录
	if oldName := asString(data["oldName"]); oldName != "" && oldName != name {
		oldDir := filepath.Join(dir, oldName)
		newDir := filepath.Join(dir, name)
		if _, err := os.Stat(oldDir); err == nil && oldDir != newDir {
			if err := os.Rename(oldDir, newDir); err != nil {
				return fmt.Errorf("重命名 Skill 目录失败: %w", err)
			}
		}
	}
	skillDir := filepath.Join(dir, name)
	if err := os.MkdirAll(skillDir, 0o755); err != nil {
		return err
	}
	mdPath := filepath.Join(skillDir, "SKILL.md")
	full := buildMarkdown(data)
	if err := os.WriteFile(mdPath, []byte(full), 0o644); err != nil {
		return err
	}
	return nil
}

// buildMarkdown 依据 data 构建 SKILL.md 内容。
func buildMarkdown(data map[string]interface{}) string {
	var lines []string
	lines = append(lines, "---")
	lines = append(lines, "name: "+asString(data["name"]))
	if v := asString(data["description"]); v != "" {
		lines = append(lines, "description: "+v)
	}
	if v := asString(data["context"]); v != "" {
		lines = append(lines, "context: "+v)
	}
	if v := asString(data["agent"]); v != "" {
		lines = append(lines, "agent: "+v)
	}
	if v := asString(data["allowed_tools"]); v != "" {
		lines = append(lines, "allowed-tools: "+v)
	}
	if v, ok := data["user_invocable"].(bool); ok && !v {
		lines = append(lines, "user-invocable: false")
	}
	if v, ok := data["disable_model_invocation"].(bool); ok && v {
		lines = append(lines, "disable-model-invocation: true")
	}
	if v := asString(data["argument_hint"]); v != "" {
		lines = append(lines, "argument-hint: "+v)
	}
	lines = append(lines, "---")
	content := asString(data["content"])
	full := strings.Join(lines, "\n") + "\n"
	if content != "" {
		full += strings.TrimSpace(content) + "\n"
	}
	return full
}

// Delete 删除指定名称的 Skill 目录。
func Delete(scope, projectDir, name string) error {
	dir, err := baseDir(scope, projectDir)
	if err != nil {
		return err
	}
	skillDir := filepath.Join(dir, name)
	if _, err := os.Stat(skillDir); err != nil {
		if os.IsNotExist(err) {
			return nil
		}
		return err
	}
	return os.RemoveAll(skillDir)
}

// asString 从 map 中安全取字符串。
func asString(v interface{}) string {
	if v == nil {
		return ""
	}
	if s, ok := v.(string); ok {
		return s
	}
	return fmt.Sprintf("%v", v)
}
