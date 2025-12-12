<template>
  <div class="window">
    <div class="title-bar">
      <span class="title">{{ title }}</span>
      <div class="controls">
        <button class="btn">_</button>
        <button class="btn">□</button>
        <button class="btn" @click=goHome>X</button>
      </div>
    </div>
    <div class="window-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
}>()
import { useRouter } from 'vue-router'
const router = useRouter()
const goHome = () => {
  router.push({ name: 'home' })
}
</script>

<style scoped>
.window {
  width: min(1100px, 100% - 48px);
  background: #c0c0c0;
  border: 2px solid #000000;
  box-shadow: 4px 4px 0 #000000;
}

.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #000080;
  color: #ffffff;
  padding: 4px 8px;
  font-size: 14px;
}

.title {
  font-weight: bold;
}

.controls {
  display: flex;
  gap: 4px;
}

.btn {
  border: 1px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #c0c0c0;
  width: 20px;
  height: 20px;
  padding: 0;
  font-size: 12px;
}

.window-body {
  padding: 16px;
  font-size: 14px;
}
</style>