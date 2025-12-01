<template>
  <div class="icon-tile" @click="handleClick">
    <div class="icon-graphic">🎵</div>
    <div class="icon-label">
      {{ label }}
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string
}>()

const emit = defineEmits<{
  (e: 'activate'): void
}>()

const handleClick = () => {
  emit('activate')
}
</script>

<style scoped>
.icon-tile {
  width: 96px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 8px;
  cursor: pointer;
  user-select: none;
}

.icon-graphic {
  width: 48px;
  height: 48px;
  background: #000080;
  border: 2px solid #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #ffffff;
  box-shadow: 2px 2px 0 #000000;
}

.icon-label {
  margin-top: 4px;
  padding: 2px 4px;
  background: rgba(192, 192, 192, 0.8);
  border: 1px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  font-size: 11px;
  text-align: center;
}
</style>
