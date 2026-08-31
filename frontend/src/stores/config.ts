import { defineStore } from 'pinia'
import {
  GetConfig, GetConfigPath, SaveConfig,
  GetAppDataPath, GetAppState, SaveAppState,
} from '../../wailsjs/go/main/App'

/**
 * 全局配置状态。所有页面共享同一个内存中的 cfg 对象，
 * 各页面修改后调用 save() 一次性写回 ~/.claude.json（Go 侧自动 .bak 备份）。
 *
 * 应用自身状态（activeTool / uiux / theme 等界面偏好）单独存于
 * appState，写入 <文档>/FNSoftware/.aiswitch/app-state.json，
 * 不再污染 ~/.claude.json。
 */
export const useConfigStore = defineStore('config', {
  state: () => ({
    cfg: {} as Record<string, any>,
    configPath: '',
    appState: {} as Record<string, any>,
    appDataPath: '',
    statusMessage: '就绪',
  }),
  getters: {
    theme: (s) => s.appState.theme ?? {},
    uiux: (s) => s.appState.uiux ?? {},
    memory: (s) => s.cfg.memory ?? {},
    modelConfiguration: (s) => s.cfg.modelConfiguration ?? {},
    contextConfiguration: (s) => s.cfg.contextConfiguration ?? {},
    usageLimits: (s) => s.cfg.usageLimits ?? {},
    permissions: (s) => s.cfg.permissions ?? {},
    globalToolPermissions: (s) => s.cfg.globalToolPermissions ?? {},
    projects: (s) => s.cfg.projects ?? {},
    githubRepoPaths: (s) => s.cfg.githubRepoPaths ?? {},
    mcpServers: (s) => s.cfg.mcpServers ?? {},
    integrations: (s) => s.cfg.integrations ?? {},
    developerTools: (s) => s.cfg.developerTools ?? {},
    hooks: (s) => s.cfg.hooks ?? {},
    providerProfiles: (s) => s.cfg.providerProfiles ?? [],
    activeProviderProfile: (s) => s.cfg.activeProviderProfile ?? '',
    cachedStatsigGates: (s) => s.cfg.cachedStatsigGates ?? {},
    cachedGrowthBookFeatures: (s) => s.cfg.cachedGrowthBookFeatures ?? {},
    skillUsage: (s) => s.cfg.skillUsage ?? {},
  },
  actions: {
    /** 加载配置到内存，并确保各分节对象存在，便于视图安全绑定 */
    async load() {
      this.cfg = await GetConfig()
      this.configPath = await GetConfigPath()
      this.appState = await GetAppState()
      this.appDataPath = await GetAppDataPath()
      this.normalize()
      await this.migrateAppState()
      this.statusMessage = '就绪'
    },
    /** 补齐缺失的分节（空对象，避免模板访问 undefined 报错） */
    normalize() {
      const objectSections = [
        'memory', 'permissions', 'globalToolPermissions',
        'projects', 'integrations', 'developerTools', 'hooks',
        'modelConfiguration', 'contextConfiguration', 'usageLimits',
        'mcpServers', 'githubRepoPaths', 'cachedStatsigGates',
        'cachedGrowthBookFeatures', 'skillUsage',
      ]
      for (const key of objectSections) {
        if (typeof this.cfg[key] !== 'object' || this.cfg[key] === null) {
          this.cfg[key] = {}
        }
      }
      if (!Array.isArray(this.cfg.providerProfiles)) {
        this.cfg.providerProfiles = []
      }
      if (!Array.isArray(this.cfg.hooks?.preHooks)) this.cfg.hooks.preHooks = []
      if (!Array.isArray(this.cfg.hooks?.postHooks)) this.cfg.hooks.postHooks = []
      // 应用状态（app-state.json）
      if (typeof this.appState.uiux !== 'object' || this.appState.uiux === null) {
        this.appState.uiux = {}
      }
      if (typeof this.appState.uiux.notifications !== 'object' || this.appState.uiux.notifications === null) {
        this.appState.uiux.notifications = {}
      }
      if (typeof this.appState.theme !== 'object' || this.appState.theme === null) {
        this.appState.theme = {}
      }
      if (typeof this.appState.theme.customColors !== 'object' || this.appState.theme.customColors === null) {
        this.appState.theme.customColors = {}
      }
      if (typeof this.appState.activeTool !== 'string' || !this.appState.activeTool) {
        this.appState.activeTool = 'claude'
      }
      // integrations / developerTools 二级嵌套对象
      if (typeof this.cfg.integrations.github !== 'object' || this.cfg.integrations.github === null) {
        this.cfg.integrations.github = {}
      }
      if (typeof this.cfg.integrations.github.features !== 'object' || this.cfg.integrations.github.features === null) {
        this.cfg.integrations.github.features = {}
      }
      if (typeof this.cfg.integrations.slack !== 'object' || this.cfg.integrations.slack === null) {
        this.cfg.integrations.slack = {}
      }
      if (typeof this.cfg.integrations.slack.notifications !== 'object' || this.cfg.integrations.slack.notifications === null) {
        this.cfg.integrations.slack.notifications = {}
      }
      if (!Array.isArray(this.cfg.integrations.customCommands)) {
        this.cfg.integrations.customCommands = []
      }
      if (typeof this.cfg.developerTools.costTracking !== 'object' || this.cfg.developerTools.costTracking === null) {
        this.cfg.developerTools.costTracking = {}
      }
      if (typeof this.cfg.developerTools.apiMonitoring !== 'object' || this.cfg.developerTools.apiMonitoring === null) {
        this.cfg.developerTools.apiMonitoring = {}
      }
    },
    /**
     * 一次性迁移：把旧版本写入 ~/.claude.json 的应用偏好（uiux/theme）
     * 迁移到 app-state.json 并从 cfg 中删除并持久化，避免后续 save() 写回污染。
     */
    async migrateAppState() {
      let changed = false
      if (typeof this.cfg.uiux === 'object' && this.cfg.uiux !== null && Object.keys(this.cfg.uiux).length > 0
        && Object.keys(this.appState.uiux).length === 0) {
        this.appState.uiux = this.cfg.uiux
        delete this.cfg.uiux
        changed = true
      }
      if (typeof this.cfg.theme === 'object' && this.cfg.theme !== null && Object.keys(this.cfg.theme).length > 0
        && Object.keys(this.appState.theme).length === 0) {
        this.appState.theme = this.cfg.theme
        delete this.cfg.theme
        changed = true
      }
      this.appState.activeTool = this.appState.uiux?.activeTool ?? 'claude'
      if (changed) {
        await SaveAppState(this.appState)
        await SaveConfig(this.cfg)
      }
    },
    /** 保存整个配置（Go 侧自动备份 .bak） */
    async save() {
      await SaveConfig(this.cfg)
      this.statusMessage = '配置已保存'
    },
    /** 保存应用自身状态到 app-state.json */
    async saveAppState() {
      await SaveAppState(this.appState)
      this.statusMessage = '应用状态已保存'
    },
    /** 保存并提示 */
    async saveWithMessage() {
      await this.save()
      return true
    },
  },
})
