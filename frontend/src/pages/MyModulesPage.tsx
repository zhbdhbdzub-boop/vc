import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { moduleService } from '@/services/moduleService'
import { modulePurchaseService } from '@/services/modulePurchaseService'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Package, Calendar, CheckCircle, CreditCard, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function MyModulesPage() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [upgradingModule, setUpgradingModule] = useState<string | null>(null)

  const { data: licenses, isLoading } = useQuery({
    queryKey: ['my-modules'],
    queryFn: moduleService.getMyModules,
  })

  const upgradeMutation = useMutation({
    mutationFn: (moduleId: string) => modulePurchaseService.purchaseModule(moduleId, 'monthly', 'pm_card_visa'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-modules'] })
      alert('Module upgraded successfully!')
      setUpgradingModule(null)
    },
    onError: (error: any) => {
      alert(error.response?.data?.error || 'Failed to upgrade module')
      setUpgradingModule(null)
    },
  })

  const handleUpgrade = (moduleId: string) => {
    if (confirm('Upgrade to monthly subscription ($9-29/month depending on module)?')) {
      setUpgradingModule(moduleId)
      upgradeMutation.mutate(moduleId)
    }
  }

  const isExpiringSoon = (expiresAt: string | null) => {
    if (!expiresAt) return false
    const daysUntilExpiry = Math.ceil((new Date(expiresAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    return daysUntilExpiry <= 3
  }

  const isExpired = (expiresAt: string | null) => {
    if (!expiresAt) return false
    return new Date(expiresAt).getTime() < Date.now()
  }

  if (isLoading) {
    return <div>Loading your modules...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">My Modules</h1>
        <p className="text-gray-600 mt-2">Manage your active modules and licenses</p>
      </div>

      {licenses && licenses.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {licenses.map((license) => (
            <Card key={license.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-3">
                      <Package className="w-6 h-6 text-indigo-600" />
                    </div>
                    <div>
                      <CardTitle>{license.module.name}</CardTitle>
                      <CardDescription className="mt-1">
                        {license.module.description}
                      </CardDescription>
                    </div>
                  </div>
                  {license.is_active && (
                    <div className="flex items-center text-green-600">
                      <CheckCircle className="w-5 h-5" />
                    </div>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-sm text-gray-600">License Type</span>
                    <span className="text-sm font-medium capitalize">{license.license_type}</span>
                  </div>
                  
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-sm text-gray-600">Status</span>
                    <span className={`text-sm font-medium ${license.is_active ? 'text-green-600' : 'text-red-600'}`}>
                      {license.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-sm text-gray-600">Activated</span>
                    <span className="text-sm">
                      {new Date(license.activated_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  {license.expires_at && (
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-sm text-gray-600">Expires</span>
                      <span className="text-sm flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {new Date(license.expires_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  {license.is_trial && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mt-3">
                      <div className="flex items-start">
                        <AlertCircle className="w-5 h-5 text-yellow-600 mr-2 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm text-yellow-800 font-medium mb-2">
                            🎉 This is a trial license. Upgrade to continue using after expiration.
                          </p>
                          {isExpiringSoon(license.expires_at) && !isExpired(license.expires_at) && (
                            <p className="text-xs text-yellow-700 mb-2">
                              ⚠️ Trial expires in {Math.ceil((new Date(license.expires_at!).getTime() - Date.now()) / (1000 * 60 * 60 * 24))} days
                            </p>
                          )}
                          {isExpired(license.expires_at) && (
                            <p className="text-xs text-red-700 mb-2 font-semibold">
                              ❌ Trial has expired - Upgrade to continue using
                            </p>
                          )}
                          <Button
                            onClick={() => handleUpgrade(license.module.id)}
                            disabled={upgradingModule === license.module.id}
                            size="sm"
                            className="bg-indigo-600 hover:bg-indigo-700 text-white"
                          >
                            <CreditCard className="w-4 h-4 mr-2" />
                            {upgradingModule === license.module.id ? 'Upgrading...' : 'Upgrade Now'}
                          </Button>
                          <Button
                            onClick={() => navigate('/marketplace')}
                            variant="outline"
                            size="sm"
                            className="ml-2"
                          >
                            View Pricing
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {!license.is_trial && license.license_type === 'monthly' && (
                    <div className="bg-blue-50 border border-blue-200 rounded-md p-3 mt-3">
                      <p className="text-sm text-blue-800">
                        💳 Monthly subscription active - Renews automatically
                      </p>
                    </div>
                  )}
                  
                  {!license.is_trial && license.license_type === 'lifetime' && (
                    <div className="bg-green-50 border border-green-200 rounded-md p-3 mt-3">
                      <p className="text-sm text-green-800">
                        ♾️ Lifetime access - No expiration
                      </p>
                    </div>
                  )}
                  
                  {license.usage_limit && (
                    <div className="mt-3">
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600">Usage</span>
                        <span className="font-medium">
                          {license.usage_count} / {license.usage_limit}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{
                            width: `${(license.usage_count / license.usage_limit) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Active Modules</h3>
            <p className="text-gray-600 mb-6">
              You haven't activated any modules yet. Browse the marketplace to get started.
            </p>
            <a
              href="/marketplace"
              className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
            >
              Browse Marketplace
            </a>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
