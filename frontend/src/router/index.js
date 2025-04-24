import { createRouter, createWebHistory } from 'vue-router'

import ApiDocsView from '../views/ApiDocsView.vue'
import DocHistoryView from '../views/DocHistoryView.vue'
import GenerateDocView from '../views/GenerateDocView.vue'
import ModelSettingsView from '../views/ModelSettingsView.vue'
import TemplateManagementView from '../views/TemplateManagementView.vue'

const routes = [
  {
    path: '/',
    name: 'GenerateDoc',
    component: GenerateDocView,
    meta: { title: 'Generate Document' },
  },
  {
    path: '/templates',
    name: 'Templates',
    component: TemplateManagementView,
    meta: { title: 'Manage Templates' },
  },
  {
    path: '/settings/llm',
    name: 'ModelSettings',
    component: ModelSettingsView,
    meta: { title: 'LLM Settings' },
  },
  {
    path: '/history/docs',
    name: 'DocHistory',
    component: DocHistoryView,
    meta: { title: 'Document History' },
  },
  {
    path: '/api-docs',
    name: 'ApiDocs',
    component: ApiDocsView,
    meta: { title: 'API Documentation' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), // Or createWebHashHistory
  routes,
  linkActiveClass: 'active', // Add Bootstrap's 'active' class to active router links
})

// Update browser tab title
router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} | SME Doc Generator` : 'SME Doc Generator Dashboard'
  next()
})

export default router
