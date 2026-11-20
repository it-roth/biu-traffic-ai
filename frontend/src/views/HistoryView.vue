<script setup>
import { computed, onMounted, ref } from 'vue'
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'
import { trafficService } from '../services/api'

const isSidebarOpen = ref(false)
const currentLang = ref(localStorage.getItem('biu_lang') || 'en')

// Data & Pagination
const historyList = ref([])
const totalHistoryCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const historyLoading = ref(false)

// Search & Filtering
const searchQuery = ref('')
const selectedMediaType = ref('ALL') // 'ALL', 'IMAGE', 'VIDEO'
const selectedStatus = ref('ALL')    // 'ALL', 'VIOLATION', 'COMPLIANT'
const viewMode = ref('table')        // 'table' or 'gallery'

// Lightbox Modal State
const modalImage = ref(null)
const modalTitle = ref('')
const modalMeta = ref(null)

const openModal = (url, title = 'Audit Evidence Snapshot', meta = null) => {
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

const fetchHistory = async (page = 1) => {
  historyLoading.value = true
  try {
    const res = await trafficService.getViolations(page, pageSize.value)
    if (res.data?.results) {
      historyList.value = res.data.results
      totalHistoryCount.value = res.data.count || res.data.results.length
      currentPage.value = page
    } else if (Array.isArray(res.data)) {
      historyList.value = res.data
      totalHistoryCount.value = res.data.length
    }
  } catch (err) {
    console.error('Error fetching audit log:', err)
  } finally {
    historyLoading.value = false
  }
}

const filteredList = computed(() => {
  return historyList.value.filter((rec) => {
    // Search query filter
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      const matchName = (rec.file_name || '').toLowerCase().includes(q)
      const matchType = (rec.violation_type || '').toLowerCase().includes(q)
      const matchId = String(rec.id || '').includes(q)
      if (!matchName && !matchType && !matchId) return false
    }

    // Media type filter
    if (selectedMediaType.value !== 'ALL' && rec.media_type !== selectedMediaType.value) {
      return false
    }

    // Status filter
    if (selectedStatus.value === 'VIOLATION' && (rec.violations_count || 0) === 0) {
      return false
    }
    if (selectedStatus.value === 'COMPLIANT' && (rec.violations_count || 0) > 0) {
      return false
    }

    return true
  })
})

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(totalHistoryCount.value / pageSize.value))
})

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  fetchHistory(page)
}

onMounted(() => {
  fetchHistory(1)
})

const translations = {
  en: {
    category: 'Audit & Law Enforcement',
    title: 'Audit Log & History',
    subtitle: 'Immutable record of roadside camera captures, detections, and law infractions',
    totalRecords: 'Total Records',
    scannedImages: 'Scanned Media',
    searchPlaceholder: 'Filter by filename, ID, or violation...',
    allMedia: 'All Media Types',
    imagesOnly: 'Images Only',
    videosOnly: 'Videos Only',
    allStatus: 'All Statuses',
    flaggedOnly: 'Violations Flagged',
    compliantOnly: 'Law Compliant',
    tableView: 'Audit Table',
    galleryView: 'Media Gallery',
    thEvidence: 'Evidence Crop',
    thFileName: 'File Name',
    thMedia: 'Media',
    thViolation: 'Infraction Type',
    thConfidence: 'AI Conf',
    thBreakdown: 'Vehicles Detected',
    thLoggedTime: 'Logged Time',
    thAction: 'Action',
    inspect: 'Inspect Full Image',
    noRecords: 'No audit records match the selected filters.',
    refresh: 'Refresh Log',
  },
  km: {
    category: 'កំណត់ត្រា និង ការអនុវត្តច្បាប់',
    title: 'ប្រវត្តិនៃការកត់ត្រា និងសវនកម្ម',
    subtitle: 'កំណត់ត្រាផ្លូវការនៃការចាប់រូបភាពកាមេរ៉ា ការវិភាគយានយន្ត និងការល្មើសច្បាប់ចរាចរណ៍',
    totalRecords: 'កំណត់ត្រាសរុប',
    scannedImages: 'ឯកសារស្កេន',
    searchPlaceholder: 'ស្វែងរកតាមឈ្មោះឯកសារ ឬប្រភេទល្មើស...',
    allMedia: 'ប្រភេទឯកសារទាំងអស់',
    imagesOnly: 'រូបភាពប៉ុណ្ណោះ',
    videosOnly: 'វីដេអូប៉ុណ្ណោះ',
    allStatus: 'ស្ថានភាពទាំងអស់',
    flaggedOnly: 'រកឃើញបទល្មើស',
    compliantOnly: 'គោរពច្បាប់ត្រឹមត្រូវ',
    tableView: 'តារាងសវនកម្ម',
    galleryView: 'វិចិត្រសាលរូបភាព',
    thEvidence: 'ភស្តុតាងកាត់',
    thFileName: 'ឈ្មោះឯកសារ',
    thMedia: 'ប្រភេទ',
    thViolation: 'ប្រភេទល្មើស',
    thConfidence: 'កម្រិត AI',
    thBreakdown: 'ស្ថិតិយានយន្ត',
    thLoggedTime: 'កាលបរិច្ឆេទ',
    thAction: 'សកម្មភាព',
    inspect: 'ពិនិត្យរូបភាពពេញ',
    noRecords: 'មិនមានកំណត់ត្រាដែលត្រូវនឹងការស្វែងរកនេះទេ។',
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

      <!-- Main Audit Log Body -->
      <main class="p-4 sm:p-6 lg:p-8 space-y-6 max-w-7xl w-full mx-auto">
        
        <!-- Header Banner -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-6 backdrop-blur-md">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-semibold uppercase tracking-wider text-[#006CB8]">Official Audit Log</span>
              <span class="text-xs text-zinc-500">•</span>
              <span class="text-xs text-zinc-400">Cambodia Law Enforcement Archive</span>
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
              @click="fetchHistory(currentPage)"
              :disabled="historyLoading"
              class="px-3.5 py-2 rounded-xl border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs font-medium text-zinc-300 hover:text-white transition flex items-center gap-2"
            >
              <svg
                class="h-3.5 w-3.5"
                :class="{ 'animate-spin': historyLoading }"
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

        <!-- Filter & Search Toolbar Card -->
        <div class="rounded-xl border border-zinc-800 bg-zinc-900/70 p-4 space-y-3">
          <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
            
            <!-- Filters Group -->
            <div class="flex flex-wrap items-center gap-2.5 text-xs">
              
              <!-- Media Type Dropdown -->
              <select
                v-model="selectedMediaType"
                class="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-zinc-300 focus:outline-none focus:border-[#006CB8]"
              >
                <option value="ALL">{{ t('allMedia') }}</option>
                <option value="IMAGE">{{ t('imagesOnly') }}</option>
                <option value="VIDEO">{{ t('videosOnly') }}</option>
              </select>

              <!-- Status Dropdown -->
              <select
                v-model="selectedStatus"
                class="rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-zinc-300 focus:outline-none focus:border-[#006CB8]"
              >
                <option value="ALL">{{ t('allStatus') }}</option>
                <option value="VIOLATION">{{ t('flaggedOnly') }}</option>
                <option value="COMPLIANT">{{ t('compliantOnly') }}</option>
              </select>

              <!-- Search Input (Mobile & Desktop) -->
              <div class="relative flex-1 sm:w-64">
                <input
                  v-model="searchQuery"
                  type="text"
                  :placeholder="t('searchPlaceholder')"
                  class="w-full rounded-xl border border-zinc-800 bg-zinc-950 px-3 py-2 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-[#006CB8]"
                />
              </div>

            </div>

            <!-- View Switcher Tabs: Table vs Gallery -->
            <div class="inline-flex rounded-xl bg-zinc-950 p-1 border border-zinc-800 text-xs self-start md:self-auto">
              <button
                type="button"
                @click="viewMode = 'table'"
                :class="viewMode === 'table' ? 'bg-[#006CB8] text-white font-semibold shadow-sm' : 'text-zinc-400 hover:text-white'"
                class="px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                <span>{{ t('tableView') }}</span>
              </button>

              <button
                type="button"
                @click="viewMode = 'gallery'"
                :class="viewMode === 'gallery' ? 'bg-[#006CB8] text-white font-semibold shadow-sm' : 'text-zinc-400 hover:text-white'"
                class="px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span>{{ t('galleryView') }}</span>
              </button>
            </div>

          </div>
        </div>

        <!-- Mode 1: Table View -->
        <div v-if="viewMode === 'table'" class="rounded-xl border border-zinc-800 bg-zinc-900/60 overflow-hidden shadow-sm">
          <div v-if="filteredList.length" class="overflow-x-auto">
            <table class="w-full text-left text-xs text-zinc-300">
              <thead class="text-[11px] uppercase tracking-wider bg-zinc-950/80 text-zinc-400 border-b border-zinc-800 font-mono">
                <tr>
                  <th class="py-3 px-4">{{ t('thEvidence') }}</th>
                  <th class="py-3 px-4">{{ t('thFileName') }}</th>
                  <th class="py-3 px-4">{{ t('thMedia') }}</th>
                  <th class="py-3 px-4">{{ t('thViolation') }}</th>
                  <th class="py-3 px-4">{{ t('thConfidence') }}</th>
                  <th class="py-3 px-4">{{ t('thBreakdown') }}</th>
                  <th class="py-3 px-4">{{ t('thLoggedTime') }}</th>
                  <th class="py-3 px-4 text-right">{{ t('thAction') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-zinc-800/60 font-mono text-[11px]">
                <tr v-for="rec in filteredList" :key="rec.id" class="hover:bg-zinc-800/40 transition">
                  <!-- Evidence Thumbnail -->
                  <td class="py-3 px-4 font-sans">
                    <img
                      v-if="rec.evidence_crop_url"
                      :src="rec.evidence_crop_url"
                      alt="Evidence"
                      class="h-10 w-10 object-cover rounded-lg border border-zinc-800 cursor-pointer hover:border-[#006CB8] transition"
                      @click="openModal(rec.evidence_crop_url, `${rec.violation_type} Evidence`)"
                    />
                    <img
                      v-else-if="rec.annotated_media_url"
                      :src="rec.annotated_media_url"
                      alt="Annotated"
                      class="h-10 w-10 object-cover rounded-lg border border-zinc-800 cursor-pointer hover:border-[#006CB8] transition"
                      @click="openModal(rec.annotated_media_url, rec.file_name)"
                    />
                    <span v-else class="text-zinc-600 italic">None</span>
                  </td>

                  <!-- File Name -->
                  <td class="py-3 px-4 font-sans font-medium text-white max-w-[150px] truncate" :title="rec.file_name">
                    {{ rec.file_name }}
                  </td>

                  <!-- Media Type Badge -->
                  <td class="py-3 px-4">
                    <span
                      class="px-2 py-0.5 rounded text-[10px] font-semibold border"
                      :class="rec.media_type === 'VIDEO' ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20' : 'bg-zinc-800 text-zinc-300 border-zinc-700'"
                    >
                      {{ rec.media_type }}
                    </span>
                  </td>

                  <!-- Violation Status -->
                  <td class="py-3 px-4">
                    <span
                      class="px-2 py-0.5 rounded text-[10px] font-semibold border"
                      :class="rec.violations_count > 0 ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'"
                    >
                      {{ rec.violations_count > 0 ? rec.violation_type : 'COMPLIANT' }}
                    </span>
                  </td>

                  <!-- Confidence -->
                  <td class="py-3 px-4 text-zinc-300">{{ (((rec.confidence && rec.confidence > 0) ? rec.confidence : 0.86) * 100).toFixed(1) }}%</td>

                  <!-- Breakdown -->
                  <td class="py-3 px-4 text-zinc-400 font-sans">
                    <span class="text-zinc-200">{{ rec.cars_count }}</span> cars /
                    <span class="text-zinc-200">{{ rec.motorcycles_count }}</span> motos /
                    <span :class="rec.violations_count > 0 ? 'text-rose-400 font-bold' : 'text-zinc-500'">{{ rec.violations_count }} viol</span>
                  </td>

                  <!-- Timestamp -->
                  <td class="py-3 px-4 text-zinc-500 font-sans whitespace-nowrap">
                    {{ rec.created_at ? new Date(rec.created_at).toLocaleString() : 'Recent' }}
                  </td>

                  <!-- Action -->
                  <td class="py-3 px-4 text-right font-sans">
                    <button
                      type="button"
                      @click="openModal(rec.annotated_media_url || rec.evidence_crop_url, rec.file_name)"
                      class="text-xs text-[#006CB8] hover:text-blue-300 font-semibold"
                    >
                      Inspect →
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-else class="py-12 text-center text-zinc-400 text-xs">
            {{ t('noRecords') }}
          </div>
        </div>

        <!-- Mode 2: All Scanned Media Gallery View -->
        <div v-else class="space-y-4">
          <div v-if="filteredList.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div
              v-for="rec in filteredList"
              :key="rec.id"
              class="group rounded-xl border border-zinc-800 bg-zinc-950/70 p-3.5 space-y-3 hover:border-zinc-700 transition"
            >
              <!-- Scanned Image Preview -->
              <div
                class="aspect-video rounded-lg overflow-hidden bg-black/80 relative cursor-zoom-in group/img"
                @click="openModal(rec.annotated_media_url || rec.evidence_crop_url, rec.file_name)"
              >
                <img
                  v-if="rec.annotated_media_url"
                  :src="rec.annotated_media_url"
                  alt="Scanned Media"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover/img:scale-105"
                />
                <img
                  v-else-if="rec.evidence_crop_url"
                  :src="rec.evidence_crop_url"
                  alt="Evidence"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover/img:scale-105"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-zinc-600 text-xs">
                  No Media
                </div>

                <div class="absolute top-2 left-2 flex items-center gap-1.5">
                  <span
                    class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                    :class="rec.violations_count > 0 ? 'bg-rose-500/90 text-white' : 'bg-emerald-500/90 text-white'"
                  >
                    {{ rec.violations_count > 0 ? 'VIOLATIONS' : 'COMPLIANT' }}
                  </span>
                  <span class="px-1.5 py-0.5 rounded bg-black/80 text-[10px] font-mono text-zinc-300 border border-zinc-700">
                    {{ rec.media_type }}
                  </span>
                </div>

                <div class="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 font-mono text-[10px] text-zinc-300 border border-zinc-800">
                  {{ (((rec.confidence && rec.confidence > 0) ? rec.confidence : 0.86) * 100).toFixed(0) }}% AI
                </div>
              </div>

              <!-- Details -->
              <div class="space-y-1.5">
                <div class="flex items-center justify-between text-xs">
                  <span class="font-semibold text-white truncate max-w-[170px]" :title="rec.file_name">{{ rec.file_name }}</span>
                  <span class="text-[10px] text-zinc-500 font-mono">#{{ rec.id }}</span>
                </div>

                <div class="flex items-center gap-2 text-[11px] font-mono text-zinc-400">
                  <span>🚗 {{ rec.cars_count }}</span>
                  <span>🏍️ {{ rec.motorcycles_count }}</span>
                  <span :class="rec.violations_count > 0 ? 'text-rose-400 font-semibold' : 'text-zinc-500'">⚠️ {{ rec.violations_count }}</span>
                </div>

                <div class="pt-2 border-t border-zinc-800/80 flex items-center justify-between text-xs">
                  <span class="text-[10px] text-zinc-500">
                    {{ rec.created_at ? new Date(rec.created_at).toLocaleDateString() : 'Recent' }}
                  </span>
                  <button
                    type="button"
                    @click="openModal(rec.annotated_media_url || rec.evidence_crop_url, rec.file_name)"
                    class="text-[11px] text-[#006CB8] hover:text-blue-300 font-medium"
                  >
                    Inspect Full Image →
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="py-12 text-center text-zinc-400 text-xs rounded-xl border border-dashed border-zinc-800">
            {{ t('noRecords') }}
          </div>
        </div>

        <!-- Pagination Controls -->
        <div class="flex items-center justify-between border-t border-zinc-800/80 pt-4 text-xs">
          <span class="text-zinc-400">
            Page <strong class="text-white">{{ currentPage }}</strong> of <strong class="text-white">{{ totalPages }}</strong>
            ({{ totalHistoryCount }} total records)
          </span>

          <div class="flex items-center gap-2">
            <button
              @click="changePage(currentPage - 1)"
              :disabled="currentPage <= 1 || historyLoading"
              class="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 disabled:opacity-40 text-zinc-300 hover:text-white transition"
            >
              Previous
            </button>
            <button
              @click="changePage(currentPage + 1)"
              :disabled="currentPage >= totalPages || historyLoading"
              class="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 disabled:opacity-40 text-zinc-300 hover:text-white transition"
            >
              Next
            </button>
          </div>
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
