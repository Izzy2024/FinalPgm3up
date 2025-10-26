import { useState, useEffect } from "react";
import { recommendationsAPI, libraryAPI } from "../services/api";

interface Recommendation {
  id: number;
  title: string;
  abstract?: string;
  authors?: string[];
  journal?: string;
  publication_year?: number;
  similarity_score?: number;
}

export default function Recommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    fetchRecommendations();
  }, [limit]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await recommendationsAPI.get(limit);
      setRecommendations(res.data.recommendations || []);
    } catch (err: any) {
      setError("Failed to load recommendations");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToLibrary = async (articleId: number) => {
    try {
      await libraryAPI.add(articleId);
      alert("Article added to your library!");
    } catch (err: any) {
      alert(
        err.response?.data?.detail ||
        "Failed to add article to library"
      );
    }
  };

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
        <h1 className="text-4xl font-bold">Recommendations</h1>
        <p className="text-gray-600 mt-2">
          Personalized articles based on your library
        </p>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading recommendations...</p>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-600">
            Upload and read articles to get personalized recommendations.
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-4 mb-8">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition"
              >
                <div className="flex justify-between items-start gap-6">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {rec.title}
                    </h3>
                    {rec.authors && (
                      <p className="text-sm text-gray-600 mb-2">
                        Authors: {Array.isArray(rec.authors) ? rec.authors.join(", ") : rec.authors}
                      </p>
                    )}
                    {rec.journal && (
                      <p className="text-sm text-gray-600 mb-2">
                        Journal: {rec.journal}
                      </p>
                    )}
                    {rec.publication_year && (
                      <p className="text-sm text-gray-600 mb-2">
                        Year: {rec.publication_year}
                      </p>
                    )}
                    {rec.abstract && (
                      <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                        {rec.abstract}
                      </p>
                    )}
                    {rec.similarity_score && (
                      <div className="mb-4">
                        <p className="text-xs text-gray-500 mb-1">Relevance</p>
                        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500"
                            style={{
                              width: `${Math.round(rec.similarity_score * 100)}%`,
                            }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {Math.round(rec.similarity_score * 100)}% match
                        </p>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 flex-shrink-0">
                    <button
                      onClick={() => handleAddToLibrary(rec.id)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium text-sm"
                    >
                      Add to Library
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center">
            <button
              onClick={() => setLimit(limit + 5)}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Load More
            </button>
          </div>
        </>
      )}
    </div>
  );
}
