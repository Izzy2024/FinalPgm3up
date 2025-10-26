import { useState, useEffect } from "react";
import { libraryAPI, usersAPI } from "../services/api";

interface Stats {
  total_articles: number;
  read_articles: number;
  unread_articles: number;
  average_rating: number;
  status_distribution: {
    unread: number;
    reading: number;
    read: number;
  };
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

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError("");

      const [statsRes, userRes] = await Promise.all([
        libraryAPI.getStats(),
        usersAPI.getProfile(1),
      ]);

      setStats(statsRes.data);
      setUser(userRes.data);
    } catch (err: any) {
      setError("Failed to load dashboard data");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-500">Loading dashboard...</p>
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

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold">
          Welcome back, {user?.first_name || user?.username}!
        </h1>
        <p className="text-gray-600 mt-2">Here's your library overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <p className="text-gray-600 text-sm font-medium">Total Articles</p>
          <h2 className="text-4xl font-bold mt-2">{stats?.total_articles || 0}</h2>
        </div>
        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <p className="text-gray-600 text-sm font-medium">Articles Read</p>
          <h2 className="text-4xl font-bold mt-2">{stats?.read_articles || 0}</h2>
        </div>
        <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition">
          <p className="text-gray-600 text-sm font-medium">Average Rating</p>
          <h2 className="text-4xl font-bold mt-2">{stats?.average_rating.toFixed(1) || "0.0"}</h2>
        </div>
      </div>

      {stats && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-xl font-semibold mb-4">Reading Status Distribution</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-gray-600 text-sm">Unread</p>
              <p className="text-2xl font-bold text-blue-600">{stats.status_distribution.unread}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Currently Reading</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.status_distribution.reading}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Read</p>
              <p className="text-2xl font-bold text-green-600">{stats.status_distribution.read}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
