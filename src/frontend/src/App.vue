<!-- src/App.vue -->
<template>
  <div class="desktop">
    <header class="taskbar">
      <div class="taskbar-start">
        <span class="start-button">Start</span>
        <span class="app-title">Music Guy</span>
      </div>
      <div class="taskbar-clock">
        <span>{{ time }}</span>
      </div>
    </header>

    <main class="desktop-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue"

const time = ref("")

function updateTime() {
  const now = new Date()
  time.value = now.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  })
}

let timer: number

onMounted(() => {
  updateTime()
  timer = window.setInterval(updateTime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>


<style scoped>
.desktop {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #008080; /* classic teal */
  font-family: "MS Sans Serif", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  color: #000;
  overflow-x: hidden;
  overflow-y: hidden;
}

.desktop-main {
  flex: 1;
  padding: 16px;
  overflow: auto;
  min-height: 0;
}

/* Taskbar */
.taskbar {
  height: 32px;
  background: #c0c0c0;
  border-top: 2px solid #ffffff;
  border-bottom: 2px solid #404040;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  box-shadow: inset 0 1px 0 #dfdfdf;
}

.taskbar-start {
  display: flex;
  align-items: center;
  gap: 8px;
}

.start-button {
  padding: 2px 10px;
  border: 2px solid #404040;
  border-right-color: #ffffff;
  border-bottom-color: #ffffff;
  background: #c0c0c0;
  font-weight: bold;
  font-size: 12px;
}

.app-title {
  font-size: 12px;
}

.taskbar-clock {
  font-size: 12px;
}
</style>
