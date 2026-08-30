<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  NModal, NCard, NForm, NFormItem, NInput, NSelect, NCheckbox,
  NButton, NSpace, NText, useMessage,
} from 'naive-ui'

const props = defineProps<{ show: boolean; hookType?: 'pre' | 'post'; data?: Record<string, any> | null }>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'submit', value: Record<string, any>): void
}>()

const message = useMessage()
const form = ref<Record<string, any>>({ trigger: '', command: '', workingDir: '', description: '', enabled: true })

const triggerOptions = computed(() => {
  if (props.hookType === 'pre') {
    return [
      { label: 'Bash 命令执行前', value: 'before-bash' },
      { label: '文件写入前', value: 'before-write' },
      { label: '工具调用前', value: 'before-tool' },
      { label: 'Git 提交前', value: 'before-git-commit' },
    ]
  }
  return [
    { label: 'Bash 命令执行后', value: 'after-bash' },
    { label: '文件写入后', value: 'after-write' },
    { label: '工具调用后', value: 'after-tool' },
    { label: 'Git 提交后', value: 'after-git-commit' },
    { label: '配置保存后', value: 'after-config-save' },
  ]
})

watch(
  () => props.show,
  (v) => {
    if (!v) return
    form.value = props.data
      ? { ...props.data }
      : { trigger: '', command: '', workingDir: '', description: '', enabled: true }
  },
)

function submit() {
  if (!form.value.command.trim()) {
    message.warning('命令不能为空')
    return
  }
  emit('submit', { ...form.value })
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 520px" :title="`${props.hookType === 'pre' ? 'Pre-Hook' : 'Post-Hook'} 配置`">
    <n-form label-placement="left" label-width="110">
      <n-form-item label="触发时机:">
        <n-select v-model:value="form.trigger" :options="triggerOptions" placeholder="选择触发时机" />
      </n-form-item>
      <n-form-item label="命令/脚本*:">
        <n-input v-model:value="form.command" placeholder="例如: python /path/to/script.py" />
      </n-form-item>
      <n-form-item label="工作目录:">
        <n-input v-model:value="form.workingDir" placeholder="留空使用当前目录" />
      </n-form-item>
      <n-form-item label="描述:">
        <n-input v-model:value="form.description" placeholder="简要描述此 Hook 的用途" />
      </n-form-item>
      <n-form-item>
        <n-checkbox v-model:checked="form.enabled">启用此 Hook</n-checkbox>
      </n-form-item>
      <n-text depth="3" style="font-size: 11px; white-space: pre-wrap">
        可用环境变量:
        $CLAUDE_TOOL - 被调用的工具名称
        $CLAUDE_ARGS - 工具参数
        $CLAUDE_EXIT_CODE - 退出码 (仅 post-hook)
        $CLAUDE_CONFIG - 配置文件路径
      </n-text>
    </n-form>
    <template #footer>
      <div style="display: flex; justify-content: flex-end; gap: 8px">
        <n-button size="small" @click="emit('update:show', false)">取消</n-button>
        <n-button size="small" type="primary" @click="submit">确定</n-button>
      </div>
    </template>
  </n-modal>
</template>
