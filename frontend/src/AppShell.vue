<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  NLayout, NLayoutHeader, NLayoutContent, NLayoutFooter,
  NMenu, NSpace, NButton, NSelect, NText, useMessage,
} from 'naive-ui'
import { useConfigStore } from './stores/config'
import { OpenInExplorer, OpenSkillsFolder, OpenClaudeFolder } from '../wailsjs/go/main/App'
import AboutModal from './components/common/AboutModal.vue'
import ConfigJsonModal from './components/common/ConfigJsonModal.vue'

const store = useConfigStore()
const route = useRoute()
const router = useRouter()
const message = useMessage()

const showAbout = ref(false)
const showConfigJson = ref(false)

// ============ 工具切换（Claude Code / Codex，两套独立界面） ============
const toolOptions = [
  { label: 'Claude Code', value: 'claude' },
  { label: 'Codex', value: 'codex' },
]
const claudeMenuOptions = [
  { label: '统计信息', key: 'stats' },
  { label: '基础配置', key: 'basic' },
  { label: '模型与权限', key: 'modelPermissions' },
  { label: '功能配置', key: 'features' },
  { label: '外观与界面', key: 'appearance' },
  { label: '集成与工具', key: 'integration' },
]
const codexMenuOptions = [
  { label: '模型切换', key: 'codexModels' },
]

const activeTool = computed({
  get: () => (store.cfg.uiux?.activeTool === 'codex' ? 'codex' : 'claude'),
  set: (v: string) => { store.cfg.uiux.activeTool = v },
})
const menuOptions = computed(() => activeTool.value === 'codex' ? codexMenuOptions : claudeMenuOptions)
const firstRouteOfTool = (tool: string) => (tool === 'codex' ? 'codexModels' : 'stats')

async function onToolChange(tool: string) {
  await store.save()
  router.push({ name: firstRouteOfTool(tool) })
}

const activeKey = computed(() => route.name as string)
const showConfigPath = computed(() => store.cfg.uiux?.showConfigPath ?? true)

function onMenuSelect(key: string) {
  router.push({ name: key })
}

async function openConfigLocation() {
  try {
    await OpenInExplorer(store.configPath)
    store.statusMessage = `已打开: ${store.configPath}`
  } catch (e: any) {
    message.error(`打开配置文件位置失败: ${e}`)
  }
}

async function openSkillsFolder() {
  try {
    await OpenSkillsFolder()
    store.statusMessage = '已打开 Skills 文件夹'
  } catch (e: any) {
    message.warning(String(e))
  }
}

async function openClaudeFolder() {
  try {
    await OpenClaudeFolder()
    store.statusMessage = '已打开 .claude 文件夹'
  } catch (e: any) {
    message.warning(String(e))
  }
}

async function refreshConfig() {
  try {
    await store.load()
    message.success('配置已刷新')
  } catch (e: any) {
    message.error(`刷新配置失败: ${e}`)
  }
}

onMounted(async () => {
  try {
    await store.load()
  } catch (e: any) {
    message.error(`加载配置文件失败: ${e}`)
  }
  // 路由优先：直接落在 Codex 页面（如刷新/深链）时强制工具为 Codex
  if (route.name === 'codexModels') {
    store.cfg.uiux.activeTool = 'codex'
  }
})
</script>

<template>
  <n-layout style="height: 100vh">
    <n-layout-header bordered style="padding: 0 16px; height: 56px; display: flex; align-items: center; gap: 24px">
      <n-select
        v-model:value="activeTool"
        :options="toolOptions"
        style="width: 150px"
        @update:value="onToolChange"
      />
      <div style="flex: 1"></div>
      <n-space :size="8">
        <n-button size="small" @click="openConfigLocation">打开配置位置</n-button>
        <n-button size="small" @click="openSkillsFolder">Skills 文件夹</n-button>
        <n-button size="small" @click="openClaudeFolder">.claude 文件夹</n-button>
        <n-button size="small" @click="showConfigJson = true">完整配置 JSON</n-button>
        <n-button size="small" @click="refreshConfig">刷新</n-button>
        <n-button size="small" @click="showAbout = true">关于</n-button>
      </n-space>
    </n-layout-header>

    <n-layout-header bordered style="padding: 0 16px">
      <n-menu
        mode="horizontal"
        :options="menuOptions"
        :value="activeKey"
        @update:value="onMenuSelect"
      />
    </n-layout-header>

    <n-layout-content style="padding: 12px 16px">
      <router-view />
    </n-layout-content>

    <n-layout-footer bordered style="padding: 4px 16px; display: flex; align-items: center; gap: 16px">
      <n-text depth="3" style="font-size: 12px">
        {{ showConfigPath ? `配置文件: ${store.configPath}` : 'Claude Configuration Manager' }}
      </n-text>
      <div style="flex: 1"></div>
      <n-text depth="3" style="font-size: 12px">{{ store.statusMessage }}</n-text>
    </n-layout-footer>
  </n-layout>

  <AboutModal v-model:show="showAbout" />
  <ConfigJsonModal v-model:show="showConfigJson" />
</template>
