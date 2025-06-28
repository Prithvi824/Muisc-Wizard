export type ApiResponse<T> = {
  status: 'success' | 'error'
  data?: T
  error?: string
}

export type AudioMatch = {
  title: string
  yt_url: string
  thumbnail: string
  artist: string
  timestamp?: number
}

export type HeroProps = {
  setFetchedSong: React.Dispatch<React.SetStateAction<Array<AudioMatch> | null>>
}

export type SongCardProps = {
  fetchedSong: Array<AudioMatch> | null
}

export const MicStates = {
  Idle: 'IDLE',
  Recording: 'RECORDING',
  Processing: 'PROCESSING',
  Error: 'ERROR'
} as const

export type MicState = typeof MicStates[keyof typeof MicStates]

export type MicrophoneProps = {
  state: MicState
}

export type AddAudioResponse = {
  title: string
  yt_url: string
  thumbnail: string
  artist: string
  timestamp: number
}

export type GetAudioResponse = {
  total: number
  count: number
  songs: AddAudioResponse[]
}
