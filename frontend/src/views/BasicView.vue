<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  NCard, NForm, NFormItem, NCheckbox, NSelect, NInput, NButton,
  NSpace, NText, useMessage, useDialog,
} from 'naive-ui'
import { useConfigStore } from '../stores/config'
import {
  ApplyEnvVars, ExportConfig, ImportConfig, ResetConfig,
  SaveFile, PickFile,
} from '../../wailsjs/go/main/App'

const store = useConfigStore()
const message = useMessage()
const dialog = useDialog()

// ============ 通用设置 ============
const autoUpdates = computed({
  get: () => store.cfg.autoUpdates ?? false,
  set: (v: boolean) => { store.cfg.autoUpdates = v },
})
const installMethod = computed(() => store.cfg.installMethod ?? '未知')

// ============ 服务商档案 ============
const profiles = computed(() => store.cfg.providerProfiles ?? [])
const activeProfileName = computed(() => store.cfg.activeProviderProfile ?? '')

function ensureProfiles() {
  if (!Array.isArray(store.cfg.providerProfiles) || store.cfg.providerProfiles.length === 0) {
    store.cfg.providerProfiles = [
      { name: 'Anthropic 默认', authToken: '', baseUrl: 'https://api.anthropic.com', model: 'claude-sonnet-4-6' },
    ]
    store.cfg.activeProviderProfile = 'Anthropic 默认'
  }
}

const activeProfile = computed(() => {
  ensureProfiles()
  return store.cfg.providerProfiles.find((p: any) => p.name === activeProfileName.value) ?? store.cfg.providerProfiles[0]
})

const profileOptions = computed(() => profiles.value.map((p: any) => ({ label: p.name, value: p.name })))

function onProfileChange(name: string) {
  store.cfg.activeProviderProfile = name
}

function addProfile() {
  let name = ''
  // 简单输入弹窗
  const input = prompt('请输入档案名称:')
  if (!input || !input.trim()) return
  name = input.trim()
  if (profiles.value.some((p: any) => p.name === name)) {
    message.warning(`档案 '${name}' 已存在!`)
    return
  }
  store.cfg.providerProfiles.push({ name, authToken: '', baseUrl: '', model: '' })
  store.cfg.activeProviderProfile = name
  message.success(`已新增档案 '${name}'`)
}

function deleteProfile() {
  if (profiles.value.length <= 1) {
    message.warning('至少保留一个服务商档案!')
    return
  }
  dialog.warning({
    title: '确认删除',
    content: `确定要删除档案 '${activeProfileName.value}' 吗?`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      store.cfg.providerProfiles = store.cfg.providerProfiles.filter((p: any) => p.name !== activeProfileName.value)
      store.cfg.activeProviderProfile = store.cfg.providerProfiles[0].name
    },
  })
}

async function applyEnvVars() {
  ensureProfiles()
  const profile = activeProfile.value
  if (!profile) {
    message.warning('没有选中的服务商档案!')
    return
  }
  const hasValue = profile.authToken || profile.baseUrl || profile.model
  if (!hasValue) {
    message.warning('当前档案所有字段为空，无需设置!')
    return
  }
  try {
    const result = await ApplyEnvVars(profile)
    message.success(result.message || '环境变量已设置')
    store.statusMessage = '环境变量已应用: ' + profile.name
    // 应用环境变量前先持久化档案
    await store.save()
  } catch (e: any) {
    message.error(String(e))
  }
}

// ============ 迁移状态 ============
const migrationItems = computed(() => [
  { label: 'Sonnet 4.5:', done: store.cfg.sonnet45MigrationComplete === true },
  { label: 'Opus 4.5:', done: store.cfg.opus45MigrationComplete === true },
  { label: 'Thinking:', done: store.cfg.thinkingMigrationComplete === true },
  { label: '市场插件尝试安装:', done: store.cfg.officialMarketplaceAutoInstallAttempted === true },
  { label: '市场插件已安装:', done: store.cfg.officialMarketplaceAutoInstalled === true },
])

// ============ 用户信息 ============
const userID = computed(() => store.cfg.userID ?? '未知')
const firstStartInfo = computed(() => {
  const raw = store.cfg.firstStartTime ?? ''
  if (!raw) return { time: '未知', duration: '未知' }
  const d = new Date(raw.endsWith('Z') ? raw : raw + 'Z')
  if (isNaN(d.getTime())) return { time: raw, duration: '未知' }
  const pad = (n: number) => String(n).padStart(2, '0')
  const time = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
  const diff = Date.now() - d.getTime()
  const days = Math.floor(diff / 86400000)
  const hours = Math.floor((diff % 86400000) / 3600000)
  return { time, duration: `${days} 天 ${hours} 小时` }
})

// ============ 备份恢复 ============
async function exportConfig() {
  const path = await SaveFile('导出配置', 'claude_config_backup.json')
  if (!path) return
  try {
    await ExportConfig(store.cfg, path)
    message.success(`配置已导出到: ${path}`)
  } catch (e: any) {
    message.error(`导出失败: ${e}`)
  }
}

async function importConfig() {
  const path = await PickFile('导入配置', 'JSON 文件 (*.json);;所有文件 (*.*)')
  if (!path) return
  dialog.warning({
    title: '确认导入',
    content: '导入配置将覆盖当前配置，确定要继续吗?',
    positiveText: '导入',
    negativeText: '取消',
    async onPositiveClick() {
      try {
        const imported = await ImportConfig(path)
        store.cfg = imported
        await store.save()
        message.success('配置已导入!')
      } catch (e: any) {
        message.error(`导入失败: ${e}`)
      }
    },
  })
}

function resetConfig() {
  dialog.warning({
    title: '确认重置',
    content: '重置配置将删除所有自定义设置!\n此操作不可撤销。\n\n确定要继续吗?',
    positiveText: '重置',
    negativeText: '取消',
    async onPositiveClick() {
      try {
        const cfg = await ResetConfig()
        store.cfg = cfg
        await store.save()
        message.success('配置已重置为默认值!')
      } catch (e: any) {
        message.error(`重置失败: ${e}`)
      }
    },
  })
}

async function saveSettings() {
  try {
    ensureProfiles()
    await store.save()
    message.success('通用设置已保存!')
  } catch (e: any) {
    message.error(`保存设置失败: ${e}`)
  }
}
</script>

<template>
  <n-space vertical :size="12" style="max-width: 860px">
    <!-- 通用设置 -->
    <n-card size="small" title="通用设置">
      <n-form-item label="启用自动更新" label-placement="left">
        <n-checkbox v-model:checked="autoUpdates">启用自动更新</n-checkbox>
      </n-form-item>
      <n-form-item label="安装方式" label-placement="left">
        <n-text>{{ installMethod }}</n-text>
      </n-form-item>
    </n-card>

    <!-- 服务商配置 -->
    <n-card size="small" title="服务商配置">
      <n-space vertical :size="12">
        <n-space :size="8" align="center">
          <n-text>当前档案:</n-text>
          <n-select
            v-model:value="store.cfg.activeProviderProfile"
            :options="profileOptions"
            style="width: 240px"
            @update:value="onProfileChange"
          />
          <n-button size="small" @click="addProfile">新增</n-button>
          <n-button size="small" @click="deleteProfile">删除</n-button>
        </n-space>

        <n-grid cols="1" :x-gap="12">
          <n-gi>
            <n-form label-placement="left" label-width="120">
              <n-form-item label="Auth Token:">
                <n-input v-model:value="activeProfile.authToken" type="password" show-password-on="click" placeholder="输入 API 认证令牌" />
              </n-form-item>
              <n-form-item label="Base URL:">
                <n-input v-model:value="activeProfile.baseUrl" placeholder="https://api.anthropic.com" />
              </n-form-item>
              <n-form-item label="Model:">
                <n-input v-model:value="activeProfile.model" placeholder="claude-sonnet-4-6" />
              </n-form-item>
            </n-form>
          </n-gi>
        </n-grid>

        <n-button size="small" type="warning" @click="applyEnvVars">应用环境变量（写入系统）</n-button>
      </n-space>
    </n-card>

    <!-- 迁移状态 -->
    <n-card size="small" title="迁移状态">
      <n-grid cols="2" :x-gap="12" :y-gap="8">
        <n-gi v-for="item in migrationItems" :key="item.label">
          <n-space :size="8" align="center">
            <n-text>{{ item.label }}</n-text>
            <n-text :type="item.done ? 'success' : 'error'">{{ item.done ? '已完成' : '未完成' }}</n-text>
          </n-space>
        </n-gi>
      </n-grid>
    </n-card>

    <!-- 用户信息 -->
    <n-card size="small" title="用户信息">
      <n-form label-placement="left" label-width="120">
        <n-form-item label="用户ID:">
          <n-text style="word-break: break-all; user-select: text">{{ userID }}</n-text>
        </n-form-item>
        <n-form-item label="首次使用时间:">
          <n-text>{{ firstStartInfo.time }}</n-text>
        </n-form-item>
        <n-form-item label="使用时长:">
          <n-text>{{ firstStartInfo.duration }}</n-text>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 备份恢复 -->
    <n-card size="small" title="配置备份与恢复">
      <n-space :size="8">
        <n-button size="small" @click="exportConfig">导出配置</n-button>
        <n-button size="small" @click="importConfig">导入配置</n-button>
        <n-button size="small" type="error" @click="resetConfig">重置为默认</n-button>
      </n-space>
      <n-text depth="3" style="font-size: 12px; display: block; margin-top: 8px">提示: 保存配置时会自动创建 .bak 备份文件</n-text>
    </n-card>

    <div style="display: flex; justify-content: flex-end">
      <n-button type="primary" size="small" @click="saveSettings">保存设置</n-button>
    </div>
  </n-space>
</template>
