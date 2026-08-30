<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NModal, NCard, NText, NButton, NSpace } from 'naive-ui'
import { GetVersion } from '../../../wailsjs/go/main/App'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{ (e: 'update:show', value: boolean): void }>()

const version = ref('')

onMounted(async () => {
  try {
    const v = await GetVersion()
    version.value = v.label ?? ''
  } catch {
    version.value = ''
  }
})

function close() {
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 420px" title="关于 Claude Configuration Manager">
    <div style="text-align: center; padding: 8px 0 16px">
      <div style="font-size: 20px; font-weight: 700; margin-bottom: 8px">Claude Configuration Manager</div>
      <n-text depth="3">{{ version }}</n-text>
      <div style="margin-top: 8px">
        <n-text>Claude Code 配置文件管理工具</n-text>
      </div>
      <n-text depth="3" style="font-size: 12px">© 2026 pengcunfu</n-text>
    </div>
    <template #footer>
      <div style="text-align: center">
        <n-button size="small" style="width: 120px" @click="close">确定</n-button>
      </div>
    </template>
  </n-modal>
</template>
