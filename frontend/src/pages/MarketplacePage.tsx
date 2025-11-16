import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { moduleService } from '@/services/moduleService'
import { modulePurchaseService } from '@/services/modulePurchaseService'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Package, Star, Check, CheckCircle, XCircle } from 'lucide-react'
import { useState } from 'react'

export default function MarketplacePage() {
  const queryClient = useQueryClient()
  const [purchasingModule, setPurchasingModule] = useState<string | null>(null)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [selectedModule, setSelectedModule] = useState<any>(null)
  const [showResultDialog, setShowResultDialog] = useState(false)
  const [resultType, setResultType] = useState<'success' | 'error'>('success')
  const [resultMessage, setResultMessage] = useState('')

  const { data: modules, isLoading } = useQuery({
    queryKey: ['marketplace'],
    queryFn: () => moduleService.getMarketplace(),
  })

  const startTrialMutation = useMutation({
    mutationFn: (moduleId: string) => modulePurchaseService.startTrial(moduleId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['marketplace'] })
      queryClient.invalidateQueries({ queryKey: ['my-modules'] })
      setResultType('success')
      setResultMessage('Trial started successfully! You can now access this module.')
      setShowResultDialog(true)
      setPurchasingModule(null)
    },
    onError: (error: any) => {
      setResultType('error')
      setResultMessage(error.response?.data?.error || 'Failed to start trial. Please try again.')
      setShowResultDialog(true)
      setPurchasingModule(null)
    },
  })

  const handleStartTrial = (module: any) => {
    setSelectedModule(module)
    setShowConfirmDialog(true)
  }

  const confirmStartTrial = () => {
    if (selectedModule) {
      setPurchasingModule(selectedModule.id)
      startTrialMutation.mutate(selectedModule.id)
      setShowConfirmDialog(false)
    }
  }

  if (isLoading) {
    return <div>Loading marketplace...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Marketplace</h1>
          <p className="text-gray-600 mt-2">Discover and purchase modules for your workspace</p>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {modules?.map((module) => (
          <Card key={module.id} className="flex flex-col">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mr-3">
                    <Package className="w-6 h-6 text-indigo-600" />
                  </div>
                  <div>
                    <CardTitle className="text-lg">{module.name}</CardTitle>
                    {module.is_featured && (
                      <div className="flex items-center mt-1">
                        <Star className="w-4 h-4 text-yellow-500 mr-1" />
                        <span className="text-xs text-gray-600">Featured</span>
                      </div>
                    )}
                  </div>
                </div>
                {module.has_access && (
                  <div className="flex items-center text-green-600 text-sm">
                    <Check className="w-4 h-4 mr-1" />
                    <span>Active</span>
                  </div>
                )}
              </div>
              <CardDescription className="mt-3">{module.description}</CardDescription>
            </CardHeader>
            
            <CardContent className="flex-grow">
              <div className="space-y-3">
                <div>
                  <span className="text-xs font-medium text-gray-600 uppercase">Category</span>
                  <p className="text-sm">{module.category}</p>
                </div>
                
                {module.features.length > 0 && (
                  <div>
                    <span className="text-xs font-medium text-gray-600 uppercase">Key Features</span>
                    <ul className="text-sm mt-1 space-y-1">
                      {module.features.slice(0, 3).map((feature: string, idx: number) => (
                        <li key={idx} className="flex items-start">
                          <span className="text-indigo-600 mr-2">•</span>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
            
            <CardFooter className="flex-col space-y-3">
              <div className="w-full flex justify-between items-center">
                <div>
                  <span className="text-sm text-gray-600">Starting at</span>
                  <div className="flex items-center">
                    <span className="text-2xl font-bold text-gray-900">
                      {module.price_monthly || module.price_lifetime || '0'}
                    </span>
                    <span className="text-sm text-gray-600 ml-1">TND</span>
                  </div>
                </div>
                {module.trial_days > 0 && !module.has_access && (
                  <div className="text-right">
                    <span className="text-xs font-medium text-green-600">
                      {module.trial_days}-day free trial
                    </span>
                  </div>
                )}
              </div>
              
              {module.has_access ? (
                <Button className="w-full" variant="outline" disabled>
                  <Check className="w-4 h-4 mr-2" />
                  Already Active
                </Button>
              ) : (
                <>
                  {module.trial_days > 0 ? (
                    <Button 
                      className="w-full"
                      onClick={() => handleStartTrial(module)}
                      disabled={purchasingModule === module.id}
                    >
                      {purchasingModule === module.id ? 'Starting...' : 'Start Free Trial'}
                    </Button>
                  ) : (
                    <div className="w-full space-y-2">
                      <Button 
                        className="w-full bg-green-600 hover:bg-green-700"
                        onClick={() => handleStartTrial(module)}
                        disabled={purchasingModule === module.id}
                      >
                        {purchasingModule === module.id ? 'Activating...' : 'Try Free Features'}
                      </Button>
                      <p className="text-xs text-center text-gray-500">
                        Free to start • Purchase for full access
                      </p>
                    </div>
                  )}
                </>
              )}
            </CardFooter>
          </Card>
        ))}
      </div>

      {(!modules || modules.length === 0) && (
        <Card>
          <CardContent className="text-center py-12">
            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Modules Available</h3>
            <p className="text-gray-600">Check back later for new modules</p>
          </CardContent>
        </Card>
      )}

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Start Free Trial</DialogTitle>
            <DialogDescription>
              Are you sure you want to start a free trial for <strong>{selectedModule?.name}</strong>?
              {selectedModule?.trial_days && (
                <span className="block mt-2 text-green-600">
                  You'll get {selectedModule.trial_days} days of free access to all features.
                </span>
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancel
            </Button>
            <Button onClick={confirmStartTrial}>
              Start Trial
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Result Dialog */}
      <Dialog open={showResultDialog} onOpenChange={setShowResultDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {resultType === 'success' ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Success
                </>
              ) : (
                <>
                  <XCircle className="w-5 h-5 text-red-600" />
                  Error
                </>
              )}
            </DialogTitle>
            <DialogDescription className="text-base">
              {resultMessage}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button onClick={() => setShowResultDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
