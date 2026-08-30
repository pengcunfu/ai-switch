<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NCard, NButton, NSpace, NInput, useMessage } from 'naive-ui'
import { useConfigStore } from '../../stores/config'
import { CopyToClipboard } from '../../../wailsjs/go/main/App'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ (e: 'update:show', value: boolean): void }>()

const store = useConfigStore()
const message = useMessage()
const text = ref('')
const loading = ref(false)

watch(
  () => props.show,
  (v) => {
    if (v) {
      text.value = JSON.stringify(store.cfg, null, 2)
    }
  },
)

function formatJson() {
  try {
    text.value = JSON.stringify(JSON.parse(text.value), null, 2)
    message.success('JSON 已格式化')
  } catch (e: any) {
    message.error(`JSON 格式错误: ${e}`)
  }
}

async function copyAll() {
  await CopyToClipboard(text.value)
  message.success('配置 JSON 已复制到剪贴板')
}

async function saveConfig() {
  try {
    const parsed = JSON.parse(text.value)
    store.cfg = parsed
    await store.save()
    message.success('配置已保存')
    emit('update:show', false)
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function close() {
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 860px; max-width: 90vw" title="完整配置 (JSON)">
    <template #header-extra>
      <n-space :size="8">
        <n-button size="small" @click="formatJson">格式化 JSON</n-button>
        <n-button size="small" @click="copyAll">复制全部</n-button>
        <n-button size="small" type="primary" :loading="loading" @click="saveConfig">保存配置</n-button>
        <n-button size="small" @click="close">关闭</n-button>
      </n-space>
    </template>
    <n-input
      v-model:value="text"
      type="textarea"
      :autosize="{ minRows: 18, maxRows: 26 }"
      style="font-family: 'Fira Code', Consolas, monospace; font-size: 12px"
      placeholder="JSON 配置内容"
    />
  </n-modal>
</template>
