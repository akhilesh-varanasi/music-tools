// src/utils/desktop.ts
export type DesktopApi = {
  pick_files: (
    title?: string,
    file_types?: Array<[string, string]>,
    allow_multiple?: boolean,
  ) => Promise<string[]>

  pick_folder: (title?: string) => Promise<string | null>

  album_art_replace: (
    song_paths: string[],
    image_paths: string[],
  ) => Promise<{
    results: Array<{
      song_path: string
      image_used: string | null
      success: boolean
      error: string | null
    }>
    total_songs: number
    total_success: number
    total_failed: number
  }>

  yt2mp3_download: (
    urls: string[],
    output_dir: string,
  ) => Promise<{
    results: Array<{
      url: string
      video_id: string | null
      title: string | null
      output_path: string | null
      success: boolean
      error: string | null
    }>
    total_tracks: number
    total_success: number
    total_failed: number
  }>
}

export function getDesktopApi(): DesktopApi | null {
  const w = window as any
  return w?.pywebview?.api ?? null
}

export function isDesktop(): boolean {
  return !!getDesktopApi()
}
