// Package version 统一管理应用版本信息，替代原 app/version.py。
package version

import "fmt"

const Version = "1.0.0"

// Build 编译版本号，打包时由 scripts 自动递增。
var Build = 8

// Label 返回用于界面显示的完整版本字符串。
func Label() string {
	return fmt.Sprintf("版本 %s · 编译 %d", Version, Build)
}

// Map 返回供前端展示的版本信息对象。
func Map() map[string]interface{} {
	return map[string]interface{}{
		"version": Version,
		"build":   Build,
		"label":   Label(),
	}
}
