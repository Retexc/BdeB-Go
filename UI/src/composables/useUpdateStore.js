// composables/useUpdateStore.js
import { reactive } from 'vue'

// Global reactive state shared between components
const updateState = reactive({
  available: false,
  checking: false,
  lastChecked: 'N/A',
  message: '',
  localHash: '',
  remoteHash: ''
})

export function useUpdateStore() {
  const checkForUpdates = async () => {
    updateState.checking = true
    try {
      const res = await fetch("/admin/check_update")
      const body = await res.json()
      
      if (res.ok) {
        updateState.available = !body.up_to_date && !body.error
        updateState.localHash = body.local || ''
        updateState.remoteHash = body.remote || ''
        updateState.lastChecked = new Date().toLocaleString()
        
        if (body.error) {
          updateState.message = body.error
        }
      } else {
        updateState.available = false
        updateState.message = body.error || "Erreur inconnue"
      }
    } catch (e) {
      console.warn("Failed to check for updates:", e)
      updateState.available = false
      updateState.message = e.message
    } finally {
      updateState.checking = false
    }
  }

  const performUpdate = async () => {
    if (!updateState.available) return
    
    updateState.checking = true
    try {
      const res = await fetch("/admin/app_update", { method: "POST" })
      const body = await res.json()
      
      if (res.ok && body.status === "success") {
        updateState.available = false
        updateState.message = body.message
        updateState.lastChecked = new Date().toLocaleString()
      } else {
        updateState.message = body.message || "Échec de la mise à jour"
      }
    } catch (e) {
      updateState.message = e.message
    } finally {
      updateState.checking = false
    }
  }

  const clearNotification = () => {
    updateState.available = false
  }

  return {
    updateState,
    checkForUpdates,
    performUpdate,
    clearNotification
  }
}