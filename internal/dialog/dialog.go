// Package dialog 封装 Wails 原生文件对话框，替代原 PySide6 QFileDialog。
package dialog

import (
	"context"

	"github.com/wailsapp/wails/v2/pkg/runtime"
)

// OpenDirectory 打开目录选择对话框，返回选中目录（取消则返回空字符串）。
func OpenDirectory(ctx context.Context, title string) (string, error) {
	return runtime.OpenDirectoryDialog(ctx, runtime.OpenDialogOptions{
		Title: title,
	})
}

// OpenFile 打开文件选择对话框，filter 形如 "JSON 文件 (*.json);;所有文件 (*.*)"。
func OpenFile(ctx context.Context, title, filter string) (string, error) {
	return runtime.OpenFileDialog(ctx, runtime.OpenDialogOptions{
		Title:   title,
		Filters: parseFilters(filter),
	})
}

// SaveFile 打开保存文件对话框。
func SaveFile(ctx context.Context, title, defaultName string) (string, error) {
	return runtime.SaveFileDialog(ctx, runtime.SaveDialogOptions{
		Title:           title,
		DefaultFilename: defaultName,
	})
}

// parseFilters 将 Qt 风格过滤器字符串转为 Wails FileFilter 列表。
// 形如 "JSON 文件 (*.json);;所有文件 (*.*)"
func parseFilters(filter string) []runtime.FileFilter {
	var result []runtime.FileFilter
	cur := ""
	for _, part := range splitOnSemicolon(filter) {
		part = trim(part)
		if part == "" {
			continue
		}
		if cur != "" {
			result = append(result, runtime.FileFilter{
				DisplayName: cur,
				Pattern:     part,
			})
			cur = ""
		} else {
			cur = part
		}
	}
	return result
}

func splitOnSemicolon(s string) []string {
	var parts []string
	last := 0
	for i := 0; i < len(s); i++ {
		if s[i] == ';' && (i+1 >= len(s) || s[i+1] != ';') {
			parts = append(parts, s[last:i])
			last = i + 1
		}
	}
	parts = append(parts, s[last:])
	return parts
}

func trim(s string) string {
	start := 0
	for start < len(s) && (s[start] == ' ' || s[start] == '\t') {
		start++
	}
	end := len(s)
	for end > start && (s[end-1] == ' ' || s[end-1] == '\t') {
		end--
	}
	return s[start:end]
}
