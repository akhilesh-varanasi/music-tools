<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'

const router = useRouter()

const songPathsText = ref('')   // one song path OR folder per line
const imagePathsText = ref('')  // one image path OR folder per line

const loading = ref(false)
const error = ref<string | null>(null)
const summary = ref<string | null>(null)
const results = ref<
  Array<{
    song_path: string
    image_used: string | null
    success: boolean
    error: string | null
  }>
>([])

const parsedSongPaths = computed(() =>
  songPathsText.value
    .split(/\r?\n/)
    .map(s => s.trim())
    .filter(Boolean),
)

const parsedImagePaths = computed(() =>
  imagePathsText.value
    .split(/\r?\n/)
    .map(s => s.trim())
    .filter(Boolean),
)

const runReplace = async () => {
  error.value = null
  summary.value = null
  results.value = []

  const hasSongs = parsedSongPaths.value.length > 0
  const hasImages = parsedImagePaths.value.length > 0

  if (!hasSongs) {
    error.value =
      'Please provide at least one song path or folder (one per line).'
    return
  }

  if (!hasImages) {
    error.value =
      'Please provide at least one image path or folder (one per line).'
    return
  }

  loading.value = true
  try {
    const res = await fetch('/api/v1/album-art/batch-paths', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        song_paths: parsedSongPaths.value,
        image_paths: parsedImagePaths.value,
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
        // ignore parse error
      }
      throw new Error(message)
    }

    const data = await res.json()
    results.value = data.results || []
    const total = data.total_songs ?? results.value.length
    const ok = data.total_success ?? results.value.filter(r => r.success).length
    const failed = data.total_failed ?? total - ok

    summary.value = `Processed ${total} song(s): ${ok} succeeded, ${failed} failed.`
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

      <ul class="hint-list">
        <li>
            Each line can be a <strong>file</strong> or a <strong>folder</strong>.
            Folders are scanned recursively for valid files.
        </li>
        <li>
            <strong>Single replace:</strong> enter one song path and one image path.
            That song’s art will be replaced with that image.
        </li>
        <li>
            <strong>Same art for many songs:</strong> enter many songs (or song folders)
            and <em>one</em> image. All songs will get that art.
        </li>
        <li>
            <strong>Shuffle art for many songs:</strong> enter many songs (or song folders)
            and many images (or image folders). Each song gets a random image.
        </li>
      </ul>


      <div class="two-column">
        <div class="col">
          <h4 class="col-title">Songs</h4>
          <div class="form-row">
            <label class="label">
              Song paths or folders (one per line):
              <textarea
                v-model="songPathsText"
                class="textarea"
                rows="6"
                placeholder="/Users/you/Music/song1.mp3
/Users/you/Music/AlbumA
/Volumes/drive/MusicFolder"
              />
            </label>
          </div>
        </div>

        <div class="col">
          <h4 class="col-title">Images</h4>
          <div class="form-row">
            <label class="label">
              Image paths or folders (one per line):
              <textarea
                v-model="imagePathsText"
                class="textarea"
                rows="6"
                placeholder="/Users/you/Pictures/covers/cover1.jpg
/Users/you/Pictures/covers
/Volumes/drive/MoreCovers"
              />
            </label>
          </div>
        </div>
      </div>

      <div class="buttons">
        <button class="btn btn--primary" :disabled="loading" @click="runReplace">
          {{ loading ? 'Processing...' : 'Run replace' }}
        </button>
        <button class="btn" @click="goHome">
          Back to desktop
        </button>
      </div>

      <p v-if="error" class="error">
        {{ error }}
      </p>

      <p v-if="summary" class="success">
        {{ summary }}
      </p>

      <div v-if="results.length" class="results-window">
        <h4 class="results-title">Results</h4>
        <table class="results-table">
          <thead>
            <tr>
              <th>Song</th>
              <th>Image used</th>
              <th>Status</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in results"
              :key="item.song_path + (item.image_used || '')"
            >
              <td>{{ item.song_path }}</td>
              <td>{{ item.image_used || '-' }}</td>
              <td :class="{ ok: item.success, fail: !item.success }">
                {{ item.success ? 'OK' : 'Failed' }}
              </td>
              <td>{{ item.error || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </RetroWindow>
  </div>
</template>

<style scoped>
.view {
  /* Fill the available space and center the window */
  min-height: calc(100vh - 80px); /* leave room for taskbar */
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}

.desc {
  margin-bottom: 6px;
  font-size: 13px;
}

.hint-list {
  margin: 4px 0 10px;
  padding-left: 18px;
  font-size: 14px;
}

.two-column {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}

.col {
  flex: 1 1 0;
  min-width: 0; /* helps prevent overflow */
}

.col-title {
  margin: 0 0 4px;
  font-size: 12px;
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
  color: #000000;
}

.textarea {
  font-size: 12px;
  padding: 2px 4px;
  border: 2px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #ffffff;
  resize: vertical;
  font-family: "MS Sans Serif", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: #000000;
}

.buttons {
  margin-top: 10px;
  display: flex;
  gap: 8px;
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

/* Results area: keep inside window with scroll */
.results-window {
  margin-top: 10px;
  border: 2px solid #000000;
  background: #ffffff;
  padding: 4px;
  max-height: 220px;      /* constrain height */
  overflow-y: auto;       /* vertical scroll if many rows */
  overflow-x: auto;       /* horizontal scroll if long paths */
}

.results-title {
  margin: 0 0 4px;
  font-size: 12px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

.results-table th,
.results-table td {
  border: 1px solid #808080;
  padding: 3px 4px;
  vertical-align: top;
  word-break: break-all; /* long paths wrap instead of blowing layout */
}

.results-table thead {
  background: #000080;
  color: #ffffff;
}

.ok {
  color: #006000;
}

.fail {
  color: #c00000;
}
</style>
