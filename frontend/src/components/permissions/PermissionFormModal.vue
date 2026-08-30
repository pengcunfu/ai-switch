<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NCard, NForm, NFormItem, NInput, NSelect, NButton, useMessage } from 'naive-ui'

const props = defineProps<{ show: boolean; data?: Record<string, any> | null }>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'submit', value: Record<string, any>): void
}>()

const message = useMessage()
const form = ref<Record<string, any>>({ name: '', type: 'bash', permission: 'prompt' })

const typeOptions = [
  { label: 'Bash', value: 'bash' },
  { label: '文件操作', value: 'file' },
  { label: 'MCP 工具', value: 'mcp' },
  { label: '网络请求', value: 'network' },
  { label: '其他', value: 'other' },
]

const permissionOptions = [
  { label: '自动允许', value: 'allow' },
  { label: '需要确认', value: 'prompt' },
  { label: '拒绝', value: 'deny' },
]

watch(
  () => props.show,
  (v) => {
    if (v) {
      form.value = props.data ? { ...props.data } : { name: '', type: 'bash', permission: 'prompt' }
    }
  },
)

function submit() {
  if (!form.value.name.trim()) {
    message.warning('工具名称不能为空')
    return
  }
  emit('submit', { ...form.value })
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 420px" title="工具权限配置">
    <n-form label-placement="left" label-width="100">
      <n-form-item label="工具名称*:">
        <n-input v-model:value="form.name" placeholder="例如: Bash, Read, Grep" />
      </n-form-item>
      <n-form-item label="工具类型:">
        <n-select v-model:value="form.type" :options="typeOptions" />
      </n-form-item>
      <n-form-item label="权限级别:">
        <n-select v-model:value="form.permission" :options="permissionOptions" />
      </n-form-item>
    </n-form>
    <template #footer>
      <div style="display: flex; justify-content: flex-end; gap: 8px">
        <n-button size="small" @click="emit('update:show', false)">取消</n-button>
        <n-button size="small" type="primary" @click="submit">确定</n-button>
      </div>
    </template>
  </n-modal>
</template>
