<script setup lang="ts">
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'
import IconTile from '../components/IconTile.vue'

// Import PNGs (Vite will handle bundling)
import albumArtIcon from '../assets/icons/album-art.png'
import yt2mp3Icon from '../assets/icons/yt-to-mp3.png'
import musicAnalyzer from '../assets/icons/music-analyzer.png'
import worldDestroyer from '../assets/icons/dagger.png'

const router = useRouter()

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
        Welcome to <strong>Music Guy</strong>. Choose a utility below:
      </p>

      <div class="icon-grid">
        <IconTile
          label="Album Art Replacer"
          :icon-src="albumArtIcon"
          tooltip="Replace ya album art"
          bgColor="#202040"
          @activate="goToAlbumArt"
        />

        <IconTile
          label="YouTube2MP3"
          :icon-src="yt2mp3Icon"
          tooltip="The artist formerly known as Ironchad"
          bgColor="#204020"
          @activate="comingSoon"
        />

        <IconTile
          label="Music Analyzer"
          :icon-src="musicAnalyzer"
          bgColor="#402020"
          @activate="comingSoon"
        />

        <IconTile
          label="World Destroyer 9000"
          :icon-src="worldDestroyer"
          tooltip="Confidential"
          bgColor="#404020"
          @activate="comingSoon"
        />
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
