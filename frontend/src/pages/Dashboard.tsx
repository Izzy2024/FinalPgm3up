import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  DocumentTextIcon, 
  BookOpenIcon, 
  StarIcon,
  ArrowUpIcon,
  ClockIcon,
  CheckCircleIcon 
} from "@heroicons/react/24/outline";
import { libraryAPI, usersAPI } from "../services/api";
import { useAuthStore } from "../context/authStore";
import { Card, Button } from "../components/ui";

interface Stats {
  total_articles: number;
  read_articles: number;
  unread_articles: number;
  reading_articles: number;
  average_rating: number;
  status_distribution: {
    unread: number;
    reading: number;
    read: number;
  };
  topic_distribution: Record<string, number>;
  default_segments: { topic: string; count: number }[];
}

interface UserProfile {
  id: number;
  username: string;
  first_name?: string;
  email: string;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { user: authUser } = useAuthStore();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const [statsRes, userRes] = await Promise.all([
        libraryAPI.getStats(),
        authUser?.id ? usersAPI.getProfile(authUser.id) : Promise.resolve(null),
      ]);

      setStats(statsRes.data);
      if (userRes) {
        setUser(userRes.data);
      } else if (authUser) {
        setUser(authUser);
      }
    } catch (err: any) {
      setError("Failed to load dashboard data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {error}
      </div>
    );
  }

  const statCards = [
    {
      label: "Total Articles",
      value: stats?.total_articles ?? 0,
      icon: DocumentTextIcon,
      color: "text-blue-600",
      bgColor: "bg-blue-50",
      change: "+12%",
    },
    {
      label: "Articles Read",
      value: stats?.read_articles ?? 0,
      icon: BookOpenIcon,
      color: "text-green-600",
      bgColor: "bg-green-50",
      change: "+8%",
    },
    {
      label: "Reading Now",
      value: stats?.reading_articles ?? 0,
      icon: ClockIcon,
      color: "text-purple-600",
      bgColor: "bg-purple-50",
      change: "+3%",
    },
    {
      label: "Average Rating",
      value:
        stats && typeof stats.average_rating === "number"
          ? stats.average_rating.toFixed(1)
          : "0.0",
      icon: StarIcon,
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
      change: "+0.3",
    },
  ];

  const topSegments =
    stats?.default_segments
      ?.filter((segment) => segment.count > 0)
      .sort((a, b) => b.count - a.count)
      .slice(0, 4) || [];

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name || user?.username}! 👋
          </h1>
          <p className="text-gray-600 mt-1">Here's your library overview</p>
        </div>
        <Button variant="primary" size="md" onClick={() => navigate('/upload')}>
          Upload Article
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, idx) => (
          <Card key={idx} hover className="relative overflow-hidden">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">{stat.label}</p>
                <h2 className="text-4xl font-bold mt-2 text-gray-900">{stat.value}</h2>
                <div className="flex items-center gap-1 mt-2">
                  <ArrowUpIcon className="h-4 w-4 text-green-600" />
                  <span className="text-sm text-green-600 font-medium">{stat.change}</span>
                  <span className="text-sm text-gray-500">vs last month</span>
                </div>
              </div>
              <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h3 className="text-lg font-semibold mb-6">Reading Progress</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <ClockIcon className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Unread</p>
                  <p className="text-sm text-gray-600">{stats?.status_distribution.unread} articles</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-blue-600">
                {stats?.status_distribution.unread}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <BookOpenIcon className="h-5 w-5 text-yellow-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Currently Reading</p>
                  <p className="text-sm text-gray-600">{stats?.status_distribution.reading} articles</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-yellow-600">
                {stats?.status_distribution.reading}
              </span>
            </div>

            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Completed</p>
                  <p className="text-sm text-gray-600">{stats?.status_distribution.read} articles</p>
                </div>
              </div>
              <span className="text-2xl font-bold text-green-600">
                {stats?.status_distribution.read}
              </span>
            </div>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-6">Quick Actions</h3>
          <div className="space-y-3">
            <Button variant="secondary" fullWidth className="justify-start" onClick={() => navigate('/library')}>
              <DocumentTextIcon className="h-5 w-5 mr-2" />
              View Library
            </Button>
            <Button variant="secondary" fullWidth className="justify-start" onClick={() => navigate('/recommendations')}>
              <BookOpenIcon className="h-5 w-5 mr-2" />
              Get Recommendations
            </Button>
            <Button variant="secondary" fullWidth className="justify-start" onClick={() => navigate('/library')}>
              <StarIcon className="h-5 w-5 mr-2" />
              Rate Articles
            </Button>
          </div>
        </Card>

        <Card>
          <h3 className="text-lg font-semibold mb-6">Top Topics</h3>
          {topSegments.length === 0 ? (
            <p className="text-sm text-gray-500">No segments detected yet.</p>
          ) : (
            <div className="space-y-4">
              {topSegments.map((segment) => (
                <div key={segment.topic} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{segment.topic}</p>
                    <p className="text-xs text-gray-500">Articles tagged automatically</p>
                  </div>
                  <span className="text-2xl font-bold text-blue-600">{segment.count}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
