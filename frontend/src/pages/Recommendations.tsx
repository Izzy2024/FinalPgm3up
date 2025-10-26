import { useState, useEffect } from "react";
import { 
  SparklesIcon,
  BookmarkIcon,
  CalendarIcon,
  DocumentTextIcon 
} from "@heroicons/react/24/outline";
import { recommendationsAPI, libraryAPI } from "../services/api";
import { Card, Badge, Button } from "../components/ui";

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
  const [addingIds, setAddingIds] = useState<Set<number>>(new Set());

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
    setAddingIds((prev) => new Set(prev).add(articleId));
    
    try {
      await libraryAPI.add(articleId);
      setRecommendations((prev) => prev.filter((rec) => rec.id !== articleId));
    } catch (err: any) {
      alert(
        err.response?.data?.detail ||
        "Failed to add article to library"
      );
    } finally {
      setAddingIds((prev) => {
        const next = new Set(prev);
        next.delete(articleId);
        return next;
      });
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
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <SparklesIcon className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Recommendations</h1>
          </div>
          <p className="text-gray-600 mt-1">
            Personalized articles based on your library
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Finding perfect matches...</p>
          </div>
        </div>
      ) : recommendations.length === 0 ? (
        <Card className="p-12 text-center">
          <SparklesIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-lg text-gray-600 mb-2">
            No recommendations yet
          </p>
          <p className="text-sm text-gray-500">
            Upload and read articles to get personalized recommendations
          </p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {recommendations.map((rec) => (
              <Card key={rec.id} hover className="flex flex-col">
                <div className="flex-1">
                  {rec.similarity_score && (
                    <div className="mb-3">
                      <Badge
                        variant={rec.similarity_score >= 0.8 ? "success" : rec.similarity_score >= 0.6 ? "primary" : "warning"}
                      >
                        {Math.round(rec.similarity_score * 100)}% Match
                      </Badge>
                    </div>
                  )}

                  <h3 className="text-lg font-semibold text-gray-900 mb-3 line-clamp-2">
                    {rec.title}
                  </h3>

                  {rec.authors && rec.authors.length > 0 && (
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Authors:</span>{" "}
                      {Array.isArray(rec.authors) 
                        ? rec.authors.slice(0, 3).join(", ") + (rec.authors.length > 3 ? " et al." : "")
                        : rec.authors}
                    </p>
                  )}

                  <div className="flex gap-4 text-sm text-gray-500 mb-3">
                    {rec.journal && (
                      <div className="flex items-center gap-1">
                        <DocumentTextIcon className="h-4 w-4" />
                        <span className="line-clamp-1">{rec.journal}</span>
                      </div>
                    )}
                    {rec.publication_year && (
                      <div className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        <span>{rec.publication_year}</span>
                      </div>
                    )}
                  </div>

                  {rec.abstract && (
                    <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                      {rec.abstract}
                    </p>
                  )}
                </div>

                <div className="flex gap-2 pt-4 border-t border-gray-100">
                  <Button
                    onClick={() => handleAddToLibrary(rec.id)}
                    variant="primary"
                    size="sm"
                    fullWidth
                    loading={addingIds.has(rec.id)}
                    disabled={addingIds.has(rec.id)}
                  >
                    <BookmarkIcon className="h-4 w-4 mr-2" />
                    Add to Library
                  </Button>
                  <Button variant="secondary" size="sm">
                    Preview
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {recommendations.length >= limit && (
            <div className="text-center pt-4">
              <Button
                onClick={() => setLimit(limit + 10)}
                variant="secondary"
                size="md"
              >
                Load More Recommendations
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
