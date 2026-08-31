<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NCard, NSpace, NText, NButton, NTag, useMessage } from 'naive-ui'
import { GetCodexProfiles, SwitchCodexProfile, OpenInExplorer } from '../../wailsjs/go/main/App'
import type { codex } from '../../wailsjs/go/models'

const message = useMessage()

const dir = ref('')
const exists = ref(false)
const profiles = ref<codex.Profile[]>([])
const active = ref('')
const activeModel = ref('')
const catalogPath = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await GetCodexProfiles()
    dir.value = res.dir
    exists.value = res.exists
    profiles.value = res.profiles ?? []
    active.value = res.active
    activeModel.value = res.activeModel
    catalogPath.value = res.catalogPath
  } catch (e: any) {
    message.error(`读取 Codex 配置失败: ${e}`)
  } finally {
    loading.value = false
  }
}

async function switchTo(name: string) {
  try {
    const res = await SwitchCodexProfile(name)
    if (res.warning) message.warning(res.warning)
    message.success(res.message || `已切换到档案 '${name}'`)
    await load()
  } catch (e: any) {
    message.error(String(e))
  }
}

async function openCodexDir() {
  try {
    await OpenInExplorer(dir.value)
  } catch (e: any) {
    message.error(`打开目录失败: ${e}`)
  }
}

onMounted(load)
</script>

<template>
  <n-space vertical :size="12" style="max-width: 860px">
    <n-card size="small" title="Codex 模型切换">
      <template v-if="!exists">
        <n-text>未找到 Codex 配置目录：{{ dir }}<br />请先安装 Codex CLI 后再使用模型切换。</n-text>
      </template>

      <template v-else>
        <n-space vertical :size="12">
          <n-text depth="3" style="font-size: 12px">
            切换将整体替换 ~/.codex 下的 config.toml 与 models.json（每个档案一套文件，如 config-mimo.toml + models-mimo.json），新启动的 Codex 会话生效。
          </n-text>

          <n-space :size="8" align="center">
            <n-text>当前活动:</n-text>
            <n-tag v-if="active !== '自定义'" type="success">{{ active }} · {{ activeModel }}</n-tag>
            <n-tag v-else type="warning">自定义（当前配置未匹配任何档案）</n-tag>
          </n-space>

          <div v-for="p in profiles" :key="p.name">
            <n-space :size="8" align="center" style="margin-bottom: 4px">
              <n-text strong style="width: 110px">{{ p.name }}</n-text>
              <n-text depth="2" style="width: 260px; user-select: text">{{ p.model }}</n-text>
              <n-tag size="small" :type="p.active ? 'success' : 'default'">{{ p.provider }}</n-tag>
              <n-tag v-if="p.active" size="small" type="success">当前</n-tag>
              <n-button size="small" :disabled="p.active" @click="switchTo(p.name)">切换</n-button>
            </n-space>
            <n-text v-if="!p.hasModels" depth="3" style="font-size: 12px; color: #f0a020">
              该档案没有 models 文件，切换时只替换 config.toml，模型目录保持不变
            </n-text>
          </div>

          <n-text v-if="catalogPath" depth="3" style="font-size: 12px; user-select: text">模型目录: {{ catalogPath }}</n-text>

          <n-space :size="8">
            <n-button size="small" :loading="loading" @click="load">重新加载</n-button>
            <n-button size="small" @click="openCodexDir">打开 .codex 文件夹</n-button>
          </n-space>
        </n-space>
      </template>
    </n-card>
  </n-space>
</template>
