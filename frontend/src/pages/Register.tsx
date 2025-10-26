import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { 
  UserIcon, 
  EnvelopeIcon, 
  LockClosedIcon,
  BuildingLibraryIcon,
  AcademicCapIcon 
} from "@heroicons/react/24/outline";
import { authAPI } from "../services/api";
import { useAuthStore } from "../context/authStore";
import { Card, Input, Button } from "../components/ui";

export default function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    institution: "",
    field_of_study: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();
  const { setToken } = useAuthStore();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authAPI.register(formData);
      
      const loginResponse = await authAPI.login(formData.username, formData.password);
      const { access_token } = loginResponse.data;
      
      localStorage.setItem("access_token", access_token);
      setToken(access_token);
      
      navigate("/");
    } catch (err: any) {
      let errorMessage = "Registration failed. Please try again.";
      
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-blue-50 px-4 py-12">
      <div className="w-full max-w-2xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">SIGRAA</h1>
          <p className="text-gray-600">Create your academic account</p>
        </div>

        <Card className="p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Create account</h2>
          
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-start gap-2">
              <span className="text-red-500">⚠</span>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                Account Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="text"
                  name="username"
                  label="Username"
                  placeholder="johndoe"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={loading}
                  icon={UserIcon}
                  required
                />

                <Input
                  type="email"
                  name="email"
                  label="Email"
                  placeholder="john@university.edu"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={loading}
                  icon={EnvelopeIcon}
                  required
                />
              </div>

              <Input
                type="password"
                name="password"
                label="Password"
                placeholder="Minimum 8 characters"
                value={formData.password}
                onChange={handleChange}
                disabled={loading}
                icon={LockClosedIcon}
                helperText="Must be at least 8 characters long"
                required
              />
            </div>

            <div className="space-y-4 pt-4 border-t border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                Personal Information (Optional)
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  type="text"
                  name="first_name"
                  label="First Name"
                  placeholder="John"
                  value={formData.first_name}
                  onChange={handleChange}
                  disabled={loading}
                />

                <Input
                  type="text"
                  name="last_name"
                  label="Last Name"
                  placeholder="Doe"
                  value={formData.last_name}
                  onChange={handleChange}
                  disabled={loading}
                />
              </div>

              <Input
                type="text"
                name="institution"
                label="Institution"
                placeholder="University of Example"
                value={formData.institution}
                onChange={handleChange}
                disabled={loading}
                icon={BuildingLibraryIcon}
              />

              <Input
                type="text"
                name="field_of_study"
                label="Field of Study"
                placeholder="Computer Science"
                value={formData.field_of_study}
                onChange={handleChange}
                disabled={loading}
                icon={AcademicCapIcon}
              />
            </div>

            <Button
              type="submit"
              disabled={loading}
              variant="primary"
              size="lg"
              fullWidth
              loading={loading}
            >
              {loading ? "Creating account..." : "Create account"}
            </Button>
          </form>
          
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Already have an account?{" "}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
                Sign in
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
