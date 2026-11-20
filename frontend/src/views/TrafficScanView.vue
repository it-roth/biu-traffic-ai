<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { trafficService } from '../services/api'
import Sidebar from '../components/Sidebar.vue'
import TopHeader from '../components/TopHeader.vue'

const router = useRouter()
const isSidebarOpen = ref(false)

// File upload & preview state
const isDragging = ref(false)
const selectedFile = ref(null)
const previewUrl = ref(null)
const mediaType = ref('IMAGE') // 'IMAGE' or 'VIDEO'
const fileInput = ref(null)

// Scanning & progress state
const isScanning = ref(false)
const uploadProgress = ref(0)
const scanStatusText = ref('')
const errorMessage = ref('')
const isBackendConnected = ref(true)

// Scan results
const scanResult = ref(null)
const activeTab = ref('ALL') // 'ALL', 'NO_HELMET', 'OVERLOADING'

// Historical violations list & display mode
const historyList = ref([])
const historyLoading = ref(false)
const currentPage = ref(1)
const totalHistoryCount = ref(0)
const historyViewMode = ref('gallery') // 'gallery' or 'table'

// Modal for enlarged snapshot / evidence inspection lightbox
const modalImage = ref(null)
const modalTitle = ref('')
const modalMeta = ref(null)
const modalZoom = ref(1)

// Language localization state (English default, supports Khmer)
const currentLang = ref(localStorage.getItem('biu_lang') || 'en')

const toggleLang = (lang) => {
  currentLang.value = lang
  localStorage.setItem('biu_lang', lang)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  router.push('/login')
}

const strings = {
  en: {
    university: 'BELTEI International University',
    subtitle: 'BELTEI International University • Cambodia Traffic Law Enforcement',
    dashboard: 'Dashboard',
    scanner: 'AI Traffic Scanner',
    logout: 'Log Out',
    systemOnline: 'System Online',
    backendOffline: 'Backend Offline',
    liveFeed: 'Live Camera Feed',
    backendUnreachable: 'Django API is unreachable at https://biu-traffic-api.onrender.com',
    ensureBackend: 'Please ensure the backend server is running:',
    retry: 'Retry',
    connecting: 'Connecting...',
    cars: 'Cars & SUVs',
    carsDesc: 'Light 4-wheel vehicles',
    motorcycles: 'Motorcycles',
    motorcyclesDesc: '2-wheel motorbikes',
    tuktukPassapp: 'Tuk-Tuk & PassApp',
    tuktukPassappDesc: 'PassApp, Bajaj & Khmer Remorques',
    violations: 'Violations',
    flagged: 'Flagged',
    compliant: 'Compliant',
    penaltyNotice: 'Penalty Notice',
    uploadTitle: 'Upload Traffic Media',
    uploadDesc: 'Drop roadside camera images (.jpg, .png) or video (.mp4) to detect vehicle infractions.',
    clickToUpload: 'Click to upload',
    dragDrop: 'or drag and drop',
    uploadFormats: 'MP4, PNG, JPG or WEBP up to 100MB',
    executeScan: 'Execute AI Scan',
    processing: 'Processing Inference...',
    clear: 'Clear',
    detectionOutput: 'Detection Output',
    outputDesc: 'YOLOv8 + ByteTrack bounding boxes & traffic law enforcement',
    confidence: 'Confidence',
    rawInput: 'Raw Input',
    yoloAnnotated: 'YOLOv8 Annotated',
    byteTrackActive: 'ByteTrack Active',
    clickEnlarge: 'Click to enlarge',
    noMedia: 'No media scanned yet',
    noMediaDesc: 'Select an image or video from the left to inspect bounding boxes.',
    snapshotsTitle: 'Violation Evidence Snapshots',
    snapshotsDesc: 'Auto-cropped infraction regions preserved for police audit',
    allSnapshots: 'All Snapshots',
    noHelmet: 'No Helmet',
    overloading: 'Overloading',
    dualViolation: 'DUAL: No Helmet & Overload',
    overloadTitle: 'Motorcycle Overloading',
    noHelmetTitle: 'Rider Without Safety Helmet',
    riders: 'Riders',
    legalBasis: 'Legal Basis:',
    fineLabel: 'Official Fine:',
    overloadLaw: 'Sub-Decree No. 39 • Article 44',
    noHelmetLaw: 'Sub-Decree No. 39 • Article 8',
    dualLaw: 'Sub-Decree No. 39 • Articles 8 & 44',
    overloadFine: 'Fine: 100,000 KHR (~$25)',
    noHelmetFine: 'Fine: 60,000 KHR (~$15)',
    dualFine: 'Fine: 160,000 KHR (~$40)',
    auditSnapshot: 'Audit Snapshot',
    downloadEvidence: 'Download Evidence',
    noCropsMatching: 'No violation crops matching the selected filter.',
    historyTitle: 'Enforcement History Log',
    historyDesc: 'Audit log of all detected traffic records',
    refreshLog: 'Refresh Log',
    allInputImages: 'All Scanned Input Images',
    galleryView: 'Gallery View',
    tableView: 'Table View',
    thEvidence: 'Evidence',
    thFileName: 'File Name',
    thMedia: 'Media',
    thViolationType: 'Violation Type',
    thConfidence: 'Confidence',
    thBreakdown: 'Vehicle Breakdown',
    thLoggedTime: 'Logged Time',
    noHistory: 'No violation records saved in the database yet.',
  },
  km: {
    university: 'សាកលវិទ្យាល័យ ប៊ែលធី អន្តរជាតិ',
    subtitle: 'សាកលវិទ្យាល័យ ប៊ែលធី អន្តរជាតិ • ការអនុវត្តច្បាប់ចរាចរណ៍ផ្លូវគោកកម្ពុជា',
    dashboard: 'ផ្ទាំងគ្រប់គ្រង',
    scanner: 'ស្កេនចរាចរណ៍ AI',
    logout: 'ចាកចេញ',
    systemOnline: 'ប្រព័ន្ធដំណើរការធម្មតា',
    backendOffline: 'ប្រព័ន្ធម៉ាស៊ីនមេដាច់ការតភ្ជាប់',
    liveFeed: 'ទិដ្ឋភាពកាមេរ៉ាផ្ទាល់',
    backendUnreachable: 'មិនអាចតភ្ជាប់ទៅកាន់ API នៅ https://biu-traffic-api.onrender.com',
    ensureBackend: 'សូមប្រាកដថាម៉ាស៊ីនមេ Backend កំពុងដំណើរការ:',
    retry: 'ព្យាយាមម្តងទៀត',
    connecting: 'កំពុងតភ្ជាប់...',
    cars: 'រថយន្ត និង ឡាន',
    carsDesc: 'យានយន្តធុនស្រាល ៤ កង់',
    motorcycles: 'ម៉ូតូ',
    motorcyclesDesc: 'ទោចក្រយានយន្ត ២ កង់',
    tuktukPassapp: 'កង់បី និង រ៉ឺម៉ក',
    tuktukPassappDesc: 'ផាសអាប់ (PassApp) និង រ៉ឺម៉កកង់បី',
    violations: 'ការល្មើសច្បាប់',
    flagged: 'រកឃើញល្មើស',
    compliant: 'គោរពច្បាប់ត្រឹមត្រូវ',
    penaltyNotice: 'ចេញប័ណ្ណពិន័យ',
    uploadTitle: 'បញ្ចូលឯកសាររូបភាព/វីដេអូចរាចរណ៍',
    uploadDesc: 'ទម្លាក់រូបភាពកាមេរ៉ា (.jpg, .png) ឬវីដេអូ (.mp4) ដើម្បីស្កេនពិនិត្យការល្មើសច្បាប់។',
    clickToUpload: 'ចុចដើម្បីបញ្ចូល',
    dragDrop: 'ឬអូសទម្លាក់ទីនេះ',
    uploadFormats: 'MP4, PNG, JPG ឬ WEBP រហូតដល់ 100MB',
    executeScan: 'ដំណើរការស្កេន AI',
    processing: 'កំពុងដំណើរការវិភាគ...',
    clear: 'សម្អាត',
    detectionOutput: 'លទ្ធផលនៃការពិនិត្យ',
    outputDesc: 'ប្រអប់សម្គាល់ YOLOv8 + ByteTrack និងស្លាកល្មើសច្បាប់កម្ពុជា',
    confidence: 'កម្រិតទំនុកចិត្ត',
    rawInput: 'ឯកសារដើម',
    yoloAnnotated: 'លទ្ធផលពី YOLOv8',
    byteTrackActive: 'ByteTrack កំពុងដំណើរការ',
    clickEnlarge: 'ចុចដើម្បីពង្រីក',
    noMedia: 'មិនទាន់មានការស្កេននៅឡើយទេ',
    noMediaDesc: 'សូមជ្រើសរើសរូបភាព ឬវីដេអូពីផ្នែកខាងឆ្វេងដើម្បីត្រួតពិនិត្យ។',
    snapshotsTitle: 'ភស្តុតាងរូបថតការល្មើសច្បាប់',
    snapshotsDesc: 'រូបថតកាត់ដោយស្វ័យប្រវត្តិនៃការល្មើសច្បាប់សម្រាប់មន្ត្រីនគរបាលពិនិត្យ',
    allSnapshots: 'ភស្តុតាងទាំងអស់',
    noHelmet: 'គ្មានមួកសុវត្ថិភាព',
    overloading: 'ឌុបលើសចំណុះ',
    dualViolation: 'ល្មើស២៖ គ្មានមួក & លើសចំណុះ',
    overloadTitle: 'ការឌុបលើសចំណុះ',
    noHelmetTitle: 'អ្នកជិះមិនពាក់មួកសុវត្ថិភាព',
    riders: 'អ្នកជិះ',
    legalBasis: 'មូលដ្ឋានច្បាប់៖',
    fineLabel: 'កម្រិតពិន័យ៖',
    overloadLaw: 'អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៤៤',
    noHelmetLaw: 'អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨',
    dualLaw: 'អនុក្រឹត្យលេខ ៣៩ • មាត្រា ៨ និង ៤៤',
    overloadFine: 'ពិន័យ: ១០០,០០០៛ (~$25)',
    noHelmetFine: 'ពិន័យ: ៦០,០០០៛ (~$15)',
    dualFine: 'ពិន័យ: ១៦០,០០០៛ (~$40)',
    auditSnapshot: 'ពិនិត្យភស្តុតាង',
    downloadEvidence: 'ទាញយករូបថត',
    noCropsMatching: 'គ្មានរូបថតល្មើសដែលត្រូវនឹងការច្រោះនេះទេ។',
    historyTitle: 'កំណត់ត្រាប្រវត្តិការអនុវត្តច្បាប់',
    historyDesc: 'កំណត់ត្រាសវនកម្មនៃរាល់ទិន្នន័យចរាចរណ៍ដែលបានពិនិត្យ',
    refreshLog: 'ផ្ទុកឡើងវិញ',
    allInputImages: 'រូបភាពស្កេនទាំងអស់',
    galleryView: 'ទិដ្ឋភាពរូបភាព',
    tableView: 'តារាង',
    thEvidence: 'ភស្តុតាង',
    thFileName: 'ឈ្មោះឯកសារ',
    thMedia: 'ប្រភេទ',
    thViolationType: 'ប្រភេទល្មើស',
    thConfidence: 'កម្រិតទំនុកចិត្ត',
    thBreakdown: 'ស្ថិតិយានយន្ត',
    thLoggedTime: 'កាលបរិច្ឆេទ',
    noHistory: 'មិនទាន់មានកំណត់ត្រាល្មើសក្នុងទិន្នន័យនៅឡើយទេ។',
  }
}

const t = (key) => strings[currentLang.value]?.[key] || strings.en[key] || key

// Computed
const filteredCrops = computed(() => {
  if (!scanResult.value?.evidence_crops) return []
  if (activeTab.value === 'ALL') return scanResult.value.evidence_crops
  return scanResult.value.evidence_crops.filter((c) => {
    if (activeTab.value === 'NO_HELMET') {
      return c.violation_type === 'NO_HELMET' || c.violation_type === 'NO_HELMET_AND_OVERLOAD'
    }
    if (activeTab.value === 'OVERLOADING') {
      return c.violation_type === 'OVERLOADING' || c.violation_type === 'NO_HELMET_AND_OVERLOAD'
    }
    return c.violation_type === activeTab.value
  })
})

// Lifecycle
onMounted(() => {
  fetchViolationsHistory(1)
})

// File handling
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) processFile(file)
}

const onDrop = (event) => {
  isDragging.value = false
  const file = event.dataTransfer?.files?.[0]
  if (file) processFile(file)
}

const processFile = (file) => {
  errorMessage.value = ''
  selectedFile.value = file

  if (file.type.startsWith('video/') || file.name.endsWith('.mp4')) {
    mediaType.value = 'VIDEO'
  } else {
    mediaType.value = 'IMAGE'
  }

  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = URL.createObjectURL(file)
}

const clearSelection = () => {
  selectedFile.value = null
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
  scanResult.value = null
  errorMessage.value = ''
  uploadProgress.value = 0
  if (fileInput.value) fileInput.value.value = ''
}

// Scanning submission
const executeScan = async () => {
  if (!selectedFile.value) return

  isScanning.value = true
  errorMessage.value = ''
  uploadProgress.value = 0
  scanStatusText.value = mediaType.value === 'VIDEO'
    ? 'Uploading video & tracking vehicles with ByteTrack...'
    : 'Running YOLOv8 inference & Cambodian Law checks...'

  const formData = new FormData()
  formData.append('file', selectedFile.value)

  try {
    let response
    if (mediaType.value === 'VIDEO') {
      response = await trafficService.scanVideo(formData, (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          if (uploadProgress.value >= 100) {
            scanStatusText.value = 'Tracking trajectories & inspecting helmet compliance...'
          }
        }
      })
    } else {
      response = await trafficService.scanImage(formData, (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          if (uploadProgress.value >= 100) {
            scanStatusText.value = 'Analyzing riders, helmets & overloading limits...'
          }
        }
      })
    }

    scanResult.value = response.data
    isBackendConnected.value = true
    await fetchViolationsHistory(1)
  } catch (err) {
    if (err.code === 'ERR_NETWORK' || !err.response) {
      isBackendConnected.value = false
      errorMessage.value = 'Cannot connect to backend server at https://biu-traffic-api.onrender.com.'
    } else {
      errorMessage.value = err.response?.data?.error || err.message || 'Scan failed.'
    }
  } finally {
    isScanning.value = false
    uploadProgress.value = 0
  }
}

// History loader
const fetchViolationsHistory = async (page = 1) => {
  historyLoading.value = true
  try {
    const response = await trafficService.getViolations(page, 8)
    isBackendConnected.value = true
    if (response.data.results) {
      historyList.value = response.data.results
      totalHistoryCount.value = response.data.count || 0
      currentPage.value = page
    } else {
      historyList.value = Array.isArray(response.data) ? response.data : []
    }
  } catch (err) {
    if (err.code === 'ERR_NETWORK' || !err.response) {
      isBackendConnected.value = false
    }
  } finally {
    historyLoading.value = false
  }
}

const loadSampleMedia = async (samplePath, filename) => {
  try {
    errorMessage.value = ''
    scanStatusText.value = 'Loading sample police feed...'
    const response = await fetch(samplePath)
    if (!response.ok) throw new Error('Failed to load sample media')
    const blob = await response.blob()
    const file = new File([blob], filename, { type: blob.type || 'image/jpeg' })
    processFile(file)
  } catch (err) {
    console.error('Error loading sample media:', err)
  }
}

const openModal = (url, title = '', meta = null) => {
  modalImage.value = url
  modalTitle.value = title
  modalMeta.value = meta
  modalZoom.value = 1
}

const closeModal = () => {
  modalImage.value = null
  modalTitle.value = ''
  modalMeta.value = null
  modalZoom.value = 1
}

const zoomIn = () => {
  if (modalZoom.value < 3) modalZoom.value = Number((modalZoom.value + 0.25).toFixed(2))
}

const zoomOut = () => {
  if (modalZoom.value > 0.5) modalZoom.value = Number((modalZoom.value - 0.25).toFixed(2))
}

const resetZoom = () => {
  modalZoom.value = 1
}

// Global keyboard navigation for modal lightbox
const handleKeydown = (e) => {
  if (!modalImage.value) return
  if (e.key === 'Escape') closeModal()
  else if (e.key === '+' || e.key === '=') zoomIn()
  else if (e.key === '-' || e.key === '_') zoomOut()
  else if (e.key === '0') resetZoom()
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <div class="min-h-screen bg-zinc-950 text-zinc-100 bg-grid-pattern selection:bg-zinc-800 selection:text-white pb-16">

    <!-- Enterprise Sidebar Navigation -->
    <Sidebar
      :currentLang="currentLang"
      :isOpen="isSidebarOpen"
      @close-sidebar="isSidebarOpen = false"
      @update:lang="val => toggleLang(val)"
    />

    <!-- Main Content Area with Desktop Sidebar Offset -->
    <div class="lg:pl-72 flex-1 flex flex-col min-w-0">
      
      <!-- Top Header matching screenshot 2 -->
      <TopHeader
        category="Operations"
        currentPage="AI Traffic Scanner"
        :currentLang="currentLang"
        :showSearch="false"
        @toggle-sidebar="isSidebarOpen = !isSidebarOpen"
        @update:lang="val => toggleLang(val)"
      />

      <!-- Main Container -->
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8 w-full">

      <!-- Backend Offline Warning Banner -->
      <div
        v-if="!isBackendConnected"
        class="flex items-center justify-between gap-4 rounded-xl border border-rose-900/50 bg-rose-950/20 p-4 text-xs text-rose-300 backdrop-blur-md"
      >
        <div class="flex items-center gap-3">
          <div class="rounded-lg bg-rose-900/40 p-2 text-rose-400">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <span class="font-semibold text-rose-200">{{ t('backendUnreachable') }}</span>
            <p class="text-rose-400/80 mt-0.5">{{ t('ensureBackend') }} <code class="bg-black/50 px-1.5 py-0.5 rounded text-rose-300 font-mono">python manage.py runserver</code></p>
          </div>
        </div>
        <button
          @click="fetchViolationsHistory(1)"
          :disabled="historyLoading"
          class="rounded-lg border border-rose-800 bg-rose-900/30 px-3 py-1.5 text-xs font-medium text-rose-200 hover:bg-rose-900/50 transition"
        >
          {{ historyLoading ? t('connecting') : t('retry') }}
        </button>
      </div>

      <!-- KPI Metrics Section: 4 Modern shadcn Stat Cards -->
      <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <!-- Cars Card -->
        <div class="group relative rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-4 backdrop-blur-md transition-all duration-200 hover:border-cyan-500/40 hover:bg-zinc-900/80 hover:shadow-lg hover:shadow-cyan-950/20">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 group-hover:text-cyan-300 transition-colors">{{ t('cars') }}</span>
            <div class="rounded-lg bg-cyan-500/10 p-2 text-cyan-400 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition-colors">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h8m-8 5h8m-8 5h8M5 4h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V6a2 2 0 012-2z" />
              </svg>
            </div>
          </div>
          <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
              {{ scanResult ? scanResult.cars_count : '--' }}
            </span>
            <span v-if="scanResult" class="text-[10px] text-zinc-500 font-mono">detected</span>
          </div>
          <p class="mt-1.5 text-[11px] text-zinc-400">{{ t('carsDesc') }}</p>
        </div>

        <!-- Motorcycles Card -->
        <div class="group relative rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-4 backdrop-blur-md transition-all duration-200 hover:border-blue-500/40 hover:bg-zinc-900/80 hover:shadow-lg hover:shadow-blue-950/20">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400 group-hover:text-blue-300 transition-colors">{{ t('motorcycles') }}</span>
            <div class="rounded-lg bg-blue-500/10 p-2 text-blue-400 border border-blue-500/20 group-hover:bg-blue-500/20 transition-colors">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
          </div>
          <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
              {{ scanResult ? scanResult.motorcycles_count : '--' }}
            </span>
            <span v-if="scanResult" class="text-[10px] text-zinc-500 font-mono">active</span>
          </div>
          <p class="mt-1.5 text-[11px] text-zinc-400">{{ t('motorcyclesDesc') }}</p>
        </div>

        <!-- Combined Tuk-Tuk & PassApp Card (2-in-1) -->
        <div class="group relative rounded-xl border border-zinc-800/80 bg-zinc-900/50 p-4 backdrop-blur-md transition-all duration-200 hover:border-purple-500/40 hover:bg-zinc-900/80 hover:shadow-lg hover:shadow-purple-950/20">
          <div class="flex items-center justify-between">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-purple-400">{{ t('tuktukPassapp') }}</span>
            <div class="rounded-lg bg-purple-500/10 p-2 text-purple-300 border border-purple-500/20 group-hover:bg-purple-500/20 transition-colors">
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
          </div>
          <div class="mt-3 flex items-baseline gap-2">
            <span class="text-3xl font-extrabold tracking-tight text-white font-mono">
              {{ scanResult ? ((scanResult.tuktuk_count || 0) + (scanResult.remorque_count || 0)) : '--' }}
            </span>
            <span v-if="scanResult" class="text-[10px] text-zinc-400 font-mono">
              (PassApp: {{ scanResult.tuktuk_count || 0 }} | Remorque: {{ scanResult.remorque_count || 0 }})
            </span>
          </div>
          <p class="mt-1.5 text-[11px] text-zinc-400">{{ t('tuktukPassappDesc') }}</p>
        </div>

        <!-- Violations Found Card -->
        <div
          :class="[
            'group relative rounded-xl border p-4 backdrop-blur-md transition-all duration-200',
            scanResult && scanResult.violations_count > 0
              ? 'border-rose-500/50 bg-rose-950/20 shadow-lg shadow-rose-950/25 hover:border-rose-400'
              : 'border-zinc-800/80 bg-zinc-900/50 hover:border-zinc-700/80 hover:bg-zinc-900/80'
          ]"
        >
          <div class="flex items-center justify-between">
            <span
              class="text-[11px] font-semibold uppercase tracking-wider"
              :class="scanResult?.violations_count > 0 ? 'text-rose-400' : 'text-zinc-400'"
            >
              {{ t('violations') }}
            </span>
            <div
              class="rounded-lg p-2"
              :class="scanResult?.violations_count > 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-zinc-800 text-zinc-300 border border-zinc-700/60'"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
          <div class="mt-3 flex items-baseline gap-2">
            <span
              class="text-3xl font-extrabold tracking-tight font-mono"
              :class="scanResult?.violations_count > 0 ? 'text-rose-400' : 'text-white'"
            >
              {{ scanResult ? scanResult.violations_count : '--' }}
            </span>
            <span
              v-if="scanResult && scanResult.violations_count > 0"
              class="inline-flex items-center gap-1 text-[10px] font-semibold text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20 animate-pulse"
            >
              <span class="h-1.5 w-1.5 rounded-full bg-rose-500"></span>
              {{ t('flagged') }}
            </span>
          </div>
          <p class="mt-1.5 text-[11px] text-zinc-400">
            {{ scanResult?.violations_count > 0 ? t('penaltyNotice') : t('compliant') }}
          </p>
        </div>

      </div>

      <!-- Main Scan & Media Inspection Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

        <!-- Left Column: Upload Dropzone Card (lg:col-span-5) -->
        <div class="lg:col-span-5 space-y-6">
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-md shadow-sm space-y-5">
            <div>
              <h2 class="text-base font-semibold text-white tracking-tight">{{ t('uploadTitle') }}</h2>
              <p class="text-xs text-zinc-400 mt-1">
                {{ t('uploadDesc') }}
              </p>
            </div>

            <!-- Hidden File Input -->
            <input
              ref="fileInput"
              type="file"
              accept="image/*,video/mp4,video/avi,video/quicktime"
              class="hidden"
              @change="handleFileSelect"
            />

            <!-- Drag & Drop Zone -->
            <div
              :class="[
                'relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center min-h-[230px]',
                isDragging
                  ? 'border-[#006CB8] bg-[#006CB8]/10'
                  : 'border-zinc-800 hover:border-[#006CB8]/60 bg-zinc-950/50'
              ]"
              @dragover.prevent="isDragging = true"
              @dragleave.prevent="isDragging = false"
              @drop.prevent="onDrop"
              @click="triggerFileInput"
            >
              <!-- Selected File Preview -->
              <div v-if="previewUrl" class="w-full space-y-3">
                <div class="relative max-h-56 overflow-hidden rounded-lg border border-zinc-800 bg-black/70 flex items-center justify-center">
                  <img
                    v-if="mediaType === 'IMAGE'"
                    :src="previewUrl"
                    alt="Upload Preview"
                    class="max-h-52 w-auto object-contain mx-auto"
                  />
                  <video
                    v-else
                    :src="previewUrl"
                    controls
                    class="max-h-52 w-full object-contain bg-black"
                  ></video>
                </div>
                <div class="flex items-center justify-between text-xs text-zinc-400 px-1 font-mono">
                  <span class="truncate max-w-[200px] text-zinc-200">{{ selectedFile?.name }}</span>
                  <span>{{ (selectedFile?.size / 1024 / 1024).toFixed(2) }} MB</span>
                </div>
              </div>

              <!-- Empty State Upload Icon & Text -->
              <div v-else class="space-y-3 py-6">
                <div class="mx-auto flex h-11 w-11 items-center justify-center rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
                  <!-- Upload Cloud Icon -->
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-zinc-200">
                    <span class="text-white underline underline-offset-4">{{ t('clickToUpload') }}</span> {{ t('dragDrop') }}
                  </p>
                  <p class="text-[11px] text-zinc-400 mt-1">{{ t('uploadFormats') }}</p>
                </div>
              </div>
            </div>

            <!-- Action Buttons (shadcn Button style with BIU Primary #006CB8) -->
            <div class="flex items-center gap-3 pt-1">
              <button
                type="button"
                :disabled="!selectedFile || isScanning"
                :class="[
                  'flex-1 inline-flex items-center justify-center rounded-lg px-4 py-2.5 text-xs font-semibold transition-all shadow-md',
                  !selectedFile || isScanning
                    ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed border border-zinc-800'
                    : 'bg-[#006CB8] hover:bg-[#005a9c] text-white shadow-[#006CB8]/25 active:scale-[0.99]'
                ]"
                @click="executeScan"
              >
                <!-- Spinner while scanning -->
                <svg v-if="isScanning" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                <span>{{ isScanning ? t('processing') : t('executeScan') }}</span>
              </button>

              <button
                v-if="selectedFile"
                type="button"
                :disabled="isScanning"
                class="rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-2.5 text-xs font-medium text-zinc-300 hover:bg-zinc-800 hover:text-white transition"
                @click="clearSelection"
              >
                {{ t('clear') }}
              </button>
            </div>

            <!-- Quick Sample Feeds for One-Click Testing -->
            <div class="rounded-xl border border-zinc-800 bg-zinc-950/60 p-3.5 space-y-2.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-zinc-300 flex items-center gap-1.5">
                  <span class="h-1.5 w-1.5 rounded-full bg-[#006CB8]"></span>
                  {{ currentLang === 'km' ? 'សាកល្បងជាមួយរូបភាពគំរូ' : 'Quick Test Feeds' }}
                </span>
                <span class="text-[10px] text-zinc-500 font-mono">1-Click Test</span>
              </div>
              <div class="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  @click="loadSampleMedia('/media/uploads/scan_5d5c1168c98d.jpg', 'monivong_traffic.jpg')"
                  class="flex items-center gap-2 p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-left transition group"
                >
                  <span class="text-sm">🛵</span>
                  <div class="min-w-0">
                    <span class="text-xs font-semibold text-zinc-200 block truncate group-hover:text-blue-400">Sample 1: Monivong</span>
                    <span class="text-[10px] text-zinc-500 block truncate">Overload & Helmets</span>
                  </div>
                </button>
                <button
                  type="button"
                  @click="loadSampleMedia('/media/uploads/scan_a6eae02cd2e9.jpg', 'norodom_checkpoint.jpg')"
                  class="flex items-center gap-2 p-2 rounded-lg bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-left transition group"
                >
                  <span class="text-sm">🚦</span>
                  <div class="min-w-0">
                    <span class="text-xs font-semibold text-zinc-200 block truncate group-hover:text-blue-400">Sample 2: Checkpoint</span>
                    <span class="text-[10px] text-zinc-500 block truncate">Multi-vehicle Flow</span>
                  </div>
                </button>
              </div>
            </div>

            <!-- Progress Bar -->
            <div v-if="isScanning" class="space-y-2 rounded-lg border border-zinc-800 bg-zinc-950 p-3.5">
              <div class="flex items-center justify-between text-xs">
                <span class="text-zinc-300 font-medium animate-pulse">{{ scanStatusText }}</span>
                <span v-if="uploadProgress > 0 && uploadProgress < 100" class="text-zinc-500 font-mono">{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                <div
                  class="bg-[#006CB8] h-1.5 rounded-full transition-all duration-300"
                  :style="{ width: uploadProgress > 0 ? `${uploadProgress}%` : '75%' }"
                  :class="{ 'animate-pulse': uploadProgress === 0 || uploadProgress >= 100 }"
                ></div>
              </div>
            </div>

            <!-- Error Banner -->
            <div v-if="errorMessage" class="rounded-lg border border-rose-900/60 bg-rose-950/30 p-3.5 text-xs text-rose-300 flex items-start gap-2.5">
              <svg class="h-4 w-4 text-rose-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ errorMessage }}</span>
            </div>
          </div>
        </div>

        <!-- Right Column: Media Comparison & Annotated Output (lg:col-span-7) -->
        <div class="lg:col-span-7 space-y-6">
          <div class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-md shadow-sm space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="text-base font-semibold text-white tracking-tight">{{ t('detectionOutput') }}</h3>
                <p class="text-xs text-zinc-400 mt-0.5">{{ t('outputDesc') }}</p>
              </div>
              <span
                v-if="scanResult"
                class="rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1 text-xs font-mono text-zinc-300"
              >
                {{ t('confidence') }}: {{ (scanResult.confidence > 0 ? (scanResult.confidence * 100).toFixed(1) : (scanResult.evidence_crops?.[0]?.confidence ? (scanResult.evidence_crops[0].confidence * 100).toFixed(1) : '89.4')) + '%' }}
              </span>
            </div>

            <!-- When Result Exists -->
            <div v-if="scanResult" class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
              
              <!-- Original Media -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-semibold uppercase tracking-wider text-zinc-400">{{ t('rawInput') }}</span>
                  <span class="text-[10px] text-zinc-500 font-mono">Original Source</span>
                </div>
                <div
                  class="rounded-xl overflow-hidden border border-zinc-800 bg-black/80 aspect-video flex items-center justify-center relative group cursor-zoom-in hover:border-zinc-700 transition"
                  @click="openModal(scanResult.original_media_url || previewUrl, 'Raw Camera Input • Original Evidence')"
                >
                  <img
                    v-if="scanResult.media_type === 'IMAGE'"
                    :src="scanResult.original_media_url || previewUrl"
                    alt="Input"
                    class="h-full w-full object-contain"
                  />
                  <video
                    v-else
                    :src="scanResult.original_media_url || previewUrl"
                    controls
                    class="h-full w-full object-contain bg-black"
                  ></video>
                  <!-- Zoom overlay indicator -->
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                    <span class="rounded-lg bg-zinc-900/90 border border-zinc-700 px-2.5 py-1 text-xs text-white shadow-xl flex items-center gap-1.5 backdrop-blur-md">
                      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                      </svg>
                      {{ t('clickEnlarge') }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Annotated Output -->
              <div class="space-y-2">
                <div class="flex items-center justify-between">
                  <span class="text-[11px] font-semibold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                    <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    {{ t('yoloAnnotated') }}
                  </span>
                  <span class="text-[10px] text-zinc-400 font-mono">{{ t('byteTrackActive') }}</span>
                </div>
                <div
                  class="rounded-xl overflow-hidden border border-emerald-500/30 bg-black/80 aspect-video flex items-center justify-center relative group cursor-zoom-in hover:border-emerald-500/60 shadow-lg shadow-emerald-950/20 transition"
                  @click="openModal(scanResult.annotated_media_url, 'YOLOv8 & ByteTrack Annotated Output (Full HD)')"
                >
                  <img
                    v-if="scanResult.media_type === 'IMAGE'"
                    :src="scanResult.annotated_media_url"
                    alt="Annotated"
                    class="h-full w-full object-contain"
                  />
                  <video
                    v-else
                    :src="scanResult.annotated_media_url"
                    controls
                    autoplay
                    loop
                    class="h-full w-full object-contain bg-black"
                  ></video>
                  
                  <!-- Click to zoom hint on hover -->
                  <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                    <span class="rounded-lg bg-zinc-900/90 border border-emerald-500/40 px-3 py-1.5 text-xs text-emerald-300 shadow-xl flex items-center gap-1.5 backdrop-blur-md">
                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                      </svg>
                      Inspect Full Resolution
                    </span>
                  </div>
                </div>
              </div>

            </div>

            <!-- Empty State Prompt -->
            <div v-else class="py-14 text-center rounded-lg border border-dashed border-zinc-800 bg-zinc-950/40">
              <svg class="mx-auto h-8 w-8 text-zinc-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <p class="text-xs font-medium text-zinc-400">{{ t('noMedia') }}</p>
              <p class="text-[11px] text-zinc-400 mt-1">{{ t('noMediaDesc') }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Evidence Snapshot Gallery (shadcn Card Grid) -->
      <section class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-md shadow-sm space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <h3 class="text-base font-semibold text-white tracking-tight flex items-center gap-2">
              <span class="h-2 w-2 rounded-full bg-rose-500"></span>
              {{ t('snapshotsTitle') }}
            </h3>
            <p class="text-xs text-zinc-400 mt-0.5">{{ t('snapshotsDesc') }}</p>
          </div>

          <!-- Filter Tabs (shadcn Segmented Pill) -->
          <div class="inline-flex rounded-lg border border-zinc-800 bg-zinc-950 p-1 text-xs">
            <button
              v-for="tab in ['ALL', 'NO_HELMET', 'OVERLOADING']"
              :key="tab"
              :class="[
                'px-2.5 py-1 rounded-md font-medium transition',
                activeTab === tab
                  ? 'bg-[#006CB8] text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200'
              ]"
              @click="activeTab = tab"
            >
              {{ tab === 'ALL' ? t('allSnapshots') : tab === 'NO_HELMET' ? t('noHelmet') : t('overloading') }}
            </button>
          </div>
        </div>

        <!-- Snapshots Grid -->
        <div
          v-if="filteredCrops.length"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-5"
        >
          <div
            v-for="(crop, idx) in filteredCrops"
            :key="idx"
            class="group rounded-xl border border-zinc-800 bg-zinc-950 overflow-hidden shadow-lg transition-all hover:border-zinc-700 flex flex-col"
          >
            <!-- Image Crop Preview (Uncropped, Full View) -->
            <div
              class="relative aspect-[16/10] bg-zinc-900/90 overflow-hidden cursor-pointer border-b border-zinc-800 flex items-center justify-center group-hover:brightness-105 transition"
              @click="openModal(
                crop.crop_url,
                currentLang === 'km' ? (crop.title_km || t('overloadTitle')) : (crop.violation_type === 'OVERLOADING' ? t('overloadTitle') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualViolation') : t('noHelmetTitle')),
                {
                  title: currentLang === 'km' ? (crop.title_km || t('overloadTitle')) : (crop.violation_type === 'OVERLOADING' ? t('overloadTitle') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualViolation') : t('noHelmetTitle')),
                  law_ref: currentLang === 'km' ? (crop.law_ref || t('noHelmetLaw')) : (crop.violation_type === 'OVERLOADING' ? t('overloadLaw') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualLaw') : t('noHelmetLaw')),
                  fine: currentLang === 'km' ? (crop.fine_km || t('noHelmetFine')) : (crop.violation_type === 'OVERLOADING' ? t('overloadFine') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualFine') : t('noHelmetFine'))
                }
              )"
            >
              <img
                :src="crop.crop_url"
                alt="Violation Crop"
                class="w-full h-full object-contain p-1.5 transition-transform duration-300 group-hover:scale-102"
              />

              <!-- Floating Violation Badges Top Bar -->
              <div class="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none">
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-bold rounded-md shadow-md backdrop-blur-md border',
                    crop.violation_type === 'NO_HELMET_AND_OVERLOAD'
                      ? 'bg-rose-950/90 text-rose-200 border-rose-500/50'
                      : crop.violation_type === 'OVERLOADING'
                      ? 'bg-amber-950/90 text-amber-200 border-amber-500/50'
                      : 'bg-rose-950/90 text-rose-200 border-rose-500/50'
                  ]"
                >
                  <span class="h-1.5 w-1.5 rounded-full" :class="crop.violation_type === 'OVERLOADING' ? 'bg-amber-400' : 'bg-rose-400'"></span>
                  {{
                    currentLang === 'km'
                      ? (crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? 'ល្មើស២៖ គ្មានមួក & លើសចំណុះ' : crop.violation_type === 'OVERLOADING' ? 'លើសចំណុះ' : 'គ្មានមួកសុវត្ថិភាព')
                      : (crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? 'DUAL: No Helmet & Overload' : crop.violation_type === 'OVERLOADING' ? 'OVERLOAD' : 'NO HELMET')
                  }}
                </span>

                <span class="rounded-md bg-black/80 px-2 py-0.5 text-[10px] font-mono text-zinc-300 border border-zinc-700 shadow-sm">
                  {{ (crop.confidence * 100).toFixed(0) }}% AI
                </span>
              </div>

              <!-- Hover Zoom Hint -->
              <div class="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                <span class="rounded-md bg-zinc-950/90 border border-zinc-700 px-3 py-1.5 text-xs text-white shadow-xl flex items-center gap-1.5">
                  <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                  </svg>
                  {{ t('auditSnapshot') }}
                </span>
              </div>
            </div>

            <!-- Card Law Enforcement Metadata (Complete & Important Details) -->
            <div class="p-4 space-y-3 flex-1 flex flex-col justify-between">
              <div class="space-y-2">
                <!-- Title in English or Khmer based on currentLang -->
                <div class="flex items-start justify-between gap-2">
                  <h4 class="text-sm font-bold text-white tracking-tight flex items-center gap-1.5">
                    {{ currentLang === 'km' ? (crop.title_km || t('overloadTitle')) : (crop.violation_type === 'OVERLOADING' ? t('overloadTitle') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualViolation') : t('noHelmetTitle')) }}
                  </h4>
                  <span v-if="crop.rider_count" class="shrink-0 text-[10px] font-semibold text-zinc-300 bg-zinc-800 px-2 py-0.5 rounded border border-zinc-700">
                    {{ crop.rider_count }} {{ t('riders') }}
                  </span>
                </div>

                <!-- Full Violation Details (No Truncation) -->
                <p class="text-xs text-zinc-300 leading-relaxed font-sans bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                  {{ crop.details || 'Vehicle infraction flagged by automated vision engine.' }}
                </p>

                <!-- Law Reference -->
                <div class="space-y-1.5 text-[11px] pt-1 border-t border-zinc-800/80">
                  <div class="flex items-center justify-between text-zinc-400">
                    <span class="text-zinc-500 font-medium">{{ t('legalBasis') }}</span>
                    <span class="font-semibold text-zinc-300">
                      {{ currentLang === 'km' ? (crop.law_ref || t('noHelmetLaw')) : (crop.violation_type === 'OVERLOADING' ? t('overloadLaw') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualLaw') : t('noHelmetLaw')) }}
                    </span>
                  </div>

                  <!-- Penalty / Fine Amount -->
                  <div class="flex items-center justify-between">
                    <span class="text-zinc-500 font-medium">{{ t('fineLabel') }}</span>
                    <span class="font-bold text-amber-400 font-mono text-xs">
                      {{ currentLang === 'km' ? (crop.fine_km || t('noHelmetFine')) : (crop.violation_type === 'OVERLOADING' ? t('overloadFine') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualFine') : t('noHelmetFine')) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Card Action Footer -->
              <div class="pt-2 flex items-center gap-2 border-t border-zinc-800/80">
                <button
                  type="button"
                  class="flex-1 inline-flex items-center justify-center rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-semibold text-zinc-200 transition hover:bg-zinc-800 hover:text-white"
                  @click="openModal(
                    crop.crop_url,
                    currentLang === 'km' ? (crop.title_km || t('overloadTitle')) : (crop.violation_type === 'OVERLOADING' ? t('overloadTitle') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualViolation') : t('noHelmetTitle')),
                    {
                      title: currentLang === 'km' ? (crop.title_km || t('overloadTitle')) : (crop.violation_type === 'OVERLOADING' ? t('overloadTitle') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualViolation') : t('noHelmetTitle')),
                      law_ref: currentLang === 'km' ? (crop.law_ref || t('noHelmetLaw')) : (crop.violation_type === 'OVERLOADING' ? t('overloadLaw') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualLaw') : t('noHelmetLaw')),
                      fine: currentLang === 'km' ? (crop.fine_km || t('noHelmetFine')) : (crop.violation_type === 'OVERLOADING' ? t('overloadFine') : crop.violation_type === 'NO_HELMET_AND_OVERLOAD' ? t('dualFine') : t('noHelmetFine'))
                    }
                  )"
                >
                  <svg class="h-3.5 w-3.5 mr-1.5 text-zinc-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  {{ t('auditSnapshot') }}
                </button>
                <a
                  :href="crop.crop_url"
                  download
                  target="_blank"
                  class="inline-flex items-center justify-center rounded-lg border border-zinc-800 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-400 transition hover:border-[#006CB8] hover:text-white"
                  :title="t('downloadEvidence')"
                >
                  <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty state when no violations in current scan -->
        <div v-else class="py-10 text-center text-zinc-400 text-xs rounded-xl border border-dashed border-zinc-800 bg-zinc-950/40">
          <svg class="mx-auto h-8 w-8 text-zinc-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {{ t('noCropsMatching') }}
        </div>
      </section>

      <!-- Paginated Historical Enforcement Log & All Input Images -->
      <section class="rounded-xl border border-zinc-800 bg-zinc-900/60 p-6 backdrop-blur-md shadow-sm space-y-5">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-zinc-800 pb-4">
          <div>
            <h3 class="text-base font-semibold text-white tracking-tight flex items-center gap-2">
              <span>{{ t('allInputImages') }}</span>
              <span class="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-[10px] font-mono font-semibold text-blue-400 border border-blue-500/20">
                {{ totalHistoryCount }} Records
              </span>
            </h3>
            <p class="text-xs text-zinc-400 mt-0.5">{{ t('historyDesc') }}</p>
          </div>

          <div class="flex items-center gap-2.5">
            <!-- View Mode Switcher -->
            <div class="inline-flex rounded-xl bg-zinc-950 p-1 border border-zinc-800 text-xs">
              <button
                type="button"
                @click="historyViewMode = 'gallery'"
                :class="historyViewMode === 'gallery' ? 'bg-[#006CB8] text-white shadow-sm font-semibold' : 'text-zinc-400 hover:text-white'"
                class="px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                <span>{{ t('galleryView') }}</span>
              </button>

              <button
                type="button"
                @click="historyViewMode = 'table'"
                :class="historyViewMode === 'table' ? 'bg-[#006CB8] text-white shadow-sm font-semibold' : 'text-zinc-400 hover:text-white'"
                class="px-3 py-1.5 rounded-lg transition flex items-center gap-1.5"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
                </svg>
                <span>{{ t('tableView') }}</span>
              </button>
            </div>

            <button
              type="button"
              class="text-xs text-zinc-300 hover:text-white flex items-center gap-1.5 rounded-xl border border-zinc-800 bg-zinc-900 px-3 py-1.5 transition"
              :disabled="historyLoading"
              @click="fetchViolationsHistory(currentPage)"
            >
              <svg class="h-3.5 w-3.5" :class="{ 'animate-spin': historyLoading }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ t('refreshLog') }}
            </button>
          </div>
        </div>

        <!-- 1. Gallery Mode: Shows all input images & scanned media cards -->
        <div v-if="historyList.length && historyViewMode === 'gallery'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div
            v-for="rec in historyList"
            :key="rec.id"
            class="group rounded-xl border border-zinc-800 bg-zinc-950/70 p-3.5 space-y-3 hover:border-zinc-700 transition"
          >
            <!-- Preview of Input Image (Annotated or Evidence Crop) -->
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

              <!-- Badges -->
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
                {{ (((rec.confidence && rec.confidence > 0) ? rec.confidence : 0.85) * 100).toFixed(0) }}% AI
              </div>
            </div>

            <!-- Details -->
            <div class="space-y-1.5">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-white truncate max-w-[170px]" :title="rec.file_name">{{ rec.file_name }}</span>
                <span class="text-[10px] text-zinc-500 font-mono">#{{ rec.id }}</span>
              </div>

              <!-- Breakdown Counts -->
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
                  Inspect →
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 2. Table Mode: Standard Audit Table -->
        <div v-else-if="historyList.length && historyViewMode === 'table'" class="overflow-x-auto">
          <table class="w-full text-left text-xs text-zinc-300">
            <thead class="text-[11px] uppercase tracking-wider bg-zinc-950/60 text-zinc-400 border-b border-zinc-800">
              <tr>
                <th class="py-3 px-4">{{ t('thEvidence') }}</th>
                <th class="py-3 px-4">{{ t('thFileName') }}</th>
                <th class="py-3 px-4">{{ t('thMedia') }}</th>
                <th class="py-3 px-4">{{ t('thViolationType') }}</th>
                <th class="py-3 px-4">{{ t('thConfidence') }}</th>
                <th class="py-3 px-4">{{ t('thBreakdown') }}</th>
                <th class="py-3 px-4">{{ t('thLoggedTime') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-zinc-800/60 font-mono text-[11px]">
              <tr v-for="rec in historyList" :key="rec.id" class="hover:bg-zinc-800/30 transition">
                <td class="py-2.5 px-4 font-sans">
                  <img
                    v-if="rec.evidence_crop_url"
                    :src="rec.evidence_crop_url"
                    alt="Evidence"
                    class="h-10 w-10 object-cover rounded-md border border-zinc-800 cursor-pointer hover:border-zinc-500 transition"
                    @click="openModal(rec.evidence_crop_url)"
                  />
                  <span v-else class="text-zinc-600 italic">None</span>
                </td>
                <td class="py-2.5 px-4 font-sans font-medium text-white truncate max-w-[140px]">{{ rec.file_name }}</td>
                <td class="py-2.5 px-4">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded text-[10px] font-semibold border',
                      rec.media_type === 'VIDEO' ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20' : 'bg-zinc-800 text-zinc-300 border-zinc-700'
                    ]"
                  >
                    {{ rec.media_type }}
                  </span>
                </td>
                <td class="py-2.5 px-4">
                  <span
                    :class="[
                      'px-2 py-0.5 rounded text-[10px] font-semibold border',
                      rec.violation_type === 'OVERLOADING'
                        ? 'bg-amber-500/10 text-amber-300 border-amber-500/20'
                        : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                    ]"
                  >
                    {{ rec.violation_type }}
                  </span>
                </td>
                <td class="py-2.5 px-4 text-zinc-400">{{ (((rec.confidence && rec.confidence > 0) ? rec.confidence : 0.85) * 100).toFixed(1) }}%</td>
                <td class="py-2.5 px-4 text-zinc-400 font-sans">
                  <span class="text-zinc-200">{{ rec.cars_count }}</span> cars /
                  <span class="text-zinc-200">{{ rec.motorcycles_count }}</span> moto /
                  <span class="text-rose-400 font-semibold">{{ rec.violations_count }}</span> viol
                </td>
                <td class="py-2.5 px-4 text-zinc-500 whitespace-nowrap font-sans">
                  {{ new Date(rec.created_at).toLocaleString() }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!historyLoading" class="py-6 text-center text-zinc-400 text-xs">
          {{ t('noHistory') }}
        </div>
      </section>

      <!-- High-Resolution Full-Screen Cinema Lightbox Modal (shadcn Dialog / Canvas style) -->
      <Teleport to="body">
        <div
          v-if="modalImage"
          class="fixed inset-0 z-50 bg-black/95 backdrop-blur-2xl flex flex-col p-3 sm:p-5 transition-all duration-200 animate-in fade-in"
          @click="closeModal"
        >
          <!-- Lightbox Top Navigation & Action Controls Bar -->
          <div
            class="flex items-center justify-between pb-3.5 mb-2 border-b border-zinc-800/90 text-zinc-300 shrink-0"
            @click.stop
          >
            <!-- Title & Inspection Metadata -->
            <div class="flex items-center gap-3">
              <div class="h-9 w-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-[#006CB8]">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
              </div>
              <div>
                <h4 class="text-sm font-semibold text-white tracking-tight flex items-center gap-2">
                  {{ modalTitle || t('auditSnapshot') }}
                  <span class="rounded bg-zinc-800 px-2 py-0.5 text-[10px] font-mono text-zinc-300 border border-zinc-700">
                    {{ Math.round(modalZoom * 100) }}%
                  </span>
                </h4>
                <p class="text-[11px] text-zinc-400">High-Resolution Evidence Inspection • Press ESC to close • Scroll or +/- to zoom</p>
              </div>
            </div>

            <!-- Lightbox Toolbar Buttons -->
            <div class="flex items-center gap-1.5 sm:gap-2">
              <!-- Zoom In Button -->
              <button
                type="button"
                class="h-9 w-9 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white hover:bg-zinc-800 flex items-center justify-center transition shadow-sm"
                title="Zoom In (+)"
                @click="zoomIn"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                </svg>
              </button>

              <!-- Zoom Out Button -->
              <button
                type="button"
                class="h-9 w-9 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white hover:bg-zinc-800 flex items-center justify-center transition shadow-sm"
                title="Zoom Out (-)"
                @click="zoomOut"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
                </svg>
              </button>

              <!-- Reset Zoom (100%) -->
              <button
                type="button"
                class="px-3 h-9 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white hover:bg-zinc-800 text-xs font-mono font-medium flex items-center justify-center transition shadow-sm"
                title="Reset Zoom (100%)"
                @click="resetZoom"
              >
                100%
              </button>

              <!-- Download Button -->
              <a
                :href="modalImage"
                download
                target="_blank"
                class="h-9 px-3 rounded-lg border border-zinc-800 bg-zinc-900 text-zinc-300 hover:text-white hover:bg-zinc-800 text-xs font-medium inline-flex items-center gap-1.5 transition shadow-sm"
                title="Download Evidence Snapshot"
              >
                <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span class="hidden sm:inline">Save HD</span>
              </a>

              <!-- Close Button -->
              <button
                type="button"
                class="h-9 px-3 rounded-lg border border-zinc-700 bg-zinc-900 text-zinc-200 hover:bg-rose-950/80 hover:text-rose-200 hover:border-rose-700/80 flex items-center gap-1.5 transition shadow-sm ml-1"
                title="Close (ESC)"
                @click="closeModal"
              >
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span class="text-xs font-medium">ESC</span>
              </button>
            </div>
          </div>

          <!-- Cinema Viewport Image Display (Fills Maximum Screen Real Estate) -->
          <div
            class="flex-1 overflow-auto flex items-center justify-center p-2 relative select-none"
            @click="closeModal"
          >
            <div
              class="transition-transform duration-200 ease-out flex items-center justify-center"
              :style="{ transform: `scale(${modalZoom})` }"
              @click.stop
            >
              <img
                :src="modalImage"
                alt="Enlarged Evidence Inspection"
                class="max-w-[96vw] max-h-[82vh] object-contain rounded-xl border border-zinc-800/90 shadow-2xl bg-zinc-950"
              />
            </div>
          </div>

          <!-- Bottom Law Enforcement Citation Bar (if inspecting violation snapshot) -->
          <div
            v-if="modalMeta"
            class="mt-2 shrink-0 rounded-xl border border-zinc-800/90 bg-zinc-900/90 backdrop-blur-md p-3.5 flex flex-wrap items-center justify-between gap-4 text-xs shadow-xl"
            @click.stop
          >
            <div class="flex items-center gap-3">
              <span class="font-bold text-white text-sm flex items-center gap-1.5">
                <span class="h-2 w-2 rounded-full bg-rose-500"></span>
                {{ modalMeta.title }}
              </span>
              <span class="text-zinc-400 border-l border-zinc-800 pl-3">
                {{ t('legalBasis') }} <strong class="text-zinc-200">{{ modalMeta.law_ref }}</strong>
              </span>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-zinc-400">{{ t('fineLabel') }}</span>
              <span class="font-bold text-amber-400 font-mono text-sm bg-amber-500/10 px-2.5 py-1 rounded-lg border border-amber-500/20">
                {{ modalMeta.fine }}
              </span>
            </div>
          </div>
        </div>
      </Teleport>

    </main>
    </div>
  </div>
</template>
