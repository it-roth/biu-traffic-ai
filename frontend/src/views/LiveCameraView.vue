<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'
import { trafficService } from '../services/api'

const isSidebarOpen = ref(false)
const currentLang = ref(localStorage.getItem('biu_lang') || 'en')

// Live Camera State - NOT streaming immediately ("don't show live ភ្លាម")
const showStream = ref(false)
const streamKey = ref(Date.now())
const streamUrl = computed(() => `${trafficService.streamUrl()}?t=${streamKey.value}`)

// Real-time telemetry counts
const liveStats = ref({
  cars: 0,
  bikes: 0,
  helmets_compliant: 0,
  violations: 0,
})

let statsInterval = null

const toggleStream = async () => {
  if (!showStream.value) {
    streamKey.value = Date.now()
    showStream.value = true
    startPollingStats()
  } else {
    // 1. Tell backend to stop the generator loop
    try { await trafficService.stopStream() } catch (_) {}
    // 2. Hide the img (removes it from DOM, drops browser HTTP connection)
    showStream.value = false
    stopPollingStats()
  }
}

const fetchLiveStats = async () => {
  try {
    const res = await trafficService.liveStats()
    if (res.data?.live) {
      liveStats.value = res.data.live
    } else if (res.data) {
      liveStats.value = res.data
    }
  } catch (err) {
    // Ignore transient poll failures
  }
}

const startPollingStats = () => {
  stopPollingStats()
  fetchLiveStats()
  statsInterval = setInterval(fetchLiveStats, 2000)
}

const stopPollingStats = () => {
  if (statsInterval) {
    clearInterval(statsInterval)
    statsInterval = null
  }
}

onMounted(() => {
  fetchLiveStats()
})

onUnmounted(() => {
  stopPollingStats()
  showStream.value = false
})

const translations = {
  en: {
    title: 'Live AI Camera Enforcement',
    subtitle: 'Real-time ByteTrack vehicle tracking & Cambodian safety law analysis',
    standbyTitle: 'Live AI Camera Stream (Standby)',
    standbyDesc: 'Camera feed is in standby mode. Click the button below to connect the live video feed.',
    startLive: 'Start Live Camera Feed',
    stopLive: 'Stop Live Stream',
    liveActive: 'LIVE DETECTION ACTIVE',
    carsTracked: 'Live Cars Tracked',
    motosTracked: 'Live Motorcycles Tracked',
    helmetsOk: 'Compliant Helmets',
    violationsFlagged: 'Active Violations',
    lawNotice: 'Enforcement Standards',
    lawDesc: 'Operating under Cambodia Sub-Decree No. 39 • Article 8 (Mandatory Helmets) and Article 44 (Motorcycle Passenger Overload Limit: 2 Persons).',
  },
  km: {
    title: 'ទិដ្ឋភាពកាមេរ៉ាផ្សាយផ្ទាល់ AI',
    subtitle: 'ការតាមដានយានយន្តដោយ ByteTrack និងការវិភាគច្បាប់ចរាចរណ៍កម្ពុជា',
    standbyTitle: 'កាមេរ៉ាស្ថិតក្នុងស្ថានភាពរង់ចាំ',
    standbyDesc: 'កាមេរ៉ាផ្ទាល់មិនទាន់បានបើកដំណើរការនៅឡើយទេ។ សូមចុចប៊ូតុងខាងក្រោមដើម្បីភ្ជាប់កាមេរ៉ា។',
    startLive: 'បើកដំណើរការកាមេរ៉ាផ្ទាល់',
    stopLive: 'បញ្ឈប់ការផ្សាយផ្ទាល់',
    liveActive: 'កំពុងចាប់សញ្ញាផ្សាយផ្ទាល់',
    carsTracked: 'រថយន្តកំពុងតាមដាន',
    motosTracked: 'ម៉ូតូកំពុងតាមដាន',
    helmetsOk: 'ពាក់មួកត្រឹមត្រូវ',
    violationsFlagged: 'ល្មើសច្បាប់សកម្ម',
    lawNotice: 'បទដ្ឋានអនុវត្តច្បាប់',
    lawDesc: 'អនុវត្តតាមអនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨ (ការពាក់មួកសុវត្ថិភាព) និង មាត្រា ៤៤ (កំណត់ចំនួនអ្នកជិះម៉ូតូ: ២ នាក់)។',
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
        category="Operations"
        currentPage="Live Camera Feed"
        :currentLang="currentLang"
        :showSearch="false"
        @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
        @update:lang="val => currentLang = val"
      />

      <!-- Main Body -->
      <main class="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl w-full mx-auto">
        
        <!-- Live Video Player Card -->
        <div class="rounded-2xl border border-zinc-800/80 bg-zinc-900/60 p-5 sm:p-6 backdrop-blur-xl shadow-2xl space-y-4">
          
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-semibold uppercase tracking-wider text-[#006CB8]">Beltei Patrol Point #1</span>
                <span class="text-xs text-zinc-500">•</span>
                <span class="text-xs text-zinc-400 font-mono">Stream: /api/traffic/stream/</span>
              </div>
              <h2 class="text-lg font-bold text-white mt-0.5">Roadside Traffic Surveillance Feed</h2>
            </div>

            <!-- Start / Stop Button -->
            <button
              @click="toggleStream"
              :class="showStream
                ? 'bg-rose-600 hover:bg-rose-500 text-white shadow-rose-900/40'
                : 'bg-[#006CB8] hover:bg-[#005a9c] text-white shadow-blue-900/40'"
              class="h-11 px-5 inline-flex items-center justify-center rounded-xl text-xs sm:text-sm font-semibold shadow-lg transition gap-2"
            >
              <svg v-if="!showStream" class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <svg v-else class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
              <span>{{ showStream ? t('stopLive') : t('startLive') }}</span>
            </button>
          </div>

          <!-- Video Monitor Box -->
          <div class="rounded-xl overflow-hidden border border-zinc-800 bg-black aspect-video flex items-center justify-center relative shadow-inner">
            
            <template v-if="showStream">
              <img
                :src="streamUrl"
                alt="Live traffic detection stream"
                class="w-full h-full object-contain"
              />
              <div class="absolute top-4 left-4 inline-flex items-center gap-2 rounded-lg bg-black/75 px-3 py-1.5 text-xs font-mono text-emerald-400 border border-emerald-500/30 backdrop-blur-md">
                <span class="h-2 w-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span>{{ t('liveActive') }}</span>
              </div>
              <div class="absolute top-4 right-4 inline-flex items-center gap-2 rounded-lg bg-black/75 px-3 py-1.5 text-xs font-mono text-zinc-300 border border-zinc-800 backdrop-blur-md">
                YOLOv8 ByteTrack Active
              </div>
            </template>

            <!-- Standby View ("don't show live ភ្លាម") -->
            <div v-else class="text-center p-8 space-y-4 max-w-md">
              <div class="h-20 w-20 mx-auto rounded-3xl bg-zinc-900/90 border border-zinc-800 flex items-center justify-center text-zinc-500 shadow-xl">
                <svg class="h-10 w-10 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 class="text-base font-bold text-white">{{ t('standbyTitle') }}</h3>
                <p class="text-xs text-zinc-400 mt-1.5 leading-relaxed">
                  {{ t('standbyDesc') }}
                </p>
              </div>
              <button
                @click="toggleStream"
                class="px-5 py-2.5 rounded-xl bg-[#006CB8] hover:bg-[#005a9c] text-xs font-semibold text-white shadow-lg shadow-blue-900/30 transition inline-flex items-center gap-2"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                </svg>
                <span>{{ t('startLive') }}</span>
              </button>
            </div>

          </div>

        </div>

        <!-- 4 Live Telemetry Stat Cards -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('carsTracked') }}</span>
            <div class="mt-2 text-2xl font-bold font-mono text-cyan-400">{{ liveStats.cars || 0 }}</div>
            <p class="text-[11px] text-zinc-500 mt-0.5">Active in view</p>
          </div>
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('motosTracked') }}</span>
            <div class="mt-2 text-2xl font-bold font-mono text-blue-400">{{ liveStats.bikes || 0 }}</div>
            <p class="text-[11px] text-zinc-500 mt-0.5">Tracked motorcycles</p>
          </div>
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('helmetsOk') }}</span>
            <div class="mt-2 text-2xl font-bold font-mono text-emerald-400">{{ liveStats.helmets_compliant || 0 }}</div>
            <p class="text-[11px] text-zinc-500 mt-0.5">Law compliant</p>
          </div>
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/50 p-4">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('violationsFlagged') }}</span>
            <div class="mt-2 text-2xl font-bold font-mono text-rose-400">{{ liveStats.violations || 0 }}</div>
            <p class="text-[11px] text-zinc-500 mt-0.5">Infractions detected</p>
          </div>
        </div>

        <!-- Legal Reference Card -->
        <div class="rounded-xl border border-blue-900/40 bg-blue-950/20 p-4 text-xs text-blue-200 space-y-1">
          <div class="font-semibold text-blue-300 flex items-center gap-1.5">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ t('lawNotice') }}
          </div>
          <p class="text-blue-300/80">{{ t('lawDesc') }}</p>
        </div>

      </main>
    </div>

  </div>
</template>
