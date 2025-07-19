import { fetcher } from '../lib/swrClient'
import type { ChamadoPorData } from '../types/chamado'

export async function fetchChamadosPorData(): Promise<ChamadoPorData[]> {
  return fetcher<ChamadoPorData[]>('/chamados/por-data')
}
