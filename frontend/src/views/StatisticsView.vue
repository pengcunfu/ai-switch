<script setup lang="ts">
import { computed, h } from 'vue'
import { NTabs, NTabPane, NCard, NStatistic, NDataTable, NButton, NTag, NGrid, NGi, NSpace } from 'naive-ui'
import { useConfigStore } from '../stores/config'

const store = useConfigStore()

interface Overview {
  totalRequests: number
  totalCost: number
  totalTokens: number
  activeProjects: number
  activeSkills: number
}

const overview = computed<Overview>(() => {
  const skillUsage = store.cfg.skillUsage ?? {}
  const projects = store.cfg.projects ?? {}
  let totalCost = 0
  let totalTokens = 0
  let totalRequests = 0
  let activeSkills = 0
  for (const key of Object.keys(projects)) {
    const p = projects[key]
    totalCost += p.lastCost ?? 0
    totalTokens += (p.lastTotalInputTokens ?? 0) + (p.lastTotalOutputTokens ?? 0)
  }
  for (const key of Object.keys(skillUsage)) {
    const count = skillUsage[key].usageCount ?? 0
    totalRequests += count
    if (count > 0) activeSkills++
  }
  return {
    totalRequests,
    totalCost,
    totalTokens,
    activeProjects: Object.keys(projects).length,
    activeSkills,
  }
})

function formatTime(ms: number): string {
  if (!ms || ms <= 0) return '从未使用'
  const d = new Date(ms)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function frequency(count: number): string {
  if (count > 10) return '高频'
  if (count > 5) return '中频'
  if (count > 0) return '低频'
  return '未使用'
}

function activity(cost: number): string {
  if (cost > 0.5) return '高活跃'
  if (cost > 0.1) return '中活跃'
  if (cost > 0) return '低活跃'
  return '未活跃'
}

const skillsColumns = [
  { title: 'Skill 名称', key: 'name' },
  { title: '使用次数', key: 'count' },
  { title: '最后使用时间', key: 'lastUsed' },
  {
    title: '频率',
    key: 'frequency',
    render: (row: any) => h(NTag, { size: 'small', type: row.frequency === '高频' ? 'success' : row.frequency === '中频' ? 'warning' : 'default' }, () => row.frequency),
  },
]

const skillsData = computed(() => {
  const skillUsage = store.cfg.skillUsage ?? {}
  const rows = Object.keys(skillUsage)
    .map((name) => ({
      name,
      count: skillUsage[name].usageCount ?? 0,
      lastUsed: formatTime(skillUsage[name].lastUsedAt ?? 0),
      frequency: frequency(skillUsage[name].usageCount ?? 0),
    }))
    .sort((a, b) => b.count - a.count)
  return rows
})

const projectsColumns = [
  { title: '项目路径', key: 'path' },
  { title: '最后成本', key: 'cost' },
  { title: 'API 持续时间', key: 'duration' },
  { title: '总 Tokens', key: 'tokens' },
  { title: '活跃度', key: 'activity' },
]

const projectsData = computed(() => {
  const projects = store.cfg.projects ?? {}
  return Object.keys(projects).map((path) => {
    const p = projects[path]
    const tokens = (p.lastTotalInputTokens ?? 0) + (p.lastTotalOutputTokens ?? 0)
    return {
      path,
      cost: `$${(p.lastCost ?? 0).toFixed(4)}`,
      duration: `${p.lastAPIDuration ?? 0}ms`,
      tokens: tokens.toLocaleString(),
      activity: activity(p.lastCost ?? 0),
    }
  })
})

const modelColumns = [
  { title: '模型', key: 'model' },
  { title: '输入 Tokens', key: 'input' },
  { title: '输出 Tokens', key: 'output' },
  { title: '缓存读取', key: 'cache' },
  { title: '成本 (USD)', key: 'cost' },
]

const modelData = computed(() => {
  const stats: Record<string, any> = {}
  const projects = store.cfg.projects ?? {}
  for (const key of Object.keys(projects)) {
    const usage = projects[key].lastModelUsage ?? {}
    for (const model of Object.keys(usage)) {
      if (!stats[model]) {
        stats[model] = { input: 0, output: 0, cache: 0, cost: 0 }
      }
      const u = usage[model]
      stats[model].input += u.inputTokens ?? 0
      stats[model].output += u.outputTokens ?? 0
      stats[model].cache += u.cacheReadInputTokens ?? 0
      stats[model].cost += u.costUSD ?? 0
    }
  }
  return Object.keys(stats).map((model) => ({
    model,
    input: stats[model].input.toLocaleString(),
    output: stats[model].output.toLocaleString(),
    cache: stats[model].cache.toLocaleString(),
    cost: `$${stats[model].cost.toFixed(4)}`,
  }))
})

function refresh() {
  store.statusMessage = '统计已刷新'
}
</script>

<template>
  <n-space vertical :size="12">
    <n-grid cols="5" :x-gap="12" :y-gap="12">
      <n-gi><n-card size="small"><n-statistic label="总请求数" :value="overview.totalRequests" /></n-card></n-gi>
      <n-gi><n-card size="small"><n-statistic label="总成本" :value="overview.totalCost" precision="4" /></n-card></n-gi>
      <n-gi><n-card size="small"><n-statistic label="总 Tokens" :value="overview.totalTokens" /></n-card></n-gi>
      <n-gi><n-card size="small"><n-statistic label="活跃项目" :value="overview.activeProjects" /></n-card></n-gi>
      <n-gi><n-card size="small"><n-statistic label="活跃 Skills" :value="overview.activeSkills" /></n-card></n-gi>
    </n-grid>

    <n-tabs type="segment">
      <n-tab-pane name="skills" tab="Skills 统计">
        <n-card size="small" title="Skills 使用统计">
          <n-data-table :columns="skillsColumns" :data="skillsData" :bordered="false" size="small" />
        </n-card>
      </n-tab-pane>
      <n-tab-pane name="projects" tab="项目统计">
        <n-card size="small" title="项目活跃度统计">
          <n-data-table :columns="projectsColumns" :data="projectsData" :bordered="false" size="small" />
        </n-card>
      </n-tab-pane>
      <n-tab-pane name="models" tab="模型统计">
        <n-card size="small" title="模型使用统计">
          <n-data-table :columns="modelColumns" :data="modelData" :bordered="false" size="small" />
        </n-card>
      </n-tab-pane>
    </n-tabs>

    <div style="display: flex; justify-content: flex-end">
      <n-button size="small" @click="refresh">刷新统计</n-button>
    </div>
  </n-space>
</template>
