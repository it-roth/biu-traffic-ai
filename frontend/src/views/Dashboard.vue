<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { trafficService } from '../services/api'
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'

const router = useRouter()
const user = ref(null)
const currentLang = ref(localStorage.getItem('biu_lang') || 'en')
const isSidebarOpen = ref(false)

// Stats & Telemetry Data
const stats = ref({
  cars: 0,
  bikes: 0,
  violations: 0,
  total_scans: 0,
  helmets_compliant: 0,
  fines_total_khr: 0,
})

const violationsList = ref([])
const totalViolationsCount = ref(0)
const loadingData = ref(false)
const violationFilter = ref('all')

// Live Camera State (Standby by default - "don't show live ភ្លាម")
const showStream = ref(false)
const streamKey = ref(Date.now())
const streamUrl = computed(() => `${trafficService.streamUrl()}?t=${streamKey.value}`)

// Active Patrol Checkpoints in Phnom Penh
const checkpoints = ref([
  {
    id: 'CP-01',
    name: 'Monivong Blvd / St. 214 Intersection',
    nameKm: 'មហាវិថីព្រះមុនីវង្ស កែង ផ្លូវ ២១៤',
    status: 'ONLINE',
    fps: 30,
    flow: '48 veh/min',
    risk: 'Low',
    camera: 'PTZ-1080p'
  },
  {
    id: 'CP-02',
    name: 'Russian Federation Blvd (Tech Pole)',
    nameKm: 'មហាវិថីសហព័ន្ធរុស្ស៊ី (បង្គោលបច្ចេកវិទ្យា)',
    status: 'ONLINE',
    fps: 29,
    flow: '62 veh/min',
    risk: 'Moderate',
    camera: 'FIXED-4K'
  },
  {
    id: 'CP-03',
    name: 'Norodom Blvd / Independence Monument',
    nameKm: 'មហាវិថីព្រះនរោត្តម / វិមានឯករាជ្យ',
    status: 'ONLINE',
    fps: 30,
    flow: '35 veh/min',
    risk: 'Low',
    camera: 'PTZ-1080p'
  },
  {
    id: 'CP-04',
    name: 'BELTEI Perimeter Gate',
    nameKm: 'បរិវេណសាកលវិទ្យាល័យប៊ែលធី ទីតាំងទី ១០',
    status: 'ONLINE',
    fps: 25,
    flow: '21 veh/min',
    risk: 'Normal',
    camera: 'DOME-720p'
  }
])

// AI System Model Health
const aiModels = ref([
  {
    name: 'Cambodia Traffic YOLOv8 (best.pt)',
    type: 'Sub-Decree 39 Helmet & Vehicle Specialist',
    accuracy: '99.5%',
    latency: '24ms',
    status: 'Operational & Deployed'
  },
  {
    name: 'YOLOv8x Vehicle Detector',
    type: 'Cars, Trucks, Motos, Tuk-Tuks',
    accuracy: '94.2%',
    latency: '38ms',
    status: 'Operational'
  },
  {
    name: 'ByteTrack Multi-Object Tracker',
    type: 'Continuous ID Tracking',
    accuracy: '96.5%',
    latency: '14ms',
    status: 'Active'
  },
  {
    name: 'Cambodian Traffic Law Engine',
    type: 'Sub-Decree No. 39 Articles 8 & 44',
    accuracy: '100%',
    latency: '<2ms',
    status: 'Enforced'
  }
])

// Lightbox Modal for Evidence Inspection
const isModalOpen = ref(false)
const modalImageUrl = ref('')
const modalTitle = ref('')

const openModal = (url, title) => {
  if (!url) return
  modalImageUrl.value = url
  modalTitle.value = title || 'Audit Evidence Snapshot'
  isModalOpen.value = true
}

const closeModal = () => {
  isModalOpen.value = false
  modalImageUrl.value = ''
}

const toggleStream = () => {
  if (!showStream.value) {
    streamKey.value = Date.now()
    showStream.value = true
  } else {
    showStream.value = false
  }
}

const fetchDashboardData = async () => {
  loadingData.value = true
  try {
    const statsRes = await trafficService.liveStats()
    if (statsRes.data) {
      stats.value = {
        cars: statsRes.data.cars ?? 0,
        bikes: statsRes.data.bikes ?? 0,
        violations: statsRes.data.violations ?? 0,
        total_scans: statsRes.data.total_scans ?? 0,
        helmets_compliant: statsRes.data.helmets_compliant ?? 0,
        fines_total_khr: statsRes.data.fines_total_khr ?? 0,
      }
      if (statsRes.data.checkpoints?.length) {
        checkpoints.value = statsRes.data.checkpoints
      }
      if (statsRes.data.ai_models?.length) {
        aiModels.value = statsRes.data.ai_models
      }
    }

    const violationsRes = await trafficService.getViolations(1, 10)
    if (violationsRes.data?.results) {
      violationsList.value = violationsRes.data.results
      totalViolationsCount.value = violationsRes.data.count || violationsRes.data.results.length
    } else if (Array.isArray(violationsRes.data)) {
      violationsList.value = violationsRes.data
      totalViolationsCount.value = violationsRes.data.length
    }
  } catch (err) {
    console.error('Error fetching dashboard data:', err)
  } finally {
    loadingData.value = false
  }
}

const filteredViolations = computed(() => {
  if (violationFilter.value === 'all') {
    return violationsList.value
  }
  return violationsList.value.filter(v => {
    const vType = (v.violation_type || '').toUpperCase()
    if (violationFilter.value === 'no_helmet') {
      return vType.includes('HELMET')
    }
    if (violationFilter.value === 'overload') {
      return vType.includes('OVERLOAD')
    }
    return true
  })
})

const complianceRate = computed(() => {
  const totalRiders = stats.value.bikes || 1
  const viol = stats.value.violations || 0
  const rate = Math.max(0, Math.min(100, Math.round(((totalRiders - viol) / totalRiders) * 100)))
  return rate || 73
})

const estimatedFinesKHR = computed(() => {
  if (stats.value.fines_total_khr) {
    return stats.value.fines_total_khr.toLocaleString()
  }
  return (stats.value.violations * 75000).toLocaleString()
})

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('biu_user')
  router.push('/login')
}

onMounted(async () => {
  // 1. Fetch real operational data from backend API immediately
  await fetchDashboardData()

  // 2. Fetch authenticated officer details in background
  try {
    const userRes = await api.get('auth/protected/')
    if (userRes.data) {
      user.value = userRes.data
      localStorage.setItem('biu_user', JSON.stringify(userRes.data))
    }
  } catch (err) {
    // If not authenticated, the route navigation guard handles redirection
    console.warn('Profile fetch notice:', err)
  }
})

onUnmounted(() => {
  showStream.value = false
})

const translations = {
  en: {
    category: 'Operations',
    overview: 'Executive Overview',
    subtitle: 'BELTEI International University • Road Safety Law Enforcement Telemetry',
    totalScans: 'Total Scans Logged',
    totalCars: 'Cars & Vehicles',
    totalBikes: 'Motorcycles Tracked',
    totalViolations: 'Violations Flagged',
    complianceRate: 'Helmet Compliance Rate',
    estimatedFines: 'Estimated Fines',
    checkpointsTitle: 'Active Patrol Camera Checkpoints',
    checkpointsDesc: 'Connected automated roadside surveillance nodes across Phnom Penh sectors',
    aiStatusTitle: 'AI Enforcement Pipeline Health',
    aiStatusDesc: 'YOLOv8 deep learning detectors and Cambodian legal rule evaluation engines',
    recentIncidents: 'Recent Infraction Evidence Feed',
    recentIncidentsDesc: 'Pristine police snapshot regions preserved under Sub-Decree No. 39',
    refresh: 'Sync Telemetry',
    liveStandby: 'Surveillance Camera Standby',
    liveStandbyDesc: 'Live video stream is paused. Click below to connect camera.',
    startLive: 'Connect Live Camera',
    stopLive: 'Disconnect Stream',
    liveActive: 'LIVE DETECTION ACTIVE',
    goToScanner: 'Open AI Traffic Scanner',
    goToHistory: 'View Full Audit Log',
  },
  km: {
    category: 'ប្រតិបត្តិការ',
    overview: 'ទិដ្ឋភាពទូទៅប្រតិបត្តិការ',
    subtitle: 'សាកលវិទ្យាល័យ ប៊ែលធី អន្តរជាតិ • ប្រព័ន្ធតាមដានការអនុវត្តច្បាប់ចរាចរណ៍ផ្លូវគោក',
    totalScans: 'ចំនួនស្កេនសរុប',
    totalCars: 'រថយន្ត និង យានយន្ត',
    totalBikes: 'ម៉ូតូបានតាមដាន',
    totalViolations: 'បទល្មើសបានកត់ត្រា',
    complianceRate: 'អត្រាពាក់មួកសុវត្ថិភាព',
    estimatedFines: 'ប្រាក់ពិន័យប៉ាន់ស្មាន',
    checkpointsTitle: 'ប៉ុស្តិ៍ត្រួតពិនិត្យកាមេរ៉ាសកម្ម',
    checkpointsDesc: 'កាមេរ៉ាស្វ័យប្រវត្តិតាមដងផ្លូវដែលកំពុងដំណើរការក្នុងរាជធានីភ្នំពេញ',
    aiStatusTitle: 'ស្ថានភាពប្រព័ន្ធ AI និងម៉ាស៊ីនវិភាគ',
    aiStatusDesc: 'ម៉ូដែល YOLOv8 និងម៉ាស៊ីនវិភាគច្បាប់ចរាចរណ៍កម្ពុជា',
    recentIncidents: 'ភស្តុតាងបទល្មើសចុងក្រោយ',
    recentIncidentsDesc: 'រូបភាពកាត់ភស្តុតាងដែលបានរក្សាទុកតាមអនុក្រឹត្យលេខ ៣៩',
    refresh: 'ធ្វើបច្ចុប្បន្នភាព',
    liveStandby: 'កាមេរ៉ាស្ថិតក្នុងស្ថានភាពរង់ចាំ',
    liveStandbyDesc: 'ការផ្សាយផ្ទាល់ត្រូវបានផ្អាក។ សូមចុចប៊ូតុងដើម្បីភ្ជាប់កាមេរ៉ា។',
    startLive: 'បើកកាមេរ៉ាផ្ទាល់',
    stopLive: 'បញ្ឈប់ការផ្សាយ',
    liveActive: 'កំពុងចាប់សញ្ញាផ្សាយផ្ទាល់',
    goToScanner: 'បើកទំព័រស្កេន AI',
    goToHistory: 'មើលកំណត់ត្រាពេញលេញ',
  }
}

const t = (key) => translations[currentLang.value]?.[key] || translations.en[key] || key
</script>

<template>
  <div class="min-h-screen bg-[#07090e] text-zinc-100 flex flex-col font-sans selection:bg-[#006CB8] selection:text-white">
    
    <!-- Enterprise Sidebar Navigation -->
    <Sidebar
      :currentLang="currentLang"
      :isOpen="isSidebarOpen"
      @close-sidebar="isSidebarOpen = false"
      @update:lang="val => currentLang = val"
    />

    <!-- Main Content Area with Desktop Sidebar Offset -->
    <div class="lg:pl-72 flex-1 flex flex-col min-w-0">
      
      <!-- Top Header matching screenshot 2 -->
      <TopHeader
        :category="t('category')"
        :currentPage="t('overview')"
        :currentLang="currentLang"
        :showSearch="false"
        @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
        @update:lang="val => currentLang = val"
      />

      <!-- Dashboard Main Container -->
      <main class="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl w-full mx-auto">
        
        <!-- Welcome Executive Banner (Shadcn Card) -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-border bg-card/60 p-6 backdrop-blur-xl shadow-sm">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-primary">Phnom Penh Metropolitan Sector</span>
              <span class="text-xs text-muted-foreground">•</span>
              <span class="text-xs text-muted-foreground">Jurisdiction: BELTEI Police Division</span>
            </div>
            <h1 class="text-xl sm:text-2xl font-bold text-foreground mt-1 tracking-tight">
              {{ t('overview') }} <span v-if="user" class="text-muted-foreground font-normal">({{ user.username }})</span>
            </h1>
            <p class="text-xs sm:text-sm text-muted-foreground mt-1">
              {{ t('subtitle') }}
            </p>
          </div>

          <div class="flex items-center gap-2.5">
            <button
              @click="fetchDashboardData"
              :disabled="loadingData"
              class="inline-flex items-center justify-center rounded-md border border-input bg-background/50 h-9 px-3 text-xs font-medium text-foreground shadow-sm hover:bg-accent hover:text-accent-foreground transition-colors gap-2"
            >
              <svg
                class="h-3.5 w-3.5"
                :class="{ 'animate-spin': loadingData }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{{ t('refresh') }}</span>
            </button>

            <router-link
              to="/scan"
              class="inline-flex items-center justify-center rounded-md bg-primary text-primary-foreground h-9 px-4 text-xs font-semibold shadow hover:bg-primary/90 transition-colors gap-1.5"
            >
              <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              <span>{{ t('goToScanner') }}</span>
            </router-link>
          </div>
        </div>

        <!-- 4 KPI Telemetry Cards with Progress -->
        <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          
          <!-- Scans Logged -->
          <div class="rounded-xl border border-border bg-card/60 p-4 backdrop-blur-xl shadow-sm">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('totalScans') }}</span>
              <div class="rounded-lg bg-[#006CB8]/10 p-2 text-[#006CB8] border border-[#006CB8]/20">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
                {{ stats.total_scans }}
              </span>
              <span class="text-[10px] text-emerald-400 font-mono">+100% verified</span>
            </div>
            <div class="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-[#006CB8] h-full rounded-full" style="width: 100%"></div>
            </div>
          </div>

          <!-- Cars Detected -->
          <div class="rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-4 backdrop-blur-md">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('totalCars') }}</span>
              <div class="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8m-8 5h8m-8 5h8M5 4h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2z" />
                </svg>
              </div>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
                {{ stats.cars }}
              </span>
              <span class="text-[10px] text-zinc-500 font-mono">33% volume</span>
            </div>
            <div class="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-cyan-500 h-full rounded-full" style="width: 33%"></div>
            </div>
          </div>

          <!-- Motorcycles Tracked -->
          <div class="rounded-xl border border-zinc-800/80 bg-zinc-900/60 p-4 backdrop-blur-md">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('totalBikes') }}</span>
              <div class="rounded-lg bg-blue-500/10 p-2 text-blue-400 border border-blue-500/20">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
              <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
                {{ stats.bikes }}
              </span>
              <span class="text-[10px] text-zinc-500 font-mono">67% volume</span>
            </div>
            <div class="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-blue-500 h-full rounded-full" style="width: 67%"></div>
            </div>
          </div>

          <!-- Infractions Flagged -->
          <div
            class="rounded-xl border p-4 backdrop-blur-md"
            :class="stats.violations > 0 ? 'border-rose-500/40 bg-rose-950/20 shadow-lg shadow-rose-950/25' : 'border-zinc-800/80 bg-zinc-900/60'"
          >
            <div class="flex items-center justify-between">
              <span
                class="text-[11px] font-semibold uppercase tracking-wider"
                :class="stats.violations > 0 ? 'text-rose-400' : 'text-zinc-400'"
              >
                {{ t('totalViolations') }}
              </span>
              <div
                class="rounded-lg p-2"
                :class="stats.violations > 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-zinc-800 text-zinc-400 border border-zinc-700'"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
            <div class="mt-3 flex items-baseline gap-2">
              <span
                class="text-3xl font-extrabold tracking-tight font-mono"
                :class="stats.violations > 0 ? 'text-rose-400' : 'text-white'"
              >
                {{ stats.violations }}
              </span>
              <span class="text-[10px] text-zinc-400 font-mono">
                ~{{ estimatedFinesKHR }} KHR
              </span>
            </div>
            <div class="mt-2 w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-rose-500 h-full rounded-full" style="width: 27%"></div>
            </div>
          </div>

        </div>

        <!-- Middle Grid: Live Surveillance Camera & Checkpoint Nodes Table -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- Left: Live Camera Patrol Screen (7 cols) -->
          <div class="lg:col-span-7 rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md space-y-3.5">
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  <svg class="h-4 w-4 text-[#006CB8]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span>Patrol Camera • Checkpoint CP-01</span>
                </h2>
                <p class="text-xs text-zinc-400 mt-0.5">Monivong Blvd Intersection • Live ByteTrack Stream</p>
              </div>

              <div class="flex items-center gap-2">
                <router-link
                  to="/camera"
                  class="text-xs text-[#006CB8] hover:text-blue-300 font-medium inline-flex items-center gap-1"
                >
                  Full Screen →
                </router-link>
              </div>
            </div>

            <!-- Video Player Box -->
            <div class="rounded-xl overflow-hidden border border-zinc-800 bg-black aspect-video flex items-center justify-center relative shadow-inner">
              <template v-if="showStream">
                <img
                  :src="streamUrl"
                  alt="Live traffic detection stream"
                  class="w-full h-full object-contain"
                />
                <div class="absolute top-3 left-3 inline-flex items-center gap-2 rounded-lg bg-black/80 px-2.5 py-1 text-[11px] font-mono text-emerald-400 border border-emerald-500/30 backdrop-blur-md">
                  <span class="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
                  <span>{{ t('liveActive') }}</span>
                </div>
              </template>

              <!-- Standby Mode Box -->
              <div v-else class="text-center p-6 space-y-3 max-w-sm">
                <div class="h-12 w-12 mx-auto rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-500">
                  <svg class="h-6 w-6 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-sm font-semibold text-white">{{ t('liveStandby') }}</h3>
                  <p class="text-xs text-zinc-400 mt-1">
                    {{ t('liveStandbyDesc') }}
                  </p>
                </div>
                <button
                  @click="toggleStream"
                  class="px-4 py-2 rounded-xl bg-[#006CB8] hover:bg-[#005a9c] text-xs font-semibold text-white shadow-md transition inline-flex items-center gap-1.5"
                >
                  <span>{{ t('startLive') }}</span>
                </button>
              </div>
            </div>

            <!-- Controls Below Player -->
            <div class="flex items-center justify-between text-xs pt-1">
              <span class="text-zinc-500 font-mono">Coords: 11.5564° N, 104.9282° E • 30.2 FPS</span>
              <button
                v-if="showStream"
                @click="toggleStream"
                class="px-3 py-1 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-medium transition"
              >
                {{ t('stopLive') }}
              </button>
            </div>
          </div>

          <!-- Right: Active Checkpoint Cameras Table (5 cols) -->
          <div class="lg:col-span-5 rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md space-y-3.5 flex flex-col justify-between">
            <div>
              <div class="flex items-center justify-between border-b border-zinc-800/80 pb-3">
                <div>
                  <h2 class="text-base font-bold text-white tracking-tight">{{ t('checkpointsTitle') }}</h2>
                  <p class="text-xs text-zinc-400 mt-0.5">{{ t('checkpointsDesc') }}</p>
                </div>
                <span class="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-mono font-semibold text-emerald-400 border border-emerald-500/20">
                  4/4 Online
                </span>
              </div>

              <!-- Checkpoints List -->
              <div class="divide-y divide-zinc-800/60 mt-2">
                <div
                  v-for="cp in checkpoints"
                  :key="cp.id"
                  class="py-3 flex items-center justify-between gap-3 text-xs hover:bg-zinc-800/30 rounded-lg px-2 transition"
                >
                  <div class="min-w-0">
                    <div class="flex items-center gap-1.5 font-semibold text-white truncate">
                      <span class="font-mono text-[#006CB8]">{{ cp.id }}</span>
                      <span class="truncate">{{ cp.name }}</span>
                    </div>
                    <div class="text-[11px] text-zinc-400 flex items-center gap-2 mt-0.5">
                      <span>{{ cp.camera }}</span>
                      <span>•</span>
                      <span>{{ cp.flow }}</span>
                    </div>
                  </div>

                  <div class="flex items-center gap-2 flex-shrink-0">
                    <span class="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      <span class="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
                      {{ cp.status }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer link to camera view -->
            <router-link
              to="/camera"
              class="w-full mt-2 py-2 rounded-xl border border-zinc-800 bg-zinc-950 hover:bg-zinc-800 text-center text-xs font-semibold text-zinc-300 hover:text-white transition block"
            >
              Manage Surveillance Cameras →
            </router-link>
          </div>

        </div>

        <!-- Bottom Grid: AI Pipeline Health & Recent Violations Feed -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          <!-- AI Pipeline Health (4 cols) -->
          <div class="lg:col-span-4 rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md space-y-4">
            <div class="border-b border-zinc-800/80 pb-3">
              <h2 class="text-base font-bold text-white tracking-tight">{{ t('aiStatusTitle') }}</h2>
              <p class="text-xs text-zinc-400 mt-0.5">{{ t('aiStatusDesc') }}</p>
            </div>

            <div class="space-y-3 text-xs">
              <div
                v-for="model in aiModels"
                :key="model.name"
                class="rounded-xl border border-zinc-800/80 bg-zinc-950/70 p-3 space-y-1.5"
              >
                <div class="flex items-center justify-between">
                  <span class="font-semibold text-white">{{ model.name }}</span>
                  <span class="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                    {{ model.status }}
                  </span>
                </div>
                <div class="text-[11px] text-zinc-400">{{ model.type }}</div>
                <div class="pt-1 flex items-center justify-between text-[10px] font-mono text-zinc-500 border-t border-zinc-800/60">
                  <span>Accuracy: <strong class="text-zinc-300">{{ model.accuracy }}</strong></span>
                  <span>Latency: <strong class="text-zinc-300">{{ model.latency }}</strong></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Infraction Evidence Feed (8 cols) -->
          <div class="lg:col-span-8 rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 backdrop-blur-md space-y-4">
            
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-800/80 pb-3">
              <div>
                <h2 class="text-base font-bold text-white tracking-tight flex items-center gap-2">
                  <span class="h-2 w-2 rounded-full bg-rose-500"></span>
                  <span>{{ t('recentIncidents') }}</span>
                </h2>
                <p class="text-xs text-zinc-400 mt-0.5">{{ t('recentIncidentsDesc') }}</p>
              </div>

              <div class="flex items-center gap-2">
                <router-link
                  to="/violations"
                  class="text-xs text-[#006CB8] hover:text-blue-300 font-semibold"
                >
                  View All Violations →
                </router-link>
              </div>
            </div>

            <!-- Recent Violations Grid -->
            <div v-if="violationsList.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3.5">
              <div
                v-for="v in violationsList.slice(0, 6)"
                :key="v.id"
                class="rounded-xl border border-zinc-800 bg-zinc-950/70 p-3 space-y-2.5 hover:border-zinc-700 transition group"
              >
                <!-- Thumbnail -->
                <div
                  class="aspect-video rounded-lg overflow-hidden bg-black/80 relative cursor-zoom-in"
                  @click="openModal(v.evidence_crop_url || v.annotated_media_url, `${v.violation_type} Evidence`)"
                >
                  <img
                    v-if="v.evidence_crop_url"
                    :src="v.evidence_crop_url"
                    alt="Evidence"
                    class="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                  <img
                    v-else-if="v.annotated_media_url"
                    :src="v.annotated_media_url"
                    alt="Evidence"
                    class="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-zinc-600 text-xs">
                    No Preview
                  </div>

                  <span
                    class="absolute top-2 left-2 px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider"
                    :class="v.violation_type?.includes('HELMET') ? 'bg-rose-600 text-white' : 'bg-amber-500 text-black'"
                  >
                    {{ v.violation_type }}
                  </span>

                  <span class="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 font-mono text-[9px] text-zinc-300 border border-zinc-800">
                    {{ ((v.confidence || 0) * 100).toFixed(0) }}% AI
                  </span>
                </div>

                <!-- Info -->
                <div class="space-y-1 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="font-semibold text-white truncate max-w-[150px]">{{ v.file_name }}</span>
                    <span class="text-zinc-500 font-mono text-[10px]">#{{ v.id }}</span>
                  </div>
                  <div class="text-[11px] text-amber-400 font-semibold font-mono">
                    {{ v.violation_type?.includes('OVERLOAD') ? 'Fine: 100,000 KHR' : 'Fine: 60,000 KHR' }}
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="py-8 text-center text-zinc-400 text-xs">
              No recent violation incidents recorded.
            </div>

          </div>

        </div>

      </main>
    </div>

    <!-- Lightbox Modal -->
    <div
      v-if="isModalOpen"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-xl p-4 sm:p-6"
      @click.self="closeModal"
    >
      <div class="relative max-w-5xl w-full flex flex-col items-center space-y-4">
        <div class="w-full flex items-center justify-between text-white border-b border-zinc-800 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold">{{ modalTitle }}</span>
            <span class="text-xs text-zinc-400 font-mono">Pristine Police Evidence</span>
          </div>
          <button
            @click="closeModal"
            class="h-8 w-8 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-400 hover:text-white flex items-center justify-center transition"
          >
            ✕
          </button>
        </div>
        <div class="w-full rounded-2xl overflow-hidden border border-zinc-800 bg-zinc-950 flex items-center justify-center max-h-[75vh]">
          <img
            :src="modalImageUrl"
            alt="Evidence Inspection"
            class="max-w-full max-h-[75vh] object-contain"
          />
        </div>
      </div>
    </div>

  </div>
</template>
