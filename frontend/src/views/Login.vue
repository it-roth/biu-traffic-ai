<script setup>
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import biuLogo from '../assets/biu-logo.png'

const router = useRouter()

// Authentication step: 'credentials' | '2fa'
const currentStep = ref('credentials')

// Dynamic 2FA data from backend API
const twoFactorData = ref({
  secret_key: '',
  qr_code_url: '',
  live_code_hint: '',
  email_sent_to: ''
})
const showQrCode = ref(false)

const form = ref({
  username: '',
  password: ''
})

// 6-digit OTP array
const otpDigits = reactive(['', '', '', '', '', ''])
const otpRefs = ref([])

const error = ref('')
const loading = ref(false)
const showPassword = ref(false)

// Google OAuth2 Client ID from environment or production setting
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
    error.value = err.response?.data?.detail || 'Google sign-in failed. Please verify credentials.'
  } finally {
    loading.value = false
  }
}

const loginWithGoogle = () => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCallback,
      auto_select: false,
    })
    window.google.accounts.id.prompt((notification) => {
      if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
        const hiddenBtn = document.getElementById('g_id_signin_hidden')
        if (hiddenBtn) {
          hiddenBtn.querySelector('div[role=button]')?.click()
        }
      }
    })
  } else {
    error.value = 'Connecting to Google Authentication Services... Please click again in a moment.'
  }
}

onMounted(() => {
  if (window.google?.accounts?.id) {
    window.google.accounts.id.initialize({
      client_id: googleClientId,
      callback: handleGoogleCallback,
    })
    const container = document.getElementById('g_id_signin_hidden')
    if (container) {
      window.google.accounts.id.renderButton(container, { theme: 'outline', size: 'large' })
    }
  }
})

const handleCredentialSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    // All users are protected by mandatory Two-Factor Authentication (2FA)
    const response = await api.post('auth/login/', {
      username: form.value.username,
      password: form.value.password,
      validate_only: true
    })
    
    // Store dynamic 2FA response from server
    twoFactorData.value = {
      secret_key: response.data.secret_key || '',
      qr_code_url: response.data.qr_code_url || '',
      live_code_hint: response.data.live_code_hint || '',
      email_sent_to: response.data.email_sent_to || ''
    }

    currentStep.value = '2fa'
    await nextTick()
    if (otpRefs.value[0]) otpRefs.value[0].focus()
  } catch (err) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Invalid username or password. Please check your credentials.'
    }
  } finally {
    loading.value = false
  }
}

// Handle OTP Digit Input & Auto-Advance
const onOtpInput = (index, event) => {
  const value = event.target.value.slice(-1)
  otpDigits[index] = value

  if (value && index < 5) {
    otpRefs.value[index + 1]?.focus()
  }

  // Auto-submit when all 6 digits are filled
  const fullCode = otpDigits.join('')
  if (fullCode.length === 6) {
    verifyTwoFactor()
  }
}

// Handle Backspace navigation across OTP slots
const onOtpKeyDown = (index, event) => {
  if (event.key === 'Backspace' && !otpDigits[index] && index > 0) {
    otpRefs.value[index - 1]?.focus()
  }
}

// Handle Clipboard Paste across 6 slots
const onOtpPaste = (event) => {
  event.preventDefault()
  const pasted = (event.clipboardData || window.clipboardData).getData('text')
  const digits = pasted.replace(/\D/g, '').slice(0, 6).split('')
  digits.forEach((d, i) => {
    otpDigits[i] = d
  })
  if (digits.length === 6) {
    verifyTwoFactor()
  } else if (otpRefs.value[digits.length]) {
    otpRefs.value[digits.length]?.focus()
  }
}

// Step 2: Finalize dynamic 2FA verification via API
const verifyTwoFactor = async () => {
  const code = otpDigits.join('')
  if (code.length !== 6) {
    error.value = 'Please enter all 6 digits of your verification code.'
    return
  }

  error.value = ''
  loading.value = true

  try {
    const response = await api.post('auth/login/', {
      username: form.value.username,
      password: form.value.password,
      code: code
    })

    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    if (response.data.user) {
      localStorage.setItem('biu_user', JSON.stringify(response.data.user))
    }
    router.push('/dashboard')
  } catch (err) {
    if (err.response?.data?.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Verification failed. Please check your authenticator code and try again.'
    }
  } finally {
    loading.value = false
  }
}

const backToCredentials = () => {
  currentStep.value = 'credentials'
  error.value = ''
  otpDigits.forEach((_, i) => (otpDigits[i] = ''))
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

    <!-- RIGHT PANEL: Authentication Form (Responsive across Mobile, Tablet & Desktop) -->
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

      <!-- Main Card Container -->
      <div class="w-full max-w-[440px] rounded-2xl border border-zinc-800/90 bg-zinc-900/80 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-200">
        
        <!-- STEP 1: CREDENTIALS & GOOGLE OAUTH -->
        <template v-if="currentStep === 'credentials'">
          <!-- Card Header -->
          <div class="p-6 pb-4 space-y-1.5 border-b border-border/60">
            <h2 class="text-lg font-semibold tracking-tight text-foreground">Sign in to your account</h2>
            <p class="text-xs text-muted-foreground">
              Continue with Google or enter your institutional credentials
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

            <!-- Official Google OAuth2 Button (Shadcn Outline Style) -->
            <button
              type="button"
              :disabled="loading"
              @click="loginWithGoogle"
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

            <!-- Hidden container for Google GSI native trigger -->
            <div id="g_id_signin_hidden" class="hidden"></div>

            <!-- Shadcn Separator -->
            <div class="relative my-3">
              <div class="absolute inset-0 flex items-center">
                <span class="w-full border-t border-border" />
              </div>
              <div class="relative flex justify-center text-[10px] uppercase">
                <span class="bg-card px-2 text-muted-foreground font-mono">Or username & password</span>
              </div>
            </div>

            <!-- Credentials Form -->
            <form @submit.prevent="handleCredentialSubmit" class="space-y-4">
              
              <!-- Username Input -->
              <div class="space-y-2">
                <label class="text-xs font-medium leading-none text-foreground">
                  Username
                </label>
                <input
                  v-model="form.username"
                  type="text"
                  placeholder="Username"
                  autocomplete="username"
                  required
                  class="flex h-10 w-full rounded-md border border-input bg-background/60 px-3.5 py-2 text-sm text-foreground shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <!-- Password Input -->
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
                  autocomplete="current-password"
                  required
                  class="flex h-10 w-full rounded-md border border-input bg-background/60 px-3.5 py-2 text-sm text-foreground shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:border-ring disabled:cursor-not-allowed disabled:opacity-50"
                />
              </div>

              <!-- Submit Button with Mandatory 2FA -->
              <button
                type="submit"
                :disabled="loading"
                class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 w-full font-semibold gap-2 mt-4"
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
                <span>{{ loading ? 'Signing In...' : 'Sign In' }}</span>
              </button>
            </form>

          </div>

          <!-- Card Footer -->
          <div class="p-6 pt-0 border-t border-border/60 text-center">
            <p class="text-xs text-muted-foreground mt-4">
              Don't have an account?
              <router-link to="/register" class="text-primary hover:text-primary/80 font-semibold underline-offset-4 hover:underline ml-1">
                Sign up
              </router-link>
            </p>
          </div>
        </template>

        <!-- STEP 2: DYNAMIC TWO-FACTOR AUTHENTICATION (EMAIL & TOTP) -->
        <template v-else>
          <!-- Card Header -->
          <div class="p-6 pb-4 text-center space-y-2 border-b border-border/60">
            <div class="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary">
              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h2 class="text-lg font-semibold tracking-tight text-foreground">Two-Factor Authentication</h2>
            <p class="text-xs text-muted-foreground max-w-xs mx-auto">
              Enter the 6-digit code sent to your email or generated by your authenticator app
            </p>
            <div v-if="twoFactorData.email_sent_to" class="inline-flex items-center gap-1.5 rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-[11px] font-mono text-primary">
              <span>✉️ Sent to {{ twoFactorData.email_sent_to }}</span>
            </div>
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

            <!-- Optional QR Code Setup Toggle -->
            <div class="text-center">
              <button
                type="button"
                @click="showQrCode = !showQrCode"
                class="text-xs text-primary hover:text-primary/80 font-medium inline-flex items-center gap-1 transition-colors"
              >
                <span>{{ showQrCode ? 'Hide QR Code' : 'Scan with Google Authenticator (QR Code)' }}</span>
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dynamic QR Code Card -->
              <div v-if="showQrCode && twoFactorData.qr_code_url" class="mt-3 p-3 rounded-lg border border-border bg-background/80 space-y-2">
                <div class="bg-white p-2 rounded-md inline-block shadow">
                  <img :src="twoFactorData.qr_code_url" alt="Authenticator QR Code" class="h-36 w-36 object-contain" />
                </div>
                <div class="text-[10px] text-muted-foreground font-mono">
                  Secret Key: <span class="text-foreground select-all">{{ twoFactorData.secret_key }}</span>
                </div>
              </div>
            </div>

            <!-- Shadcn InputOTP 6-Box Grid -->
            <div class="flex items-center justify-center gap-2 pt-1" @paste="onOtpPaste">
              <template v-for="(digit, idx) in otpDigits" :key="idx">
                <input
                  :ref="el => (otpRefs[idx] = el)"
                  v-model="otpDigits[idx]"
                  type="text"
                  inputmode="numeric"
                  maxlength="1"
                  class="flex h-12 w-11 rounded-md border border-input bg-background/60 text-center font-mono text-lg font-semibold text-foreground shadow-sm transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:border-primary disabled:cursor-not-allowed disabled:opacity-50"
                  @input="onOtpInput(idx, $event)"
                  @keydown="onOtpKeyDown(idx, $event)"
                />
                <span v-if="idx === 2" class="text-muted-foreground text-sm font-bold px-0.5">•</span>
              </template>
            </div>

            <!-- Verify Button -->
            <button
              type="button"
              :disabled="loading"
              @click="verifyTwoFactor"
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
              <span>{{ loading ? 'Verifying Code...' : 'Verify Code & Sign In' }}</span>
            </button>

            <!-- Back to Credentials Button -->
            <button
              type="button"
              @click="backToCredentials"
              class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium text-muted-foreground hover:text-foreground transition-colors h-9 px-4 w-full"
            >
              ← Back to credentials
            </button>

          </div>
        </template>

      </div>

      <!-- Footer Info -->
      <p class="text-center text-[11px] text-zinc-400 font-mono mt-6">
        © 2026 BELTEI International University
      </p>

    </div>
  </div>
</template>
