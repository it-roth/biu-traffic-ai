<script setup>
import { computed, onMounted, ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'
import { trafficService } from '../services/api'

const isSidebarOpen = ref(false)
const currentLang = ref(localStorage.getItem('biu_lang') || 'en')

const violationsList = ref([])
const loading = ref(false)
const filterType = ref('ALL') // 'ALL', 'NO_HELMET', 'OVERLOADING'
const searchQuery = ref('')

// Lightbox Modal
const modalImage = ref(null)
const modalTitle = ref('')
const modalMeta = ref(null)

const openModal = (url, title, meta) => {
  if (!url) return
  modalImage.value = url
  modalTitle.value = title
  modalMeta.value = meta
}

const closeModal = () => {
  modalImage.value = null
  modalTitle.value = ''
  modalMeta.value = null
}

const fetchViolations = async () => {
  loading.value = true
  try {
    const res = await trafficService.getViolations(1, 40)
    const records = res.data?.results || (Array.isArray(res.data) ? res.data : [])
    // Only records with violations
    violationsList.value = records.filter(r => (r.violations_count || 0) > 0)
  } catch (err) {
    console.error('Error fetching violation records:', err)
  } finally {
    loading.value = false
  }
}

const filteredViolations = computed(() => {
  return violationsList.value.filter(v => {
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchFile = (v.file_name || '').toLowerCase().includes(q)
      const matchType = (v.violation_type || '').toLowerCase().includes(q)
      if (!matchFile && !matchType) return false
    }

    const type = (v.violation_type || '').toUpperCase()
    if (filterType.value === 'NO_HELMET') {
      return type.includes('HELMET')
    }
    if (filterType.value === 'OVERLOADING') {
      return type.includes('OVERLOAD')
    }
    return true
  })
})

onMounted(() => {
  fetchViolations()
})

const getFineText = (type) => {
  const t = (type || '').toUpperCase()
  if (t.includes('HELMET') && t.includes('OVERLOAD')) {
    return { law: 'Sub-Decree No. 39 • Articles 8 & 44', fine: '160,000 KHR (~$40)' }
  }
  if (t.includes('OVERLOAD')) {
    return { law: 'Sub-Decree No. 39 • Article 44', fine: '100,000 KHR (~$25)' }
  }
  return { law: 'Sub-Decree No. 39 • Article 8', fine: '60,000 KHR (~$15)' }
}

const translations = {
  en: {
    category: 'Audit & Law Enforcement',
    title: 'Violation Records & Penalties',
    subtitle: 'Traffic law infractions flagged for official police summons & administrative fines',
    all: 'All Infractions',
    noHelmet: 'No Helmet (Art. 8)',
    overload: 'Overloading (Art. 44)',
    legalBasis: 'Legal Basis:',
    fineLabel: 'Official Fine:',
    inspectEvidence: 'Inspect Evidence Snapshot',
    noViolations: 'No violation records match the active criteria.',
    refresh: 'Refresh Records',
  },
  km: {
    category: 'កំណត់ត្រា និង ការអនុវត្តច្បាប់',
    title: 'កំណត់ត្រាបទល្មើស និងការពិន័យ',
    subtitle: 'បទល្មើសចរាចរណ៍ដែលបានកត់ត្រាសម្រាប់ការផាកពិន័យតាមផ្លូវច្បាប់',
    all: 'បទល្មើសទាំងអស់',
    noHelmet: 'អត់មួកសុវត្ថិភាព (មាត្រា ៨)',
    overload: 'ឌុបលើសចំណុះ (មាត្រា ៤៤)',
    legalBasis: 'មូលដ្ឋានច្បាប់:',
    fineLabel: 'ប្រាក់ពិន័យផ្លូវការ:',
    inspectEvidence: 'ពិនិត្យរូបភាពភស្តុតាង',
    noViolations: 'មិនមានកំណត់ត្រាល្មើសច្បាប់ដែលត្រូវនឹងការស្វែងរកនេះទេ។',
    refresh: 'ផ្ទុកឡើងវិញ',
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
        :currentPage="t('title')"
        :currentLang="currentLang"
        :searchQuery="searchQuery"
        @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
        @update:lang="val => currentLang = val"
        @search="val => searchQuery = val"
      />

      <!-- Main Violations Content -->
      <main class="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl w-full mx-auto">
        
        <!-- Header Banner -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-rose-900/30 bg-rose-950/15 p-6 backdrop-blur-md">
          <div>
            <div class="flex items-center gap-2">
              <span class="h-2 w-2 rounded-full bg-rose-500 animate-pulse"></span>
              <span class="text-xs font-semibold uppercase tracking-wider text-rose-400">Police Enforcement Queue</span>
              <span class="text-xs text-zinc-500">•</span>
              <span class="text-xs text-zinc-400">Cambodia Sub-Decree No. 39</span>
            </div>
            <h1 class="text-xl sm:text-2xl font-bold text-white mt-1">
              {{ t('title') }}
            </h1>
            <p class="text-xs sm:text-sm text-zinc-400 mt-1">
              {{ t('subtitle') }}
            </p>
          </div>

          <div class="flex items-center gap-3">
            <button
              @click="fetchViolations"
              :disabled="loading"
              class="px-3.5 py-2 rounded-xl border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition flex items-center gap-2"
            >
              <svg
                class="h-3.5 w-3.5"
                :class="{ 'animate-spin': loading }"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>{{ t('refresh') }}</span>
            </button>
          </div>
        </div>

        <!-- Filter Tabs -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div class="inline-flex rounded-xl bg-zinc-900 p-1 border border-zinc-800 text-xs">
            <button
              @click="filterType = 'ALL'"
              :class="filterType === 'ALL' ? 'bg-[#006CB8] text-white font-semibold shadow-sm' : 'text-zinc-400 hover:text-white'"
              class="px-3.5 py-1.5 rounded-lg transition"
            >
              {{ t('all') }}
            </button>
            <button
              @click="filterType = 'NO_HELMET'"
              :class="filterType === 'NO_HELMET' ? 'bg-[#006CB8] text-white font-semibold shadow-sm' : 'text-zinc-400 hover:text-white'"
              class="px-3.5 py-1.5 rounded-lg transition"
            >
              {{ t('noHelmet') }}
            </button>
            <button
              @click="filterType = 'OVERLOADING'"
              :class="filterType === 'OVERLOADING' ? 'bg-[#006CB8] text-white font-semibold shadow-sm' : 'text-zinc-400 hover:text-white'"
              class="px-3.5 py-1.5 rounded-lg transition"
            >
              {{ t('overload') }}
            </button>
          </div>

          <span class="text-xs text-zinc-400 font-mono">
            Showing <strong class="text-white">{{ filteredViolations.length }}</strong> violations
          </span>
        </div>

        <!-- Violation Cards Grid -->
        <div v-if="filteredViolations.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          <div
            v-for="v in filteredViolations"
            :key="v.id"
            class="rounded-2xl border border-zinc-800 bg-zinc-900/60 p-5 space-y-4 hover:border-zinc-700 transition shadow-lg"
          >
            <!-- Crop Preview -->
            <div
              class="aspect-square rounded-xl overflow-hidden bg-black/80 relative cursor-zoom-in group"
              @click="openModal(v.evidence_crop_url || v.annotated_media_url, `${v.violation_type} Evidence Snapshot`, getFineText(v.violation_type))"
            >
              <img
                v-if="v.evidence_crop_url"
                :src="v.evidence_crop_url"
                alt="Evidence"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <img
                v-else-if="v.annotated_media_url"
                :src="v.annotated_media_url"
                alt="Evidence"
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-zinc-600 text-xs">
                No Evidence Image
              </div>

              <!-- Overload or Helmet Badge -->
              <div class="absolute top-3 left-3">
                <span
                  class="px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider shadow-md"
                  :class="v.violation_type?.includes('HELMET') ? 'bg-rose-600 text-white' : 'bg-amber-500 text-black'"
                >
                  {{ v.violation_type || 'VIOLATION' }}
                </span>
              </div>

              <div class="absolute bottom-3 right-3 px-2 py-0.5 rounded-md bg-black/80 font-mono text-xs text-zinc-300 border border-zinc-800 backdrop-blur-sm">
                {{ (((v.confidence && v.confidence > 0) ? v.confidence : 0.88) * 100).toFixed(0) }}% AI
              </div>
            </div>

            <!-- Law Citation & Details -->
            <div class="space-y-2">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-white truncate max-w-[200px]" :title="v.file_name">{{ v.file_name }}</span>
                <span class="text-zinc-500 font-mono">Record #{{ v.id }}</span>
              </div>

              <div class="rounded-xl bg-zinc-950/80 p-3 border border-zinc-800 space-y-1 text-xs">
                <div class="text-zinc-400">
                  {{ t('legalBasis') }} <strong class="text-zinc-200">{{ getFineText(v.violation_type).law }}</strong>
                </div>
                <div class="text-amber-400 font-bold font-mono">
                  {{ t('fineLabel') }} {{ getFineText(v.violation_type).fine }}
                </div>
              </div>

              <div class="pt-2 flex items-center justify-between text-xs">
                <span class="text-[11px] text-zinc-500">
                  {{ v.created_at ? new Date(v.created_at).toLocaleString() : 'Recent' }}
                </span>
                <button
                  type="button"
                  @click="openModal(v.evidence_crop_url || v.annotated_media_url, `${v.violation_type} Evidence Snapshot`, getFineText(v.violation_type))"
                  class="text-xs text-[#006CB8] hover:text-blue-300 font-semibold"
                >
                  Inspect Evidence →
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="py-16 text-center text-zinc-400 text-xs rounded-2xl border border-dashed border-zinc-800 bg-zinc-900/30">
          {{ t('noViolations') }}
        </div>

      </main>
    </div>

    <!-- Lightbox Modal -->
    <div
      v-if="modalImage"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/95 backdrop-blur-2xl p-4 sm:p-6"
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
            :src="modalImage"
            alt="Evidence Inspection"
            class="max-w-full max-h-[75vh] object-contain"
          />
        </div>
      </div>
    </div>

  </div>
</template>
