<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import api from '../services/api'
import biuLogo from '../assets/biu-logo.png'

const router = useRouter()

// Authentication step: 'credentials' | '2fa'
const currentStep = ref('credentials')
const useTwoFactor = ref(true)

// Dynamic 2FA data from backend API
const twoFactorData = ref({
  secret_key: '',
  qr_code_url: '',
  live_code_hint: ''
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

const handleCredentialSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    if (useTwoFactor.value) {
      // Step 1: Pre-validate credentials dynamically against backend API
      const response = await api.post('auth/login/', {
        username: form.value.username,
        password: form.value.password,
        validate_only: true
      })
      
      // Store dynamic 2FA response from server
      twoFactorData.value = {
        secret_key: response.data.secret_key || '',
        qr_code_url: response.data.qr_code_url || '',
        live_code_hint: response.data.live_code_hint || ''
      }

      currentStep.value = '2fa'
      await nextTick()
      if (otpRefs.value[0]) otpRefs.value[0].focus()
    } else {
      // Direct login without 2FA
      const response = await api.post('auth/login/', form.value)
      localStorage.setItem('access_token', response.data.access)
      localStorage.setItem('refresh_token', response.data.refresh)
      if (response.data.user) {
        localStorage.setItem('biu_user', JSON.stringify(response.data.user))
      }
      router.push('/dashboard')
    }
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
  <div class="min-h-screen bg-background flex flex-col justify-center items-center px-4 sm:px-6 lg:px-8 relative overflow-hidden bg-grid-pattern selection:bg-primary selection:text-primary-foreground">
    
    <!-- Ambient Atmospheric Glows -->
    <div class="absolute top-[-15%] left-[25%] w-[600px] h-[600px] bg-primary/10 rounded-full blur-[140px] pointer-events-none"></div>
    <div class="absolute bottom-[-15%] right-[25%] w-[500px] h-[500px] bg-sky-900/10 rounded-full blur-[140px] pointer-events-none"></div>

    <div class="w-full max-w-[420px] relative z-10 space-y-6">
      
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

      <!-- Main Card Container -->
      <div class="rounded-xl border border-border bg-card/80 backdrop-blur-xl shadow-2xl overflow-hidden transition-all duration-200">
        
        <!-- STEP 1: CREDENTIALS FORM -->
        <template v-if="currentStep === 'credentials'">
          <!-- Card Header -->
          <div class="p-6 pb-4 space-y-1.5 border-b border-border/60">
            <h2 class="text-lg font-semibold tracking-tight text-foreground">Sign in to your account</h2>
            <p class="text-xs text-muted-foreground">
              Enter your credentials below to access the platform
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

              <!-- 2FA Checkbox Option -->
              <div class="flex items-center space-x-2.5 pt-1">
                <input
                  id="two-factor"
                  v-model="useTwoFactor"
                  type="checkbox"
                  class="h-4 w-4 rounded border-input bg-background text-primary focus:ring-1 focus:ring-primary focus:ring-offset-background cursor-pointer"
                />
                <label for="two-factor" class="text-xs font-medium text-foreground cursor-pointer select-none flex items-center gap-1.5">
                  <span>Enable Two-Factor Authentication (2FA)</span>
                  <span class="rounded bg-primary/10 text-primary border border-primary/20 text-[10px] px-1.5 py-0.2 font-mono">TOTP</span>
                </label>
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
                <span>{{ loading ? 'Verifying...' : (useTwoFactor ? 'Continue with 2FA →' : 'Sign in') }}</span>
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

        <!-- STEP 2: DYNAMIC TWO-FACTOR AUTHENTICATION (TOTP) -->
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
              Enter the 6-digit code from Google Authenticator
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

            <!-- Optional QR Code Setup Toggle -->
            <div class="text-center">
              <button
                type="button"
                @click="showQrCode = !showQrCode"
                class="text-xs text-primary hover:text-primary/80 font-medium inline-flex items-center gap-1 transition-colors"
              >
                <span>{{ showQrCode ? 'Hide QR Code' : 'Scan with Authenticator App (QR Code)' }}</span>
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
      <p class="text-center text-[11px] text-muted-foreground font-mono">
        © 2026 BELTEI International University
      </p>

    </div>
  </div>
</template>
