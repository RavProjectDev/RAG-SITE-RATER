"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Loader2, BarChart3, TrendingUp, Users, AlertTriangle, CheckCircle, XCircle, Trophy, Medal, ChevronDown, ChevronUp } from "lucide-react";

interface AnalyticsData {
  summary: {
    totalResponses: number;
    hallucinationStats: {
      total: number;
      byType: Record<string, number>;
      byModel: Record<string, Record<string, number>>;
    };
  };
  leaderboard: Array<{
    rank: number;
    configuration: string;
    elo: number;
    winRate: number;
    wins: number;
    losses: number;
    ties: number;
    bothBad: number;
    totalComparisons: number;
  }>;
  modelPerformance: Record<string, {
    wins: number;
    losses: number;
    ties: number;
    bothBad: number;
  }>;
  recentResponses: Array<{
    _id: string;
    vote: string;
    query: string;
    model_a_id: string;
    model_b_id: string;
    model_a_response: string;
    model_b_response: string;
    timestamp: string;
    created_at: string;
    has_flags: boolean;
    hallucination_flags: {
      modelA: string[];
      modelB: string[];
    };
  }>;
}

export default function AnalyticsPage() {
  const [password, setPassword] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [expandedResponses, setExpandedResponses] = useState<Record<string, boolean>>({});

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/analytics?password=${encodeURIComponent(password)}`);
      
      if (response.status === 401) {
        setError("Invalid password. Please try again.");
        setPassword("");
        return;
      }

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || "Failed to authenticate");
        return;
      }

      setIsAuthenticated(true);
      fetchAnalytics();
    } catch (err) {
      setError("An error occurred. Please try again.");
      console.error("Login error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    setIsLoadingData(true);
    setError(null);

    try {
      const response = await fetch(`/api/analytics?password=${encodeURIComponent(password)}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || "Failed to fetch analytics");
        return;
      }

      const analyticsData = await response.json();
      setData(analyticsData);
    } catch (err) {
      setError("Failed to load analytics data");
      console.error("Analytics fetch error:", err);
    } finally {
      setIsLoadingData(false);
    }
  };

  // Login form
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Analytics Dashboard</CardTitle>
            <p className="text-center text-sm text-gray-500 dark:text-gray-400 mt-2">
              Enter password to access analytics
            </p>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter passcode"
                  required
                  className="mt-1"
                />
              </div>
              {error && (
                <div className="text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded">
                  {error}
                </div>
              )}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  "Access Analytics"
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Analytics dashboard
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              User comparison response analytics
            </p>
          </div>
          <Button
            variant="outline"
            onClick={() => {
              setIsAuthenticated(false);
              setPassword("");
              setData(null);
            }}
          >
            Logout
          </Button>
        </div>

        {isLoadingData ? (
          <Card>
            <CardContent className="pt-6 pb-6">
              <div className="flex flex-col items-center justify-center space-y-4">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
                <p className="text-center text-gray-600 dark:text-gray-400">
                  Loading analytics...
                </p>
              </div>
            </CardContent>
          </Card>
        ) : error ? (
          <Card>
            <CardContent className="pt-6 pb-6">
              <div className="text-center text-red-600 dark:text-red-400">
                <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
                <p>{error}</p>
              </div>
            </CardContent>
          </Card>
        ) : data ? (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Responses</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{data.summary.totalResponses}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Hallucination Flags</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{data.summary.hallucinationStats.total}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Issues flagged by users
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Elo Leaderboard */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Trophy className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                  <CardTitle>Elo Rating Leaderboard</CardTitle>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Rankings based on pairwise comparisons. Higher Elo = stronger performance.
                </p>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Rank</th>
                        <th className="text-left p-2">Configuration</th>
                        <th className="text-center p-2">Elo Score</th>
                        <th className="text-center p-2">Win Rate</th>
                        <th className="text-center p-2">Wins</th>
                        <th className="text-center p-2">Losses</th>
                        <th className="text-center p-2">Ties</th>
                        <th className="text-center p-2">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.leaderboard.map((entry, index) => {
                        const rank = index + 1;
                        const getRankIcon = () => {
                          if (rank === 1) return <Trophy className="h-4 w-4 text-yellow-500" />;
                          if (rank === 2) return <Medal className="h-4 w-4 text-gray-400" />;
                          if (rank === 3) return <Medal className="h-4 w-4 text-amber-600" />;
                          return null;
                        };
                        return (
                          <tr 
                            key={entry.configuration} 
                            className={`border-b hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors ${
                              rank <= 3 ? 'bg-yellow-50/50 dark:bg-yellow-900/10' : ''
                            }`}
                          >
                            <td className="p-2">
                              <div className="flex items-center gap-2">
                                <span className="font-bold">{rank}</span>
                                {getRankIcon()}
                              </div>
                            </td>
                            <td className="p-2 font-mono text-xs">{entry.configuration}</td>
                            <td className="text-center p-2">
                              <span className="font-bold text-lg">{entry.elo}</span>
                            </td>
                            <td className="text-center p-2 font-semibold">
                              {entry.winRate.toFixed(1)}%
                            </td>
                            <td className="text-center p-2 text-green-600 dark:text-green-400">
                              {entry.wins}
                            </td>
                            <td className="text-center p-2 text-red-600 dark:text-red-400">
                              {entry.losses}
                            </td>
                            <td className="text-center p-2 text-yellow-600 dark:text-yellow-400">
                              {entry.ties}
                            </td>
                            <td className="text-center p-2 text-gray-600 dark:text-gray-400">
                              {entry.totalComparisons}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
                {data.leaderboard.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    No comparison data available yet. Start comparing models to see rankings!
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Model Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Model Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">Model</th>
                        <th className="text-center p-2">Wins</th>
                        <th className="text-center p-2">Losses</th>
                        <th className="text-center p-2">Ties</th>
                        <th className="text-center p-2">Both Bad</th>
                        <th className="text-center p-2">Win Rate</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(data.modelPerformance).map(([model, stats]) => {
                        const total = stats.wins + stats.losses + stats.ties + stats.bothBad;
                        const winRate = total > 0 ? (stats.wins / total) * 100 : 0;
                        return (
                          <tr key={model} className="border-b">
                            <td className="p-2 font-mono text-xs">{model}</td>
                            <td className="text-center p-2 text-green-600 dark:text-green-400">
                              {stats.wins}
                            </td>
                            <td className="text-center p-2 text-red-600 dark:text-red-400">
                              {stats.losses}
                            </td>
                            <td className="text-center p-2 text-yellow-600 dark:text-yellow-400">
                              {stats.ties}
                            </td>
                            <td className="text-center p-2 text-gray-600 dark:text-gray-400">
                              {stats.bothBad}
                            </td>
                            <td className="text-center p-2 font-semibold">
                              {winRate.toFixed(1)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Hallucination Flags */}
            {data.summary.hallucinationStats.total > 0 && (
              <>
                {/* Hallucination Flags by Model */}
                <Card>
                  <CardHeader>
                    <CardTitle>Hallucination Flags by Model</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Breakdown of flagged issues per model configuration
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {Object.entries(data.summary.hallucinationStats.byModel).map(([modelId, flags]) => {
                        const totalModelFlags = Object.values(flags).reduce((sum, count) => sum + count, 0);
                        return (
                          <div key={modelId} className="border-l-4 border-red-500 pl-4">
                            <h4 className="font-semibold text-sm mb-2 font-mono">{modelId}</h4>
                            <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                              Total flags: <span className="font-bold text-red-600">{totalModelFlags}</span>
                            </div>
                            <div className="space-y-1">
                              {Object.entries(flags).map(([type, count]) => (
                                <div key={type} className="flex items-center justify-between p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs">
                                  <span className="capitalize">{type.replace(/_/g, " ")}</span>
                                  <span className="font-semibold text-red-600">{count}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>

                {/* Overall Flag Summary by Type */}
                <Card>
                  <CardHeader>
                    <CardTitle>Flag Summary by Type</CardTitle>
                    <p className="text-sm text-muted-foreground mt-1">
                      Overall distribution across all models
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {Object.entries(data.summary.hallucinationStats.byType)
                        .sort(([, a], [, b]) => b - a)
                        .map(([type, count]) => (
                          <div key={type} className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded">
                            <span className="text-sm font-medium capitalize">{type.replace(/_/g, " ")}</span>
                            <span className="font-bold text-red-600 text-lg">{count}</span>
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}

            {/* Recent Responses */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Responses</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Last 10 comparisons with full response details
                </p>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {data.recentResponses.map((response) => (
                    <div
                      key={response._id}
                      className="p-4 border-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                    >
                      {/* Header */}
                      <div className="flex items-start justify-between mb-3 pb-3 border-b">
                        <div className="flex-1">
                          <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                            Query: {response.query}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
                            <span>Vote: <strong className={
                              response.vote === 'A' ? 'text-blue-600' : 
                              response.vote === 'B' ? 'text-purple-600' : 
                              response.vote === 'tie' ? 'text-yellow-600' : 'text-red-600'
                            }>{response.vote.toUpperCase()}</strong></span>
                            <span className="text-xs text-gray-500">
                              {new Date(response.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Model Responses */}
                      <div className="grid md:grid-cols-2 gap-4">
                        {/* Model A */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-blue-600 dark:text-blue-400">
                              MODEL A: {response.model_a_id}
                            </h4>
                            {response.hallucination_flags.modelA.length > 0 && (
                              <span className="text-xs bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 px-2 py-0.5 rounded">
                                {response.hallucination_flags.modelA.length} flag{response.hallucination_flags.modelA.length > 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                          <div className="relative">
                            <div className={`text-xs text-gray-700 dark:text-gray-300 p-3 bg-blue-50 dark:bg-blue-900/10 rounded border border-blue-200 dark:border-blue-800 ${
                              !expandedResponses[`${response._id}-a`] ? 'max-h-24 overflow-hidden' : ''
                            }`}>
                              {response.model_a_response}
                            </div>
                            {response.model_a_response.length > 200 && (
                              <button
                                onClick={() => setExpandedResponses(prev => ({
                                  ...prev,
                                  [`${response._id}-a`]: !prev[`${response._id}-a`]
                                }))}
                                className="mt-1 text-xs text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                              >
                                {expandedResponses[`${response._id}-a`] ? (
                                  <>Show Less <ChevronUp className="h-3 w-3" /></>
                                ) : (
                                  <>Show More <ChevronDown className="h-3 w-3" /></>
                                )}
                              </button>
                            )}
                          </div>
                          {response.hallucination_flags.modelA.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {response.hallucination_flags.modelA.map((flag, idx) => (
                                <span key={idx} className="text-xs bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 px-2 py-0.5 rounded">
                                  {flag.replace(/_/g, " ")}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        {/* Model B */}
                        <div className="space-y-2">
                          <div className="flex items-center justify-between">
                            <h4 className="text-xs font-bold text-purple-600 dark:text-purple-400">
                              MODEL B: {response.model_b_id}
                            </h4>
                            {response.hallucination_flags.modelB.length > 0 && (
                              <span className="text-xs bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 px-2 py-0.5 rounded">
                                {response.hallucination_flags.modelB.length} flag{response.hallucination_flags.modelB.length > 1 ? 's' : ''}
                              </span>
                            )}
                          </div>
                          <div className="relative">
                            <div className={`text-xs text-gray-700 dark:text-gray-300 p-3 bg-purple-50 dark:bg-purple-900/10 rounded border border-purple-200 dark:border-purple-800 ${
                              !expandedResponses[`${response._id}-b`] ? 'max-h-24 overflow-hidden' : ''
                            }`}>
                              {response.model_b_response}
                            </div>
                            {response.model_b_response.length > 200 && (
                              <button
                                onClick={() => setExpandedResponses(prev => ({
                                  ...prev,
                                  [`${response._id}-b`]: !prev[`${response._id}-b`]
                                }))}
                                className="mt-1 text-xs text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1"
                              >
                                {expandedResponses[`${response._id}-b`] ? (
                                  <>Show Less <ChevronUp className="h-3 w-3" /></>
                                ) : (
                                  <>Show More <ChevronDown className="h-3 w-3" /></>
                                )}
                              </button>
                            )}
                          </div>
                          {response.hallucination_flags.modelB.length > 0 && (
                            <div className="flex flex-wrap gap-1">
                              {response.hallucination_flags.modelB.map((flag, idx) => (
                                <span key={idx} className="text-xs bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 px-2 py-0.5 rounded">
                                  {flag.replace(/_/g, " ")}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </>
        ) : null}
      </div>
    </div>
  );
}

