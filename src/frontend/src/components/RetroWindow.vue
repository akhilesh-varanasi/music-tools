<template>
  <div class="window">
    <div class="title-bar">
      <span class="title">{{ title }}</span>
      <div class="controls">
        <button class="btn">_</button>
        <button class="btn">□</button>
        <button class="btn">X</button>
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
</script>

<style scoped>
.window {
  background: #c0c0c0;
  border: 2px solid #000000;
  box-shadow: 2px 2px 0 #000000;
  max-width: 640px;
}

.title-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #000080;
  color: #ffffff;
  padding: 2px 4px;
  font-size: 12px;
}

.title {
  font-weight: bold;
}

.controls {
  display: flex;
  gap: 2px;
}

.btn {
  border: 1px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  background: #c0c0c0;
  width: 16px;
  height: 16px;
  padding: 0;
  font-size: 10px;
  line-height: 12px;
}
.window-body {
  padding: 8px;
  font-size: 13px;
}
</style>
