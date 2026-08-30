// Package mcp 使用 mcp-go 客户端实现 MCP 服务器连接测试与工具/资源列表，
// 替代原 PySide6 mcp_servers_tab 与 mcp_tools_dialog 中基于 Python mcp SDK 的逻辑。
package mcp

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"strings"
	"time"

	"github.com/mark3labs/mcp-go/client"
	"github.com/mark3labs/mcp-go/mcp"
)

// ServerConfig 单个 MCP 服务器的配置。
type ServerConfig struct {
	Command string            `json:"command"`
	Args    []string          `json:"args"`
	Env     map[string]string `json:"env"`
}

// TestResult MCP 连接测试结果。
type TestResult struct {
	Success    bool                   `json:"success"`
	Message    string                 `json:"message,omitempty"`
	Error      string                 `json:"error,omitempty"`
	ServerInfo map[string]interface{} `json:"serverInfo,omitempty"`
}

// ListResult MCP 工具与资源列表结果。
type ListResult struct {
	Tools     []map[string]interface{} `json:"tools"`
	Resources []map[string]interface{} `json:"resources"`
}

// buildEnv 合并进程环境与配置 env（配置 env 覆盖当前环境），
// 与 Python StdioServerParameters 的 env 合并语义保持一致。
func buildEnv(env map[string]string) []string {
	if len(env) == 0 {
		return nil // nil 时子进程继承父环境
	}
	merged := map[string]string{}
	for _, kv := range os.Environ() {
		if i := strings.IndexByte(kv, '='); i > 0 {
			merged[kv[:i]] = kv[i+1:]
		}
	}
	for k, v := range env {
		merged[k] = v
	}
	out := make([]string, 0, len(merged))
	for k, v := range merged {
		out = append(out, k+"="+v)
	}
	return out
}

func connect(cfg ServerConfig) (*client.Client, error) {
	if strings.TrimSpace(cfg.Command) == "" {
		return nil, errors.New("未配置命令")
	}
	return client.NewStdioMCPClient(cfg.Command, buildEnv(cfg.Env), cfg.Args...)
}

func initializeRequest() mcp.InitializeRequest {
	return mcp.InitializeRequest{
		Params: mcp.InitializeParams{
			ProtocolVersion: mcp.LATEST_PROTOCOL_VERSION,
			Capabilities:    mcp.ClientCapabilities{},
			ClientInfo: mcp.Implementation{
				Name:    "claude-config-manager",
				Version: "1.0.0",
			},
		},
	}
}

func classifyError(err error, command string) string {
	if errors.Is(err, os.ErrNotExist) {
		return "找不到命令: " + command
	}
	if errors.Is(err, os.ErrPermission) {
		return "权限不足，无法执行: " + command
	}
	return err.Error()
}

// TestConnection 测试 MCP 服务器连接（5 秒超时）。
func TestConnection(cfg ServerConfig) *TestResult {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	c, err := connect(cfg)
	if err != nil {
		return &TestResult{Success: false, Error: classifyError(err, cfg.Command)}
	}
	defer c.Close()

	res, err := c.Initialize(ctx, initializeRequest())
	if err != nil {
		if errors.Is(err, context.DeadlineExceeded) {
			return &TestResult{Success: false, Error: "连接超时 (5秒)。服务器可能启动缓慢或配置错误。"}
		}
		return &TestResult{Success: false, Error: "初始化失败: " + classifyError(err, cfg.Command)}
	}

	return &TestResult{
		Success: true,
		Message: "连接成功",
		ServerInfo: map[string]interface{}{
			"name":    res.ServerInfo.Name,
			"version": res.ServerInfo.Version,
		},
	}
}

// ListToolsAndResources 列出 MCP 服务器的工具与资源（10 秒超时）。
func ListToolsAndResources(cfg ServerConfig) (*ListResult, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	c, err := connect(cfg)
	if err != nil {
		return nil, errors.New(classifyError(err, cfg.Command))
	}
	defer c.Close()

	if _, err := c.Initialize(ctx, initializeRequest()); err != nil {
		if errors.Is(err, context.DeadlineExceeded) {
			return nil, errors.New("连接超时 (10秒)。MCP 服务器可能启动缓慢或无响应。")
		}
		return nil, errors.New("初始化失败: " + classifyError(err, cfg.Command))
	}

	result := &ListResult{Tools: []map[string]interface{}{}, Resources: []map[string]interface{}{}}

	if tr, err := c.ListTools(ctx, mcp.ListToolsRequest{}); err == nil {
		for _, t := range tr.Tools {
			schema := "无"
			if t.InputSchema.Type != "" {
				if b, err := json.Marshal(t.InputSchema); err == nil {
					schema = string(b)
				}
			}
			result.Tools = append(result.Tools, map[string]interface{}{
				"name":        t.Name,
				"title":       t.Title,
				"description": t.Description,
				"inputSchema": schema,
			})
		}
	}

	if rr, err := c.ListResources(ctx, mcp.ListResourcesRequest{}); err == nil {
		for _, r := range rr.Resources {
			result.Resources = append(result.Resources, map[string]interface{}{
				"uri":         r.URI,
				"name":        r.Name,
				"description": r.Description,
				"mimeType":    r.MIMEType,
			})
		}
	}

	return result, nil
}
