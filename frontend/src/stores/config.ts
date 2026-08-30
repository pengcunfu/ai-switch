import { defineStore } from 'pinia'
import { GetConfig, GetConfigPath, SaveConfig } from '../../wailsjs/go/main/App'

/**
 * 全局配置状态。所有页面共享同一个内存中的 config 对象，
 * 各页面修改后调用 save() 一次性写回 ~/.claude.json（Go 侧自动 .bak 备份）。
 */
export const useConfigStore = defineStore('config', {
  state: () => ({
    cfg: {} as Record<string, any>,
    configPath: '',
    statusMessage: '就绪',
  }),
  getters: {
    theme: (s) => s.cfg.theme ?? {},
    uiux: (s) => s.cfg.uiux ?? {},
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
      this.normalize()
      this.statusMessage = '就绪'
    },
    /** 补齐缺失的分节（空对象，避免模板访问 undefined 报错） */
    normalize() {
      const objectSections = [
        'theme', 'uiux', 'memory', 'permissions', 'globalToolPermissions',
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
    },
    /** 保存整个配置（Go 侧自动备份 .bak） */
    async save() {
      await SaveConfig(this.cfg)
      this.statusMessage = '配置已保存'
    },
    /** 保存并提示 */
    async saveWithMessage() {
      await this.save()
      return true
    },
  },
})
