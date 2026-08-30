<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  NModal, NCard, NForm, NFormItem, NInput, NSelect, NCheckbox,
  NButton, NSpace, NText, useMessage,
} from 'naive-ui'

const props = defineProps<{ show: boolean; data?: Record<string, any> | null }>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'submit', value: Record<string, any>): void
}>()

const message = useMessage()
const form = ref<Record<string, any>>({
  name: '',
  description: '',
  context: '',
  agent: '',
  allowed_tools: '',
  argument_hint: '',
  user_invocable: true,
  disable_model_invocation: false,
  content: '',
})

const contextOptions = [
  { label: '(默认: 无)', value: '' },
  { label: 'fork', value: 'fork' },
  { label: 'agent', value: 'agent' },
]
const agentOptions = [
  { label: '(默认: 无)', value: '' },
  { label: 'Explore', value: 'Explore' },
  { label: 'Plan', value: 'Plan' },
  { label: 'general-purpose', value: 'general-purpose' },
]

watch(
  () => props.show,
  (v) => {
    if (!v) return
    form.value = props.data
      ? {
          name: props.data.name ?? '',
          description: props.data.description ?? '',
          context: props.data.context ?? '',
          agent: props.data.agent ?? '',
          allowed_tools: props.data.allowed_tools ?? '',
          argument_hint: props.data.argument_hint ?? '',
          user_invocable: props.data.user_invocable !== false,
          disable_model_invocation: props.data.disable_model_invocation === true,
          content: props.data.content ?? '',
          oldName: props.data.name ?? '',
        }
      : {
          name: '', description: '', context: '', agent: '',
          allowed_tools: '', argument_hint: '', user_invocable: true,
          disable_model_invocation: false, content: '', oldName: '',
        }
  },
)

function submit() {
  if (!form.value.name.trim()) {
    message.warning('Skill 名称不能为空')
    return
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(form.value.name)) {
    message.warning('Skill 名称只能包含字母、数字、连字符和下划线')
    return
  }
  emit('submit', { ...form.value })
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 700px; max-width: 90vw" title="Skill 配置">
    <n-space vertical :size="12">
      <n-card size="small" title="Frontmatter 配置">
        <n-form label-placement="left" label-width="100">
          <n-form-item label="名称*:">
            <n-input v-model:value="form.name" placeholder="skill 名称 (同时作为目录名和斜杠命令名)" />
          </n-form-item>
          <n-form-item label="描述:">
            <n-input v-model:value="form.description" placeholder="简要描述此 skill 的功能和使用场景" />
          </n-form-item>
          <n-form-item label="Context:">
            <n-select v-model:value="form.context" :options="contextOptions" :show-arrow="true" filterable tag />
          </n-form-item>
          <n-form-item label="Agent:">
            <n-select v-model:value="form.agent" :options="agentOptions" :show-arrow="true" filterable tag />
          </n-form-item>
          <n-form-item label="允许工具:">
            <n-input v-model:value="form.allowed_tools" placeholder="例如: Read Grep Bash (空格分隔)" />
          </n-form-item>
          <n-form-item label="参数提示:">
            <n-input v-model:value="form.argument_hint" placeholder="例如: [issue-number] 或 [filename] [format]" />
          </n-form-item>
          <n-form-item>
            <n-space :size="16">
              <n-checkbox v-model:checked="form.user_invocable">用户可调用 (斜杠命令)</n-checkbox>
              <n-checkbox v-model:checked="form.disable_model_invocation">禁用模型自动调用</n-checkbox>
            </n-space>
          </n-form-item>
        </n-form>
      </n-card>

      <n-card size="small" title="Skill 内容 (SKILL.md 正文)">
        <n-text depth="3" style="font-size: 12px">提示: 这是 Claude 在触发此 skill 时收到的指令内容。Frontmatter 已在上方配置，无需在此重复。</n-text>
        <n-input
          v-model:value="form.content"
          type="textarea"
          :autosize="{ minRows: 8, maxRows: 14 }"
          style="margin-top: 8px; font-family: 'Fira Code', Consolas, monospace; font-size: 12px"
          placeholder="输入 skill 的指令内容..."
        />
      </n-card>
    </n-space>

    <template #footer>
      <div style="display: flex; justify-content: flex-end; gap: 8px">
        <n-button size="small" @click="emit('update:show', false)">取消</n-button>
        <n-button size="small" type="primary" @click="submit">确定</n-button>
      </div>
    </template>
  </n-modal>
</template>
