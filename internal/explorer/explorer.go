// Package explorer 提供在系统文件管理器中打开文件/目录的功能，
// 替代原 PySide6 open_file_location。
package explorer

import (
	"fmt"
	"os"
	"os/exec"
	"runtime"
)

// Open 在系统文件管理器中打开文件或目录。
// Windows: explorer /select, 定位文件；目录直接打开。
func Open(path string) error {
	fi, err := os.Stat(path)
	if err != nil {
		return err
	}
	switch runtime.GOOS {
	case "windows":
		if fi.IsDir() {
			return exec.Command("explorer", path).Start()
		}
		return exec.Command("explorer", "/select,", path).Start()
	case "darwin":
		if fi.IsDir() {
			return exec.Command("open", path).Start()
		}
		return exec.Command("open", "-R", path).Start()
	default:
		// Linux
		if fi.IsDir() {
			return exec.Command("xdg-open", path).Start()
		}
		return exec.Command("xdg-open", fileDir(path)).Start()
	}
}

// OpenDir 打开一个目录（不存在时提示）。
func OpenDir(path string) error {
	if _, err := os.Stat(path); err != nil {
		if os.IsNotExist(err) {
			return fmt.Errorf("目录不存在: %s", path)
		}
		return err
	}
	return Open(path)
}

func fileDir(path string) string {
	i := len(path) - 1
	for i >= 0 && os.IsPathSeparator(path[i]) {
		i--
	}
	for i >= 0 && !os.IsPathSeparator(path[i]) {
		i--
	}
	if i < 0 {
		return "."
	}
	return path[:i]
}
