<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  NDrawer, NDrawerContent, NCard, NDataTable, NInput, NButton,
  NSpace, NSpin, NText, useMessage,
} from 'naive-ui'
import { ListMCPToolsAndResources } from '../../../wailsjs/go/main/App'

const props = defineProps<{ show: boolean; serverName?: string; config?: Record<string, any> | null }>()
const emit = defineEmits<{ (e: 'update:show', value: boolean): void }>()

const message = useMessage()
const loading = ref(false)
const tools = ref<any[]>([])
const resources = ref<any[]>([])
const detail = ref('')
const serverInfoText = ref('')

const toolColumns = [
  { title: '工具名称', key: 'name' },
  { title: '描述', key: 'description' },
  { title: '输入架构', key: 'inputSchema', ellipsis: { tooltip: true } },
]
const resourceColumns = [
  { title: '资源名称', key: 'name' },
  { title: 'URI', key: 'uri' },
  { title: '描述', key: 'description' },
]

watch(
  () => props.show,
  async (v) => {
    if (!v) return
    const cfg = props.config ?? {}
    serverInfoText.value = `命令: ${cfg.command ?? ''}\n参数: ${(cfg.args ?? []).join(' ')}`
    tools.value = []
    resources.value = []
    detail.value = ''
    loading.value = true
    try {
      const result = await ListMCPToolsAndResources(cfg)
      tools.value = result.tools ?? []
      resources.value = result.resources ?? []
      detail.value = `成功加载 ${tools.value.length} 个工具和 ${resources.value.length} 个资源`
    } catch (e: any) {
      detail.value = `连接失败: ${e}`
      message.error(String(e))
    } finally {
      loading.value = false
    }
  },
)
</script>

<template>
  <n-drawer :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" :width="820">
    <n-drawer-content :title="`MCP 工具列表 - ${props.serverName}`" closable>
      <n-space vertical :size="12">
        <n-card size="small" title="服务器信息">
          <pre style="margin: 0; white-space: pre-wrap; font-family: inherit; font-size: 12px">{{ serverInfoText }}</pre>
        </n-card>

        <n-card size="small" title="可用工具">
          <n-spin :show="loading">
            <n-data-table :columns="toolColumns" :data="tools" :bordered="false" size="small" />
          </n-spin>
        </n-card>

        <n-card size="small" title="可用资源">
          <n-spin :show="loading">
            <n-data-table :columns="resourceColumns" :data="resources" :bordered="false" size="small" />
          </n-spin>
        </n-card>

        <n-card size="small" title="详细信息">
          <n-input :value="detail" type="textarea" :autosize="{ minRows: 2, maxRows: 6 }" readonly />
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" :loading="loading" @click="emit('update:show', false)">关闭</n-button>
          </n-space>
        </div>
      </n-space>
    </n-drawer-content>
  </n-drawer>
</template>
