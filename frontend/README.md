# Modular Platform - Frontend

React 18 + TypeScript + Vite frontend with Tailwind CSS and Radix UI components.

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- npm or yarn

### Installation

1. **Install dependencies**
   ```powershell
   cd frontend
   npm install
   ```

2. **Configure environment**
   ```powershell
   # Create .env file
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

3. **Run development server**
   ```powershell
   npm run dev
   ```

   App will be available at `http://localhost:5173`

### Build for Production

```powershell
npm run build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── layouts/      # Layout components
│   │   └── ui/           # Reusable UI components
│   ├── pages/            # Page components
│   │   ├── auth/         # Login, Register
│   │   ├── DashboardPage.tsx
│   │   ├── MarketplacePage.tsx
│   │   ├── MyModulesPage.tsx
│   │   └── ProfilePage.tsx
│   ├── services/         # API service layer
│   ├── store/            # Zustand state management
│   ├── lib/              # Utilities, API client
│   ├── App.tsx           # Main app with routing
│   ├── main.tsx          # App entry point
│   └── index.css         # Global styles
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## 🎨 UI Components

Built with Radix UI primitives and Tailwind CSS:

- **Button** - Multiple variants (default, outline, ghost, etc.)
- **Input** - Form input with validation
- **Card** - Container with header, content, footer
- **Dialog** - Modal dialogs
- **Dropdown** - Dropdown menus
- **Select** - Select inputs
- **Toast** - Notifications

## 🗺️ Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/login` | LoginPage | User login |
| `/register` | RegisterPage | User registration |
| `/dashboard` | DashboardPage | Main dashboard |
| `/marketplace` | MarketplacePage | Module marketplace |
| `/my-modules` | MyModulesPage | Active modules |
| `/profile` | ProfilePage | User profile |

## 🔐 Authentication

JWT authentication with automatic token refresh:

```typescript
// authStore.ts
- Stores user, accessToken, refreshToken
- Persists to localStorage
- Auto-refresh on 401 responses

// api.ts
- Axios interceptors for auth headers
- Automatic token refresh
- Logout on auth failure
```

## 📡 API Integration

```typescript
// services/authService.ts
- login(credentials)
- register(data)
- logout()
- getProfile()
- updateProfile(data)
- changePassword(data)
- getDashboard()

// services/moduleService.ts
- getMarketplace(params)
- getModuleById(id)
- getMyModules()
```

## 🎨 Styling

**Tailwind CSS** with custom design system:

```css
/* Design Tokens */
Primary: Indigo (#4F46E5)
Secondary: Purple
Success: Green
Danger: Red
Font: Inter

/* Breakpoints */
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
```

## 🧪 Development

```powershell
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npm run type-check
```

## 📦 Dependencies

**Core:**
- React 18.3
- React Router DOM 6
- TypeScript 5

**State Management:**
- Zustand (lightweight state)
- TanStack React Query (server state)

**UI:**
- Tailwind CSS 3
- Radix UI primitives
- Lucide React icons

**HTTP:**
- Axios

**Build:**
- Vite 5
- SWC (fast compilation)

## 🐳 Docker

```powershell
# Development
docker-compose -f docker-compose.dev.yml up frontend

# Production
docker-compose up frontend
```

## 🔧 Configuration

### vite.config.ts
```typescript
- API proxy to backend
- Path aliases (@/)
- SWC React plugin
```

### tailwind.config.js
```javascript
- Custom color palette
- Design tokens
- Typography scale
```

### tsconfig.json
```json
- Strict type checking
- Path aliases
- Modern ES features
```

## 🌐 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## 📱 Responsive Design

- Mobile-first approach
- Responsive navigation
- Adaptive layouts
- Touch-friendly UI

## ♿ Accessibility

- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## 🚀 Performance

- Code splitting
- Lazy loading
- Image optimization
- Bundle size monitoring

## 📚 Documentation

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
- [TanStack Query](https://tanstack.com/query/)

## 🆘 Troubleshooting

**Module not found errors:**
```powershell
rm -rf node_modules package-lock.json
npm install
```

**API connection issues:**
- Check VITE_API_URL in .env
- Ensure backend is running
- Check CORS settings in Django

**Build errors:**
- Clear Vite cache: `npm run dev -- --force`
- Check TypeScript errors: `npm run type-check`
