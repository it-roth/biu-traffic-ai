<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import biuLogo from '../assets/biu-logo.png'

const router = useRouter()

const form = ref({
  username: '',
  email: '',
  password: ''
})
const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '1030898514261-k50cgev5g3tk45ai4k0jhkb9cm65a1h6.apps.googleusercontent.com'

const handleGoogleCallback = async (response) => {
  if (!response?.credential) return
  error.value = ''
  loading.value = true

  try {
    const res = await api.post('auth/google/', { token: response.credential })
    localStorage.setItem('access_token', res.data.access)
    localStorage.setItem('refresh_token', res.data.refresh)
    if (res.data.user) {
      localStorage.setItem('biu_user', JSON.stringify(res.data.user))
    }
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Google sign-up failed. Please verify credentials.'
  } finally {
    loading.value = false
  }
}

const registerWithGoogle = () => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCallback,
      auto_select: false,
    })
    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        const hiddenBtn = document.getElementById('g_id_register_hidden')
        if (hiddenBtn) {
          hiddenBtn.querySelector('div[role=button]')?.click()
        }
      }
    })
  } else {
    error.value = 'Connecting to Google Authentication Services... Please try again in a moment.'
  }
}

onMounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCallback,
    })
    const container = document.getElementById('g_id_register_hidden')
    if (container) {
      window.google.accounts.id.renderButton(container, { theme: 'outline', size: 'large' })
    }
  }
})

const register = async () => {
  error.value = ''
  loading.value = true
  try {
    await api.post('auth/register/', form.value)
    router.push('/login')
  } catch (err) {
    const data = err.response?.data
    error.value = data
      ? Object.values(data).flat().join(' ')
      : 'Registration failed. Please check your information and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-[#07090e] text-zinc-100 flex flex-col lg:grid lg:grid-cols-12 overflow-x-hidden selection:bg-blue-600 selection:text-white relative">
    
    <!-- LEFT PANEL: Enterprise Hero Presentation (Visible on lg+ screens, filling the screen) -->
    <div class="lg:col-span-7 xl:col-span-7 hidden lg:flex flex-col justify-between p-10 xl:p-14 border-r border-zinc-800/80 bg-gradient-to-br from-[#0a0e1a] via-[#07090e] to-[#04060a] relative overflow-hidden">
      <!-- Ambient Lighting Glows -->
      <div class="absolute top-[-10%] left-[-10%] w-[550px] h-[550px] bg-blue-600/10 rounded-full blur-[140px] pointer-events-none"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-sky-500/10 rounded-full blur-[140px] pointer-events-none"></div>

      <!-- Top Institutional Branding -->
      <div class="relative z-10 space-y-4">
        <div class="flex items-center gap-3.5">
          <div class="p-2.5 rounded-2xl border border-zinc-800 bg-zinc-900/80 shadow-2xl backdrop-blur-xl">
            <img :src="biuLogo" alt="BELTEI Logo" class="h-12 w-auto object-contain" />
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xl font-bold tracking-tight text-white"><span class="text-blue-500">BIU</span> Traffic AI</span>
              <span class="rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[10px] px-2 py-0.5 font-mono">Sub-Decree 39</span>
            </div>
            <p class="text-xs text-zinc-400 font-medium mt-0.5">
              BELTEI International University • Phnom Penh, Cambodia
            </p>
          </div>
        </div>

        <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/10 text-blue-400 text-xs font-medium">
          <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Official AI Law Enforcement System • Production Node Active</span>
        </div>
      </div>

      <!-- Center Hero Content & Dynamic Capabilities -->
      <div class="relative z-10 my-auto py-8 space-y-6 max-w-xl">
        <div class="space-y-3">
          <h1 class="text-3xl xl:text-4xl font-extrabold tracking-tight text-white leading-tight">
            AI-Driven Traffic Law Enforcement & Telemetry System
          </h1>
          <p class="text-sm xl:text-base text-zinc-400 leading-relaxed">
            Real-time multi-class traffic violation detection, automated license plate inspection, and statutory penalty computation powered by custom YOLOv8 Nano (99.5% mAP50) and ByteTrack.
          </p>
        </div>

        <!-- 4 Dynamic Architecture Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
          <div class="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-sm space-y-1.5 hover:border-zinc-700 transition-colors">
            <div class="flex items-center gap-2 text-xs font-semibold text-blue-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>Sub-Decree No. 39</span>
            </div>
            <p class="text-xs text-zinc-400">
              Automated statutory fine computation pursuant to Royal Government of Cambodia Articles 8, 44 & 56.
            </p>
          </div>

          <div class="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-sm space-y-1.5 hover:border-zinc-700 transition-colors">
            <div class="flex items-center gap-2 text-xs font-semibold text-blue-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
              <span>YOLOv8 & ByteTrack</span>
            </div>
            <p class="text-xs text-zinc-400">
              Custom-trained on 15,000+ Cambodian traffic frames with multi-object tracking and 24ms inference.
            </p>
          </div>

          <div class="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-sm space-y-1.5 hover:border-zinc-700 transition-colors">
            <div class="flex items-center gap-2 text-xs font-semibold text-emerald-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
              <span>Mandatory 2FA Security</span>
            </div>
            <p class="text-xs text-zinc-400">
              Dynamic RFC 6238 TOTP security codes dispatched to real Gmail via asynchronous SMTP background worker.
            </p>
          </div>

          <div class="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/50 backdrop-blur-sm space-y-1.5 hover:border-zinc-700 transition-colors">
            <div class="flex items-center gap-2 text-xs font-semibold text-indigo-400">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
              <span>User-Isolated Data</span>
            </div>
            <p class="text-xs text-zinc-400">
              Strict per-user data scoping — new accounts start with clean audit logs until they execute scans.
            </p>
          </div>
        </div>
      </div>

      <!-- Bottom Academic Roster & Telemetry Footer -->
      <div class="relative z-10 pt-6 border-t border-zinc-800/80 flex items-center justify-between text-xs text-zinc-400">
        <div>
          <span class="text-zinc-300 font-semibold">Faculty of Information Technology & Science</span> • CS & Software Engineering
        </div>
        <div class="flex items-center gap-2 font-mono text-[11px] text-zinc-400">
          <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
          <span>Cloud API: Online</span>
        </div>
      </div>
    </div>

    <!-- RIGHT PANEL: Registration Form (Fully Responsive across Mobile, Tablet & Desktop) -->
    <div class="lg:col-span-5 xl:col-span-5 flex-1 flex flex-col justify-center items-center p-6 sm:p-10 lg:p-12 relative z-10 min-h-screen">
      
      <!-- Mobile Branding Header (visible only on mobile/tablet) -->
      <div class="lg:hidden text-center space-y-2 mb-6">
        <div class="inline-flex p-2.5 rounded-2xl border border-zinc-800 bg-zinc-900/80 shadow-2xl backdrop-blur-xl">
          <img :src="biuLogo" alt="BELTEI Logo" class="h-12 w-auto object-contain" />
        </div>
        <h1 class="text-2xl font-bold tracking-tight text-white flex items-center justify-center gap-1.5">
          <span class="text-blue-500">BIU</span> Traffic AI
        </h1>
        <p class="text-xs text-zinc-400">
          BELTEI International University
        </p>
      </div>

      <!-- Responsive Form Card -->
      <div class="w-full max-w-[440px] rounded-2xl border border-zinc-800/90 bg-zinc-900/80 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-200">
        
        <!-- Card Header -->
        <div class="p-6 pb-4 space-y-1.5 border-b border-zinc-800/80">
          <h2 class="text-xl font-bold tracking-tight text-white">Create an account</h2>
          <p class="text-xs text-zinc-400">
            Enter your details below to register for institutional AI access
          </p>
        </div>

        <!-- Card Content -->
        <div class="p-6 space-y-4">
          
          <!-- Destructive Alert -->
          <div
            v-if="error"
            class="relative w-full rounded-lg border border-red-500/40 bg-red-500/10 p-3.5 text-xs text-red-300 flex items-start gap-3 transition-all animate-in fade-in"
          >
            <svg class="h-4 w-4 flex-shrink-0 text-red-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="flex-1 leading-relaxed">{{ error }}</div>
          </div>

          <!-- Official Google OAuth2 Button -->
          <button
            type="button"
            :disabled="loading"
            @click="registerWithGoogle"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-colors border border-zinc-700/80 bg-zinc-800/60 hover:bg-zinc-700/60 hover:text-white text-zinc-200 h-11 px-4 py-2 w-full shadow-sm gap-2.5"
          >
            <svg class="h-4 w-4" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
            </svg>
            <span>Continue with Google</span>
          </button>

          <div id="g_id_register_hidden" class="hidden"></div>

          <!-- Separator -->
          <div class="relative my-3">
            <div class="absolute inset-0 flex items-center">
              <span class="w-full border-t border-zinc-800" />
            </div>
            <div class="relative flex justify-center text-[10px] uppercase">
              <span class="bg-zinc-900 px-2.5 text-zinc-400 font-mono">Or register with email</span>
            </div>
          </div>

          <!-- Registration Form -->
          <form @submit.prevent="register" class="space-y-4">
            
            <!-- Username -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-zinc-300">
                Username
              </label>
              <input
                v-model="form.username"
                type="text"
                placeholder="saaroth"
                autocomplete="username"
                required
                class="flex h-10 w-full rounded-lg border border-zinc-700/80 bg-zinc-800/50 px-3.5 py-2 text-sm text-white shadow-sm transition-colors placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 focus-visible:border-blue-500"
              />
            </div>

            <!-- Email -->
            <div class="space-y-1.5">
              <label class="text-xs font-semibold text-zinc-300">
                Email
              </label>
              <input
                v-model="form.email"
                type="email"
                placeholder="saaroth@gmail.com"
                autocomplete="email"
                required
                class="flex h-10 w-full rounded-lg border border-zinc-700/80 bg-zinc-800/50 px-3.5 py-2 text-sm text-white shadow-sm transition-colors placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 focus-visible:border-blue-500"
              />
            </div>

            <!-- Password -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between">
                <label class="text-xs font-semibold text-zinc-300">
                  Password
                </label>
                <button
                  type="button"
                  tabindex="-1"
                  @click="showPassword = !showPassword"
                  class="text-[11px] text-zinc-400 hover:text-white transition-colors font-medium"
                >
                  {{ showPassword ? 'Hide' : 'Show' }}
                </button>
              </div>
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="••••••••"
                minlength="8"
                autocomplete="new-password"
                required
                class="flex h-10 w-full rounded-lg border border-zinc-700/80 bg-zinc-800/50 px-3.5 py-2 text-sm text-white shadow-sm transition-colors placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 focus-visible:border-blue-500"
              />
              <p class="text-[11px] text-zinc-400">
                Must be at least 8 characters.
              </p>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-500 disabled:pointer-events-none disabled:opacity-50 bg-blue-600 text-white shadow-lg hover:bg-blue-500 h-10 px-4 py-2 w-full gap-2 mt-2"
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
              <span>{{ loading ? 'Creating account...' : 'Create account' }}</span>
            </button>
          </form>

        </div>

        <!-- Card Footer -->
        <div class="p-6 pt-0 border-t border-zinc-800/80 text-center">
          <p class="text-xs text-zinc-400 mt-4">
            Already have an account?
            <router-link to="/login" class="text-blue-400 hover:text-blue-300 font-semibold underline-offset-4 hover:underline ml-1">
              Sign in
            </router-link>
          </p>
        </div>

      </div>

      <!-- Footer Info -->
      <p class="text-center text-[11px] text-zinc-400 font-mono mt-6">
        © 2026 BELTEI International University
      </p>

    </div>
  </div>
</template>
