import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { 
  LayoutDashboard, 
  ShoppingBag, 
  Package, 
  User, 
  LogOut,
  Menu,
  X,
  FileText,
  MessageSquare,
  Code
} from 'lucide-react'
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { moduleService } from '@/services/moduleService'

export default function DashboardLayout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  // Fetch user's active modules
  const { data: myModules } = useQuery({
    queryKey: ['my-modules'],
    queryFn: () => moduleService.getMyModules(),
    enabled: !!user,
    staleTime: 0, // Always refetch
    cacheTime: 0, // Don't cache
  })

  // Debug logging
  console.log('MyModules data:', myModules)
  console.log('Module codes:', myModules?.map(l => l.module.code))

  // Check if user has access to a module
  const hasModuleAccess = (moduleCode: string) => {
    if (!myModules) {
      console.log(`No modules loaded yet for check: ${moduleCode}`)
      return false
    }
    const hasAccess = myModules.some(license => 
      license.module.code === moduleCode && license.is_active
    )
    console.log(`Module ${moduleCode}: ${hasAccess}`)
    return hasAccess
  }

  // All possible navigation items with their required module
  const allNavigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, requiresModule: null },
    { name: 'ATS Checker', href: '/cv-analysis/ats-checker', icon: FileText, requiresModule: 'ats_checker' },
    { name: 'CV-Job Matcher', href: '/cv-analysis/cv-job-matcher', icon: FileText, requiresModule: 'cv_job_matcher' },
    { name: 'Advanced Analyzer', href: '/cv-analysis/advanced-analyzer', icon: FileText, requiresModule: 'advanced_analyzer' },
    { name: 'Interview Simulator', href: '/interview-simulator', icon: MessageSquare, requiresModule: 'interview_simulator' },
    { name: 'Code Challenges', href: '/code-assessment', icon: Code, requiresModule: 'code_assessment' },
    { name: 'Marketplace', href: '/marketplace', icon: ShoppingBag, requiresModule: null },
    { name: 'My Modules', href: '/my-modules', icon: Package, requiresModule: null },
  ]

  // Filter navigation based on module access
  const navigation = allNavigation.filter(item => {
    // If no module required, always show
    if (!item.requiresModule) return true
    // Otherwise, check if user has access
    const access = hasModuleAccess(item.requiresModule)
    console.log(`Filtering ${item.name} (${item.requiresModule}): ${access}`)
    return access
  })
  
  console.log('Filtered navigation:', navigation.map(n => n.name))

  // Primary navigation for desktop (filtered)
  const primaryNav = navigation.filter(item => 
    item.name !== 'Profile' // Exclude profile from top nav
  )

  const handleLogout = async () => {
    logout()
    navigate('/login')
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/dashboard" className="flex items-center">
                <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">M</span>
                </div>
                <span className="ml-2 text-xl font-bold text-gray-900">Modular Platform</span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex lg:items-center lg:space-x-2">
              {primaryNav.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive(item.href)
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-1.5" />
                    <span className="whitespace-nowrap">{item.name}</span>
                  </Link>
                )
              })}
              
              {/* User Menu */}
              <div className="flex items-center space-x-2 ml-3 pl-3 border-l border-gray-200">
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 px-3 py-2 rounded-md hover:bg-gray-100"
                >
                  <User className="w-4 h-4 text-gray-600" />
                  <div className="text-left hidden xl:block">
                    <p className="text-sm font-medium text-gray-900">{user?.full_name || 'User'}</p>
                    <p className="text-xs text-gray-500">{user?.tenant?.name || 'zeze'}</p>
                  </div>
                </Link>
                <Button variant="outline" size="sm" onClick={handleLogout} className="hidden lg:flex">
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Mobile menu button */}
            <div className="flex items-center lg:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-md text-gray-700 hover:bg-gray-100"
              >
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-200">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {navigation.map((item) => {
                const Icon = item.icon
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium ${
                      isActive(item.href)
                        ? 'bg-indigo-50 text-indigo-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                )
              })}
              <div className="pt-4 pb-3 border-t border-gray-200">
                <div className="px-3 mb-3">
                  <p className="text-base font-medium text-gray-900">{user?.full_name || user?.email}</p>
                  <p className="text-sm text-gray-500">{user?.tenant?.name}</p>
                </div>
                <Button 
                  variant="outline" 
                  className="w-full" 
                  onClick={() => {
                    handleLogout()
                    setMobileMenuOpen(false)
                  }}
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
