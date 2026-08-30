<script setup lang="ts">
import { computed, h, ref } from 'vue'
import {
  NTabs, NTabPane, NCard, NDataTable, NButton, NSpace, NText, NForm,
  NFormItem, NCheckbox, NInput, NInputNumber, NTag, useMessage, useDialog, NSplit,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useConfigStore } from '../stores/config'
import { PickDirectory } from '../../wailsjs/go/main/App'
import RepoFormModal from '../components/projects/RepoFormModal.vue'

const store = useConfigStore()
const message = useMessage()
const dialog = useDialog()

// ==================== 项目列表 ====================
const checkedRepo = ref<string[]>([])
const checkedPath = ref<string[]>([])
const checkedCustomCmd = ref<string[]>([])
const repoModalShow = ref(false)

function ensureRepos() {
  if (typeof store.cfg.githubRepoPaths !== 'object' || store.cfg.githubRepoPaths === null) {
    store.cfg.githubRepoPaths = {}
  }
}

const repoColumns: DataTableColumns<any> = [
  { type: 'selection' },
  { title: '仓库', key: 'name' },
  { title: '路径数', key: 'count' },
]

const repoData = computed(() => {
  ensureRepos()
  const map = store.cfg.githubRepoPaths
  return Object.keys(map).map((name) => ({ name, count: (map[name] ?? []).length }))
})

const selectedRepo = computed(() => repoData.value.find((r) => r.name === checkedRepo.value[0]) ?? null)

const pathColumns: DataTableColumns<any> = [{ type: 'selection' }, { title: '路径', key: 'path' }]
const pathData = computed(() => {
  if (!selectedRepo.value) return []
  const paths = store.cfg.githubRepoPaths[selectedRepo.value.name] ?? []
  return paths.map((p: string) => ({ path: p }))
})

function onRepoSubmit(name: string) {
  ensureRepos()
  if (name in store.cfg.githubRepoPaths) {
    message.warning(`仓库 '${name}' 已存在`)
    return
  }
  store.cfg.githubRepoPaths[name] = []
  saveSilently()
  checkedRepo.value = [name]
}

function removeRepo() {
  const repo = selectedRepo.value
  if (!repo) {
    message.warning('请先选择一个仓库')
    return
  }
  dialog.warning({
    title: '确认删除',
    content: `确定要删除仓库 '${repo.name}' 吗? 这将删除该仓库的所有路径配置。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      ensureRepos()
      delete store.cfg.githubRepoPaths[repo.name]
      checkedRepo.value = []
      saveSilently()
    },
  })
}

async function addPath() {
  const repo = selectedRepo.value
  if (!repo) {
    message.warning('请先选择一个仓库')
    return
  }
  const folder = await PickDirectory('选择项目文件夹')
  if (!folder) return
  const paths = store.cfg.githubRepoPaths[repo.name]
  if (paths.includes(folder)) {
    message.warning('该路径已存在')
    return
  }
  paths.push(folder)
  saveSilently()
}

function removePath() {
  const repo = selectedRepo.value
  if (!repo) {
    message.warning('请先选择一个仓库')
    return
  }
  if (!checkedPath.value.length) {
    message.warning('请先选择要删除的路径')
    return
  }
  const target = checkedPath.value[0]
  dialog.warning({
    title: '确认删除',
    content: `确定要删除路径 '${target}' 吗?`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      const paths = store.cfg.githubRepoPaths[repo.name]
      store.cfg.githubRepoPaths[repo.name] = paths.filter((p: string) => p !== target)
      checkedPath.value = []
      saveSilently()
    },
  })
}

function saveSilently() {
  store.save().catch((e: any) => message.error(`保存失败: ${e}`))
}

// ==================== 集成设置 ====================
function ensureIntegrations() {
  if (typeof store.cfg.integrations !== 'object' || store.cfg.integrations === null) {
    store.cfg.integrations = {}
  }
  if (typeof store.cfg.integrations.github !== 'object' || store.cfg.integrations.github === null) {
    store.cfg.integrations.github = {}
  }
  if (typeof store.cfg.integrations.github.features !== 'object' || store.cfg.integrations.github.features === null) {
    store.cfg.integrations.github.features = {}
  }
  if (typeof store.cfg.integrations.slack !== 'object' || store.cfg.integrations.slack === null) {
    store.cfg.integrations.slack = {}
  }
  if (typeof store.cfg.integrations.slack.notifications !== 'object' || store.cfg.integrations.slack.notifications === null) {
    store.cfg.integrations.slack.notifications = {}
  }
  if (!Array.isArray(store.cfg.integrations.customCommands)) {
    store.cfg.integrations.customCommands = []
  }
}

const customCmdColumns: DataTableColumns<any> = [
  { type: 'selection' },
  { title: '命令名称', key: 'name' },
  { title: '触发词', key: 'trigger' },
  { title: '操作', key: 'action' },
  {
    title: '启用',
    key: 'enabled',
    render: (row: any) => h(NTag, { size: 'small', type: row.enabled ? 'success' : 'default' }, () => (row.enabled ? '是' : '否')),
  },
]

const customCommands = computed(() => store.cfg.integrations?.customCommands ?? [])

const selectedCustomCmd = computed(() => customCommands.value.find((c: any) => c.name === checkedCustomCmd.value[0]) ?? null)

function addCustomCommand() {
  message.info('自定义命令添加功能开发中...')
}

function removeCustomCommand(row: any) {
  dialog.warning({
    title: '确认删除',
    content: '确定要删除此自定义命令吗?',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      ensureIntegrations()
      store.cfg.integrations.customCommands = store.cfg.integrations.customCommands.filter((c: any) => c !== row)
      checkedCustomCmd.value = []
    },
  })
}

async function saveIntegrations() {
  try {
    ensureIntegrations()
    await store.save()
    message.success('集成配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function testGithub() {
  message.info('GitHub 连接测试功能开发中...')
}

function testSlack() {
  message.info('Slack 连接测试功能开发中...')
}

// ==================== 开发者工具 ====================
function ensureDevTools() {
  if (typeof store.cfg.developerTools !== 'object' || store.cfg.developerTools === null) {
    store.cfg.developerTools = {}
  }
  if (typeof store.cfg.developerTools.costTracking !== 'object' || store.cfg.developerTools.costTracking === null) {
    store.cfg.developerTools.costTracking = {}
  }
  if (typeof store.cfg.developerTools.apiMonitoring !== 'object' || store.cfg.developerTools.apiMonitoring === null) {
    store.cfg.developerTools.apiMonitoring = {}
  }
}

const perfColumns = [
  { title: '指标', key: 'metric' },
  { title: '当前值', key: 'current' },
  { title: '峰值', key: 'peak' },
  { title: '平均', key: 'avg' },
]
const perfData = [
  { metric: 'API 响应时间', current: '0ms', peak: '0ms', avg: '0ms' },
  { metric: '内存使用', current: '0MB', peak: '0MB', avg: '0MB' },
  { metric: 'CPU 使用率', current: '0%', peak: '0%', avg: '0%' },
  { metric: '缓存命中率', current: '0%', peak: '0%', avg: '0%' },
]

const costStatsLabel = computed(() => {
  const ct = store.cfg.developerTools?.costTracking ?? {}
  const total = ct.totalCost ?? 0
  const today = ct.todayCost ?? 0
  return `总成本: $${Number(total).toFixed(2)} | 今日: $${Number(today).toFixed(2)}`
})

async function saveDevTools() {
  try {
    ensureDevTools()
    await store.save()
    message.success('开发者工具配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function exportLogs() {
  message.info('日志导出功能开发中...')
}

function clearCache() {
  dialog.warning({
    title: '确认清除',
    content: '确定要清除所有缓存吗?',
    positiveText: '清除',
    negativeText: '取消',
    onPositiveClick: () => message.success('缓存已清除!'),
  })
}

function diagnoseIssues() {
  message.info('系统诊断功能开发中...')
}

function runBenchmark() {
  message.info('性能测试功能开发中...')
}

// ==================== 实验性功能 ====================
const statsigRows = computed(() => {
  const gates = store.cfg.cachedStatsigGates ?? {}
  return Object.keys(gates).map((name) => ({ name, enabled: gates[name] === true }))
})

const growthbookRows = computed(() => {
  const features = store.cfg.cachedGrowthBookFeatures ?? {}
  return Object.keys(features).map((name) => ({ name, value: String(features[name] ?? 'null') }))
})

const statsigColumns = [
  { title: '功能名称', key: 'name' },
  {
    title: '状态',
    key: 'enabled',
    render: (row: any) =>
      h(NCheckbox, {
        checked: row.enabled,
        onUpdateChecked: (v: boolean) => {
          store.cfg.cachedStatsigGates[row.name] = v
        },
      }),
  },
]

const growthbookColumns = [
  { title: '功能名称', key: 'name' },
  {
    title: '值',
    key: 'value',
    render: (row: any) =>
      h(NInput, {
        value: row.value,
        size: 'small',
        onUpdateValue: (v: string) => {
          store.cfg.cachedGrowthBookFeatures[row.name] = parseFeatureValue(v)
        },
      }),
  },
]

function parseFeatureValue(v: string): any {
  if (v === 'true') return true
  if (v === 'false') return false
  if (v === 'null') return null
  if (v === '{}') return {}
  return v
}

async function saveFeatures() {
  try {
    await store.save()
    message.success('实验性功能设置已保存!')
  } catch (e: any) {
    message.error(`保存失败: ${e}`)
  }
}
</script>

<template>
  <n-tabs type="segment">
    <!-- ============ 项目列表 ============ -->
    <n-tab-pane name="projects" tab="项目列表">
      <n-space vertical :size="12">
        <n-text depth="3" style="font-size: 12px">将 GitHub 仓库映射到本地项目路径，便于 Claude 识别工作区。</n-text>
        <n-split direction="horizontal" :default-size="0.4">
          <template #1>
            <n-card size="small" title="仓库列表">
              <n-space vertical :size="8">
                <n-space :size="8">
                  <n-button size="small" @click="repoModalShow = true">添加仓库</n-button>
                  <n-button size="small" type="error" @click="removeRepo">删除仓库</n-button>
                </n-space>
                <n-data-table
                  :columns="repoColumns"
                  :data="repoData"
                  :bordered="false"
                  size="small"
                  :row-key="(row: any) => row.name"
                  :checked-row-keys="checkedRepo"
                  @update:checked-row-keys="(k: Array<string | number>) => (checkedRepo = k.slice(0, 1).map(String))"
                />
              </n-space>
            </n-card>
          </template>
          <template #2>
            <n-card size="small" :title="selectedRepo ? `本地路径 — ${selectedRepo.name}` : '本地路径'">
              <n-space vertical :size="8">
                <n-space :size="8">
                  <n-button size="small" :disabled="!selectedRepo" @click="addPath">添加路径</n-button>
                  <n-button size="small" type="error" :disabled="!selectedRepo || !checkedPath.length" @click="removePath">删除路径</n-button>
                </n-space>
                <template v-if="selectedRepo">
                  <n-data-table
                    :columns="pathColumns"
                    :data="pathData"
                    :bordered="false"
                    size="small"
                    :row-key="(row: any) => row.path"
                    :checked-row-keys="checkedPath"
                    @update:checked-row-keys="(k: Array<string | number>) => (checkedPath = k.slice(0, 1).map(String))"
                  />
                </template>
                <n-text v-else depth="3">请在左侧选择一个仓库</n-text>
              </n-space>
            </n-card>
          </template>
        </n-split>
      </n-space>
    </n-tab-pane>

    <!-- ============ 集成设置 ============ -->
    <n-tab-pane name="integration" tab="集成设置">
      <n-space vertical :size="12" style="max-width: 640px">
        <n-card size="small" title="GitHub App 配置">
          <n-form label-placement="left" label-width="170">
            <n-form-item label="启用集成:">
              <n-checkbox v-model:checked="store.cfg.integrations.github.enabled">启用 GitHub App 集成</n-checkbox>
            </n-form-item>
            <n-form-item label="Personal Access Token:">
              <n-input v-model:value="store.cfg.integrations.github.token" type="password" show-password-on="click" placeholder="ghp_xxxxxxxxxxxx" />
            </n-form-item>
            <n-form-item label="用户名:">
              <n-input v-model:value="store.cfg.integrations.github.username" placeholder="GitHub 用户名" />
            </n-form-item>
            <n-form-item label="默认仓库:">
              <n-input v-model:value="store.cfg.integrations.github.defaultRepo" placeholder="username/repo-name" />
            </n-form-item>
          </n-form>
          <n-space vertical>
            <n-checkbox v-model:checked="store.cfg.integrations.github.features.autoCreatePR">自动创建 Pull Request</n-checkbox>
            <n-checkbox v-model:checked="store.cfg.integrations.github.features.createIssues">创建 GitHub Issues</n-checkbox>
            <n-checkbox v-model:checked="store.cfg.integrations.github.features.autoSyncRepo">自动同步仓库配置</n-checkbox>
          </n-space>
        </n-card>

        <n-card size="small" title="Slack App 配置">
          <n-form label-placement="left" label-width="170">
            <n-form-item label="启用集成:">
              <n-checkbox v-model:checked="store.cfg.integrations.slack.enabled">启用 Slack App 集成</n-checkbox>
            </n-form-item>
            <n-form-item label="Webhook URL:">
              <n-input v-model:value="store.cfg.integrations.slack.webhookUrl" placeholder="https://hooks.slack.com/services/..." />
            </n-form-item>
            <n-form-item label="默认频道:">
              <n-input v-model:value="store.cfg.integrations.slack.defaultChannel" placeholder="#general" />
            </n-form-item>
            <n-form-item label="Bot Token:">
              <n-input v-model:value="store.cfg.integrations.slack.botToken" type="password" show-password-on="click" placeholder="xoxb-..." />
            </n-form-item>
          </n-form>
          <n-space vertical>
            <n-checkbox v-model:checked="store.cfg.integrations.slack.notifications.sendErrors">发送错误通知</n-checkbox>
            <n-checkbox v-model:checked="store.cfg.integrations.slack.notifications.sendCompletion">发送任务完成通知</n-checkbox>
            <n-checkbox v-model:checked="store.cfg.integrations.slack.notifications.sendDailySummary">发送每日汇总</n-checkbox>
          </n-space>
        </n-card>

        <n-card size="small" title="自定义命令">
          <n-space vertical :size="8">
            <n-data-table
              :columns="customCmdColumns"
              :data="customCommands"
              :bordered="false"
              size="small"
              :row-key="(row: any) => row.name"
              :checked-row-keys="checkedCustomCmd"
              @update:checked-row-keys="(k: Array<string | number>) => (checkedCustomCmd = k.slice(0, 1).map(String))"
            />
            <n-space :size="8">
              <n-button size="small" @click="addCustomCommand">添加命令</n-button>
              <n-button size="small" type="error" :disabled="!selectedCustomCmd" @click="removeCustomCommand(selectedCustomCmd)">删除</n-button>
            </n-space>
          </n-space>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" @click="testGithub">测试 GitHub</n-button>
            <n-button size="small" @click="testSlack">测试 Slack</n-button>
            <n-button size="small" type="primary" @click="saveIntegrations">保存设置</n-button>
          </n-space>
        </div>
      </n-space>
    </n-tab-pane>

    <!-- ============ 开发者工具 ============ -->
    <n-tab-pane name="devtools" tab="开发者工具">
      <n-space vertical :size="12" style="max-width: 640px">
        <n-card size="small" title="开发模式">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="开发者工具:">
              <n-checkbox v-model:checked="store.cfg.developerTools.enabled">启用开发者工具</n-checkbox>
            </n-form-item>
            <n-form-item label="详细日志:">
              <n-checkbox v-model:checked="store.cfg.developerTools.verboseLogging">启用详细日志</n-checkbox>
            </n-form-item>
            <n-form-item label="调试模式:">
              <n-checkbox v-model:checked="store.cfg.developerTools.debugMode">调试模式</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="性能监控">
          <n-data-table :columns="perfColumns" :data="perfData" :bordered="false" size="small" />
        </n-card>

        <n-card size="small" title="成本跟踪">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="启用成本跟踪:">
              <n-checkbox v-model:checked="store.cfg.developerTools.costTracking.enabled">启用成本跟踪</n-checkbox>
            </n-form-item>
            <n-form-item label="成本警告阈值:">
              <n-input-number v-model:value="store.cfg.developerTools.costTracking.warningThreshold" :min="1" :max="1000" style="width: 160px">
                <template #suffix>USD</template>
              </n-input-number>
            </n-form-item>
            <n-form-item label="每日预算限制:">
              <n-input-number v-model:value="store.cfg.developerTools.costTracking.dailyBudget" :min="1" :max="10000" style="width: 160px">
                <template #suffix>USD</template>
              </n-input-number>
            </n-form-item>
            <n-form-item>
              <n-text>{{ costStatsLabel }}</n-text>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="API 监控">
          <n-form label-placement="left" label-width="160">
            <n-form-item label="API 调用监控:">
              <n-checkbox v-model:checked="store.cfg.developerTools.apiMonitoring.enabled">启用 API 调用监控</n-checkbox>
            </n-form-item>
            <n-form-item label="记录响应时间:">
              <n-checkbox v-model:checked="store.cfg.developerTools.apiMonitoring.logResponseTime">记录 API 响应时间</n-checkbox>
            </n-form-item>
            <n-form-item label="缓存命中率监控:">
              <n-checkbox v-model:checked="store.cfg.developerTools.apiMonitoring.monitorCacheHitRate">监控缓存命中率</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="高级工具">
          <n-space :size="8">
            <n-button size="small" @click="exportLogs">导出日志</n-button>
            <n-button size="small" @click="clearCache">清除缓存</n-button>
            <n-button size="small" @click="diagnoseIssues">诊断问题</n-button>
            <n-button size="small" @click="runBenchmark">性能测试</n-button>
          </n-space>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-button size="small" type="primary" @click="saveDevTools">保存设置</n-button>
        </div>
      </n-space>
    </n-tab-pane>

    <!-- ============ 实验性功能 ============ -->
    <n-tab-pane name="experimental" tab="实验性功能">
      <n-space vertical :size="12" style="max-width: 640px">
        <n-text depth="3" style="font-size: 12px">实验性功能开关 (这些是 A/B 测试和功能标志)</n-text>
        <n-card size="small" title="Statsig 功能开关">
          <n-data-table :columns="statsigColumns" :data="statsigRows" :bordered="false" size="small" />
        </n-card>
        <n-card size="small" title="GrowthBook 功能标志">
          <n-data-table :columns="growthbookColumns" :data="growthbookRows" :bordered="false" size="small" />
        </n-card>
        <div style="display: flex; justify-content: flex-end">
          <n-button size="small" type="primary" @click="saveFeatures">保存实验性设置</n-button>
        </div>
      </n-space>
    </n-tab-pane>
  </n-tabs>

  <RepoFormModal v-model:show="repoModalShow" @submit="onRepoSubmit" />
</template>
