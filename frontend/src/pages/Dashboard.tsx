export default function Dashboard() {
  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-2">0</h2>
          <p className="text-gray-600">Articles</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-2">0</h2>
          <p className="text-gray-600">Read</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-semibold mb-2">0</h2>
          <p className="text-gray-600">Favorites</p>
        </div>
      </div>
    </div>
  );
}
