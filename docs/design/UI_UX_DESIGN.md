# UI/UX Design Specification

## Design Philosophy

**Inspired by Odoo:** Clean, professional, modular interface with clear information hierarchy.

**Core Principles:**
1. **Clarity**: Every action and status is obvious
2. **Consistency**: Reusable components across modules
3. **Efficiency**: Minimize clicks, maximize productivity
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Responsiveness**: Desktop-first, mobile-friendly

---

## Color Palette

### Primary Colors
```
Primary:     #4F46E5 (Indigo-600)  - Buttons, links, active states
Primary-dark:#4338CA (Indigo-700)  - Hover states
Secondary:   #10B981 (Emerald-500) - Success, positive actions
```

### Semantic Colors
```
Success:     #10B981 (Green)   - Completed, approved
Warning:     #F59E0B (Amber)   - Pending, attention needed
Error:       #EF4444 (Red)     - Failed, errors
Info:        #3B82F6 (Blue)    - Information, neutral actions
```

### Neutral Colors
```
Gray-900: #111827  - Primary text
Gray-700: #374151  - Secondary text
Gray-500: #6B7280  - Tertiary text, icons
Gray-300: #D1D5DB  - Borders
Gray-100: #F3F4F6  - Backgrounds
Gray-50:  #F9FAFB  - Page background
White:    #FFFFFF  - Cards, modals
```

---

## Typography

**Font Family:** Inter (Google Fonts)
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Type Scale
```
Heading 1:  32px / 2rem   - font-bold   - Page titles
Heading 2:  24px / 1.5rem - font-semibold - Section headers
Heading 3:  20px / 1.25rem - font-semibold - Card titles
Heading 4:  18px / 1.125rem - font-medium - Sub-sections
Body:       16px / 1rem   - font-normal - Default text
Small:      14px / 0.875rem - font-normal - Captions, labels
Tiny:       12px / 0.75rem - font-normal - Metadata
```

---

## Layout Structure

### App Shell
```
┌─────────────────────────────────────────────────────┐
│  Top Navigation Bar (64px height)                   │
│  - Logo  - Module Nav  - Search  - Profile          │
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│  Sidebar │         Main Content Area               │
│  (240px) │         (Fluid width)                    │
│          │                                          │
│  - Home  │  ┌─────────────────────────────────┐   │
│  - Mods  │  │  Page Header                    │   │
│  - Market│  │  - Title  - Actions  - Breadcrumb│  │
│  - Dash  │  ├─────────────────────────────────┤   │
│          │  │                                 │   │
│          │  │  Content Cards                  │   │
│          │  │                                 │   │
│          │  └─────────────────────────────────┘   │
│          │                                          │
└──────────┴──────────────────────────────────────────┘
```

### Responsive Breakpoints
```
Mobile:     < 640px   - Single column, hamburger menu
Tablet:     640-1024px - Collapsible sidebar
Desktop:    > 1024px   - Full layout
Wide:       > 1536px   - Max-width content, centered
```

---

## Component Library

### 1. Navigation Components

#### Top Navigation Bar
```tsx
<header className="bg-white border-b border-gray-300 h-16 px-6">
  <div className="flex items-center justify-between h-full">
    {/* Logo */}
    <div className="flex items-center gap-6">
      <img src="/logo.svg" alt="Logo" className="h-8" />
      
      {/* Module Quick Access */}
      <nav className="hidden md:flex gap-2">
        <NavItem icon={<ChartIcon />} label="CV Analysis" />
        <NavItem icon={<MicIcon />} label="Interview" />
      </nav>
    </div>
    
    {/* Right Section */}
    <div className="flex items-center gap-4">
      <SearchBar />
      <NotificationBell />
      <UserProfileDropdown />
    </div>
  </div>
</header>
```

#### Sidebar Navigation
```tsx
<aside className="w-60 bg-gray-50 border-r border-gray-300 h-screen">
  <nav className="p-4 space-y-2">
    <SidebarItem icon={<HomeIcon />} label="Dashboard" to="/" />
    <SidebarItem icon={<ModuleIcon />} label="My Modules" to="/modules" />
    <SidebarItem icon={<StoreIcon />} label="Marketplace" to="/marketplace" />
    <SidebarItem icon={<ChartIcon />} label="Analytics" to="/analytics" />
    
    <div className="pt-4 mt-4 border-t border-gray-300">
      <p className="text-xs font-semibold text-gray-500 px-3 mb-2">
        MODULES
      </p>
      <SidebarItem icon={<DocumentIcon />} label="CV Analysis" to="/cv" />
      <SidebarItem icon={<MicIcon />} label="Interviews" to="/interviews" />
    </div>
  </nav>
</aside>
```

### 2. Cards

#### Module Card (Marketplace)
```tsx
<div className="bg-white rounded-lg border border-gray-300 p-6 hover:shadow-lg transition">
  {/* Header */}
  <div className="flex items-start gap-4 mb-4">
    <img src={iconUrl} alt="" className="w-12 h-12 rounded" />
    <div className="flex-1">
      <h3 className="text-lg font-semibold text-gray-900">CV Analysis</h3>
      <p className="text-sm text-gray-500">Recruitment</p>
    </div>
    {isPremium && <Badge variant="premium">Premium</Badge>}
  </div>
  
  {/* Description */}
  <p className="text-sm text-gray-700 mb-4 line-clamp-2">
    AI-powered CV matching and analysis for job descriptions...
  </p>
  
  {/* Features */}
  <div className="flex flex-wrap gap-2 mb-4">
    <Tag>CV Parsing</Tag>
    <Tag>AI Matching</Tag>
    <Tag>Reports</Tag>
  </div>
  
  {/* Footer */}
  <div className="flex items-center justify-between pt-4 border-t border-gray-200">
    <div>
      <span className="text-2xl font-bold text-gray-900">$49</span>
      <span className="text-sm text-gray-500">/month</span>
    </div>
    <Button variant="primary">Start Trial</Button>
  </div>
</div>
```

#### Analysis Result Card
```tsx
<div className="bg-white rounded-lg border border-gray-300 p-6">
  {/* Score Badge */}
  <div className="flex items-center justify-between mb-4">
    <h3 className="text-lg font-semibold">Match Analysis</h3>
    <div className="flex items-center gap-2">
      <CircularProgress value={85} size="lg" color="green" />
      <span className="text-2xl font-bold text-green-600">85%</span>
    </div>
  </div>
  
  {/* Skill Matches */}
  <div className="space-y-3 mb-4">
    <SkillMatch skill="Python" status="matched" proficiency="Expert" />
    <SkillMatch skill="Django" status="matched" proficiency="Advanced" />
    <SkillMatch skill="PostgreSQL" status="missing" />
  </div>
  
  {/* Actions */}
  <div className="flex gap-2">
    <Button variant="outline">View Details</Button>
    <Button variant="primary">Download PDF</Button>
  </div>
</div>
```

### 3. Forms

#### Upload CV Form
```tsx
<form className="space-y-6">
  {/* File Upload Dropzone */}
  <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary transition">
    <UploadIcon className="w-12 h-12 mx-auto text-gray-400 mb-2" />
    <p className="text-sm text-gray-600 mb-2">
      Drag and drop CV file or <span className="text-primary">browse</span>
    </p>
    <p className="text-xs text-gray-500">PDF, DOCX up to 10MB</p>
    <input type="file" className="hidden" accept=".pdf,.docx" />
  </div>
  
  {/* Job Details */}
  <div className="space-y-4">
    <Input label="Job Title" placeholder="e.g., Senior Python Developer" />
    <Textarea 
      label="Job Description" 
      rows={6}
      placeholder="Enter the full job description..."
    />
    <MultiSelect 
      label="Required Skills"
      placeholder="Select skills..."
      options={skillOptions}
    />
    <Select 
      label="Experience Level"
      options={[
        { value: 'entry', label: 'Entry Level' },
        { value: 'mid', label: 'Mid Level' },
        { value: 'senior', label: 'Senior' },
        { value: 'lead', label: 'Lead / Principal' }
      ]}
    />
  </div>
  
  {/* Actions */}
  <div className="flex justify-end gap-2">
    <Button variant="outline" type="button">Cancel</Button>
    <Button variant="primary" type="submit">Analyze CV</Button>
  </div>
</form>
```

### 4. Buttons

```tsx
// Primary
<button className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary-dark transition">
  Start Analysis
</button>

// Secondary
<button className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition">
  Cancel
</button>

// Outline
<button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition">
  View Details
</button>

// Icon Button
<button className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100 transition">
  <IconSettings className="w-5 h-5" />
</button>
```

### 5. Data Display

#### Table (Candidate List)
```tsx
<table className="w-full">
  <thead className="bg-gray-50 border-b border-gray-300">
    <tr>
      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">
        Candidate
      </th>
      <th>Position</th>
      <th>Match Score</th>
      <th>Interview Status</th>
      <th>Actions</th>
    </tr>
  </thead>
  <tbody className="divide-y divide-gray-200">
    <tr className="hover:bg-gray-50">
      <td className="px-6 py-4">
        <div className="flex items-center gap-3">
          <Avatar name="John Doe" src="/avatar.jpg" />
          <div>
            <p className="font-medium text-gray-900">John Doe</p>
            <p className="text-sm text-gray-500">john@example.com</p>
          </div>
        </div>
      </td>
      <td className="px-6 py-4 text-sm text-gray-700">
        Senior Developer
      </td>
      <td className="px-6 py-4">
        <Badge variant="success">85%</Badge>
      </td>
      <td className="px-6 py-4">
        <StatusBadge status="completed" />
      </td>
      <td className="px-6 py-4">
        <DropdownMenu>
          <MenuItem>View Report</MenuItem>
          <MenuItem>Schedule Interview</MenuItem>
          <MenuItem>Send Email</MenuItem>
        </DropdownMenu>
      </td>
    </tr>
  </tbody>
</table>
```

#### Progress Indicators
```tsx
// Linear Progress
<div className="space-y-2">
  <div className="flex justify-between text-sm">
    <span className="text-gray-700">Analyzing CV...</span>
    <span className="text-gray-500">60%</span>
  </div>
  <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
    <div className="h-full bg-primary transition-all duration-300" style={{width: '60%'}} />
  </div>
</div>

// Circular Progress (Match Score)
<div className="relative w-24 h-24">
  <svg className="w-full h-full" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="45" fill="none" stroke="#E5E7EB" strokeWidth="10" />
    <circle 
      cx="50" cy="50" r="45" fill="none" 
      stroke="#10B981" strokeWidth="10"
      strokeDasharray="282.7" 
      strokeDashoffset={282.7 * (1 - 0.85)}
      strokeLinecap="round"
      transform="rotate(-90 50 50)"
    />
  </svg>
  <div className="absolute inset-0 flex items-center justify-center">
    <span className="text-2xl font-bold">85</span>
  </div>
</div>
```

### 6. Modals & Dialogs

#### Purchase Confirmation Modal
```tsx
<Modal isOpen={isOpen} onClose={onClose}>
  <div className="p-6">
    <h2 className="text-2xl font-bold mb-4">Purchase Module</h2>
    
    <div className="bg-gray-50 rounded-lg p-4 mb-6">
      <div className="flex items-center gap-4 mb-4">
        <img src="/cv-icon.svg" className="w-12 h-12" />
        <div>
          <h3 className="font-semibold">CV Analysis Module</h3>
          <p className="text-sm text-gray-500">Lifetime license</p>
        </div>
      </div>
      
      <div className="flex justify-between text-lg font-bold">
        <span>Total:</span>
        <span>$299.00</span>
      </div>
    </div>
    
    <StripePaymentForm />
    
    <div className="flex gap-2 mt-6">
      <Button variant="outline" onClick={onClose}>Cancel</Button>
      <Button variant="primary">Complete Purchase</Button>
    </div>
  </div>
</Modal>
```

---

## Key Pages

### 1. Dashboard (Home)
```
┌─────────────────────────────────────────────────────┐
│  Dashboard                                          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Active   │ │ CVs      │ │ Interviews│           │
│  │ Modules  │ │ Analyzed │ │ Completed │           │
│  │    2     │ │   145    │ │    89     │           │
│  └──────────┘ └──────────┘ └──────────┘           │
│                                                      │
│  Recent Activity                                     │
│  ┌────────────────────────────────────────────┐    │
│  │ ✓ CV Analysis completed - John Doe (85%)  │    │
│  │ ⏳ Interview in progress - Jane Smith      │    │
│  │ ✓ Module purchased - CV Analysis           │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  Quick Actions                                       │
│  [Upload CV] [Create Interview] [View Reports]      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 2. Module Marketplace
```
┌─────────────────────────────────────────────────────┐
│  Module Marketplace                                 │
│  [Search...]  [Filter: All Categories ▼]  [Sort ▼] │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │ CV Analysis │ │  Interview  │ │   Email     │  │
│  │             │ │ Simulation  │ │ Campaigns   │  │
│  │ ⭐⭐⭐⭐⭐ │ │ ⭐⭐⭐⭐☆  │ │ ⭐⭐⭐⭐☆   │  │
│  │             │ │             │ │             │  │
│  │ $49/month   │ │ $69/month   │ │ $39/month   │  │
│  │ [Free Trial]│ │ [Free Trial]│ │ [Free Trial]│  │
│  └─────────────┘ └─────────────┘ └─────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### 3. CV Analysis Workflow
```
Step 1: Upload
┌─────────────────────────────────────────────────────┐
│  Upload CV for Analysis                             │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────┐ │
│  │  📄  Drag and drop CV or browse                │ │
│  │     PDF, DOCX up to 10MB                       │ │
│  └───────────────────────────────────────────────┘ │
│                                                      │
│  Job Details                                         │
│  Job Title:     [Senior Python Developer       ]    │
│  Description:   [Multiline textarea...         ]    │
│  Skills:        [Python] [Django] [PostgreSQL] +    │
│  Level:         [Senior ▼]                          │
│                                                      │
│  [Cancel]  [Analyze CV →]                           │
└─────────────────────────────────────────────────────┘

Step 2: Processing
┌─────────────────────────────────────────────────────┐
│  Analyzing CV...                                    │
├─────────────────────────────────────────────────────┤
│  ✓ File uploaded                                    │
│  ✓ Text extracted                                   │
│  ⏳ AI analysis in progress... 60%                  │
│  ░ Generating report                                │
│                                                      │
│  [████████████████░░░░░░░░] 60%                     │
│  Estimated time remaining: 15 seconds               │
└─────────────────────────────────────────────────────┘

Step 3: Results
┌─────────────────────────────────────────────────────┐
│  CV Analysis Results                   [Download PDF]│
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐                                    │
│  │     85      │  Match Score                       │
│  │   ⭕⭕⭕  │  Strong Match                        │
│  └─────────────┘                                    │
│                                                      │
│  Skill Comparison                                    │
│  ✓ Python         Expert      (Required)            │
│  ✓ Django         Advanced    (Required)            │
│  ⚠ PostgreSQL     Not Found   (Required)            │
│  ✓ Docker         Intermediate (Preferred)          │
│                                                      │
│  Experience: 8 years (Requirement: 5+ years) ✓      │
│  Education: B.S. Computer Science ✓                 │
│                                                      │
│  Recommendations:                                    │
│  Strong candidate with excellent Python/Django...   │
│                                                      │
│  [← Back]  [Create Interview]  [Share Results]      │
└─────────────────────────────────────────────────────┘
```

### 4. Module Settings
```
┌─────────────────────────────────────────────────────┐
│  CV Analysis Settings                               │
├─────────────────────────────────────────────────────┤
│  General                                             │
│  ┌────────────────────────────────────────────┐    │
│  │ Module Status:  [Enabled ✓]                │    │
│  │ API Access:     [Enabled ✓]                │    │
│  │ Webhooks:       [Configure →]              │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  Usage Limits                                        │
│  ┌────────────────────────────────────────────┐    │
│  │ Max CV Uploads:   [100] per month          │    │
│  │ Current Usage:    45 / 100 (45%)           │    │
│  │ [██████░░░░░░░░░░░░░]                       │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  Integrations                                        │
│  ┌────────────────────────────────────────────┐    │
│  │ Interview Simulation  [Connected ✓]        │    │
│  │ Email Module          [Not Installed]      │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  [Cancel]  [Save Changes]                           │
└─────────────────────────────────────────────────────┘
```

---

## Mobile Responsiveness

### Mobile Dashboard (< 640px)
```
┌─────────────────────┐
│ ☰  Logo  🔔  👤    │ ← Hamburger menu
├─────────────────────┤
│                     │
│ Active Modules: 2   │
│ CVs Analyzed: 145   │
│ Interviews: 89      │
│                     │
│ [Upload CV]         │
│ [Create Interview]  │
│                     │
│ Recent Activity     │
│ ┌─────────────────┐ │
│ │ CV Analysis ✓   │ │
│ │ John Doe (85%)  │ │
│ └─────────────────┘ │
│                     │
└─────────────────────┘
```

---

## Accessibility Features

1. **Keyboard Navigation**: Tab order, focus indicators, shortcuts (Alt+S = Search)
2. **Screen Readers**: ARIA labels, semantic HTML, alt text
3. **Color Contrast**: 4.5:1 minimum for text
4. **Focus States**: Clear blue outline on interactive elements
5. **Error Messages**: Associated with form fields via `aria-describedby`

---

## Animation & Transitions

```css
/* Default transitions */
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1);

/* Hover effects */
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

/* Loading spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Progress bar */
.progress-bar {
  transition: width 300ms ease-in-out;
}
```

---

## Component Reusability

All components built with:
- **Tailwind CSS** for styling
- **Radix UI** for accessible primitives (Dialog, Dropdown, etc.)
- **React Hook Form** for forms
- **Recharts** for data visualization

Example component structure:
```
src/components/
  ├── ui/              # Reusable primitives
  │   ├── Button.tsx
  │   ├── Input.tsx
  │   ├── Card.tsx
  │   └── Modal.tsx
  ├── modules/         # Module-specific
  │   ├── CVUploadForm.tsx
  │   ├── AnalysisResult.tsx
  │   └── InterviewQuestions.tsx
  └── layout/          # Layout components
      ├── Sidebar.tsx
      ├── TopNav.tsx
      └── PageHeader.tsx
```

---

## Design System Tools

**Figma Component Library:** Shareable design system with all components
**Storybook:** Component documentation and testing
**Tailwind Config:** Centralized theming

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          dark: '#4338CA',
        },
      },
    },
  },
};
```

---

## Summary

This design system provides:
✓ Professional, Odoo-inspired aesthetic
✓ Reusable component library
✓ Responsive layouts
✓ Accessibility compliance
✓ Scalable for new modules
