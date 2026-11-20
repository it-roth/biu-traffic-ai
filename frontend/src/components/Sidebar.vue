<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import biuLogo from '../assets/biu-logo.png'

const props = defineProps({
  currentLang: {
    type: String,
    default: 'en'
  },
  isOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:lang', 'close-sidebar'])

const route = useRoute()
const router = useRouter()

const lang = computed(() => props.currentLang || localStorage.getItem('biu_lang') || 'en')

const currentUser = computed(() => {
  try {
    const raw = localStorage.getItem('biu_user')
    if (raw) return JSON.parse(raw)
  } catch {}
  return {
    username: 'admin',
    role: 'System Administrator',
    email: 'admin@istad.edu.kh'
  }
})

const userInitials = computed(() => {
  const name = currentUser.value.username || 'SA'
  return name.slice(0, 2).toUpperCase()
})

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

// Navigation structure matching User's Enterprise Sidebar screenshot
const menuGroups = [
  {
    title: 'Operations',
    titleKm: 'ប្រតិបត្តិការ',
    items: [
      {
        name: 'Overview',
        nameKm: 'ទិដ្ឋភាពទូទៅ',
        path: '/dashboard',
        icon: 'overview'
      },
      {
        name: 'AI Traffic Scanner',
        nameKm: 'ស្កេនចរាចរណ៍ AI',
        path: '/scan',
        icon: 'scan'
      },
      {
        name: 'Live Camera Feed',
        nameKm: 'កាមេរ៉ាផ្សាយផ្ទាល់',
        path: '/camera',
        icon: 'camera',
        badge: 'Live'
      }
    ]
  },
  {
    title: 'Audit & Law Enforcement',
    titleKm: 'កំណត់ត្រា និង ការអនុវត្តច្បាប់',
    items: [
      {
        name: 'Audit Log & History',
        nameKm: 'ប្រវត្តិនៃការកត់ត្រា',
        path: '/history',
        icon: 'audit'
      },
      {
        name: 'Violation Records',
        nameKm: 'កំណត់ត្រាបទល្មើស',
        path: '/violations',
        icon: 'violations'
      }
    ]
  }
]
</script>

<template>
  <div>
    <!-- Mobile Backdrop -->
    <div
      v-if="isOpen"
      class="fixed inset-0 z-40 bg-black/75 backdrop-blur-sm lg:hidden transition-opacity"
      @click="emit('close-sidebar')"
    ></div>

    <!-- Enterprise Sidebar (Matching User Screenshot 1) -->
    <aside
      :class="[
        'fixed top-0 bottom-0 left-0 z-50 w-64 lg:w-72 bg-[#090c14] border-r border-zinc-800/90 flex flex-col justify-between transition-transform duration-200 ease-in-out select-none',
        isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
      ]"
    >
      <!-- Top Branding Section (Matching Screenshot: ISTAD / Identity & Access style) -->
      <div class="px-5 py-4 border-b border-zinc-800/80">
        <div class="flex items-center gap-3">
          <img
            :src="biuLogo"
            alt="BELTEI"
            class="h-9 w-auto object-contain flex-shrink-0 drop-shadow"
          />
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 text-xs text-zinc-400 font-medium">
              <span class="font-bold text-white tracking-tight">BIU</span>
              <span class="text-zinc-600">/</span>
              <span class="truncate">Traffic Enforcement</span>
            </div>
            <p class="text-[10px] text-zinc-500 font-mono mt-0.5 truncate">
              BELTEI International Univ.
            </p>
          </div>
        </div>
      </div>

      <!-- Navigation Menu Groups (Matching Screenshot 1) -->
      <nav class="flex-1 px-3 py-4 space-y-6 overflow-y-auto">
        <div v-for="group in menuGroups" :key="group.title" class="space-y-1">
          
          <!-- Category Section Header -->
          <div class="px-3 pb-1.5 text-[11px] font-semibold text-zinc-400">
            {{ lang === 'km' ? group.titleKm : group.title }}
          </div>

          <!-- Nav Items -->
          <router-link
            v-for="item in group.items"
            :key="item.path"
            :to="item.path"
            @click="emit('close-sidebar')"
            :class="[
              'group relative flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all duration-150',
              route.path === item.path
                ? 'bg-blue-600/10 text-blue-400 font-semibold shadow-sm'
                : 'text-zinc-400 hover:text-white hover:bg-zinc-900/60'
            ]"
          >
            <!-- Vertical Active Pill Indicator (Exact match to screenshot 1 active state) -->
            <span
              v-if="route.path === item.path"
              class="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r-full bg-[#006CB8]"
            ></span>

            <!-- Overview Icon -->
            <svg
              v-if="item.icon === 'overview'"
              class="h-4 w-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>

            <!-- Scanner Icon -->
            <svg
              v-else-if="item.icon === 'scan'"
              class="h-4 w-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>

            <!-- Camera Icon -->
            <svg
              v-else-if="item.icon === 'camera'"
              class="h-4 w-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>

            <!-- Audit Log Icon -->
            <svg
              v-else-if="item.icon === 'audit'"
              class="h-4 w-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>

            <!-- Violations Icon -->
            <svg
              v-else-if="item.icon === 'violations'"
              class="h-4 w-4 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>

            <span class="truncate">{{ lang === 'km' ? item.nameKm : item.name }}</span>

            <!-- Badge for Camera -->
            <span
              v-if="item.badge"
              class="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider"
              :class="route.path === item.path ? 'bg-blue-500/20 text-blue-300' : 'bg-zinc-800 text-zinc-400'"
            >
              {{ item.badge }}
            </span>
          </router-link>

        </div>
      </nav>

      <!-- Bottom Profile Bar (Exact match to User Screenshot 1: SA System Administrator) -->
      <div class="p-3 border-t border-zinc-800/80">
        <div class="rounded-xl bg-zinc-900/60 border border-zinc-800/80 p-2.5 flex items-center justify-between gap-2.5 hover:bg-zinc-900 transition">
          
          <div class="flex items-center gap-2.5 min-w-0">
            <!-- Avatar Circle -->
            <div class="h-8 w-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 font-bold text-xs flex-shrink-0">
              {{ userInitials }}
            </div>
            <div class="min-w-0">
              <span class="text-xs font-semibold text-white block truncate leading-tight">{{ currentUser.role || 'System Administrator' }}</span>
              <span class="text-[10px] text-zinc-400 font-mono block truncate">{{ currentUser.email || 'admin@istad.edu.kh' }}</span>
            </div>
          </div>

          <!-- Log Out Action Button -->
          <button
            type="button"
            @click="logout"
            class="p-1.5 rounded-lg hover:bg-rose-500/10 text-zinc-400 hover:text-rose-400 transition"
            title="Log Out"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>

        </div>
      </div>

    </aside>
  </div>
</template>
