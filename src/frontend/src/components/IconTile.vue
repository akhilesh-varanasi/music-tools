<!-- src/components/IconTile.vue -->
<template>
  <div
    class="icon-tile"
    :data-tooltip="tooltip || null"
    @click="handleClick"
  >
    <div
      class="icon-graphic"
      :class="{ 'icon-graphic--image': !!iconSrc }"
      :style="iconSrc ? {} : { backgroundColor: bgColor || defaultBg }"
    >
      <!-- If PNG provided, use it without background box -->
      <img
        v-if="iconSrc"
        :src="iconSrc"
        alt=""
        class="icon-img"
        draggable="false"
      />
      <!-- Fallback: emoji/text icon inside retro square -->
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
const { label, icon, bgColor, iconSrc, tooltip } = defineProps<{
  label: string
  icon?: string
  bgColor?: string
  iconSrc?: string
  tooltip?: string
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
  position: relative; /* needed for tooltip positioning */
  width: 110px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 12px;
  cursor: pointer;
  user-select: none;
}

/* Default: retro square box for emoji/text icons */
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

/* When using PNG: no background box */
.icon-graphic--image {
  border: none;
  box-shadow: none;
  background: transparent;
  width: auto;
  height: auto;
}

/* PNG icon */
.icon-img {
  width: 64px;
  height: 64px;
  object-fit: contain;
  image-rendering: pixelated; /* optional: retro feel */
}

/* Emoji/text fallback */
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

/* --- Custom tooltip (instant) --- */

.icon-tile[data-tooltip]::after {
  content: attr(data-tooltip);
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: -32px;
  white-space: nowrap;
  background: #ffffe1; /* classic tooltip yellow-ish */
  color: #000000;
  border: 1px solid #404040;
  padding: 2px 6px;
  font-size: 12px;
  box-shadow: 2px 2px 0 #000000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.05s linear;
  z-index: 10;
}

.icon-tile[data-tooltip]:hover::after {
  opacity: 1;
}
</style>
