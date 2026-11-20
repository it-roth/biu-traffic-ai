<script setup>
import { computed } from 'vue'

const props = defineProps({
  category: {
    type: String,
    default: 'Operations'
  },
  currentPage: {
    type: String,
    default: 'Dashboard'
  },
  currentLang: {
    type: String,
    default: 'en'
  },
  searchQuery: {
    type: String,
    default: ''
  },
  showSearch: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['toggle-sidebar', 'update:lang', 'search'])

const lang = computed(() => props.currentLang || localStorage.getItem('biu_lang') || 'en')

const toggleLang = (newLang) => {
  localStorage.setItem('biu_lang', newLang)
  emit('update:lang', newLang)
}
</script>

<template>
  <header class="sticky top-0 z-30 flex items-center justify-between border-b border-zinc-800/80 bg-[#07090e]/95 px-4 sm:px-6 py-3.5 backdrop-blur-xl">
    
    <!-- Left: Sidebar Toggle & Breadcrumbs -->
    <div class="flex items-center gap-3 min-w-0">
      <!-- Toggle button for mobile & desktop collapse -->
      <button
        type="button"
        @click="emit('toggle-sidebar')"
        class="p-2 rounded-xl border border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-white transition flex-shrink-0"
        title="Toggle Navigation Sidebar"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
        </svg>
      </button>

      <!-- Breadcrumbs (Matching User Screenshot 2) -->
      <nav class="flex items-center gap-1.5 text-xs sm:text-sm font-medium min-w-0" aria-label="Breadcrumb">
        <span class="text-zinc-400 truncate">{{ category }}</span>
        <span class="text-zinc-600">/</span>
        <span class="text-white font-semibold truncate">{{ currentPage }}</span>
      </nav>
    </div>

    <!-- Right: Search, Language Switcher, and Status -->
    <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
      
      <!-- Quick Search Bar (Matching User Screenshot 2) -->
      <div v-if="showSearch" class="hidden md:flex items-center relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-500">
          <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          :value="searchQuery"
          @input="emit('search', $event.target.value)"
          placeholder="Search or jump to...  ⌘ K"
          class="w-48 lg:w-64 pl-8 pr-3 py-1.5 rounded-xl border border-zinc-800 bg-zinc-950/80 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-[#006CB8] focus:w-72 transition-all font-mono"
        />
      </div>

      <!-- Language Switcher (Matching User Screenshot 2: 文A EN / ខ្មែរ) -->
      <div class="inline-flex rounded-xl bg-zinc-900/90 p-1 border border-zinc-800 text-xs items-center gap-1">
        <span class="text-zinc-400 pl-1.5 text-xs font-serif font-medium">文A</span>
        <button
          type="button"
          @click="toggleLang('en')"
          :class="lang === 'en' ? 'bg-[#006CB8] text-white font-bold shadow-sm' : 'text-zinc-400 hover:text-white'"
          class="px-2 py-0.5 rounded-lg transition text-xs flex items-center"
        >
          <span>EN</span>
        </button>
        <button
          type="button"
          @click="toggleLang('km')"
          :class="lang === 'km' ? 'bg-[#006CB8] text-white font-bold shadow-sm' : 'text-zinc-400 hover:text-white'"
          class="px-2 py-0.5 rounded-lg transition text-xs flex items-center"
        >
          <span>ខ្មែរ</span>
        </button>
      </div>

      <!-- Theme Mode Pill / Icon (Matching Screenshot 2: Sun Icon) -->
      <button
        type="button"
        class="p-2 rounded-xl border border-zinc-800 bg-zinc-900/80 hover:bg-zinc-800 text-zinc-400 hover:text-amber-300 transition"
        title="Dark / Light Mode"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="4" stroke-width="2" />
          <path stroke-linecap="round" stroke-width="2" d="M12 2v2m0 16v2m-7.07-14.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2m-14.93 7.07l1.41-1.41m11.32-11.32l1.41-1.41" />
        </svg>
      </button>

      <!-- Live Online Status Indicator -->
      <span class="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-2.5 py-1 text-[11px] font-semibold text-emerald-400 border border-emerald-500/20">
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        Online
      </span>

    </div>

  </header>
</template>
