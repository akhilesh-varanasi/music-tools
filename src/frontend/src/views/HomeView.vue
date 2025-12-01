<script setup lang="ts">
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'
import IconTile from '../components/IconTile.vue'

const router = useRouter()

const goToExample = () => {
  router.push({ name: 'example-service' })
}

const goToAlbumArt = () => {
  router.push({ name: 'album-art' })
}

const comingSoon = () => {
  alert('This utility is coming soon!')
}
</script>

<template>
  <div class="home">
    <RetroWindow title="My Music Utilities">
      <p class="intro">
        Welcome to <strong>My Music Tools 95</strong>. Choose a utility below:
      </p>

      <div class="icon-grid">
        <IconTile label="Example Service" @activate="goToExample" />
        <IconTile label="Album Art Replacer" @activate="goToAlbumArt" />
        <IconTile label="Tag Cleaner" @activate="comingSoon" />
        <IconTile label="Playlist Tools" @activate="comingSoon" />
        <IconTile label="Audio Lab" @activate="comingSoon" />
      </div>
    </RetroWindow>
  </div>
</template>

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
