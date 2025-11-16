import api from '../lib/api'

export interface Module {
  id: string
  code: string
  name: string
  description: string
  icon: string
  price_monthly: number | null
  price_annual: number | null
  price_lifetime: number | null
  trial_days: number
  is_active: boolean
  is_featured: boolean
  version: string
  category: string
  tags: string[]
  features: string[]
  requirements: string[]
  documentation_url: string
  demo_url: string
  created_at: string
  has_access: boolean  // NEW: Indicates if user has access to this module
}

export interface ModuleLicense {
  id: string
  module: Module
  license_type: 'trial' | 'monthly' | 'annual' | 'lifetime'
  is_active: boolean
  activated_at: string
  expires_at: string | null
  usage_limit: number | null
  usage_count: number
  is_expired: boolean
  is_trial: boolean
}

export const moduleService = {
  getMarketplace: async (params?: {
    category?: string
    search?: string
    is_featured?: boolean
  }): Promise<Module[]> => {
    const response = await api.get('/api/modules/marketplace/', { params })
    return response.data.results || response.data
  },

  getModuleById: async (id: string): Promise<Module> => {
    const response = await api.get(`/api/modules/marketplace/${id}/`)
    return response.data
  },

  getMyModules: async (): Promise<ModuleLicense[]> => {
    const response = await api.get('/api/modules/my-modules/')
    return response.data.results || response.data
  },
}
