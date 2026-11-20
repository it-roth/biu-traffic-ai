import { createRouter, createWebHistory } from 'vue-router'

import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import TrafficScanView from '../views/TrafficScanView.vue'
import LiveCameraView from '../views/LiveCameraView.vue'
import HistoryView from '../views/HistoryView.vue'
import ViolationsView from '../views/ViolationsView.vue'

const routes = [
  {
    path: '/',
    redirect: () => {
      const token = localStorage.getItem('access_token')
      return token ? '/dashboard' : '/login'
    },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/scan',
    name: 'TrafficScan',
    component: TrafficScanView,
    meta: { requiresAuth: true },
  },
  {
    path: '/camera',
    name: 'LiveCamera',
    component: LiveCameraView,
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'AuditHistory',
    component: HistoryView,
    meta: { requiresAuth: true },
  },
  {
    path: '/violations',
    name: 'ViolationsReview',
    component: ViolationsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Authentication navigation guard
router.beforeEach((to) => {
  const token = localStorage.getItem('access_token')

  // If route requires auth and user is not logged in, force login form
  if (to.meta.requiresAuth && !token) {
    return '/login'
  }

  // If already logged in and visiting login or register, direct to dashboard
  if ((to.path === '/login' || to.path === '/register') && token) {
    return '/dashboard'
  }
})

export default router
