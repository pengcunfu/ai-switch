<script setup lang="ts">
import { computed } from 'vue'
import {
  NConfigProvider, NMessageProvider, NDialogProvider, NLoadingBarProvider,
  darkTheme as darkThemeNaive,
} from 'naive-ui'
import { useConfigStore } from './stores/config'
import AppShell from './AppShell.vue'

const store = useConfigStore()
const darkTheme = computed(() => store.appState.theme?.mode === 'dark')
</script>

<template>
  <n-config-provider :theme="darkTheme ? darkThemeNaive : null">
    <n-message-provider>
      <n-dialog-provider>
        <n-loading-bar-provider>
          <AppShell />
        </n-loading-bar-provider>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>
