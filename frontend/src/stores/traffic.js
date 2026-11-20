import { ref } from 'vue'
import { defineStore } from 'pinia'
import { trafficApi } from '../services/api'

export const useTrafficStore = defineStore('traffic', () => {
  const violations = ref([])
  const stats = ref({ cars: 0, bikes: 0, helmets_compliant: 0, violations: 0 })
  const error = ref('')

  async function refreshViolations() {
    try {
      const response = await trafficApi.violations()
      violations.value = response.data.results || response.data
      const statsResponse = await trafficApi.stats()
      stats.value = statsResponse.data
      error.value = ''
    } catch {
      error.value = 'Unable to load violation feed.'
    }
  }

  return { violations, error, stats, refreshViolations }
})
