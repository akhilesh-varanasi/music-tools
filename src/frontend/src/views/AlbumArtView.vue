<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'

const router = useRouter()

const mp3Path = ref('')
const imagePath = ref('')
const loading = ref(false)
const error = ref<string | null>(null)
const success = ref<string | null>(null)

const submit = async () => {
  error.value = null
  success.value = null

  if (!mp3Path.value.trim() || !imagePath.value.trim()) {
    error.value = 'Please enter both an MP3 path and an image path.'
    return
  }

  loading.value = true
  try {
    const res = await fetch('/api/v1/album-art/single-path', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        mp3_path: mp3Path.value,
        image_path: imagePath.value,
      }),
    })

    if (!res.ok) {
      let message = `HTTP ${res.status}`
      try {
        const data = await res.json()
        if (data && data.detail) {
          message = Array.isArray(data.detail)
            ? data.detail.map((d: any) => d.msg ?? d).join(', ')
            : data.detail
        }
      } catch {
        // ignore JSON parse error, keep default message
      }
      throw new Error(message)
    }

    const data = await res.json()
    success.value = `Album art updated in place for: ${data.mp3_path}`
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to update album art.'
  } finally {
    loading.value = false
  }
}

const goHome = () => {
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="view">
    <RetroWindow title="Album Art Replacer">
      <p class="desc">
        Mode 1 (paths): replace the album art of a single MP3
        <strong>in place</strong> on disk using local file paths.
      </p>
      <p class="hint">
        Example paths (macOS):
        <br />
        <code>/Users/you/Music/track1.mp3</code>
        <br />
        <code>/Users/you/Pictures/cover.jpg</code>
      </p>

      <div class="form-row">
        <label class="label">
          MP3 file path:
          <input
            v-model="mp3Path"
            type="text"
            class="input"
            placeholder="/Users/you/Music/song.mp3"
          />
        </label>
      </div>

      <div class="form-row">
        <label class="label">
          Cover image path:
          <input
            v-model="imagePath"
            type="text"
            class="input"
            placeholder="/Users/you/Pictures/cover.jpg"
          />
        </label>
      </div>

      <div class="buttons">
        <button class="btn" :disabled="loading" @click="submit">
          {{ loading ? 'Processing...' : 'Replace Album Art (in place)' }}
        </button>
        <button class="btn" @click="goHome">
          Back to desktop
        </button>
      </div>

      <p v-if="error" class="error">
        {{ error }}
      </p>

      <p v-if="success" class="success">
        ✅ {{ success }}
      </p>
    </RetroWindow>
  </div>
</template>

<style scoped>
.view {
  display: flex;
  justify-content: center;
  padding-top: 32px;
}

.desc {
  margin-bottom: 8px;
  font-size: 13px;
}

.hint {
  margin-bottom: 10px;
  font-size: 11px;
  background: #ffffff;
  border: 1px solid #808080;
  padding: 4px 6px;
}

.form-row {
  margin-bottom: 8px;
  font-size: 13px;
}

.label {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.input {
  font-size: 12px;
  padding: 2px 4px;
  border: 2px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #ffffff;
  font-family: "MS Sans Serif", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.buttons {
  margin-top: 10px;
  display: flex;
  gap: 8px;
}

.btn {
  padding: 2px 10px;
  border: 2px solid #404040;
  border-right-color: #ffffff;
  border-bottom-color: #ffffff;
  background: #c0c0c0;
  font-size: 12px;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: default;
}

.error {
  margin-top: 8px;
  color: #c00000;
  font-size: 12px;
}

.success {
  margin-top: 8px;
  color: #006000;
  font-size: 12px;
}
</style>
