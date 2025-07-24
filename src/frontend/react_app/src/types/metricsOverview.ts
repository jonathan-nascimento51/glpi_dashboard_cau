export interface LevelMetrics {
  open: number
  closed: number
}

export interface MetricsOverview {
  [level: string]: LevelMetrics
}
