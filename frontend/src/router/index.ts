import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: '/tasks'
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue')
  },
  {
    path: '/prompts',
    name: 'Prompts',
    component: () => import('../views/Prompts.vue')
  },
  {
    path: '/llm',
    name: 'LLMConfigs',
    component: () => import('../views/LLMConfigs.vue')
  },
  {
    path: '/data',
    name: 'DataView',
    component: () => import('../views/DataView.vue')
  },
  {
    path: '/executions',
    name: 'Executions',
    component: () => import('../views/Executions.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const title = to.meta.title as string
  if (title) {
    document.title = `${title} - Browser-Use WebUI`
  }
  next()
})

export default router
