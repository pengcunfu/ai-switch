<script setup lang="ts">
import { computed, h, ref } from 'vue'
import {
  NTabs, NTabPane, NCard, NForm, NFormItem, NSelect, NInputNumber,
  NCheckbox, NButton, NSpace, NDataTable, NTag, NText, useMessage, useDialog,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useConfigStore } from '../stores/config'
import PermissionFormModal from '../components/permissions/PermissionFormModal.vue'

const store = useConfigStore()
const message = useMessage()
const dialog = useDialog()

// ============ Model 配置 ============
const modelOptions = [
  { label: 'Claude Sonnet 4.6 (推荐)', value: 'claude-sonnet-4-6' },
  { label: 'Claude Opus 4.7', value: 'claude-opus-4-7' },
  { label: 'Claude Haiku 4.5', value: 'claude-haiku-4-5-20251001' },
]
const fastModelOptions = [
  { label: 'Claude Sonnet 4.6', value: 'claude-sonnet-4-6' },
  { label: 'Claude Haiku 4.5', value: 'claude-haiku-4-5-20251001' },
  { label: 'Claude Opus 4.6', value: 'claude-opus-4-6' },
]

function ensure(sec: string, defaults: Record<string, any>) {
  if (typeof store.cfg[sec] !== 'object' || store.cfg[sec] === null) {
    store.cfg[sec] = { ...defaults }
  }
}

function resetDefaults() {
  dialog.warning({
    title: '确认重置',
    content: '确定要重置为默认值吗?',
    positiveText: '重置',
    negativeText: '取消',
    onPositiveClick: () => {
      store.cfg.modelConfiguration = { temperature: 0.7, maxTokens: 8192, topP: 1.0 }
      store.cfg.contextConfiguration = { contextWindowSize: 200000, thinkingEnabled: false, compactionEnabled: false }
      store.cfg.promptCachingEnabled = true
      store.cfg.streamEnabled = true
      store.cfg.usageLimits = { dailyMaxRequests: 0, maxCostPerRequest: 0 }
    },
  })
}

async function saveModel() {
  try {
    ensure('modelConfiguration', {})
    ensure('contextConfiguration', {})
    ensure('usageLimits', {})
    await store.save()
    message.success('Model 配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

// ============ 权限管理 ============
const permissionModalShow = ref(false)
const permissionModalData = ref<Record<string, any> | null>(null)
const editingGlobalKey = ref<string | null>(null)

function ensurePermissions() {
  if (typeof store.cfg.permissions !== 'object' || store.cfg.permissions === null) {
    store.cfg.permissions = {}
  }
  if (typeof store.cfg.globalToolPermissions !== 'object' || store.cfg.globalToolPermissions === null) {
    store.cfg.globalToolPermissions = {}
  }
}

const permissionLevelOptions = [
  { label: '严格 (所有操作需确认)', value: 'strict' },
  { label: '平衡 (只读自动，写入确认)', value: 'balanced' },
  { label: '宽松 (仅危险操作确认)', value: 'permissive' },
]

const globalToolsColumns: DataTableColumns<any> = [
  { type: 'selection' },
  { title: '工具名称', key: 'name' },
  { title: '类型', key: 'type' },
  {
    title: '权限',
    key: 'permission',
    render: (row: any) => h(NTag, { size: 'small', type: row.permission === 'allow' ? 'success' : row.permission === 'deny' ? 'error' : 'warning' }, () => row.permission),
  },
]

const globalToolsData = computed(() => {
  ensurePermissions()
  const map = store.cfg.globalToolPermissions
  return Object.keys(map).map((name) => ({ name, type: map[name].type ?? 'unknown', permission: map[name].permission ?? 'prompt' }))
})

const checkedGlobalTools = ref<string[]>([])
const selectedGlobalTool = computed(() => {
  const row = globalToolsData.value.find((r) => r.name === checkedGlobalTools.value[0])
  return row ?? null
})

function openAddGlobalTool() {
  editingGlobalKey.value = null
  permissionModalData.value = null
  permissionModalShow.value = true
}

function openEditGlobalTool(row: any) {
  editingGlobalKey.value = row.name
  permissionModalData.value = { name: row.name, type: row.type, permission: row.permission }
  permissionModalShow.value = true
}

function onPermissionSubmit(data: Record<string, any>) {
  ensurePermissions()
  const map = store.cfg.globalToolPermissions
  // 名称变更时删除旧条目
  if (editingGlobalKey.value && editingGlobalKey.value !== data.name) {
    delete map[editingGlobalKey.value]
  }
  map[data.name] = { type: data.type, permission: data.permission }
}

function removeGlobalTool(row: any) {
  dialog.warning({
    title: '确认删除',
    content: `确定要移除工具 '${row.name}' 的权限设置吗?`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      ensurePermissions()
      delete store.cfg.globalToolPermissions[row.name]
    },
  })
}

// 项目权限
const projectOptions = computed(() => Object.keys(store.cfg.projects ?? {}).map((p) => ({ label: p, value: p })))
const selectedProject = ref<string | null>(null)
const projectToolsData = computed(() => {
  const projects = store.cfg.projects ?? {}
  const cfg = selectedProject.value ? (projects[selectedProject.value] ?? {}) : {}
  return (cfg.allowedTools ?? []).map((t: string) => ({ name: t, type: 'allowed', permission: 'allowed' }))
})
const projectToolsColumns = [
  { title: '工具名称', key: 'name' },
  { title: '类型', key: 'type' },
  { title: '权限', key: 'permission' },
]

async function savePermissions() {
  try {
    ensurePermissions()
    await store.save()
    message.success('权限配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}
</script>

<template>
  <n-tabs type="segment">
    <n-tab-pane name="model" tab="Model 配置">
      <n-space vertical :size="12" style="max-width: 560px">
        <n-card size="small" title="Model 选择">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="默认模型:">
              <n-select v-model:value="store.cfg.modelConfiguration.defaultModel" :options="modelOptions" @update:value="ensure('modelConfiguration', {})" />
            </n-form-item>
            <n-form-item label="Fast 模式模型:">
              <n-select v-model:value="store.cfg.modelConfiguration.fastModel" :options="fastModelOptions" @update:value="ensure('modelConfiguration', {})" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="模型参数">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="Temperature:">
              <n-input-number v-model:value="store.cfg.modelConfiguration.temperature" :min="0" :max="1" :step="0.1" style="width: 200px" />
            </n-form-item>
            <n-form-item label="Max Tokens:">
              <n-input-number v-model:value="store.cfg.modelConfiguration.maxTokens" :min="1" :max="200000" :step="100" style="width: 200px" />
            </n-form-item>
            <n-form-item label="Top P:">
              <n-input-number v-model:value="store.cfg.modelConfiguration.topP" :min="0" :max="1" :step="0.1" style="width: 200px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="上下文配置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="上下文窗口大小:">
              <n-input-number v-model:value="store.cfg.contextConfiguration.contextWindowSize" :min="1000" :max="200000" :step="1000" style="width: 200px" />
            </n-form-item>
            <n-form-item label="启用 Thinking:">
              <n-checkbox v-model:checked="store.cfg.contextConfiguration.thinkingEnabled">启用 Thinking 模式</n-checkbox>
            </n-form-item>
            <n-form-item label="启用压缩:">
              <n-checkbox v-model:checked="store.cfg.contextConfiguration.compactionEnabled">启用上下文压缩</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="高级配置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="提示缓存:">
              <n-checkbox v-model:checked="store.cfg.promptCachingEnabled">启用提示缓存</n-checkbox>
            </n-form-item>
            <n-form-item label="流式输出:">
              <n-checkbox v-model:checked="store.cfg.streamEnabled">启用流式输出</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="使用限制">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="每日最大请求数:">
              <n-input-number v-model:value="store.cfg.usageLimits.dailyMaxRequests" :min="0" :max="10000" style="width: 200px" />
            </n-form-item>
            <n-form-item label="单次最大成本 (USD):">
              <n-input-number v-model:value="store.cfg.usageLimits.maxCostPerRequest" :min="0" :max="1000" :step="0.1" style="width: 200px" />
            </n-form-item>
          </n-form>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" @click="resetDefaults">重置默认</n-button>
            <n-button size="small" type="primary" @click="saveModel">保存设置</n-button>
          </n-space>
        </div>
      </n-space>
    </n-tab-pane>

    <n-tab-pane name="permissions" tab="权限管理">
      <n-space vertical :size="12" style="max-width: 720px">
        <n-card size="small" title="自动权限设置">
          <n-form label-placement="left" label-width="180">
            <n-form-item label="自动允许只读:">
              <n-checkbox v-model:checked="store.cfg.permissions.autoAllowRead">自动允许只读操作</n-checkbox>
            </n-form-item>
            <n-form-item label="写入确认:">
              <n-checkbox v-model:checked="store.cfg.permissions.promptOnWrite">写入操作需要确认</n-checkbox>
            </n-form-item>
            <n-form-item label="允许危险操作:">
              <n-checkbox v-model:checked="store.cfg.permissions.allowDangerous">允许危险操作</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="默认权限级别">
          <n-select v-model:value="store.cfg.permissions.defaultLevel" :options="permissionLevelOptions" style="max-width: 320px" />
        </n-card>

        <n-card size="small" title="全局工具权限">
          <n-space vertical :size="8">
            <n-data-table
              :columns="globalToolsColumns"
              :data="globalToolsData"
              :bordered="false"
              size="small"
              :row-key="(row: any) => row.name"
              :checked-row-keys="checkedGlobalTools"
              @update:checked-row-keys="(keys: Array<string | number>) => (checkedGlobalTools = keys.slice(0, 1).map(String))"
            />
            <n-space :size="8">
              <n-button size="small" @click="openAddGlobalTool">添加工具</n-button>
              <n-button size="small" :disabled="!selectedGlobalTool" @click="openEditGlobalTool(selectedGlobalTool)">编辑工具</n-button>
              <n-button size="small" type="error" :disabled="!selectedGlobalTool" @click="removeGlobalTool(selectedGlobalTool)">移除工具</n-button>
            </n-space>
          </n-space>
        </n-card>

        <n-card size="small" title="项目权限覆盖">
          <n-space vertical :size="8">
            <n-select v-model:value="selectedProject" :options="projectOptions" placeholder="选择项目" clearable style="max-width: 360px" />
            <n-data-table v-if="selectedProject" :columns="projectToolsColumns" :data="projectToolsData" :bordered="false" size="small" />
            <n-text v-else depth="3" style="font-size: 12px">请先在"集成与工具 → 项目列表"中添加项目</n-text>
          </n-space>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-button size="small" type="primary" @click="savePermissions">保存设置</n-button>
        </div>
      </n-space>
    </n-tab-pane>
  </n-tabs>

  <PermissionFormModal
    v-model:show="permissionModalShow"
    :data="permissionModalData"
    @submit="onPermissionSubmit"
  />
</template>
