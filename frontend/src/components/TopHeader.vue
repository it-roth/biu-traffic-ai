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
  <header class="sticky top-0 z-30 flex items-center justify-between border-b border-border/80 bg-background/80 px-4 sm:px-6 py-3 backdrop-blur-xl">
    
    <!-- Left: Sidebar Toggle & Breadcrumbs -->
    <div class="flex items-center gap-3 min-w-0">
      <!-- Toggle button for mobile & desktop collapse -->
      <button
        type="button"
        @click="emit('toggle-sidebar')"
        class="inline-flex items-center justify-center rounded-md border border-input bg-background/50 h-9 w-9 text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors flex-shrink-0"
        title="Toggle Navigation Sidebar"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
        </svg>
      </button>

      <!-- Breadcrumbs in Shadcn breadcrumb style -->
      <nav class="flex items-center gap-1.5 text-xs sm:text-sm font-medium min-w-0 text-muted-foreground" aria-label="Breadcrumb">
        <span class="truncate hover:text-foreground transition-colors cursor-default">{{ category }}</span>
        <svg class="h-3.5 w-3.5 text-muted-foreground/60 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
        <span class="text-foreground font-semibold truncate">{{ currentPage }}</span>
      </nav>
    </div>

    <!-- Right: Search, Language Switcher, and Status -->
    <div class="flex items-center gap-2 sm:gap-3 flex-shrink-0">
      
      <!-- Quick Search Bar (Shadcn Input style) -->
      <div v-if="showSearch" class="hidden md:flex items-center relative">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground">
          <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          :value="searchQuery"
          @input="emit('search', $event.target.value)"
          placeholder="Search records... ⌘K"
          class="flex h-9 w-48 lg:w-64 rounded-md border border-input bg-background/50 pl-8 pr-3 py-1 text-xs text-foreground shadow-sm transition-all placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring focus-visible:w-72 font-mono"
        />
      </div>

      <!-- Language Switcher (Shadcn Segmented Control / Tabs) -->
      <div class="inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground border border-border/60">
        <span class="text-[11px] font-semibold px-1.5 text-muted-foreground">文A</span>
        <button
          type="button"
          @click="toggleLang('en')"
          :class="lang === 'en' ? 'bg-background text-foreground shadow-sm font-semibold' : 'hover:text-foreground'"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md px-2.5 py-1 text-xs font-medium ring-offset-background transition-all"
        >
          <span>EN</span>
        </button>
        <button
          type="button"
          @click="toggleLang('km')"
          :class="lang === 'km' ? 'bg-background text-foreground shadow-sm font-semibold' : 'hover:text-foreground'"
          class="inline-flex items-center justify-center whitespace-nowrap rounded-md px-2.5 py-1 text-xs font-medium ring-offset-background transition-all"
        >
          <span>ខ្មែរ</span>
        </button>
      </div>

      <!-- Live Online Status Indicator (Shadcn Badge) -->
      <div class="hidden sm:inline-flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-2.5 py-1 text-[11px] font-medium text-emerald-400">
        <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
        <span class="font-mono">Sub-Decree 39</span>
      </div>

    </div>

  </header>
</template>
