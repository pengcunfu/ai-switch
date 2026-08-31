import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  // 桌面 WebView 内使用 hash 模式最稳妥
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/stats' },
    { path: '/stats', name: 'stats', component: () => import('../views/StatisticsView.vue'), meta: { title: '统计信息' } },
    { path: '/basic', name: 'basic', component: () => import('../views/BasicView.vue'), meta: { title: '基础配置' } },
    { path: '/model-permissions', name: 'modelPermissions', component: () => import('../views/ModelPermissionsView.vue'), meta: { title: '模型与权限' } },
    { path: '/features', name: 'features', component: () => import('../views/FeaturesView.vue'), meta: { title: '功能配置' } },
    { path: '/appearance', name: 'appearance', component: () => import('../views/AppearanceView.vue'), meta: { title: '外观与界面' } },
    { path: '/integration', name: 'integration', component: () => import('../views/IntegrationView.vue'), meta: { title: '集成与工具' } },
    // Codex 工具
    { path: '/codex/models', name: 'codexModels', component: () => import('../views/CodexView.vue'), meta: { title: '模型切换' } },
  ],
})

export default router
