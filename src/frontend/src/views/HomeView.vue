<template>
  <div class="home">
    <RetroWindow title="My Music Utilities">
      <p class="intro">
        Welcome to <strong>My Music Tools 95</strong>. Choose a utility below:
      </p>

      <div class="icon-grid">
        <!-- Example service icon -->
        <IconTile
          label="Example Service"
          @click="goToExample"
        />

        <!-- Placeholder icons for future tools -->
        <IconTile label="Tag Cleaner" @click="comingSoon" />
        <IconTile label="Playlist Tools" @click="comingSoon" />
        <IconTile label=" Audio Lab " @click="comingSoon" />
      </div>
    </RetroWindow>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'
import IconTile from '../components/IconTile.vue'

const router = useRouter()

const goToExample = () => {
  router.push({ name: 'example-service' })
}

const comingSoon = () => {
  alert('This utility is coming soon!')
}
</script>

<style scoped>
.home {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 32px;
}

.icon-grid {
  display: flex;
  flex-wrap: wrap;
  margin-top: 12px;
}
.intro {
  margin-bottom: 8px;
}
</style>
