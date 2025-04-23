import { createRouter, createWebHistory } from 'vue-router'
import AuditTrailView from '../views/AuditTrailView.vue'
import ConfigurationView from '../views/ConfigurationView.vue'
import DashboardView from '../views/DashboardView.vue'
import DetailedLogsView from '../views/DetailedLogsView.vue'
import HistoryView from '../views/HistoryView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: DashboardView,
    meta: { title: 'Dashboard' }, // Add titles for browser tab
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { title: 'Sync History' },
  },
  {
    path: '/logs',
    name: 'DetailedLogs',
    component: DetailedLogsView,
    meta: { title: 'Detailed Logs' },
  },
  // Optional: Route for logs specific to a job
  {
    path: '/logs/:jobId',
    name: 'JobLogs',
    component: DetailedLogsView, // Reuse the same component
    props: true, // Pass route params as props
    meta: { title: 'Job Logs' },
  },
  {
    path: '/audit',
    name: 'AuditTrail',
    component: AuditTrailView,
    meta: { title: 'Audit Trail' },
  },
  {
    path: '/config',
    name: 'Configuration',
    component: ConfigurationView,
    meta: { title: 'Configuration' },
  },
  // Add a fallback route for 404?
  // { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFoundView }
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
