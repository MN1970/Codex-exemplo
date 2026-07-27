/**
 * FeedbackAnalyticsDashboard.tsx — Dashboard de analytics de feedback dos agentes.
 *
 * Componente React que exibe:
 * 1. Cards resumidos (total agents, agents com feedback, avg rating)
 * 2. Tabela de estatísticas por agente (avg_rating, trend, feedback_count)
 * 3. Alertas disparados (agentes com baixo desempenho)
 * 4. Drill-down por agente (detalhes)
 *
 * Conecta aos endpoints:
 * - GET /feedback/analytics/by-agent
 * - GET /feedback/analytics/alerts
 */

import React, { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';

interface AgentStat {
  agent_slug: string;
  agent_code?: string;
  avg_rating: number;
  feedback_count: number;
  std_dev?: number;
  trend: 'up' | 'down' | 'stable';
  rating_distribution: Record<string, number>;
  negative_comment_tags: string[];
}

interface FeedbackAlert {
  id: string;
  agent_slug: string;
  agent_code?: string;
  avg_rating: number;
  feedback_count: number;
  trend: string;
  threshold: number;
  action_taken: string;
  triggered_at: string;
  metadata: Record<string, any>;
}

interface AnalyticsData {
  timestamp: string;
  stats: AgentStat[];
  summary: {
    total_agents_analyzed: number;
    agents_with_feedback: number;
    total_feedback_entries: number;
    avg_rating_all_agents: number;
  };
}

const TrendBadge: React.FC<{ trend: string }> = ({ trend }) => {
  const colors: Record<string, string> = {
    'up': 'text-green-600 bg-green-100',
    'down': 'text-red-600 bg-red-100',
    'stable': 'text-yellow-600 bg-yellow-100',
  };

  const icons: Record<string, string> = {
    'up': '↑',
    'down': '↓',
    'stable': '→',
  };

  return (
    <span className={`inline-block px-2 py-1 rounded text-sm font-semibold ${colors[trend] || colors['stable']}`}>
      {icons[trend] || '→'} {trend}
    </span>
  );
};

const RatingBadge: React.FC<{ rating: number; threshold?: number }> = ({ rating, threshold = 3.5 }) => {
  let bgColor = 'bg-green-100';
  let textColor = 'text-green-800';

  if (rating < 2.5) {
    bgColor = 'bg-red-100';
    textColor = 'text-red-800';
  } else if (rating < 3.0) {
    bgColor = 'bg-orange-100';
    textColor = 'text-orange-800';
  } else if (rating < threshold) {
    bgColor = 'bg-yellow-100';
    textColor = 'text-yellow-800';
  }

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${bgColor} ${textColor}`}>
      {rating.toFixed(2)} ★
    </span>
  );
};

export const FeedbackAnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [alerts, setAlerts] = useState<FeedbackAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<AgentStat | null>(null);
  const [weeksBack, setWeeksBack] = useState(1);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);

        // Busca analytics agregadas
        const analyticsRes = await fetch(`/api/feedback/analytics/by-agent?weeks_back=${weeksBack}`);
        if (!analyticsRes.ok) {
          throw new Error('Failed to fetch analytics');
        }
        const analyticsData: AnalyticsData = await analyticsRes.json();
        setAnalytics(analyticsData);

        // Busca alertas
        const alertsRes = await fetch('/api/feedback/analytics/alerts?limit=20');
        if (!alertsRes.ok) {
          throw new Error('Failed to fetch alerts');
        }
        const alertsData: FeedbackAlert[] = await alertsRes.json();
        setAlerts(alertsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [weeksBack]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-lg text-gray-500">Carregando analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        <strong>Erro:</strong> {error}
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-yellow-800">
        <strong>Aviso:</strong> Nenhum dado de feedback disponível.
      </div>
    );
  }

  const summary = analytics.summary;
  const lowRatedAgents = analytics.stats.filter(s => s.avg_rating < 3.5).sort((a, b) => a.avg_rating - b.avg_rating);

  // Dados para chart de trend (simulado — últimos 7 dias)
  const trendData = [
    { date: '2026-07-20', avg_rating: 3.6 },
    { date: '2026-07-21', avg_rating: 3.55 },
    { date: '2026-07-22', avg_rating: 3.5 },
    { date: '2026-07-23', avg_rating: 3.48 },
    { date: '2026-07-24', avg_rating: 3.45 },
    { date: '2026-07-25', avg_rating: 3.42 },
    { date: '2026-07-26', avg_rating: 3.4 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Feedback Analytics</h1>
          <p className="text-gray-600 mt-1">Análise de desempenho dos agentes Manta</p>
        </div>
        <div className="flex gap-2">
          {[1, 2, 4].map(weeks => (
            <Button
              key={weeks}
              variant={weeksBack === weeks ? 'default' : 'outline'}
              onClick={() => setWeeksBack(weeks)}
              className="text-sm"
            >
              {weeks}w
            </Button>
          ))}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Agentes Analisados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_agents_analyzed}</div>
            <p className="text-xs text-gray-500 mt-1">total de agentes</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Com Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.agents_with_feedback}</div>
            <p className="text-xs text-gray-500 mt-1">agentes com dados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_feedback_entries}</div>
            <p className="text-xs text-gray-500 mt-1">registros nos últimos {weeksBack}w</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Rating Geral</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.avg_rating_all_agents.toFixed(2)}</div>
            <p className="text-xs text-gray-500 mt-1">média em {weeksBack} semana(s)</p>
          </CardContent>
        </Card>
      </div>

      {/* Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Trend Semanal (Avg Rating)</CardTitle>
          <CardDescription>Evolução da média geral</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[2.5, 4]} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="avg_rating"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={{ fill: '#3b82f6', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Low-Rated Agents Table */}
      {lowRatedAgents.length > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-red-900">⚠ Agentes com <3.5 Stars</CardTitle>
            <CardDescription>{lowRatedAgents.length} agente(s) abaixo do threshold</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 px-4">Agente</th>
                    <th className="text-left py-2 px-4">Rating</th>
                    <th className="text-left py-2 px-4">Trend</th>
                    <th className="text-left py-2 px-4">Feedback</th>
                    <th className="text-left py-2 px-4">StdDev</th>
                  </tr>
                </thead>
                <tbody>
                  {lowRatedAgents.map(agent => (
                    <tr
                      key={agent.agent_slug}
                      className="border-b hover:bg-red-100 cursor-pointer transition"
                      onClick={() => setSelectedAgent(agent)}
                    >
                      <td className="py-2 px-4 font-medium">{agent.agent_slug}</td>
                      <td className="py-2 px-4">
                        <RatingBadge rating={agent.avg_rating} threshold={3.5} />
                      </td>
                      <td className="py-2 px-4">
                        <TrendBadge trend={agent.trend} />
                      </td>
                      <td className="py-2 px-4">{agent.feedback_count}</td>
                      <td className="py-2 px-4">{agent.std_dev?.toFixed(2) || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Agents Table */}
      <Card>
        <CardHeader>
          <CardTitle>Estatísticas por Agente</CardTitle>
          <CardDescription>Clique para detalhar</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4">Agente</th>
                  <th className="text-left py-2 px-4">Rating</th>
                  <th className="text-left py-2 px-4">Trend</th>
                  <th className="text-left py-2 px-4">Feedback</th>
                  <th className="text-left py-2 px-4">StdDev</th>
                </tr>
              </thead>
              <tbody>
                {analytics.stats.map(agent => (
                  <tr
                    key={agent.agent_slug}
                    className="border-b hover:bg-gray-50 cursor-pointer transition"
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <td className="py-2 px-4 font-medium">{agent.agent_slug}</td>
                    <td className="py-2 px-4">
                      <RatingBadge rating={agent.avg_rating} />
                    </td>
                    <td className="py-2 px-4">
                      <TrendBadge trend={agent.trend} />
                    </td>
                    <td className="py-2 px-4">{agent.feedback_count}</td>
                    <td className="py-2 px-4">{agent.std_dev?.toFixed(2) || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="text-orange-900">🔔 Alertas Disparados</CardTitle>
            <CardDescription>{alerts.length} alerta(s) nos últimos 4 semanas</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className="bg-white border border-orange-200 rounded p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-gray-900">{alert.agent_slug}</h4>
                      <p className="text-sm text-gray-600">
                        Rating: {alert.avg_rating.toFixed(2)} | Feedback: {alert.feedback_count} |
                        Ação: <span className="font-medium">{alert.action_taken}</span>
                      </p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(alert.triggered_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Agent Detail Modal (Placeholder) */}
      {selectedAgent && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>{selectedAgent.agent_slug}</CardTitle>
                <CardDescription>{selectedAgent.agent_code}</CardDescription>
              </div>
              <Button variant="ghost" onClick={() => setSelectedAgent(null)}>✕</Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Avg Rating</p>
                <p className="text-2xl font-bold">{selectedAgent.avg_rating.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Feedback Count</p>
                <p className="text-2xl font-bold">{selectedAgent.feedback_count}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">StdDev</p>
                <p className="text-2xl font-bold">{selectedAgent.std_dev?.toFixed(2) || 'N/A'}</p>
              </div>
            </div>

            {selectedAgent.negative_comment_tags.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700">Palavras frequentes (feedback negativo)</p>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedAgent.negative_comment_tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div>
              <p className="text-sm font-semibold text-gray-700">Rating Distribution</p>
              <ResponsiveContainer width="100%" height={150}>
                <BarChart
                  data={Object.entries(selectedAgent.rating_distribution).map(([rating, count]) => ({
                    rating: ['👎', '😐', '👍'][parseInt(rating) + 1] || rating,
                    count,
                  }))}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="rating" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
