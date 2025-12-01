<template>
  <div class="view">
    <RetroWindow title="Example Service">
      <p class="desc">
        This is a sample utility wired to the Python backend.
        Later, we’ll replace this with a real music tool.
      </p>

      <section v-if="loading">
        Loading data from backend...
      </section>

      <section v-else-if="error" class="error">
        Error: {{ error }}
      </section>

      <section v-else>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>{{ item.id }}</td>
              <td>{{ item.name }}</td>
              <td>{{ item.description || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <div class="footer">
        <button class="btn" @click="goHome">Back to desktop</button>
      </div>
    </RetroWindow>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'

interface ExampleItem {
  id: number
  name: string
  description?: string | null
}

const items = ref<ExampleItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const router = useRouter()

const goHome = () => router.push({ name: 'home' })

onMounted(async () => {
  try {
    const res = await fetch('/api/v1/example/')
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`)
    }
    items.value = await res.json()
  } catch (e: any) {
    error.value = e?.message ?? 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.view {
  display: flex;
  justify-content: center;
  padding-top: 32px;
}

.desc {
  margin-bottom: 8px;
}

.error {
  color: #c00000;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 8px;
}

.data-table th,
.data-table td {
  border: 1px solid #808080;
  padding: 4px 6px;
}

.data-table thead {
  background: #000080;
  color: #ffffff;
}

.footer {
  margin-top: 12px;
  text-align: right;
}

.btn {
  padding: 2px 10px;
  border: 2px solid #404040;
  border-right-color: #ffffff;
  border-bottom-color: #ffffff;
  background: #c0c0c0;
  font-size: 12px;
}
</style>
