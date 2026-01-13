<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'
import { getDesktopApi, isDesktop as isDesktopEnv } from '../utils/desktop'

const router = useRouter()

const desktop = getDesktopApi()
const isDesktop = isDesktopEnv()

const videoUrlsText = ref('')
const playlistUrlsText = ref('')
const outputDir = ref('')

const loading = ref(false)
const error = ref<string | null>(null)
const summary = ref<string | null>(null)
const results = ref<
  Array<{
    url: string
    video_id: string | null
    title: string | null
    output_path: string | null
    success: boolean
    error: string | null
  }>
>([])

function sanitizeVideoUrl(raw: string): string | null {
  const trimmed = raw.trim()
  if (!trimmed) return null

  try {
    const url = new URL(trimmed)

    const params = url.searchParams
    params.delete('list')
    params.delete('start_radio')
    params.delete('index')

    url.search = params.toString()
    return url.toString()
  } catch {
    return trimmed
  }
}

const parsedVideoUrls = computed(() =>
  videoUrlsText.value
    .split(/\r?\n/)
    .map(s => s.trim())
    .filter(Boolean)
    .map(sanitizeVideoUrl)
    .filter((u): u is string => !!u),
)

const parsedPlaylistUrls = computed(() =>
  playlistUrlsText.value
    .split(/\r?\n/)
    .map(s => s.trim())
    .filter(Boolean),
)

const combinedUrls = computed(() => [
  ...parsedVideoUrls.value,
  ...parsedPlaylistUrls.value,
])

const pickOutputFolder = async () => {
  if (!desktop) return
  const folder = await desktop.pick_folder('Pick output folder')
  if (folder) outputDir.value = folder
}

const runDownload = async () => {
  error.value = null
  summary.value = null
  results.value = []

  if (combinedUrls.value.length === 0) {
    error.value = 'Please enter at least one video or playlist URL.'
    return
  }

  if (!outputDir.value.trim()) {
    error.value = 'Please enter an output folder path.'
    return
  }

  loading.value = true
  try {
    if (desktop) {
      const data = await desktop.yt2mp3_download(combinedUrls.value, outputDir.value)

      results.value = data.results || []

      const total = data.total_tracks ?? results.value.length
      const ok = data.total_success ?? results.value.filter(r => r.success).length
      const failed = data.total_failed ?? total - ok

      summary.value = `Downloaded ${ok} of ${total} track(s). ${failed} failed.`
      return
    }

    const res = await fetch('/api/v1/yt2mp3/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        urls: combinedUrls.value,
        output_dir: outputDir.value,
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
      } catch {}
      throw new Error(message)
    }

    const data = await res.json()
    results.value = data.results || []

    const total = data.total_tracks ?? results.value.length
    const ok = data.total_success ?? results.value.filter(r => r.success).length
    const failed = data.total_failed ?? total - ok

    summary.value = `Downloaded ${ok} of ${total} track(s). ${failed} failed.`
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to download audio.'
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
    <RetroWindow title="YouTube2MP3">
      <header class="header">
        <div class="header-title">Ironchadder</div>
        <div class="header-subtitle">
          Paste YouTube links, pick a folder, and we’ll save all
          tracks as MP3s.
        </div>
      </header>

      <div class="hint-bar">
        <span class="hint-label">How it works:</span>
        <ul>
          <li>Use <strong>Videos</strong> box for individual songs.</li>
          <li>Use <strong>Playlists</strong> box for full playlists.</li>
          <li>All MP3s are written into the single output folder.</li>
        </ul>
      </div>

      <div class="panels">
        <section class="panel panel-left">
          <h4 class="panel-title">YouTube URLs</h4>

          <p class="panel-help">
            <strong>Singles:</strong> all your single songs here. format does not matter.
          </p>
          <textarea
            v-model="videoUrlsText"
            class="textarea"
            rows="5"
            placeholder="https://www.youtube.com/watch?v=..."
          />

          <p class="panel-help" style="margin-top: 10px;">
            <strong>Playlists:</strong>
            drop ya playlists. if u include single songs here that look like
            <code class="inline-url">https://www.youtube.com/watch?v=ID&amp;list=X&amp;start_radio=1</code>
            then it'll download random shit.
          </p>
          <textarea
            v-model="playlistUrlsText"
            class="textarea"
            rows="5"
            placeholder="https://www.youtube.com/playlist?list=..."
          />
        </section>

        <section class="panel panel-right">
          <h4 class="panel-title">Output folder</h4>
          <p class="panel-help">
            All MP3 files will be saved to this folder.
          </p>
          <input
            v-model="outputDir"
            type="text"
            class="input"
            placeholder="/Users/you/Music/YTDownloads"
          />

          <div v-if="isDesktop" class="picker-row">
            <button class="btn" :disabled="loading" @click="pickOutputFolder">
              Pick folder
            </button>
          </div>

          <div class="buttons">
            <button class="btn btn--primary" :disabled="loading" @click="runDownload">
              {{ loading ? 'Downloading…' : 'Download MP3s' }}
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
        </section>
      </div>

      <section v-if="results.length" class="results-window">
        <h4 class="results-title">Tracks</h4>
        <table class="results-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>URL</th>
              <th>Output file</th>
              <th>Status</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, idx) in results" :key="item.url + (item.video_id || '')">
              <td>{{ idx + 1 }}</td>
              <td>{{ item.title || '(no title)' }}</td>
              <td class="url-cell">{{ item.url }}</td>
              <td class="path-cell">{{ item.output_path || '-' }}</td>
              <td :class="{ ok: item.success, fail: !item.success }">
                {{ item.success ? 'OK' : 'Failed' }}
              </td>
              <td>{{ item.error || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </RetroWindow>
  </div>
</template>

<style scoped>
.view {
  min-height: calc(100vh - 80px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
}

.header {
  margin-bottom: 10px;
  border-bottom: 2px groove #ffffff;
  padding-bottom: 6px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
}

.header-subtitle {
  font-size: 14px;
}

.hint-bar {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  margin: 10px 0 16px;
  padding: 6px 8px;
  background: #e0e0ff;
  border: 1px solid #808080;
}

.hint-label {
  font-weight: bold;
  font-size: 13px;
  white-space: nowrap;
}

.hint-bar ul {
  margin: 0;
  padding-left: 18px;
  font-size: 13px;
}

.panels {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.panel {
  flex: 1 1 0;
  min-width: 260px;
  background: #d0d0d0;
  border: 2px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  padding: 8px;
}

.panel-title {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: bold;
}

.panel-help {
  margin: 0 0 8px;
  font-size: 13px;
}

.input {
  font-size: 14px;
  padding: 4px 6px;
  border: 2px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #ffffff;
  color: #000000;
  width: 100%;
  box-sizing: border-box;
  font-family: "MS Sans Serif", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.textarea {
  font-size: 14px;
  padding: 4px 6px;
  border: 2px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #ffffff;
  color: #000000;
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  min-height: 170px;
  font-family: "MS Sans Serif", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

.input::placeholder,
.textarea::placeholder {
  color: #555555;
}

.picker-row {
  margin-top: 8px;
}

.buttons {
  margin-top: 12px;
  display: flex;
  gap: 10px;
}

.error {
  margin-top: 10px;
  color: #c00000;
  font-size: 13px;
}

.success {
  margin-top: 10px;
  color: #006000;
  font-size: 13px;
}

.results-window {
  margin-top: 16px;
  border: 2px solid #000000;
  background: #ffffff;
  padding: 6px;
  max-height: 280px;
  overflow-y: auto;
  overflow-x: auto;
}

.results-title {
  margin: 0 0 6px;
  font-size: 14px;
  font-weight: bold;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.results-table th,
.results-table td {
  border: 1px solid #808080;
  padding: 4px 6px;
  vertical-align: top;
}

.url-cell,
.path-cell {
  word-break: break-all;
}

.results-table thead {
  background: #000080;
  color: #ffffff;
}

.ok {
  color: #006000;
  font-weight: bold;
}

.fail {
  color: #c00000;
  font-weight: bold;
}

.inline-url {
  font-family: "SF Mono", Menlo, Monaco, Consolas, "Courier New", monospace;
  font-size: 12px;
  padding: 1px 3px;
  background: #f0f0f0;
  border: 1px solid #c0c0c0;
  border-radius: 2px;
  white-space: nowrap;
}
</style>
