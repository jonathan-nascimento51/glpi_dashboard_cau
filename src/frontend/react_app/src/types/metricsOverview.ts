export interface LevelMetrics {
  open: number
  closed: number
  [key: string]: number
}

export interface MetricsOverview {
  [level: string]: LevelMetrics
}
