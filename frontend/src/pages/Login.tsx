import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { UserIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import { authAPI } from "../services/api";
import { useAuthStore } from "../context/authStore";
import { Card, Input, Button } from "../components/ui";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { setToken, setUser } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await authAPI.login(username, password);
      const { access_token } = response.data;
      
      localStorage.setItem("access_token", access_token);
      setToken(access_token);
      
      const userResponse = await authAPI.getCurrentUser();
      setUser(userResponse.data);
      
      navigate("/");
    } catch (err: any) {
      let errorMessage = "Invalid username or password";
      
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg).join(", ");
        } else if (typeof detail === "string") {
          errorMessage = detail;
        }
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-blue-50 px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">SIGRAA</h1>
          <p className="text-gray-600">Academic Article Recommendation System</p>
        </div>

        <Card className="p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Welcome back</h2>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-start gap-2">
              <span className="text-red-500">⚠</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <Input
              type="text"
              label="Username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              icon={UserIcon}
              required
            />

            <Input
              type="password"
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              icon={LockClosedIcon}
              required
            />

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-gray-700">Remember me</span>
              </label>
              <a href="#" className="text-primary-600 hover:text-primary-700 font-medium">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              disabled={loading}
              variant="primary"
              size="lg"
              fullWidth
              loading={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Don't have an account?{" "}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-semibold">
                Create account
              </Link>
            </p>
          </div>
        </Card>

        <p className="text-center text-sm text-gray-500 mt-8">
          © 2025 SIGRAA. All rights reserved.
        </p>
      </div>
    </div>
  );
}
