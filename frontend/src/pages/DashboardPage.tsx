import { useQuery } from '@tanstack/react-query'
import { authService } from '@/services/authService'
import { moduleService } from '@/services/moduleService'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Package, Users, ShoppingBag, TrendingUp, FileText, MessageSquare, Code, Lock } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: authService.getDashboard,
  })

  const { data: myModules } = useQuery({
    queryKey: ['my-modules'],
    queryFn: () => moduleService.getMyModules(),
  })

  const hasModuleAccess = (moduleCode: string) => {
    if (!myModules) return false
    return myModules.some(license => license.module.code === moduleCode && license.is_active)
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  const stats = [
    { name: 'Active Modules', value: myModules?.length || 0, icon: Package, color: 'bg-indigo-500' },
    { name: 'Team Members', value: dashboardData?.tenant?.total_users || 1, icon: Users, color: 'bg-green-500' },
    { name: 'Subscription', value: myModules?.length ? `${myModules.length} Modules` : 'Free Plan', icon: ShoppingBag, color: 'bg-purple-500' },
    { name: 'Status', value: 'Active', icon: TrendingUp, color: 'bg-blue-500' },
  ]

  const quickActions = [
    { href: '/cv-analysis/upload', icon: FileText, color: 'blue' as const, title: 'Upload CV', description: 'AI-powered CV analysis', requiresModule: 'cv_analysis' },
    { href: '/interviews', icon: MessageSquare, color: 'purple' as const, title: 'Practice Interview', description: 'Mock interview sessions', requiresModule: 'interviews' },
    { href: '/code-assessment', icon: Code, color: 'green' as const, title: 'Code Challenges', description: 'Solve coding problems', requiresModule: 'code_assessment' },
    { href: '/marketplace', icon: ShoppingBag, color: 'indigo' as const, title: 'Browse Marketplace', description: 'Discover new modules', requiresModule: null },
    { href: '/my-modules', icon: Package, color: 'pink' as const, title: 'My Modules', description: 'Manage subscriptions', requiresModule: null }
  ]

  const colorClasses: Record<'blue' | 'purple' | 'green' | 'indigo' | 'pink', { icon: string; hover: string }> = {
    blue: { icon: 'text-blue-600', hover: 'hover:border-blue-500' },
    purple: { icon: 'text-purple-600', hover: 'hover:border-purple-500' },
    green: { icon: 'text-green-600', hover: 'hover:border-green-500' },
    indigo: { icon: 'text-indigo-600', hover: 'hover:border-indigo-500' },
    pink: { icon: 'text-pink-600', hover: 'hover:border-pink-500' },
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back, {dashboardData?.user?.full_name}!</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map(stat => {
          const Icon = stat.icon
          return (
            <Card key={stat.name}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-2">{stat.value}</p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Get started with your platform</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {quickActions.map(action => {
              const Icon = action.icon
              const hasAccess = !action.requiresModule || hasModuleAccess(action.requiresModule)
              const colors = colorClasses[action.color]

              if (!hasAccess) {
                return (
                  <Link
                    key={action.title}
                    to="/marketplace"
                    className="p-4 border border-gray-200 rounded-lg hover:border-orange-500 hover:shadow-md transition-all relative"
                  >
                    <div className="absolute top-2 right-2">
                      <Lock className="w-4 h-4 text-orange-500" />
                    </div>
                    <Icon className={`w-8 h-8 ${colors.icon} opacity-50 mb-2`} />
                    <h3 className="font-semibold mb-1">{action.title}</h3>
                    <p className="text-sm text-gray-600">{action.description}</p>
                    <p className="text-xs text-orange-600 mt-2 font-medium">🔒 Start Free Trial</p>
                  </Link>
                )
              }

              return (
                <Link
                  key={action.title}
                  to={action.href}
                  className={`p-4 border rounded-lg ${colors.hover} hover:shadow-md transition-all`}
                >
                  <Icon className={`w-8 h-8 ${colors.icon} mb-2`} />
                  <h3 className="font-semibold mb-1">{action.title}</h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </Link>
              )
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <p>No recent activity</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}