//go:build !windows

package appdata

import (
	"os"
	"path/filepath"
)

// documentsDir 返回用户文档目录（非 Windows 平台回退到 ~/Documents）。
func documentsDir() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}
	return filepath.Join(home, "Documents"), nil
}
