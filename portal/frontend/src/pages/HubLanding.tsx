import React, { useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  MOCK_AGENTS,
  MOCK_TOOLS,
  MOCK_SYNC_EVENTS,
  MOCK_HEALTH_METRICS,
  searchAgents,
  Agent,
} from '../lib/hub-constants'
import { useTheme } from '../lib/ThemeContext'

// Icons (using simple SVG inline for no external deps)
const SearchIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
    />
  </svg>
)

const SunIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
    />
  </svg>
)

const MoonIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
    />
  </svg>
)

const CheckIcon = () => (
  <svg
    className="w-5 h-5"
    fill="currentColor"
    viewBox="0 0 20 20"
  >
    <path
      fillRule="evenodd"
      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
      clipRule="evenodd"
    />
  </svg>
)

const AlertIcon = () => (
  <svg
    className="w-5 h-5"
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M12 9v2m0 4v2m0-6a4 4 0 100 8 4 4 0 000-8z"
    />
  </svg>
)

// KPI Card Component
interface KPICardProps {
  label: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  accentColor: string
}

const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  subtitle,
  icon,
  accentColor,
}) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      whileHover={{ scale: 1.02, y: -4 }}
      className={`relative p-6 rounded-lg border transition-all ${
        isDark
          ? 'bg-slate-800 border-slate-700 hover:border-slate-600'
          : 'bg-white border-gray-200 hover:border-gray-300'
      }`}
    >
      <div
        className="absolute inset-0 rounded-lg opacity-0 hover:opacity-10 transition-opacity"
        style={{ backgroundColor: accentColor }}
      />

      <div className="relative">
        <div className="flex items-start justify-between mb-4">
          <div
            className="p-2 rounded-lg"
            style={{
              backgroundColor: accentColor + '20',
              color: accentColor,
            }}
          >
            {icon}
          </div>
        </div>

        <div className="text-sm font-medium opacity-70 mb-2">{label}</div>
        <div className="text-3xl font-bold mb-1">{value}</div>

        {subtitle && (
          <div className="text-xs opacity-60">
            {subtitle}
          </div>
        )}
      </div>
    </motion.div>
  )
}

// Navigation Card Component
interface NavCardProps {
  title: string
  description: string
  to: string
  icon: React.ReactNode
  count?: number
}

const NavCard: React.FC<NavCardProps> = ({
  title,
  description,
  to,
  icon,
  count,
}) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.98 }}
    >
      <Link
        to={to}
        className={`block p-6 rounded-lg border transition-all ${
          isDark
            ? 'bg-slate-800 border-slate-700 hover:border-blue-500 hover:bg-slate-700'
            : 'bg-white border-gray-200 hover:border-blue-400 hover:bg-gray-50'
        }`}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="text-3xl">{icon}</div>
          {count && (
            <span className="text-xs font-bold bg-blue-500 text-white px-2 py-1 rounded-full">
              {count}
            </span>
          )}
        </div>
        <h3 className="font-semibold mb-2">{title}</h3>
        <p className="text-sm opacity-70">{description}</p>
      </Link>
    </motion.div>
  )
}

// Search Results Component
interface SearchResultsProps {
  results: Agent[]
  onClose: () => void
}

const SearchResults: React.FC<SearchResultsProps> = ({ results, onClose }) => {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={`absolute top-16 left-0 right-0 z-50 rounded-lg border shadow-lg ${
        isDark
          ? 'bg-slate-800 border-slate-700'
          : 'bg-white border-gray-200'
      }`}
    >
      <div className="max-h-96 overflow-y-auto">
        {results.length === 0 ? (
          <div className="p-4 text-center opacity-60">No agents found</div>
        ) : (
          results.map((agent, idx) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={onClose}
              className={`p-4 border-b cursor-pointer transition-colors hover:bg-blue-500 hover:bg-opacity-10 ${
                isDark ? 'border-slate-700' : 'border-gray-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="font-semibold">{agent.name}</div>
                  <div className="text-xs opacity-60">{agent.code}</div>
                  <div className="text-sm opacity-70 mt-1">
                    {agent.description}
                  </div>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    {agent.aliases.map(alias => (
                      <span
                        key={alias}
                        className={`text-xs px-2 py-1 rounded ${
                          isDark
                            ? 'bg-slate-700'
                            : 'bg-gray-200'
                        }`}
                      >
                        {alias}
                      </span>
                    ))}
                  </div>
                </div>
                <span
                  className={`text-xs px-2 py-1 rounded font-medium ${
                    agent.status === 'operational'
                      ? 'bg-green-500 bg-opacity-20 text-green-400'
                      : agent.status === 'new'
                        ? 'bg-blue-500 bg-opacity-20 text-blue-400'
                        : 'bg-yellow-500 bg-opacity-20 text-yellow-400'
                  }`}
                >
                  {agent.status}
                </span>
              </div>
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  )
}

// Sync Timeline Component
const SyncTimeline: React.FC = () => {
  const { theme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.4 }}
      className={`p-6 rounded-lg border ${
        isDark
          ? 'bg-slate-800 border-slate-700'
          : 'bg-white border-gray-200'
      }`}
    >
      <h3 className="text-lg font-semibold mb-6">Recent Sync Events</h3>

      <div className="space-y-4">
        {MOCK_SYNC_EVENTS.map((event, idx) => (
          <motion.div
            key={event.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + idx * 0.1 }}
            className="flex gap-4"
          >
            {/* Timeline dot and line */}
            <div className="flex flex-col items-center">
              <motion.div
                animate={{
                  scale: [1, 1.2, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: idx * 0.2,
                }}
                className={`w-3 h-3 rounded-full ${
                  event.status === 'success'
                    ? 'bg-green-500'
                    : event.status === 'partial'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                }`}
              />
              {idx < MOCK_SYNC_EVENTS.length - 1 && (
                <div
                  className={`w-0.5 h-8 ${
                    isDark ? 'bg-slate-700' : 'bg-gray-300'
                  }`}
                />
              )}
            </div>

            {/* Event content */}
            <div className="flex-1 pb-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium">{event.message}</p>
                  <p className="text-sm opacity-60 mt-1">
                    {event.itemsSync} items · {event.duration}s
                  </p>
                </div>
                <time className="text-xs opacity-60">
                  {event.timestamp.toLocaleTimeString()}
                </time>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-6 py-2 px-4 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors"
      >
        View Full Timeline
      </motion.button>
    </motion.div>
  )
}

// Main Component
const HubLanding: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  const searchResults = useMemo(() => {
    return searchQuery.trim() ? searchAgents(searchQuery) : []
  }, [searchQuery])

  const showSearchResults = searchQuery.trim().length > 0

  const formatTime = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`

    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`

    return date.toLocaleDateString()
  }

  return (
    <div
      className={`min-h-screen transition-colors duration-300 ${
        isDark
          ? 'bg-slate-950 text-white'
          : 'bg-gray-50 text-gray-900'
      }`}
    >
      {/* Header with Theme Toggle */}
      <div className={`border-b ${isDark ? 'border-slate-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-6 py-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Codex Portal Master</h1>
            <p className="text-sm opacity-70 mt-1">
              Agent Registry & Knowledge Base v5.0
            </p>
          </div>

          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            className={`p-2 rounded-lg transition-colors ${
              isDark
                ? 'bg-slate-800 hover:bg-slate-700'
                : 'bg-gray-200 hover:bg-gray-300'
            }`}
            aria-label="Toggle theme"
          >
            {isDark ? <SunIcon /> : <MoonIcon />}
          </motion.button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <KPICard
            label="Total Agents"
            value={MOCK_HEALTH_METRICS.totalAgents}
            subtitle="All segments"
            icon={<span className="text-xl">🤖</span>}
            accentColor="#3b82f6"
          />
          <KPICard
            label="Total Tools"
            value={MOCK_HEALTH_METRICS.totalTools}
            subtitle="Active integrations"
            icon={<span className="text-xl">⚙️</span>}
            accentColor="#10b981"
          />
          <KPICard
            label="Last Sync"
            value={formatTime(MOCK_HEALTH_METRICS.lastSyncTime)}
            subtitle="Registry synchronized"
            icon={<span className="text-xl">🔄</span>}
            accentColor="#f59e0b"
          />
          <KPICard
            label="Health"
            value={`${MOCK_HEALTH_METRICS.healthPercentage}%`}
            subtitle={`${MOCK_HEALTH_METRICS.operationalServices}/${MOCK_HEALTH_METRICS.totalTools} services`}
            icon={<span className="text-xl">✓</span>}
            accentColor="#06b6d4"
          />
        </div>

        {/* Quick Search Box */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-12 relative"
        >
          <div
            className={`relative rounded-lg border ${
              isDark
                ? 'bg-slate-800 border-slate-700'
                : 'bg-white border-gray-200'
            }`}
          >
            <div className="absolute left-4 top-1/2 -translate-y-1/2 opacity-60">
              <SearchIcon />
            </div>
            <input
              type="text"
              placeholder="Search agents by name, code, or alias..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className={`w-full pl-12 pr-4 py-3 rounded-lg outline-none transition-colors ${
                isDark
                  ? 'bg-slate-800 text-white placeholder-slate-500'
                  : 'bg-white text-gray-900 placeholder-gray-400'
              }`}
            />

            {/* Search Results */}
            {showSearchResults && (
              <SearchResults
                results={searchResults}
                onClose={() => setSearchQuery('')}
              />
            )}
          </div>

          {searchQuery && !showSearchResults && (
            <p className="mt-2 text-sm opacity-60">
              No results for "{searchQuery}"
            </p>
          )}
        </motion.div>

        {/* Navigation Menu */}
        <div className="mb-12">
          <h2 className="text-xl font-semibold mb-6">Navigation</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <NavCard
              title="Agents"
              description="Browse all AI agents and their configurations"
              to="/agents"
              icon="🤖"
              count={MOCK_AGENTS.length}
            />
            <NavCard
              title="Tools"
              description="Explore available tools and integrations"
              to="/tools"
              icon="⚙️"
              count={MOCK_TOOLS.length}
            />
            <NavCard
              title="Knowledge Base"
              description="Access RAG collections and documentation"
              to="/knowledge"
              icon="📚"
            />
            <NavCard
              title="Documentation"
              description="Read guides, APIs, and architecture docs"
              to="/docs"
              icon="📖"
            />
          </div>
        </div>

        {/* Sync Timeline and Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sync Timeline */}
          <div className="lg:col-span-2">
            <SyncTimeline />
          </div>

          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className={`p-6 rounded-lg border space-y-6 ${
              isDark
                ? 'bg-slate-800 border-slate-700'
                : 'bg-white border-gray-200'
            }`}
          >
            <div>
              <h3 className="text-lg font-semibold mb-4">Services Status</h3>

              <div className="space-y-3">
                {[
                  { label: 'Operational', count: 13, color: 'green' },
                  { label: 'Beta', count: 1, color: 'blue' },
                  { label: 'Planned', count: 0, color: 'gray' },
                ].map(stat => (
                  <div key={stat.label} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div
                        className={`w-2 h-2 rounded-full bg-${stat.color}-500`}
                      />
                      <span className="text-sm">{stat.label}</span>
                    </div>
                    <span className="font-semibold">{stat.count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className={`border-t ${isDark ? 'border-slate-700' : 'border-gray-200'}`} />

            <div>
              <h4 className="font-medium mb-3">Latest Updates</h4>
              <ul className="space-y-2 text-sm opacity-70">
                <li className="flex gap-2">
                  <span className="text-green-400">+</span>
                  <span>5 new vertical agents (S6-S10)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-400">✓</span>
                  <span>RAG collections integrated</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-yellow-400">→</span>
                  <span>Routing rules updated</span>
                </li>
              </ul>
            </div>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full py-2 px-4 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-sm font-medium transition-opacity hover:opacity-90"
            >
              View Full Registry
            </motion.button>
          </motion.div>
        </div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className={`mt-16 pt-8 border-t ${
            isDark ? 'border-slate-800' : 'border-gray-200'
          }`}
        >
          <div className="flex items-center justify-between text-sm opacity-60">
            <p>Portal Knowledge | Manta Maestro v5.0</p>
            <p>ADK-5 Layer Architecture</p>
          </div>
        </motion.footer>
      </div>
    </div>
  )
}

export default HubLanding
