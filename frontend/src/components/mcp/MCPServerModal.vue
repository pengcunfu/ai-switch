<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  NModal, NCard, NTabs, NTabPane, NForm, NFormItem, NInput, NButton,
  NSpace, NDataTable, NText, useMessage,
} from 'naive-ui'
import { PickFile } from '../../../wailsjs/go/main/App'

const props = defineProps<{ show: boolean; name?: string; config?: Record<string, any> | null }>()
const emit = defineEmits<{ (e: 'update:show', value: boolean): void; (e: 'submit', value: { name: string; config: Record<string, any> }): void }>()

const message = useMessage()
const activeTab = ref('form')

const name = ref('')
const command = ref('')
const argsText = ref('')
const envRows = ref<Array<{ key: string; value: string }>>([])
const jsonText = ref('')

watch(
  () => props.show,
  (v) => {
    if (!v) return
    name.value = props.name ?? ''
    command.value = props.config?.command ?? ''
    const args = props.config?.args
    argsText.value = Array.isArray(args) ? args.join(' ') : args ? String(args) : ''
    const env = props.config?.env ?? {}
    envRows.value = Object.keys(env).map((k) => ({ key: k, value: String(env[k]) }))
    jsonText.value = JSON.stringify(props.config ?? {}, null, 2)
    activeTab.value = 'form'
  },
)

function syncFormToJson() {
  jsonText.value = JSON.stringify(buildConfigFromForm(), null, 2)
}

function syncJsonToForm() {
  try {
    const cfg = JSON.parse(jsonText.value)
    command.value = cfg.command ?? ''
    argsText.value = Array.isArray(cfg.args) ? cfg.args.join(' ') : cfg.args ? String(cfg.args) : ''
    const env = cfg.env ?? {}
    envRows.value = Object.keys(env).map((k) => ({ key: k, value: String(env[k]) }))
  } catch (e: any) {
    message.warning(`JSON 格式无效，无法同步到表单模式: ${e}`)
    activeTab.value = 'json'
  }
}

function buildConfigFromForm(): Record<string, any> {
  const cfg: Record<string, any> = {}
  if (command.value.trim()) cfg.command = command.value.trim()
  const args = argsText.value.trim() ? argsText.value.trim().split(/\s+/) : []
  if (args.length) cfg.args = args
  const env: Record<string, string> = {}
  for (const row of envRows.value) {
    if (row.key.trim()) env[row.key.trim()] = row.value
  }
  if (Object.keys(env).length) cfg.env = env
  return cfg
}

const envColumns = [
  { title: '变量名', key: 'key' },
  { title: '值', key: 'value' },
]

function addEnvRow() {
  envRows.value.push({ key: '', value: '' })
}
function removeEnvRow(row: any) {
  envRows.value = envRows.value.filter((r) => r !== row)
}

async function browseCommand() {
  const path = await PickFile('选择可执行文件', '可执行文件 (*.exe *.bat *.cmd);;所有文件 (*.*)')
  if (path) command.value = path
}

function formatJson() {
  try {
    jsonText.value = JSON.stringify(JSON.parse(jsonText.value), null, 2)
  } catch (e: any) {
    message.error(`JSON 格式错误: ${e}`)
  }
}

function validateJson() {
  try {
    JSON.parse(jsonText.value)
    message.success('JSON 格式正确!')
  } catch (e: any) {
    message.error(`JSON 格式错误: ${e}`)
  }
}

function submit() {
  if (!name.value.trim()) {
    message.warning('服务器名称不能为空')
    return
  }
  let config: Record<string, any>
  if (activeTab.value === 'form') {
    if (!command.value.trim()) {
      message.warning('命令不能为空')
      return
    }
    config = buildConfigFromForm()
  } else {
    try {
      config = JSON.parse(jsonText.value)
    } catch (e: any) {
      message.error(`JSON 格式错误: ${e}`)
      return
    }
  }
  emit('submit', { name: name.value.trim(), config })
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 700px; max-width: 90vw" title="MCP 服务器配置">
    <n-space vertical :size="12">
      <n-form label-placement="left" label-width="100">
        <n-form-item label="服务器名称:">
          <n-input v-model:value="name" placeholder="MCP 服务器名称" />
        </n-form-item>
      </n-form>

      <n-tabs v-model:value="activeTab" type="line" @update:value="(t: string) => (t === 'json' ? syncFormToJson() : syncJsonToForm())">
        <n-tab-pane name="form" tab="表单模式">
          <n-form label-placement="left" label-width="100">
            <n-form-item label="命令:">
              <n-space :size="8" style="width: 100%">
                <n-input v-model:value="command" placeholder="MCP 服务器启动命令" style="flex: 1" />
                <n-button size="small" @click="browseCommand">浏览...</n-button>
              </n-space>
            </n-form-item>
            <n-form-item label="参数:">
              <n-input v-model:value="argsText" placeholder="用空格分隔参数，例如: --host localhost --port 3306" />
            </n-form-item>
          </n-form>

          <n-card size="small" title="环境变量 (可选)">
            <n-space vertical :size="8">
              <n-data-table :columns="envColumns" :data="envRows" :bordered="false" size="small" />
              <n-space :size="8">
                <n-button size="tiny" @click="addEnvRow">添加变量</n-button>
                <n-button size="tiny" @click="removeEnvRow(envRows[0])" :disabled="!envRows.length">删除变量</n-button>
              </n-space>
            </n-space>
          </n-card>
        </n-tab-pane>

        <n-tab-pane name="json" tab="JSON 模式">
          <n-text depth="3" style="font-size: 12px">提示: 直接编辑 JSON 配置，支持所有 MCP 服务器属性 (如 url, headers, type 等)</n-text>
          <n-input
            v-model:value="jsonText"
            type="textarea"
            :autosize="{ minRows: 14, maxRows: 20 }"
            style="margin-top: 8px; font-family: 'Fira Code', Consolas, monospace; font-size: 12px"
          />
          <n-space :size="8" style="margin-top: 8px">
            <n-button size="tiny" @click="formatJson">格式化 JSON</n-button>
            <n-button size="tiny" @click="validateJson">验证 JSON</n-button>
          </n-space>
        </n-tab-pane>
      </n-tabs>
    </n-space>

    <template #footer>
      <div style="display: flex; justify-content: flex-end; gap: 8px">
        <n-button size="small" @click="emit('update:show', false)">取消</n-button>
        <n-button size="small" type="primary" @click="submit">确定</n-button>
      </div>
    </template>
  </n-modal>
</template>
