<script setup lang="ts">
import { ref, watch } from 'vue'
import { NModal, NCard, NForm, NFormItem, NInput, NButton, useMessage } from 'naive-ui'

const props = defineProps<{ show: boolean }>()
const emit = defineEmits<{
  (e: 'update:show', value: boolean): void
  (e: 'submit', value: string): void
}>()

const message = useMessage()
const repoName = ref('')

watch(
  () => props.show,
  (v) => {
    if (v) repoName.value = ''
  },
)

function submit() {
  const name = repoName.value.trim()
  if (!name) {
    message.warning('仓库名称不能为空')
    return
  }
  if (!name.includes('/')) {
    message.warning('仓库名称格式应为: username/repo-name')
    return
  }
  emit('submit', name)
  emit('update:show', false)
}
</script>

<template>
  <n-modal :show="props.show" :on-update:show="(v: boolean) => emit('update:show', v)" preset="card" style="width: 420px" title="添加 GitHub 仓库">
    <n-form label-placement="left" label-width="90">
      <n-form-item label="仓库名称:">
        <n-input v-model:value="repoName" placeholder="例如: username/repo-name" @keydown.enter="submit" />
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
