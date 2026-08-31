//go:build windows

package appdata

import "golang.org/x/sys/windows"

// documentsDir 返回用户文档目录（Windows 已知文件夹，支持重定向后的路径，如 D:\Data\Documents）。
func documentsDir() (string, error) {
	return windows.KnownFolderPath(windows.FOLDERID_Documents, windows.KF_FLAG_CREATE)
}
