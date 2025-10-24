import { Link } from "react-router-dom";

export default function Navigation() {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link to="/" className="font-bold text-2xl text-blue-600">
          SIGRAA
        </Link>
        <div className="space-x-4">
          <Link to="/" className="text-gray-700 hover:text-blue-600">
            Dashboard
          </Link>
          <Link to="/library" className="text-gray-700 hover:text-blue-600">
            Library
          </Link>
          <Link to="/upload" className="text-gray-700 hover:text-blue-600">
            Upload
          </Link>
          <Link to="/recommendations" className="text-gray-700 hover:text-blue-600">
            Recommendations
          </Link>
        </div>
      </div>
    </nav>
  );
}
