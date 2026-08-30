// Command buildver 是打包前的版本递增工具，由 wails.json 的 preBuildHooks 触发，
// 替代原 PySide6 build.py 的 bump_build_number。每次执行将
// internal/version/version.go 中的 Build 递增 1 并写回。
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
)

const versionFilePath = "internal/version/version.go"

// findVersionFile 从当前目录向上逐级查找 version.go，兼容 wails hook（build/bin）与手动运行。
func findVersionFile() (string, error) {
	dir, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for {
		candidate := filepath.Join(dir, versionFilePath)
		if _, err := os.Stat(candidate); err == nil {
			return candidate, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			cwd, _ := os.Getwd()
			return "", fmt.Errorf("未找到 %s（从 %s 向上查找）", versionFilePath, cwd)
		}
		dir = parent
	}
}

func main() {
	path, err := findVersionFile()
	if err != nil {
		fmt.Fprintln(os.Stderr, "buildver:", err)
		os.Exit(1)
	}

	content, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, "buildver: 读取版本文件失败:", err)
		os.Exit(1)
	}

	re := regexp.MustCompile(`Build\s*=\s*\d+`)
	match := re.Find(content)
	if match == nil {
		fmt.Fprintln(os.Stderr, "buildver: 未找到 Build 字段")
		os.Exit(1)
	}

	reNum := regexp.MustCompile(`\d+`)
	numStr := reNum.FindString(string(match))
	build, err := strconv.Atoi(numStr)
	if err != nil {
		fmt.Fprintln(os.Stderr, "buildver: 解析编译号失败:", err)
		os.Exit(1)
	}
	build++

	updated := re.ReplaceAll(content, []byte(fmt.Sprintf("Build = %d", build)))
	if err := os.WriteFile(path, updated, 0o644); err != nil {
		fmt.Fprintln(os.Stderr, "buildver: 写入版本文件失败:", err)
		os.Exit(1)
	}

	fmt.Printf("已递增编译号 -> Build = %d\n", build)
}
