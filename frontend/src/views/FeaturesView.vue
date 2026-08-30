<script setup lang="ts">
import { computed, h, ref } from 'vue'
import {
  NTabs, NTabPane, NCard, NDataTable, NButton, NSpace, NTag, NText,
  NForm, NFormItem, NCheckbox, NInput, NInputNumber, NRadioGroup, NRadioButton,
  NDescriptions, NDescriptionsItem,
  useMessage, useDialog, NSplit,
} from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import { useConfigStore } from '../stores/config'
import { TestMCPConnection, ListSkills, SaveSkill, DeleteSkill, PickDirectory } from '../../wailsjs/go/main/App'
import MCPServerModal from '../components/mcp/MCPServerModal.vue'
import MCPToolsDrawer from '../components/mcp/MCPToolsDrawer.vue'
import SkillFormModal from '../components/skills/SkillFormModal.vue'
import HookFormModal from '../components/hooks/HookFormModal.vue'

const store = useConfigStore()
const message = useMessage()
const dialog = useDialog()

// ==================== MCP 服务器 ====================
const mcpModalShow = ref(false)
const mcpModalName = ref('')
const mcpModalConfig = ref<Record<string, any> | null>(null)
const editingMCPKey = ref<string | null>(null)
const toolsDrawerShow = ref(false)
const toolsDrawerServer = ref('')
const toolsDrawerConfig = ref<Record<string, any> | null>(null)
const checkedMCP = ref<string[]>([])
const statusMap = ref<Record<string, string>>({})

function ensureMcpServers() {
  if (typeof store.cfg.mcpServers !== 'object' || store.cfg.mcpServers === null) {
    store.cfg.mcpServers = {}
  }
}

const mcpColumns: DataTableColumns<any> = [
  { type: 'selection' },
  {
    title: '服务器名称',
    key: 'name',
    render: (row: any) => h('span', { style: 'font-weight: 600' }, row.name),
  },
  { title: '命令', key: 'command' },
  { title: '参数', key: 'args' },
  { title: '环境变量', key: 'env' },
  {
    title: '状态',
    key: 'status',
    render: (row: any) => {
      const s = statusMap.value[row.name] ?? '未测试'
      const type = s === '正常' ? 'success' : s === '失败' ? 'error' : s === '测试中...' ? 'info' : 'default'
      return h(NTag, { size: 'small', type }, () => s)
    },
  },
]

const mcpData = computed(() => {
  ensureMcpServers()
  const map = store.cfg.mcpServers
  return Object.keys(map).map((name) => ({
    name,
    command: map[name].command ?? '',
    args: Array.isArray(map[name].args) ? map[name].args.join(' ') : '',
    env: Object.keys(map[name].env ?? {}).map((k) => `${k}=${map[name].env[k]}`).join('; '),
  }))
})

function openAddServer() {
  editingMCPKey.value = null
  mcpModalName.value = ''
  mcpModalConfig.value = null
  mcpModalShow.value = true
}

function openEditServer(row: any) {
  editingMCPKey.value = row.name
  mcpModalName.value = row.name
  mcpModalConfig.value = store.cfg.mcpServers[row.name]
  mcpModalShow.value = true
}

async function onServerSubmit(data: { name: string; config: Record<string, any> }) {
  ensureMcpServers()
  if (editingMCPKey.value && editingMCPKey.value !== data.name) {
    delete store.cfg.mcpServers[editingMCPKey.value]
  }
  store.cfg.mcpServers[data.name] = data.config
  try {
    await store.save()
    message.success(`MCP服务器 '${data.name}' 已保存!`)
  } catch (e: any) {
    message.error(`保存失败: ${e}`)
  }
}

function removeServer(row: any) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除MCP服务器 '${row.name}' 吗?`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      ensureMcpServers()
      delete store.cfg.mcpServers[row.name]
      await store.save()
      message.success(`MCP服务器 '${row.name}' 已删除!`)
    },
  })
}

async function testConnection(row: any) {
  statusMap.value[row.name] = '测试中...'
  try {
    const cfg = store.cfg.mcpServers[row.name]
    const result = await TestMCPConnection(cfg)
    if (result.success) {
      statusMap.value[row.name] = '正常'
      const info = result.serverInfo
      message.success(`MCP服务器 '${row.name}' 连接正常! 服务器: ${info?.name ?? '未知'} 版本: ${info?.version ?? '未知'}`)
    } else {
      statusMap.value[row.name] = '失败'
      dialog.error({
        title: '连接测试失败',
        content: result.error || '未知错误',
        positiveText: '确定',
      })
    }
  } catch (e: any) {
    statusMap.value[row.name] = '失败'
    dialog.error({ title: '连接测试失败', content: String(e), positiveText: '确定' })
  }
}

function viewTools(row: any) {
  toolsDrawerServer.value = row.name
  toolsDrawerConfig.value = store.cfg.mcpServers[row.name]
  toolsDrawerShow.value = true
}

// ==================== Skills ====================
const scope = ref<'global' | 'project'>('global')
const projectDir = ref('')
const skills = ref<any[]>([])
const selectedSkill = ref<any | null>(null)
const skillModalShow = ref(false)
const skillModalData = ref<Record<string, any> | null>(null)
const editingSkillPath = ref('')

const skillColumns: DataTableColumns<any> = [
  { type: 'selection' },
  { title: '名称', key: 'name' },
  { title: '描述', key: 'description', ellipsis: { tooltip: true } },
  { title: '斜杠命令', key: 'slash' },
  { title: '作用域', key: 'scopeLabel' },
]

async function refreshSkills() {
  try {
    const rows = await ListSkills(scope.value, projectDir.value)
    skills.value = rows.map((s) => ({
      ...s,
      slash: s.user_invocable !== false ? `/${s.name}` : '—',
      scopeLabel: scope.value === 'global' ? '全局' : '项目',
    }))
    selectedSkill.value = null
  } catch (e: any) {
    message.error(`加载 Skills 失败: ${e}`)
  }
}

async function onScopeChange() {
  await refreshSkills()
}

async function pickProjectDir() {
  const dir = await PickDirectory('选择项目目录')
  if (dir) {
    projectDir.value = dir
    await refreshSkills()
  }
}

function onSkillSelect(keys: string[]) {
  if (!keys.length) {
    selectedSkill.value = null
    return
  }
  selectedSkill.value = skills.value.find((s) => s.path === keys[0]) ?? null
}

function openAddSkill() {
  skillModalData.value = null
  skillModalShow.value = true
}

function openEditSkill() {
  if (!selectedSkill.value) {
    message.warning('请先选择一个 Skill')
    return
  }
  editingSkillPath.value = selectedSkill.value.path
  skillModalData.value = selectedSkill.value
  skillModalShow.value = true
}

async function onSkillSubmit(data: Record<string, any>) {
  try {
    await SaveSkill(scope.value, projectDir.value, data)
    await refreshSkills()
    message.success(`Skill '${data.name}' 已保存!`)
  } catch (e: any) {
    message.error(`保存 Skill 失败: ${e}`)
  }
}

function removeSkill() {
  if (!selectedSkill.value) {
    message.warning('请先选择一个 Skill')
    return
  }
  dialog.warning({
    title: '确认删除',
    content: `确定要删除 Skill '${selectedSkill.value.name}' 吗? 这将删除整个 skill 目录。`,
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await DeleteSkill(scope.value, projectDir.value, selectedSkill.value.name)
        await refreshSkills()
        message.success(`Skill '${selectedSkill.value.name}' 已删除!`)
      } catch (e: any) {
        message.error(`删除 Skill 失败: ${e}`)
      }
    },
  })
}

// ==================== Hooks ====================
const hookTab = ref<'pre' | 'post'>('pre')
const hookModalShow = ref(false)
const hookModalType = ref<'pre' | 'post'>('pre')
const hookModalData = ref<Record<string, any> | null>(null)
const hookEditingIndex = ref<number | null>(null)
const checkedPreHook = ref<string[]>([])
const checkedPostHook = ref<string[]>([])

function ensureHooks() {
  if (typeof store.cfg.hooks !== 'object' || store.cfg.hooks === null) {
    store.cfg.hooks = {}
  }
  if (!Array.isArray(store.cfg.hooks.preHooks)) store.cfg.hooks.preHooks = []
  if (!Array.isArray(store.cfg.hooks.postHooks)) store.cfg.hooks.postHooks = []
}

const hookColumns: DataTableColumns<any> = [
  { type: 'selection' },
  { title: '触发时机', key: 'trigger' },
  { title: '命令/脚本', key: 'command', ellipsis: { tooltip: true } },
  {
    title: '启用',
    key: 'enabled',
    render: (row: any) => h(NTag, { size: 'small', type: row.enabled ? 'success' : 'default' }, () => (row.enabled ? '是' : '否')),
  },
  { title: '描述', key: 'description' },
]

const preHooks = computed(() => {
  ensureHooks()
  return store.cfg.hooks.preHooks.map((h: any, i: number) => ({ _i: i, ...h }))
})
const postHooks = computed(() => {
  ensureHooks()
  return store.cfg.hooks.postHooks.map((h: any, i: number) => ({ _i: i, ...h }))
})
const selectedPreHook = computed(() => preHooks.value.find((r: any) => 'hook-' + r._i === checkedPreHook.value[0]) ?? null)
const selectedPostHook = computed(() => postHooks.value.find((r: any) => 'hook-' + r._i === checkedPostHook.value[0]) ?? null)

function openAddHook(type: 'pre' | 'post') {
  hookModalType.value = type
  hookModalData.value = null
  hookEditingIndex.value = null
  hookModalShow.value = true
}

function openEditHook(type: 'pre' | 'post', row: any) {
  hookModalType.value = type
  const data = { ...row }
  delete data._i
  hookModalData.value = data
  hookEditingIndex.value = row._i
  hookModalShow.value = true
}

function onHookSubmit(data: Record<string, any>) {
  ensureHooks()
  const list = hookModalType.value === 'pre' ? store.cfg.hooks.preHooks : store.cfg.hooks.postHooks
  const item = { trigger: data.trigger, command: data.command, workingDir: data.workingDir, description: data.description, enabled: data.enabled }
  if (hookEditingIndex.value !== null) {
    list[hookEditingIndex.value] = item
    hookEditingIndex.value = null
  } else {
    list.push(item)
  }
}

function removeHook(type: 'pre' | 'post', row: any) {
  ensureHooks()
  const list = type === 'pre' ? store.cfg.hooks.preHooks : store.cfg.hooks.postHooks
  dialog.warning({
    title: '确认删除',
    content: '确定要删除此 Hook 吗?',
    positiveText: '删除',
    negativeText: '取消',
    onPositiveClick: () => {
      list.splice(row._i, 1)
    },
  })
}

async function saveHooks() {
  try {
    ensureHooks()
    await store.save()
    message.success('Hooks 配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

// ==================== Memory ====================
function ensureMemory() {
  if (typeof store.cfg.memory !== 'object' || store.cfg.memory === null) {
    store.cfg.memory = {}
  }
}

const defaultMemoryTypes = [
  { type: '用户记忆', status: '启用', desc: '记住用户的角色、偏好和专业知识' },
  { type: '项目记忆', status: '启用', desc: '记住项目相关的目标和决策' },
  { type: '反馈记忆', status: '启用', desc: '记住用户对方法的反馈和偏好' },
  { type: '引用记忆', status: '启用', desc: '记住外部系统和文档的位置' },
]

const memoryTypeColumns = [
  { title: 'Memory 类型', key: 'type' },
  { title: '状态', key: 'status' },
  { title: '描述', key: 'desc' },
]

async function saveMemory() {
  try {
    ensureMemory()
    await store.save()
    message.success('Memory 配置已保存!')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function cleanupMemory() {
  message.info('Memory 清理功能开发中...')
}
</script>

<template>
  <n-tabs type="segment">
    <!-- ============ MCP 服务器 ============ -->
    <n-tab-pane name="mcp" tab="MCP 服务器">
      <n-space vertical :size="12">
        <n-space :size="8">
          <n-button size="small" type="primary" @click="openAddServer">添加服务器</n-button>
          <n-button size="small" :disabled="!checkedMCP.length" @click="openEditServer(mcpData.find((r) => r.name === checkedMCP[0]))">编辑服务器</n-button>
          <n-button size="small" type="error" :disabled="!checkedMCP.length" @click="removeServer(mcpData.find((r) => r.name === checkedMCP[0]))">删除服务器</n-button>
          <n-button size="small" :disabled="!checkedMCP.length" @click="testConnection(mcpData.find((r) => r.name === checkedMCP[0]))">测试连接</n-button>
          <n-button size="small" :disabled="!checkedMCP.length" @click="viewTools(mcpData.find((r) => r.name === checkedMCP[0]))">查看工具</n-button>
        </n-space>
        <n-data-table
          :columns="mcpColumns"
          :data="mcpData"
          :bordered="false"
          size="small"
          :row-key="(row: any) => row.name"
          :checked-row-keys="checkedMCP"
          @update:checked-row-keys="(keys: Array<string | number>) => (checkedMCP = keys.slice(0, 1).map(String))"
        />
      </n-space>
    </n-tab-pane>

    <!-- ============ Skills ============ -->
    <n-tab-pane name="skills" tab="Skills">
      <n-space vertical :size="12">
        <n-space :size="8" align="center">
          <n-text>作用域:</n-text>
          <n-radio-group v-model:value="scope" @update:value="onScopeChange">
            <n-radio-button value="global">全局 (~/.claude/skills/)</n-radio-button>
            <n-radio-button value="project">项目 (.claude/skills/)</n-radio-button>
          </n-radio-group>
          <n-button v-if="scope === 'project'" size="small" @click="pickProjectDir">选择项目目录</n-button>
          <n-text v-if="scope === 'project' && projectDir" depth="3" style="font-size: 12px">{{ projectDir }}</n-text>
        </n-space>

        <n-split direction="horizontal" :default-size="0.5">
          <template #1>
            <n-space vertical :size="8">
              <n-space :size="8">
                <n-button size="small" type="primary" @click="openAddSkill">添加 Skill</n-button>
                <n-button size="small" @click="openEditSkill">编辑 Skill</n-button>
                <n-button size="small" type="error" @click="removeSkill">删除 Skill</n-button>
                <n-button size="small" @click="refreshSkills">刷新</n-button>
              </n-space>
              <n-data-table
                :columns="skillColumns"
                :data="skills"
                :bordered="false"
                size="small"
                :row-key="(row: any) => row.path"
                :checked-row-keys="selectedSkill ? [selectedSkill.path] : []"
                @update:checked-row-keys="(keys: Array<string | number>) => onSkillSelect(keys.map(String))"
              />
            </n-space>
          </template>
          <template #2>
            <n-card size="small" title="Skill 详情" style="height: 100%">
              <template v-if="selectedSkill">
                <n-descriptions :column="1" size="small" bordered>
                  <n-descriptions-item label="名称">{{ selectedSkill.name }}</n-descriptions-item>
                  <n-descriptions-item label="描述">{{ selectedSkill.description || '—' }}</n-descriptions-item>
                  <n-descriptions-item label="Context">{{ selectedSkill.context || '—' }}</n-descriptions-item>
                  <n-descriptions-item label="Agent">{{ selectedSkill.agent || '—' }}</n-descriptions-item>
                  <n-descriptions-item label="允许工具">{{ selectedSkill.allowed_tools || '—' }}</n-descriptions-item>
                  <n-descriptions-item label="用户可调用">{{ selectedSkill.user_invocable ? '是' : '否' }}</n-descriptions-item>
                  <n-descriptions-item label="禁用模型调用">{{ selectedSkill.disable_model_invocation ? '是' : '否' }}</n-descriptions-item>
                  <n-descriptions-item label="路径">{{ selectedSkill.path }}</n-descriptions-item>
                </n-descriptions>
                <n-text depth="3" style="font-size: 12px; display: block; margin: 8px 0">Skill 内容:</n-text>
                <n-input :value="selectedSkill.content" type="textarea" :autosize="{ minRows: 8, maxRows: 16 }" readonly style="font-family: 'Fira Code', Consolas, monospace; font-size: 12px" />
              </template>
              <n-text v-else depth="3">请在左侧选择一个 Skill</n-text>
            </n-card>
          </template>
        </n-split>
      </n-space>
    </n-tab-pane>

    <!-- ============ Hooks ============ -->
    <n-tab-pane name="hooks" tab="Hooks 配置">
      <n-space vertical :size="12">
        <n-tabs v-model:value="hookTab" type="line">
          <n-tab-pane name="pre" tab="Pre-Hooks">
            <n-space vertical :size="8">
              <n-text depth="3" style="font-size: 12px">Pre-Hooks 在操作执行前运行，可以用于验证、修改输入或阻止操作。</n-text>
              <n-data-table
                :columns="hookColumns"
                :data="preHooks"
                :bordered="false"
                size="small"
                :row-key="(row: any) => 'hook-' + row._i"
                :checked-row-keys="checkedPreHook"
                @update:checked-row-keys="(k: Array<string | number>) => (checkedPreHook = k.slice(0, 1).map(String))"
              />
              <n-space :size="8">
                <n-button size="small" @click="openAddHook('pre')">添加 Pre-Hook</n-button>
                <n-button size="small" :disabled="!selectedPreHook" @click="openEditHook('pre', selectedPreHook)">编辑</n-button>
                <n-button size="small" type="error" :disabled="!selectedPreHook" @click="removeHook('pre', selectedPreHook)">删除</n-button>
              </n-space>
            </n-space>
          </n-tab-pane>
          <n-tab-pane name="post" tab="Post-Hooks">
            <n-space vertical :size="8">
              <n-text depth="3" style="font-size: 12px">Post-Hooks 在操作执行后运行，可以用于通知、清理或触发后续操作。</n-text>
              <n-data-table
                :columns="hookColumns"
                :data="postHooks"
                :bordered="false"
                size="small"
                :row-key="(row: any) => 'hook-' + row._i"
                :checked-row-keys="checkedPostHook"
                @update:checked-row-keys="(k: Array<string | number>) => (checkedPostHook = k.slice(0, 1).map(String))"
              />
              <n-space :size="8">
                <n-button size="small" @click="openAddHook('post')">添加 Post-Hook</n-button>
                <n-button size="small" :disabled="!selectedPostHook" @click="openEditHook('post', selectedPostHook)">编辑</n-button>
                <n-button size="small" type="error" :disabled="!selectedPostHook" @click="removeHook('post', selectedPostHook)">删除</n-button>
              </n-space>
            </n-space>
          </n-tab-pane>
        </n-tabs>
        <div style="display: flex; justify-content: flex-end">
          <n-button size="small" type="primary" @click="saveHooks">保存配置</n-button>
        </div>
      </n-space>
    </n-tab-pane>

    <!-- ============ Memory ============ -->
    <n-tab-pane name="memory" tab="Memory 系统">
      <n-space vertical :size="12" style="max-width: 620px">
        <n-card size="small" title="Memory 设置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="启用自动记忆:">
              <n-checkbox v-model:checked="store.cfg.memory.autoMemoryEnabled">启用自动记忆</n-checkbox>
            </n-form-item>
            <n-form-item label="存储路径:">
              <n-input v-model:value="store.cfg.memory.memoryPath" placeholder="Memory 存储路径" />
            </n-form-item>
            <n-form-item label="最大条目数:">
              <n-input-number v-model:value="store.cfg.memory.maxEntries" :min="10" :max="10000" style="width: 200px" />
            </n-form-item>
            <n-form-item label="过期天数:">
              <n-input-number v-model:value="store.cfg.memory.expiryDays" :min="7" :max="365" style="width: 200px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="Memory 类型">
          <n-data-table :columns="memoryTypeColumns" :data="defaultMemoryTypes" :bordered="false" size="small" />
        </n-card>

        <n-card size="small" title="高级设置">
          <n-form label-placement="left" label-width="180">
            <n-form-item label="自动清理过期:">
              <n-checkbox v-model:checked="store.cfg.memory.autoCleanup">自动清理过期 Memory</n-checkbox>
            </n-form-item>
            <n-form-item label="启用压缩:">
              <n-checkbox v-model:checked="store.cfg.memory.compressionEnabled">启用 Memory 压缩</n-checkbox>
            </n-form-item>
            <n-form-item label="跨项目共享:">
              <n-checkbox v-model:checked="store.cfg.memory.crossProjectSharing">跨项目共享 Memory</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" @click="cleanupMemory">清理过期 Memory</n-button>
            <n-button size="small" type="primary" @click="saveMemory">保存设置</n-button>
          </n-space>
        </div>
      </n-space>
    </n-tab-pane>
  </n-tabs>

  <MCPServerModal v-model:show="mcpModalShow" :name="mcpModalName" :config="mcpModalConfig" @submit="onServerSubmit" />
  <MCPToolsDrawer v-model:show="toolsDrawerShow" :server-name="toolsDrawerServer" :config="toolsDrawerConfig" />
  <SkillFormModal v-model:show="skillModalShow" :data="skillModalData" @submit="onSkillSubmit" />
  <HookFormModal v-model:show="hookModalShow" :hook-type="hookModalType" :data="hookModalData" @submit="onHookSubmit" />
</template>
