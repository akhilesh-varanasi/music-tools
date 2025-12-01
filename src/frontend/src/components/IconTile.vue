<template>
  <div class="icon-tile" @click="handleClick">
    <div class="icon-graphic" :style="{ backgroundColor: bgColor || defaultBg }">
      <img
        v-if="iconSrc"
        :src="iconSrc"
        alt=""
        class="icon-img"
        draggable="false"
      />
      <!-- Fallback: emoji/text icon -->
      <span v-else class="icon-text">
        {{ icon || '🎵' }}
      </span>
    </div>
    <div class="icon-label">
      {{ label }}
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string
  icon?: string         // optional emoji/text fallback
  bgColor?: string      // optional background color
  iconSrc?: string      // optional PNG path
}>()

const emit = defineEmits<{
  (e: 'activate'): void
}>()

const defaultBg = '#000080'

const handleClick = () => {
  emit('activate')
}
</script>

<style scoped>
.icon-tile {
  width: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 12px;
  cursor: pointer;
  user-select: none;
}

.icon-graphic {
  width: 64px;
  height: 64px;
  border: 2px solid #ffffff;
  box-shadow: 3px 3px 0 #000000;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.icon-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  image-rendering: pixelated; /* subject to change */
}

.icon-text {
  font-size: 28px;
}

.icon-label {
  margin-top: 6px;
  padding: 3px 6px;
  background: rgba(192, 192, 192, 0.9);
  border: 1px solid #ffffff;
  border-right-color: #404040;
  border-bottom-color: #404040;
  font-size: 12px;
  text-align: center;
  line-height: 1.2;
}
</style>
