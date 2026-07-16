# Portal Landing Page Implementation Guide

## Overview

The Portal Landing page (`HubLanding.tsx`) serves as the entry point for the Codex-exemplo Portal Master, displaying KPIs, navigation, and system status using React 19, Framer Motion, and Tailwind CSS.

## File Structure

```
src/
├── pages/
│   └── HubLanding.tsx          # Main landing page component
├── lib/
│   ├── hub-constants.ts         # Mock data and agent/tool definitions
│   └── ThemeContext.tsx         # Dark/light theme management
├── App.tsx                      # Updated with theme provider
├── index.css                    # Tailwind CSS base styles
├── main.tsx                     # Entry point (unchanged)
└── ...

Root directory:
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration for Tailwind
├── package.json                 # Dependencies
└── ...
```

## Key Features

### 1. KPI Cards (4 Cards)
- **Total Agents**: 20 agents across horizontal, infrastructure, and vertical segments
- **Total Tools**: 14 tools with operational status
- **Last Sync**: Relative time formatting (e.g., "5m ago")
- **Health Status**: Percentage with service count breakdown

**Animation**: Fade-in on load, scale-up on hover with smooth transitions.

### 2. Quick Search Box
- Real-time search across agent names, codes, aliases, and descriptions
- Dropdown results with metadata display
- Clickable results to explore agents
- Responsive filtering with 0 debounce (instant results)

### 3. Navigation Menu (4 Cards)
- **Agents** → `/agents` (count badge: 20)
- **Tools** → `/tools` (count badge: 14)
- **Knowledge Base** → `/knowledge`
- **Documentation** → `/docs`

**Animation**: Hover scale effect with color transitions.

### 4. Sync Timeline
- Recent sync events with status indicators (success/partial/failed)
- Animated timeline dots with pulse effect
- Timestamp display with relative time
- Item count and duration metrics
- "View Full Timeline" action button

### 5. Services Status & Updates
- Quick stats panel showing operational/beta/planned services
- Latest updates list with categorized badges
- "View Full Registry" call-to-action button

## Mock Data

### Agents (20 total)
- **11 Horizontal**: maestro, claims, contratual, imobiliario, orcamento, modelagem, cronograma, bd, apresentacoes, advisory, arquiteto-ia
- **4 Infrastructure (S1-S4)**: rodovias, OAE, ferrovia, metro
- **5 Vertical (S6-S10)**: portos, aeroportos, saneamento, energia, barragens

Each agent includes:
- Unique ID and code (Manta XX/XX-SN format)
- Display name and aliases
- Category and status (operational/partial/new)
- Description
- Tool count

### Tools (14 total)
Balanço de Massa, Paisagismo, Sinalização, Orçamento, MantaCAD, Estrutural, Iluminação, Pavimentação, AskCAD, Terraplenagem, LandXML, IFC, Sondagem, OAE.

Each tool includes:
- Name, port number, and status
- Description
- Associated agents

### Health Metrics
- Operational services: 13/14
- Health percentage: 93%
- Last sync: 5 minutes ago
- Uptime: 99.8%

## Theme System

### Implementation
- **ThemeContext.tsx**: React Context API for theme state
- **Data attribute**: `[data-theme="dark|light"]` on `<html>` element
- **Persistence**: Theme preference saved to localStorage
- **System preference**: Respects OS dark mode preference on first visit

### Dark Theme (Default)
- Background: `#0f172a` (Slate-950)
- Cards: `bg-slate-800` with `border-slate-700`
- Text: White with opacity-based hierarchy
- Accents: Blue, green, yellow, cyan

### Light Theme
- Background: `#f9fafb` (Gray-50)
- Cards: White with gray borders
- Text: Gray-900 with opacity-based hierarchy
- Accents: Blue, green, yellow, cyan

### Toggle Button
Located in the header, uses sun/moon icons for visual feedback.

## Animations

### Framer Motion Animations

1. **KPI Cards**
   - `initial`: opacity 0, y +20px
   - `animate`: opacity 1, y 0
   - `whileHover`: scale 1.02, y -4px
   - Staggered delays (0s - 0.3s)

2. **Search Results**
   - `initial`: opacity 0, y -10px
   - `animate`: opacity 1, y 0
   - Exit animation on close
   - Staggered items (delay * 0.05s)

3. **Sync Timeline**
   - Timeline dots: continuous pulse animation
   - Events: staggered fade-in from left

4. **Navigation Cards**
   - `whileHover`: scale 1.05
   - `whileTap`: scale 0.98

5. **Theme Toggle**
   - `whileHover`: scale 1.1
   - `whileTap`: scale 0.95

## Responsive Design

- **Mobile (< 768px)**: 1-column grid for KPI cards and nav cards
- **Tablet (768px - 1024px)**: 2-column grids
- **Desktop (> 1024px)**: 4-column KPI, 4-column nav, 3-column sync layout

## Component Hierarchy

```
HubLanding (main page)
├── Header with Theme Toggle
├── KPI Cards Section
│   ├── KPICard (×4)
├── Quick Search Section
│   ├── Input field
│   └── SearchResults (conditional)
├── Navigation Menu Section
│   ├── NavCard (×4)
├── Main Content Grid
│   ├── SyncTimeline (left, 2/3 width)
│   └── Services Status (right, 1/3 width)
└── Footer
```

## Utility Functions

### From `hub-constants.ts`

```typescript
// Search agents by name, code, alias, or description
searchAgents(query: string): Agent[]

// Get agent by ID
getAgentById(id: string): Agent | undefined

// Get tool by ID
getToolById(id: string): Tool | undefined
```

### From `ThemeContext.tsx`

```typescript
// React hook for theme control
useTheme(): {
  theme: 'dark' | 'light'
  toggleTheme: () => void
  setTheme: (theme: 'dark' | 'light') => void
}
```

## Usage in App.tsx

```typescript
import HubLanding from './pages/HubLanding'
import { ThemeProvider } from './lib/ThemeContext'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HubLanding />} />
          {/* other routes */}
        </Routes>
      </Router>
    </ThemeProvider>
  )
}
```

## Styling Approach

### Tailwind CSS

All styling uses Tailwind utility classes with:
- Responsive modifiers (sm:, md:, lg:)
- Dark mode support via `isDark` boolean from theme context
- Conditional classes for theme-aware colors
- Custom color palette for status badges

### CSS-in-JS (Framer Motion)

- Inline styles for dynamic colors
- Color accent mapping for KPI cards
- Gradient backgrounds for buttons

## Icons

Simple inline SVG icons (no external icon library dependency):
- SearchIcon
- SunIcon / MoonIcon
- CheckIcon / AlertIcon

## Performance Considerations

1. **Memoization**: `useMemo` for search results to avoid unnecessary filtering
2. **Motion Performance**: Framer Motion GPU acceleration for smooth animations
3. **Lazy Rendering**: SearchResults only render when query is non-empty
4. **No External APIs**: Mock data enables offline-first development

## Future Enhancements

1. **API Integration**
   - Replace mock data with real API calls
   - WebSocket connections for real-time sync events
   - User-specific agent/tool recommendations

2. **Advanced Search**
   - Full-text search with highlighting
   - Filter by agent category, status
   - Search history and saved searches

3. **Dashboard Widgets**
   - Agent performance metrics
   - Tool usage analytics
   - Custom widget layouts

4. **Notifications**
   - Toast notifications for sync updates
   - Email digest summaries
   - Slack integration alerts

5. **Agent Details Modal**
   - Click agent card to see full details
   - Tool associations
   - Related agents
   - Documentation links

## Development Commands

```bash
# Install dependencies
npm install

# Start development server (Vite)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test
```

## Browser Support

- Modern browsers with ES2020+ support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Accessibility

- Semantic HTML structure
- ARIA labels on theme toggle
- Keyboard navigation support
- Color contrast ratios meeting WCAG AA standards
- Motion respects `prefers-reduced-motion`

## Known Limitations

1. Mock data is hard-coded (no real-time updates)
2. Search is client-side only (no backend indexing)
3. Theme preference stored in localStorage (no backend sync)
4. No data persistence across sessions

## Troubleshooting

### Tailwind styles not applying
- Ensure `tailwind.config.js` is in project root
- Check that `index.css` imports `@tailwind` directives
- Clear Vite cache: `rm -rf node_modules/.vite`

### Dark mode not working
- Check that `[data-theme]` attribute is set on `<html>`
- Verify `ThemeProvider` wraps the entire app
- Check browser console for theme context errors

### Animations stuttering
- Reduce animation count if on low-end device
- Check GPU acceleration in browser DevTools
- Consider reducing motion in theme settings

## License

Part of Codex-exemplo / Manta Hub project
