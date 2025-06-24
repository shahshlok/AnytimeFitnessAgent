import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from "@/components/ui/chart"
import {
  MessageCircle,
  MessageSquare,
  Clock,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Mic,
  Type,
  HelpCircle,
  Zap,
  Calendar,
  Filter,
} from "lucide-react"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"

// API Configuration
const API_BASE_URL = "http://localhost:7479"

// Types for API responses
interface OverviewData {
  total_conversations: number
  total_messages: number
  avg_response_time: number
  conversations_change: number
  messages_change: number
  error_rate: number
}

interface DailyConversation {
  date: string
  conversations: number
}

interface MessageVolume {
  date: string
  userMessages: number
  assistantMessages: number
}

interface InputMethod {
  name: string
  value: number
  color: string
}

interface TopQuestion {
  question: string
  count: number
}

interface ResponseTime {
  date: string
  responseTime: number
}

// API utility functions
const fetchData = async (endpoint: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error(`Error fetching ${endpoint}:`, error)
    return null
  }
}

// Sample data for charts (fallback data)
const dailyConversationsData = [
  { date: "2024-01-01", conversations: 145 },
  { date: "2024-01-02", conversations: 167 },
  { date: "2024-01-03", conversations: 189 },
  { date: "2024-01-04", conversations: 203 },
  { date: "2024-01-05", conversations: 178 },
  { date: "2024-01-06", conversations: 234 },
  { date: "2024-01-07", conversations: 267 },
  { date: "2024-01-08", conversations: 245 },
  { date: "2024-01-09", conversations: 289 },
  { date: "2024-01-10", conversations: 312 },
]

const messageVolumeData = [
  { date: "Jan 1", userMessages: 234, assistantMessages: 267 },
  { date: "Jan 2", userMessages: 289, assistantMessages: 334 },
  { date: "Jan 3", userMessages: 345, assistantMessages: 398 },
  { date: "Jan 4", userMessages: 378, assistantMessages: 445 },
  { date: "Jan 5", userMessages: 298, assistantMessages: 356 },
  { date: "Jan 6", userMessages: 456, assistantMessages: 523 },
  { date: "Jan 7", userMessages: 534, assistantMessages: 612 },
]

const inputMethodData = [
  { name: "Text Input", value: 78, color: "#8b5cf6" },
  { name: "Voice Input", value: 22, color: "#06b6d4" },
]

const responseTimeData = [
  { date: "Week 1", responseTime: 1.2 },
  { date: "Week 2", responseTime: 1.4 },
  { date: "Week 3", responseTime: 1.1 },
  { date: "Week 4", responseTime: 1.8 },
]

const transcriptionTimeData = [
  { date: "Week 1", transcriptionTime: 0.8 },
  { date: "Week 2", transcriptionTime: 0.9 },
  { date: "Week 3", transcriptionTime: 0.7 },
  { date: "Week 4", transcriptionTime: 1.1 },
]

const tokenUsageData = [
  { model: "gpt-4o-mini", promptTokens: 45000, completionTokens: 23000 },
  { model: "gpt-4o", promptTokens: 12000, completionTokens: 8000 },
  { model: "whisper-1", promptTokens: 8000, completionTokens: 0 },
]

const topQuestionsData = [
  { question: "What are your gym hours?", count: 234 },
  { question: "How do I cancel my membership?", count: 189 },
  { question: "What equipment do you have?", count: 167 },
  { question: "Do you offer personal training?", count: 145 },
  { question: "What are your membership rates?", count: 134 },
  { question: "How do I freeze my membership?", count: 123 },
  { question: "Do you have group classes?", count: 112 },
  { question: "Where are you located?", count: 98 },
  { question: "Do you have a pool?", count: 87 },
  { question: "What safety protocols do you follow?", count: 76 },
]

const chartConfig = {
  conversations: {
    label: "Conversations",
    color: "#8b5cf6",
  },
  userMessages: {
    label: "User Messages",
    color: "#8b5cf6",
  },
  assistantMessages: {
    label: "Assistant Messages",
    color: "#06b6d4",
  },
  responseTime: {
    label: "Response Time (s)",
    color: "#8b5cf6",
  },
  transcriptionTime: {
    label: "Transcription Time (s)",
    color: "#06b6d4",
  },
  promptTokens: {
    label: "Prompt Tokens",
    color: "#8b5cf6",
  },
  completionTokens: {
    label: "Completion Tokens",
    color: "#06b6d4",
  },
}

interface StatCardProps {
  title: string
  value: string | number
  change: string
  changeType: "positive" | "negative" | "neutral"
  icon: React.ComponentType<{ className?: string }>
  suffix?: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, change, changeType, icon: Icon, suffix = "" }) => {
  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {value}
          {suffix}
        </div>
        <div className="flex items-center text-xs text-muted-foreground">
          {changeType === "positive" && <TrendingUp className="mr-1 h-3 w-3 text-green-500" />}
          {changeType === "negative" && <TrendingDown className="mr-1 h-3 w-3 text-red-500" />}
          <span
            className={
              changeType === "positive"
                ? "text-green-500"
                : changeType === "negative"
                  ? "text-red-500"
                  : "text-muted-foreground"
            }
          >
            {change}
          </span>
          <span className="ml-1">vs. last period</span>
        </div>
      </CardContent>
    </Card>
  )
}

interface GaugeChartProps {
  value: number
  max: number
  title: string
  subtitle: string
}

const GaugeChart: React.FC<GaugeChartProps> = ({ value, max, title, subtitle }) => {
  const percentage = (value / max) * 100
  const circumference = 2 * Math.PI * 45
  const strokeDasharray = circumference
  const strokeDashoffset = circumference - (percentage / 100) * circumference

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className="relative w-32 h-32">
        <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="45" stroke="#e5e7eb" strokeWidth="8" fill="none" />
          <circle
            cx="50"
            cy="50"
            r="45"
            stroke="#8b5cf6"
            strokeWidth="8"
            fill="none"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-300 ease-in-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg font-bold">${value}</div>
            <div className="text-xs text-muted-foreground">/ ${max}</div>
          </div>
        </div>
      </div>
      <div className="text-center">
        <div className="font-medium">{title}</div>
        <div className="text-sm text-muted-foreground">{subtitle}</div>
      </div>
    </div>
  )
}

const AnytimeFitnessDashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState("Last 30 Days")
  const [isFilterOpen, setIsFilterOpen] = useState(false)
  
  // State for API data
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null)
  const [dailyConversations, setDailyConversations] = useState<DailyConversation[]>(dailyConversationsData)
  const [messageVolume, setMessageVolume] = useState<MessageVolume[]>(messageVolumeData)
  const [inputMethods, setInputMethods] = useState<InputMethod[]>(inputMethodData)
  const [topQuestions, setTopQuestions] = useState<TopQuestion[]>(topQuestionsData)
  const [responseTimes, setResponseTimes] = useState<ResponseTime[]>(responseTimeData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch all dashboard data
  const fetchAllData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [
        overview,
        conversations,
        messages,
        inputs,
        questions,
        performance
      ] = await Promise.all([
        fetchData('/analytics/overview'),
        fetchData('/analytics/conversations/daily'),
        fetchData('/analytics/messages/volume'),
        fetchData('/analytics/input-methods'),
        fetchData('/analytics/questions/top'),
        fetchData('/analytics/performance/response-times')
      ])
      
      if (overview) setOverviewData(overview)
      if (conversations) setDailyConversations(conversations)
      if (messages) setMessageVolume(messages)
      if (inputs) setInputMethods(inputs)
      if (questions) setTopQuestions(questions)
      if (performance) setResponseTimes(performance)
      
    } catch (err) {
      setError('Failed to fetch dashboard data')
      console.error('Error fetching dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }
  
  // Fetch data on component mount and set up auto-refresh
  useEffect(() => {
    fetchAllData()
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchAllData, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const handleDateRangeChange = (range: string) => {
    setDateRange(range)
  }

  const toggleFilter = () => {
    setIsFilterOpen(!isFilterOpen)
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-cyan-50 p-4 md:p-6 lg:p-8 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Dashboard Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={fetchAllData}>Retry</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-cyan-50 p-4 md:p-6 lg:p-8">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Header */}
        <div className="flex flex-col space-y-2 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div>
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-purple-600 to-cyan-600 bg-clip-text text-transparent">
              Anytime Fitness Chatbot Dashboard
            </h1>
            <p className="text-muted-foreground">
              Live Dashboard • {loading ? 'Updating...' : `Last updated ${new Date().toLocaleTimeString()}`}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={() => handleDateRangeChange("Last 7 Days")}>
              <Calendar className="mr-2 h-4 w-4" />
              {dateRange}
            </Button>
            <Button variant="outline" size="sm" onClick={toggleFilter}>
              <Filter className="mr-2 h-4 w-4" />
              Filter
            </Button>
          </div>
        </div>

        {/* Executive Summary - KPI Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Conversations"
            value={loading ? "Loading..." : (overviewData?.total_conversations?.toLocaleString() || "0")}
            change={`${(overviewData?.conversations_change || 0) > 0 ? '+' : ''}${overviewData?.conversations_change || 0}%`}
            changeType={(overviewData?.conversations_change || 0) > 0 ? "positive" : (overviewData?.conversations_change || 0) < 0 ? "negative" : "neutral"}
            icon={MessageCircle}
          />
          <StatCard 
            title="Total Messages" 
            value={loading ? "Loading..." : (overviewData?.total_messages?.toLocaleString() || "0")} 
            change={`${(overviewData?.messages_change || 0) > 0 ? '+' : ''}${overviewData?.messages_change || 0}%`} 
            changeType={(overviewData?.messages_change || 0) > 0 ? "positive" : (overviewData?.messages_change || 0) < 0 ? "negative" : "neutral"} 
            icon={MessageSquare} 
          />
          <StatCard
            title="Avg Response Time"
            value={loading ? "Loading..." : (overviewData?.avg_response_time?.toString() || "0")}
            change="Real-time data"
            changeType="neutral"
            icon={Clock}
            suffix="s"
          />
          <StatCard
            title="API Error Rate"
            value={loading ? "Loading..." : (overviewData?.error_rate?.toString() || "0")}
            change="Real-time data"
            changeType="positive"
            icon={AlertTriangle}
            suffix="%"
          />
        </div>

        {/* Usage Trends & Adoption */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Chatbot Usage Over Time</h2>
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Daily Active Conversations */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Daily Active Conversations</CardTitle>
                <CardDescription>Conversation trends over the last 10 days</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={dailyConversations}>
                      <defs>
                        <linearGradient id="conversationsGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="date"
                        tickFormatter={(value) =>
                          new Date(value).toLocaleDateString("en-US", { month: "short", day: "numeric" })
                        }
                      />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Area
                        type="monotone"
                        dataKey="conversations"
                        stroke="#8b5cf6"
                        fillOpacity={1}
                        fill="url(#conversationsGradient)"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Input Method Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle>Input Method Distribution</CardTitle>
                <CardDescription>Text vs Voice input usage</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[300px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={inputMethods}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {inputMethods.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <ChartTooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            return (
                              <div className="rounded-lg border bg-background p-2 shadow-sm">
                                <div className="flex items-center gap-2">
                                  {payload[0].payload.name === "Text Input" ? (
                                    <Type className="h-4 w-4" />
                                  ) : (
                                    <Mic className="h-4 w-4" />
                                  )}
                                  <span className="font-medium">{payload[0].payload.name}</span>
                                </div>
                                <div className="text-sm text-muted-foreground">{payload[0].value}% of total inputs</div>
                              </div>
                            )
                          }
                          return null
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
                <div className="mt-4 space-y-2">
                  {inputMethods.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {item.name === "Text Input" ? <Type className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                        <span className="text-sm">{item.name}</span>
                      </div>
                      <Badge variant="secondary">{item.value}%</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Message Volume by Day */}
          <Card>
            <CardHeader>
              <CardTitle>Message Volume by Day</CardTitle>
              <CardDescription>User and Assistant message distribution over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={messageVolume}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <ChartLegend content={<ChartLegendContent />} />
                    <Bar dataKey="userMessages" stackId="a" fill="#8b5cf6" />
                    <Bar dataKey="assistantMessages" stackId="a" fill="#06b6d4" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        {/* Performance & Efficiency Details */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">System Performance & Resource Consumption</h2>
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Response Time Trend */}
            <Card>
              <CardHeader>
                <CardTitle>AI Response Time Trend</CardTitle>
                <CardDescription>Average response time over 4 weeks</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={responseTimes}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="responseTime"
                        stroke="#8b5cf6"
                        strokeWidth={2}
                        dot={{ fill: "#8b5cf6" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* Transcription Time Trend */}
            <Card>
              <CardHeader>
                <CardTitle>Transcription Time Trend</CardTitle>
                <CardDescription>Average transcription time over 4 weeks</CardDescription>
              </CardHeader>
              <CardContent>
                <ChartContainer config={chartConfig} className="h-[200px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={transcriptionTimeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <ChartTooltip content={<ChartTooltipContent />} />
                      <Line
                        type="monotone"
                        dataKey="transcriptionTime"
                        stroke="#06b6d4"
                        strokeWidth={2}
                        dot={{ fill: "#06b6d4" }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartContainer>
              </CardContent>
            </Card>

            {/* OpenAI Cost Gauge */}
            <Card>
              <CardHeader>
                <CardTitle>Daily OpenAI Cost</CardTitle>
                <CardDescription>Estimated daily spending vs budget</CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <GaugeChart value={15} max={50} title="Current Usage" subtitle="Daily Budget" />
              </CardContent>
            </Card>
          </div>

          {/* Token Usage by Model */}
          <Card>
            <CardHeader>
              <CardTitle>OpenAI Token Usage by Model</CardTitle>
              <CardDescription>Prompt and completion tokens across different AI models</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={chartConfig} className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={tokenUsageData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="model" type="category" width={100} />
                    <ChartTooltip content={<ChartTooltipContent />} />
                    <ChartLegend content={<ChartLegendContent />} />
                    <Bar dataKey="promptTokens" stackId="a" fill="#8b5cf6" />
                    <Bar dataKey="completionTokens" stackId="a" fill="#06b6d4" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        {/* Content Insights & Quality */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Conversation Topics & Quality</h2>
          <div className="grid gap-4 lg:grid-cols-3">
            {/* Top Questions */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Top 10 User Questions</CardTitle>
                <CardDescription>Most frequently asked questions by users</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {topQuestions.map((item, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{item.question}</p>
                      </div>
                      <div className="ml-4 flex items-center space-x-2">
                        <div className="w-20 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${topQuestions.length > 0 ? (item.count / topQuestions[0].count) * 100 : 0}%` }}
                          ></div>
                        </div>
                        <Badge variant="secondary">{item.count}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <div className="space-y-4">
              {/* AI "I Don't Know" Rate */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">AI "I Don't Know" Rate</CardTitle>
                  <HelpCircle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">3%</div>
                  <p className="text-xs text-muted-foreground">out of 24,392 total questions</p>
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm">
                      <span>Knowledge Coverage</span>
                      <span className="font-medium">97%</span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: "97%" }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* User Satisfaction Placeholder */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">User Satisfaction</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8">
                    <div className="text-lg font-medium text-muted-foreground mb-2">Coming Soon!</div>
                    <p className="text-sm text-muted-foreground">User feedback and rating system in development</p>
                    <Badge variant="outline" className="mt-2">
                      Future Feature
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnytimeFitnessDashboard
