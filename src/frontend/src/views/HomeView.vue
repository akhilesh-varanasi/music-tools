<script setup lang="ts">
import { useRouter } from 'vue-router'
import RetroWindow from '../components/RetroWindow.vue'
import IconTile from '../components/IconTile.vue'

import albumArtIcon from '../assets/icons/album-art.png'
import yt2mp3Icon from '../assets/icons/yt-to-mp3.png'
import musicAnalyzer from '../assets/icons/music-analyzer.png'
import worldDestroyer from '../assets/icons/dagger.png'
import marioGif from '../assets/animations/mario.gif'
import doomguyGif from '../assets/animations/doomguy.gif'
import streetfighterGif from '../assets/animations/streetfighter.gif'
import linkGif from '../assets/animations/link.gif'
import ff7Gif from '../assets/animations/ff7.gif'
import laraGif from '../assets/animations/lara.gif'

const router = useRouter()

const cornerGifs = [
  { key: 'mario', src: marioGif, alt: 'maaaario' },
  { key: 'lara', src: laraGif, alt: 'lara' },
  { key: 'cloud', src: ff7Gif, alt: 'ff7' },
  { key: 'link', src: linkGif, alt: 'link' },
  { key: 'doomguy', src: doomguyGif, alt: 'doomdoomdoom' },
  { key: 'streetfighter', src: streetfighterGif, alt: 'hadouken' },
] as const

const goToAlbumArt = () => {
  router.push({ name: 'album-art' })
}

const goToYt2Mp3 = () => {
  router.push({ name: 'yt2mp3' })
}

const comingSoon = () => {
  alert('This utility is coming soon!')
}
</script>

<template>
  <div class="home">
    <div class="corner-gifs">
      <img
        v-for="gif in cornerGifs"
        :key="gif.key"
        class="corner-gif"
        :src="gif.src"
        :alt="gif.alt"
      />
    </div>

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
          @activate="goToYt2Mp3"
        />

        <IconTile
          label="Music Analyzer"
          :icon-src="musicAnalyzer"
          tooltip="Wouldn't you like to know weatherboy"
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

.corner-gifs {
  position: fixed;
  bottom: 8px;
  right: 8px;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  gap: 8px;
  z-index: 5;
  pointer-events: none;
}

.corner-gif {
  height: 96px;
  width: auto;
  image-rendering: pixelated;
}
</style>
