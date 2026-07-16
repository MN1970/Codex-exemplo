# Portal Landing Page - Quick Start Guide

## What Was Implemented

A fully functional Portal Landing page (`HubLanding.tsx`) for the Codex-exemplo Portal Master with:

### 1. Dashboard KPI Cards (4 cards)
- **Total Agents**: 20 (from CLAUDE.md v4.2)
- **Total Tools**: 14 (Balanço, Paisagismo, etc.)
- **Last Sync**: Real-time formatted (e.g., "5m ago")
- **Health Status**: 93% (13/14 services operational)

Each card features:
- Animated entrance (fade + slide)
- Hover effects (scale, glow)
- Custom accent colors (blue, green, yellow, cyan)
- Responsive icons

### 2. Quick Search Box
- Real-time agent search by name, code, or alias
- Dropdown results with full agent metadata
- Instant filtering with visual feedback
- Supports all 20 agents from the registry

### 3. Navigation Menu (4 Cards)
- **Agents** → Explore all AI agents (20 total)
- **Tools** → Browse available tools (14 total)
- **Knowledge Base** → Access RAG collections
- **Documentation** → Read guides and architecture

Each card includes:
- Hover animations (scale, color shift)
- Count badges
- Routing to `/agents`, `/tools`, `/knowledge`, `/docs`

### 4. Sync Timeline Widget
- 3 recent sync events with status indicators
- Color-coded status (green/yellow/red)
- Animated timeline dots with pulsing effect
- Item count and duration metrics
- Relative timestamp display
- View full timeline action button

### 5. Services Status Panel
- Quick stats showing operational/beta/planned counts
- Latest updates list with categorized badges
- Call-to-action buttons for deeper exploration
- Compact layout for quick glance

### 6. Dark/Light Theme Support
- Toggle button in header (sun/moon icon)
- Persistent theme preference (localStorage)
- Respects system dark mode preference
- Smooth color transitions on toggle
- All components have dual-theme support

## File Manifest

### New Files Created

```
src/pages/HubLanding.tsx          (480 lines) - Main landing page component
src/lib/hub-constants.ts          (280 lines) - Mock data with 20 agents & 14 tools
src/lib/ThemeContext.tsx          (60 lines)  - Dark/light theme management
tailwind.config.js                (40 lines)  - Tailwind CSS configuration
postcss.config.js                 (8 lines)   - PostCSS config for Tailwind
IMPLEMENTATION_GUIDE.md           (400 lines) - Complete documentation
QUICK_START.md                    (this file) - Quick start and file manifest
```

### Modified Files

```
src/App.tsx                       - Updated with ThemeProvider wrapper
src/index.css                     - Added Tailwind imports and theme styles
```

## Installation & Running

### Prerequisites
- Node.js 16+ (for React 19 + Vite)
- npm or yarn

### 1. Install Dependencies (if not already done)
```bash
cd /home/user/Codex-exemplo/portal/frontend
npm install
```

This installs:
- `react` ^19.0.0
- `react-dom` ^19.0.0
- `react-router` ^7.0.0
- `framer-motion` ^10.16.0 (for animations)
- `tailwindcss` ^4.0.0 (for styling)
- Plus dev tools (Vite, TypeScript, Autoprefixer)

### 2. Start Development Server
```bash
npm run dev
```

Output:
```
  VITE v7.0.0  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### 3. Open in Browser
Navigate to: **http://localhost:5173/**

You should see:
- Full-width landing page with dark theme by default
- 4 KPI cards at the top
- Quick search box (try searching "barragens" or "energia")
- Navigation menu (4 cards with links)
- Sync timeline on the left
- Services status on the right
- Theme toggle button in header (sun icon for light mode)

### 4. Build for Production
```bash
npm run build
```

Output files in `dist/` directory ready for deployment.

## Architecture Overview

```
HubLanding Component
├── Header (with theme toggle)
├── KPI Section (4 animated cards)
├── Quick Search (with dropdown)
├── Navigation Menu (4 route cards)
└── Main Content Grid
    ├── SyncTimeline (left, 2/3)
    └── Services Status (right, 1/3)

Global Context:
├── ThemeProvider (wraps entire app)
└── ThemeContext (dark/light mode state)

Mock Data Store:
└── hub-constants.ts (20 agents, 14 tools)
```

## Key Design Decisions

### 1. Mock Data First
- No backend API calls required
- All data from `hub-constants.ts`
- Ready for API integration later
- Enables offline development

### 2. Framer Motion for Animations
- Staggered entrance animations for visual hierarchy
- Micro-interactions on hover/click
- Performance optimized (GPU acceleration)
- Smooth transitions between theme changes

### 3. Tailwind CSS + Theme Context
- Utility-first styling approach
- Theme-aware colors using `isDark` boolean
- Responsive grid layouts (mobile-first)
- No CSS-in-JS conflicts

### 4. React Router Integration
- Navigation links to `/agents`, `/tools`, `/knowledge`, `/docs`
- Placeholder pages ready for implementation
- URL-based navigation without page reloads

### 5. TypeScript Strict Mode
- Full type safety across components
- Interface definitions for agents, tools, sync events
- Better IDE autocompletion and error detection

## Component Features Explained

### KPICard Component
```typescript
<KPICard
  label="Total Agents"
  value={20}
  subtitle="All segments"
  icon={<span>🤖</span>}
  accentColor="#3b82f6"
/>
```
- Takes label, value, subtitle, icon, and color
- Reusable across different metric types
- Hover effect with color blending

### NavCard Component
```typescript
<NavCard
  title="Agents"
  description="Browse all AI agents..."
  to="/agents"
  icon="🤖"
  count={20}
/>
```
- Link-based navigation
- Optional count badge
- Hover scale animation

### SearchResults Component
```typescript
{showSearchResults && (
  <SearchResults
    results={searchResults}
    onClose={() => setSearchQuery('')}
  />
)}
```
- Conditional rendering based on query length
- Memoized search results (prevents unnecessary re-renders)
- Interactive items with click-to-close

### SyncTimeline Component
- Standalone component for sync events
- Animated timeline dots with colors
- Relative time formatting
- Responsive layout

## Responsive Behavior

### Mobile (< 768px)
- 1-column grid for KPI cards
- Full-width search box
- 1-column navigation
- Stack layout for sync + status

### Tablet (768px - 1024px)
- 2-column KPI grid
- 2-column navigation grid
- Side-by-side sync + status

### Desktop (> 1024px)
- 4-column KPI grid
- 4-column navigation grid
- 2/3 + 1/3 split for sync + status

## Customization Guide

### Add New Agent to Registry
Edit `src/lib/hub-constants.ts`:
```typescript
export const MOCK_AGENTS: Agent[] = [
  // ... existing agents
  {
    id: 'manta-99',
    code: 'Manta 99',
    name: 'new-agent',
    aliases: ['new', 'alias'],
    category: 'horizontal',
    status: 'operational',
    description: 'New agent description',
    tools: 5,
  },
]
```

### Change Theme Colors
Edit `src/pages/HubLanding.tsx`:
```typescript
<KPICard
  ...
  accentColor="#ff0000"  // Change to custom color
/>
```

### Add Navigation Link
Edit `src/pages/HubLanding.tsx`:
```typescript
<NavCard
  title="New Page"
  to="/new-page"
  icon="📄"
/>
```

Then add route in `src/App.tsx`:
```typescript
<Route path="/new-page" element={<NewPageComponent />} />
```

### Adjust Animations
Edit framer motion `transition` props in `HubLanding.tsx`:
```typescript
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.5, delay: 0.2 }}  // Adjust here
```

## Common Issues & Solutions

### Styles not appearing
```bash
# Clear cache and reinstall
rm -rf node_modules/.vite
npm run dev
```

### Theme toggle not working
- Check browser console for errors
- Ensure `ThemeProvider` wraps the app in `App.tsx`
- Check that `data-theme` attribute exists on `<html>`

### Search not working
- Check that agent names include search terms
- Try "barragens", "energia", "maestro" as test queries
- Check browser console for JS errors

### Animations stuttering
- Check if running on low-end device
- Try closing other browser tabs
- Check GPU acceleration in DevTools Performance tab

## Next Steps for Enhancement

### Phase 1: Agent Details Page
- Click on agent card to view full details
- Show tool associations
- Display agent status and history

### Phase 2: Real-time Updates
- WebSocket connection for sync events
- Auto-refresh KPI metrics
- Live agent status updates

### Phase 3: Advanced Search
- Full-text search with highlighting
- Filter by category and status
- Search history and saved searches

### Phase 4: Analytics Dashboard
- Agent usage metrics
- Tool performance stats
- System health trends

## Testing the Implementation

### Manual Testing Checklist

- [ ] Page loads without errors in browser console
- [ ] Dark theme is default
- [ ] Theme toggle switches between dark/light
- [ ] All 4 KPI cards display with correct values
- [ ] Search box filters agents in real-time
- [ ] Try searching: "barragens", "energia", "maestro", "portos"
- [ ] Click navigation cards - should route (show placeholder pages)
- [ ] Hover animations work smoothly on KPI cards
- [ ] Timeline events display with colors
- [ ] Responsive layout works on mobile (viewport < 768px)
- [ ] Scroll to see footer
- [ ] Refresh page - theme preference persists

### Performance Metrics (Target)
- First Paint: < 1s
- Largest Contentful Paint: < 2s
- Interaction to Paint: < 100ms
- Cumulative Layout Shift: < 0.1

## File Sizes

```
src/pages/HubLanding.tsx       ~15 KB (minified)
src/lib/hub-constants.ts       ~10 KB (minified)
src/lib/ThemeContext.tsx       ~2 KB (minified)
Total JS bundle impact         ~27 KB
```

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Support & Documentation

For detailed information, see:
- `IMPLEMENTATION_GUIDE.md` - Complete feature documentation
- Component JSDoc comments in source files
- TypeScript interfaces for type safety

## License

Part of Codex-exemplo / Manta Hub - Manta Associados
Version 5.0 - ADK-5 Layer Architecture
