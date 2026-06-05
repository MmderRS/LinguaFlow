import { onBeforeUnmount, onMounted } from 'vue'

import { useRealtimeStore } from '../stores/realtime'
import { useSettingsStore } from '../stores/settings'

export function useRealtimeSession() {
  const realtimeStore = useRealtimeStore()
  const settingsStore = useSettingsStore()

  onMounted(async () => {
    if (!settingsStore.settings) {
      await settingsStore.load()
    }
    await realtimeStore.connect(settingsStore.settings?.websocket_path || '/ws/realtime')
  })

  onBeforeUnmount(() => {
    realtimeStore.disconnect()
  })

  return {
    realtimeStore,
    settingsStore,
  }
}
