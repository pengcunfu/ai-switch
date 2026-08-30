<script setup lang="ts">
import { computed } from 'vue'
import {
  NTabs, NTabPane, NCard, NForm, NFormItem, NSelect, NInputNumber,
  NCheckbox, NButton, NSpace, NColorPicker, NSlider, useMessage, useDialog, NText,
} from 'naive-ui'
import { useConfigStore } from '../stores/config'

const store = useConfigStore()
const message = useMessage()
const dialog = useDialog()

// ============ 主题 ============
const themeModeOptions = [
  { label: '跟随系统', value: 'system' },
  { label: '浅色主题', value: 'light' },
  { label: '深色主题', value: 'dark' },
]
const colorSchemeOptions = [
  { label: '默认', value: 'default' },
  { label: '蓝色', value: 'blue' },
  { label: '绿色', value: 'green' },
  { label: '紫色', value: 'purple' },
  { label: '自定义', value: 'custom' },
]
const uiFontOptions = ['默认', '微软雅黑', '宋体', '黑体', 'Arial'].map((v) => ({ label: v, value: v }))
const codeFontOptions = ['Consolas', 'Courier New', 'Monaco', '默认'].map((v) => ({ label: v, value: v }))
const highlightPresetOptions = [
  { label: '默认 (VS Code)', value: 'vscode' },
  { label: 'Monokai', value: 'monokai' },
  { label: 'Solarized', value: 'solarized' },
  { label: 'GitHub', value: 'github' },
]

const customColors = computed(() => {
  if (typeof store.cfg.theme.customColors !== 'object' || store.cfg.theme.customColors === null) {
    store.cfg.theme.customColors = {}
  }
  return store.cfg.theme.customColors
})

const colorDefs = [
  { key: 'primary', label: '主要颜色', default: '#0066cc' },
  { key: 'accent', label: '强调颜色', default: '#0099ff' },
  { key: 'background', label: '背景颜色', default: '#ffffff' },
  { key: 'text', label: '文本颜色', default: '#333333' },
]

function resetTheme() {
  dialog.warning({
    title: '确认重置',
    content: '确定要重置为默认主题吗?',
    positiveText: '重置',
    negativeText: '取消',
    onPositiveClick: () => {
      store.cfg.theme = {
        mode: 'system',
        colorScheme: 'default',
        uiFont: '默认',
        codeFont: 'Consolas',
        fontSize: 12,
        codeFontSize: 11,
        customColors: { primary: '#0066cc', accent: '#0099ff', background: '#ffffff', text: '#333333' },
        syntaxHighlight: true,
        jsonHighlightPreset: 'vscode',
        windowOpacity: 1.0,
        animationEnabled: true,
        shadowEnabled: true,
      }
    },
  })
}

async function saveTheme() {
  try {
    await store.save()
    message.success('主题配置已保存! 部分设置可能需要重启应用后生效。')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function previewTheme() {
  message.info('主题预览功能开发中... 请保存设置后查看效果。')
}

// ============ UI/UX ============
const tabPositionOptions = [
  { label: '顶部', value: 'top' },
  { label: '底部', value: 'bottom' },
  { label: '左侧', value: 'left' },
  { label: '右侧', value: 'right' },
]

async function saveUIUX() {
  try {
    if (typeof store.cfg.uiux.notifications !== 'object' || store.cfg.uiux.notifications === null) {
      store.cfg.uiux.notifications = {}
    }
    await store.save()
    message.success('UI/UX 配置已保存! 部分设置可能需要重启应用后生效。')
  } catch (e: any) {
    message.error(`保存配置失败: ${e}`)
  }
}

function resetUIUX() {
  dialog.warning({
    title: '确认重置',
    content: '确定要重置为默认值吗?',
    positiveText: '重置',
    negativeText: '取消',
    onPositiveClick: () => {
      store.cfg.uiux = {
        showStatusBar: true,
        showToolbar: true,
        showConfigPath: true,
        tabPosition: 'top',
        doubleClickToEdit: true,
        confirmBeforeDelete: true,
        autoSave: false,
        autoSaveInterval: 5,
        showSpinnerTree: false,
        animationsEnabled: true,
        refreshRate: 100,
        notifications: { showSuccess: true, showError: true, showWarning: true, duration: 3 },
      }
    },
  })
}
</script>

<template>
  <n-tabs type="segment">
    <!-- ============ 主题外观 ============ -->
    <n-tab-pane name="theme" tab="主题外观">
      <n-space vertical :size="12" style="max-width: 620px">
        <n-card size="small" title="主题设置">
          <n-form label-placement="left" label-width="120">
            <n-form-item label="主题模式:">
              <n-select v-model:value="store.cfg.theme.mode" :options="themeModeOptions" style="width: 220px" />
            </n-form-item>
            <n-form-item label="配色方案:">
              <n-select v-model:value="store.cfg.theme.colorScheme" :options="colorSchemeOptions" style="width: 220px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="字体设置">
          <n-form label-placement="left" label-width="120">
            <n-form-item label="界面字体:">
              <n-select v-model:value="store.cfg.theme.uiFont" :options="uiFontOptions" style="width: 220px" />
            </n-form-item>
            <n-form-item label="代码字体:">
              <n-select v-model:value="store.cfg.theme.codeFont" :options="codeFontOptions" style="width: 220px" />
            </n-form-item>
            <n-form-item label="基础字体大小:">
              <n-input-number v-model:value="store.cfg.theme.fontSize" :min="8" :max="24" style="width: 160px" />
            </n-form-item>
            <n-form-item label="代码字体大小:">
              <n-input-number v-model:value="store.cfg.theme.codeFontSize" :min="8" :max="24" style="width: 160px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="自定义颜色">
          <n-form label-placement="left" label-width="120">
            <n-form-item v-for="def in colorDefs" :key="def.key" :label="`${def.label}:`">
              <n-color-picker v-model:value="customColors[def.key]" :show-alpha="false" :swatches="[def.default, '#0066cc', '#0099ff', '#333333', '#ffffff']" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="代码高亮设置">
          <n-form label-placement="left" label-width="120">
            <n-form-item label="语法高亮:">
              <n-checkbox v-model:checked="store.cfg.theme.syntaxHighlight">启用语法高亮</n-checkbox>
            </n-form-item>
            <n-form-item label="JSON 高亮方案:">
              <n-select v-model:value="store.cfg.theme.jsonHighlightPreset" :options="highlightPresetOptions" style="width: 220px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="界面布局">
          <n-form label-placement="left" label-width="120">
            <n-form-item label="窗口透明度:">
              <n-space :size="12" style="width: 320px">
                <n-slider v-model:value="store.cfg.theme.windowOpacity" :min="0.5" :max="1" :step="0.05" style="flex: 1" />
                <n-text>{{ Number(store.cfg.theme.windowOpacity).toFixed(2) }}</n-text>
              </n-space>
            </n-form-item>
            <n-form-item label="界面动画:">
              <n-checkbox v-model:checked="store.cfg.theme.animationEnabled">启用界面动画</n-checkbox>
            </n-form-item>
            <n-form-item label="窗口阴影:">
              <n-checkbox v-model:checked="store.cfg.theme.shadowEnabled">显示窗口阴影</n-checkbox>
            </n-form-item>
          </n-form>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" @click="resetTheme">重置默认</n-button>
            <n-button size="small" @click="previewTheme">预览效果</n-button>
            <n-button size="small" type="primary" @click="saveTheme">保存设置</n-button>
          </n-space>
        </div>
      </n-space>
    </n-tab-pane>

    <!-- ============ UI/UX 设置 ============ -->
    <n-tab-pane name="uiux" tab="UI/UX 设置">
      <n-space vertical :size="12" style="max-width: 620px">
        <n-card size="small" title="界面显示">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="状态栏:">
              <n-checkbox v-model:checked="store.cfg.uiux.showStatusBar">显示状态栏</n-checkbox>
            </n-form-item>
            <n-form-item label="工具栏:">
              <n-checkbox v-model:checked="store.cfg.uiux.showToolbar">显示工具栏</n-checkbox>
            </n-form-item>
            <n-form-item label="配置文件路径:">
              <n-checkbox v-model:checked="store.cfg.uiux.showConfigPath">显示配置文件路径</n-checkbox>
            </n-form-item>
            <n-form-item label="标签页位置:">
              <n-select v-model:value="store.cfg.uiux.tabPosition" :options="tabPositionOptions" style="width: 200px" />
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="交互设置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="双击编辑:">
              <n-checkbox v-model:checked="store.cfg.uiux.doubleClickToEdit">双击编辑项目</n-checkbox>
            </n-form-item>
            <n-form-item label="删除确认:">
              <n-checkbox v-model:checked="store.cfg.uiux.confirmBeforeDelete">删除前确认</n-checkbox>
            </n-form-item>
            <n-form-item label="自动保存:">
              <n-checkbox v-model:checked="store.cfg.uiux.autoSave">自动保存配置</n-checkbox>
            </n-form-item>
            <n-form-item label="自动保存间隔:">
              <n-input-number v-model:value="store.cfg.uiux.autoSaveInterval" :min="1" :max="60" style="width: 160px">
                <template #suffix>分钟</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="性能设置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="Spinner 树:">
              <n-checkbox v-model:checked="store.cfg.uiux.showSpinnerTree">显示 Spinner 树</n-checkbox>
            </n-form-item>
            <n-form-item label="界面动画:">
              <n-checkbox v-model:checked="store.cfg.uiux.animationsEnabled">启用界面动画</n-checkbox>
            </n-form-item>
            <n-form-item label="刷新频率:">
              <n-input-number v-model:value="store.cfg.uiux.refreshRate" :min="10" :max="1000" style="width: 160px">
                <template #suffix>ms</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </n-card>

        <n-card size="small" title="通知设置">
          <n-form label-placement="left" label-width="140">
            <n-form-item label="成功通知:">
              <n-checkbox v-model:checked="store.cfg.uiux.notifications.showSuccess">显示成功通知</n-checkbox>
            </n-form-item>
            <n-form-item label="错误通知:">
              <n-checkbox v-model:checked="store.cfg.uiux.notifications.showError">显示错误通知</n-checkbox>
            </n-form-item>
            <n-form-item label="警告通知:">
              <n-checkbox v-model:checked="store.cfg.uiux.notifications.showWarning">显示警告通知</n-checkbox>
            </n-form-item>
            <n-form-item label="通知持续时间:">
              <n-input-number v-model:value="store.cfg.uiux.notifications.duration" :min="1" :max="10" style="width: 160px">
                <template #suffix>秒</template>
              </n-input-number>
            </n-form-item>
          </n-form>
        </n-card>

        <div style="display: flex; justify-content: flex-end">
          <n-space :size="8">
            <n-button size="small" @click="resetUIUX">重置默认</n-button>
            <n-button size="small" type="primary" @click="saveUIUX">保存设置</n-button>
          </n-space>
        </div>
      </n-space>
    </n-tab-pane>
  </n-tabs>
</template>
