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
  <div class="min-h-screen bg-background flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-grid-pattern selection:bg-primary selection:text-primary-foreground">
    
    <!-- Ambient Atmospheric Glows -->
    <div class="absolute top-[-15%] right-[25%] w-[600px] h-[600px] bg-primary/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[-15%] left-[25%] w-[500px] h-[500px] bg-sky-900/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="w-full max-w-[400px] relative z-10 space-y-6">
      
      <!-- System Branding Header -->
      <div class="text-center space-y-3">
        <div class="inline-flex p-2.5 rounded-2xl border border-border bg-card/80 shadow-2xl backdrop-blur-xl">
          <img :src="biuLogo" alt="BELTEI International University" class="h-14 w-auto object-contain" />
        </div>
        <div>
          <h1 class="text-2xl font-bold tracking-tight text-foreground flex items-center justify-center gap-2">
            <span class="text-primary">BIU</span> Traffic AI
          </h1>
          <p class="text-xs text-muted-foreground mt-1">
            BELTEI International University
          </p>
        </div>
      </div>

      <!-- Shadcn Card Container -->
      <div class="rounded-xl border border-border bg-card/80 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-200">
        
        <!-- Card Header -->
        <div class="p-6 pb-4 space-y-1.5 border-b border-border/60">
          <h2 class="text-lg font-semibold tracking-tight text-foreground">Create an account</h2>
          <p class="text-xs text-muted-foreground">
            Enter your information below to create your account
          </p>
        </div>

        <!-- Card Content -->
        <div class="p-6 space-y-4">
          
          <!-- Destructive Alert -->
          <div
            v-if="error"
            class="relative w-full rounded-lg border border-destructive/50 bg-destructive/10 p-3.5 text-xs text-rose-300 flex items-start gap-3 transition-all animate-in fade-in"
          >
            <svg class="h-4 w-4 flex-shrink-0 text-rose-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div class="flex-1 leading-relaxed">{{ error }}</div>
          </div>

          <!-- Official Google OAuth2 Button -->
          <button
            type="button"
            :disabled="loading"
            @click="registerWithGoogle"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors border border-input bg-background/60 hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-full shadow-sm gap-2.5"
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
              <span class="w-full border-t border-border" />
            </div>
            <div class="relative flex justify-center text-[10px] uppercase">
              <span class="bg-card px-2 text-muted-foreground font-mono">Or register with email</span>
            </div>
          </div>

          <!-- Registration Form -->
          <form @submit.prevent="register" class="space-y-4">
            
            <!-- Username -->
            <div class="space-y-2">
              <label class="text-xs font-medium leading-none text-foreground">
                Username
              </label>
              <input
                v-model="form.username"
                type="text"
                placeholder="johndoe"
                autocomplete="username"
                required
                class="flex h-10 w-full rounded-md border border-input bg-background/60 px-3.5 py-2 text-sm text-foreground shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <!-- Email -->
            <div class="space-y-2">
              <label class="text-xs font-medium leading-none text-foreground">
                Email
              </label>
              <input
                v-model="form.email"
                type="email"
                placeholder="name@beltei.edu.kh"
                autocomplete="email"
                required
                class="flex h-10 w-full rounded-md border border-input bg-background/60 px-3.5 py-2 text-sm text-foreground shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
            </div>

            <!-- Password -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="text-xs font-medium leading-none text-foreground">
                  Password
                </label>
                <button
                  type="button"
                  tabindex="-1"
                  @click="showPassword = !showPassword"
                  class="text-[11px] text-muted-foreground hover:text-foreground transition-colors font-medium"
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
                class="flex h-10 w-full rounded-md border border-input bg-background/60 px-3.5 py-2 text-sm text-foreground shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50"
              />
              <p class="text-[11px] text-muted-foreground">
                Must be at least 8 characters.
              </p>
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              :disabled="loading"
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 w-full font-semibold gap-2 mt-2"
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
        <div class="p-6 pt-0 border-t border-border/60 text-center">
          <p class="text-xs text-muted-foreground mt-4">
            Already have an account?
            <router-link to="/login" class="text-primary hover:text-primary/80 font-semibold underline-offset-4 hover:underline ml-1">
              Sign in
            </router-link>
          </p>
        </div>

      </div>

      <!-- Footer Info -->
      <p class="text-center text-[11px] text-muted-foreground font-mono">
        © 2026 BELTEI International University
      </p>

    </div>
  </div>
</template>
