<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import biuLogo from '../assets/biu-logo.png'

const router = useRouter()

const form = ref({
  username: '',
  password: ''
})

const error = ref('')
const loading = ref(false)

const login = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await api.post('auth/login/', form.value)

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    router.push('/dashboard')
  } catch (err) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Invalid username or password. Please verify admin credentials.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#07090e] flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Ambient Background Glows -->
    <div class="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-[#006CB8]/15 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[20%] w-[500px] h-[500px] bg-purple-900/10 rounded-full blur-[120px] pointer-events-none"></div>

    <div class="w-full max-w-md relative z-10 space-y-6">
      
      <!-- Logo & System Branding -->
      <div class="text-center space-y-3">
        <div class="inline-flex p-3 rounded-2xl bg-zinc-900/80 border border-zinc-800 shadow-xl backdrop-blur-md">
          <img :src="biuLogo" alt="BELTEI International University" class="h-16 w-auto object-contain" />
        </div>
        <div>
          <h1 class="text-xl sm:text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-2">
            <span class="text-[#006CB8]">BIU</span> Traffic Enforcement
          </h1>
          <p class="text-xs text-zinc-400 mt-1">
            BELTEI International University • Official AI Police Portal
          </p>
        </div>
      </div>

      <!-- Main Login Card -->
      <div class="rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-6 sm:p-8 backdrop-blur-xl shadow-2xl space-y-6">
        <div>
          <h2 class="text-base font-semibold text-white tracking-tight">Admin & Officer Login</h2>
          <p class="text-xs text-zinc-400 mt-0.5">Enter authorized law enforcement credentials</p>
        </div>

        <!-- Error Alert -->
        <div
          v-if="error"
          class="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300 flex items-center gap-2.5"
        >
          <svg class="h-4 w-4 flex-shrink-0 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{{ error }}</span>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="login" class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">Username / Admin ID</label>
            <div class="relative">
              <input
                v-model="form.username"
                type="text"
                placeholder="admin"
                required
                class="w-full rounded-xl border border-zinc-800 bg-zinc-950/70 px-3.5 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-[#006CB8] focus:outline-none focus:ring-1 focus:ring-[#006CB8] transition"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-medium text-zinc-300 mb-1.5">Password</label>
            <div class="relative">
              <input
                v-model="form.password"
                type="password"
                placeholder="••••••••"
                required
                class="w-full rounded-xl border border-zinc-800 bg-zinc-950/70 px-3.5 py-2.5 text-sm text-white placeholder-zinc-500 focus:border-[#006CB8] focus:outline-none focus:ring-1 focus:ring-[#006CB8] transition"
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 h-11 inline-flex items-center justify-center rounded-xl bg-[#006CB8] hover:bg-[#005a9c] disabled:opacity-50 text-sm font-semibold text-white shadow-lg shadow-blue-900/25 transition gap-2"
          >
            <svg
              v-if="loading"
              class="h-4 w-4 animate-spin text-white"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>{{ loading ? 'Authenticating...' : 'Sign In to Dashboard' }}</span>
          </button>
        </form>

        <div class="pt-2 border-t border-zinc-800 text-center">
          <p class="text-xs text-zinc-400">
            Need a new enforcement profile?
            <router-link to="/register" class="text-[#006CB8] hover:text-blue-400 font-semibold ml-1">Register</router-link>
          </p>
        </div>
      </div>

      <!-- Footer Info -->
      <p class="text-center text-[11px] text-zinc-500">
        © 2026 BELTEI International University • Cambodia Traffic Law Enforcement
      </p>

    </div>
  </div>
</template>
