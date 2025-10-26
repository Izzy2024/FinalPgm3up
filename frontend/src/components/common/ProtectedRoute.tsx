import { Navigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuthStore } from "../../context/authStore";
import { authAPI } from "../../services/api";

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, user, setUser } = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      if (isAuthenticated && !user) {
        try {
          const response = await authAPI.getCurrentUser();
          setUser(response.data);
        } catch (error) {
          console.error("Failed to load user:", error);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [isAuthenticated, user, setUser]);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return <>{children}</>;
}
