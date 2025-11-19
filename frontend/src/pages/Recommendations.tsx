import { useState, useEffect } from "react";
import {
  AcademicCapIcon,
  BookOpenIcon,
  ChartBarIcon
} from "@heroicons/react/24/outline";
import { recommendationsAPI } from "../services/api";
import { Card, Badge, Button } from "../components/ui";
import { useNavigate } from "react-router-dom";

interface Recommendation {
  article_id: number;
  title: string;
  authors?: string[];
  score?: number;
  reason?: string;
  journal?: string;
  year?: number;
}

export default function Recommendations() {
  const navigate = useNavigate();
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
      // Scope is fixed to 'library' as requested to replace the old view
      const res = await recommendationsAPI.get(limit, "library");
      setRecommendations(res.data.recommendations || []);
    } catch (err: any) {
      setError("Failed to analyze library documents");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "success";
    if (score >= 0.5) return "primary";
    return "warning";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 0.8) return "High Impact";
    if (score >= 0.5) return "Good Reference";
    return "Needs Review";
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
            <AcademicCapIcon className="h-8 w-8 text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Research Quality Analysis</h1>
          </div>
          <p className="text-gray-600 mt-1">
            AI-powered analysis of your library to highlight high-grade research documents.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Analyzing document quality...</p>
          </div>
        </div>
      ) : recommendations.length === 0 ? (
        <Card className="p-12 text-center">
          <ChartBarIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <p className="text-lg text-gray-600 mb-2">
            No analysis available
          </p>
          <p className="text-sm text-gray-500">
            Upload more academic papers to get quality insights.
          </p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {recommendations.map((rec) => (
              <Card key={rec.article_id} hover className="flex flex-col border-l-4 border-l-primary-500">
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-3">
                    {rec.score !== undefined && (
                      <Badge variant={getScoreColor(rec.score)}>
                        {Math.round(rec.score * 100)}% - {getScoreLabel(rec.score)}
                      </Badge>
                    )}
                    {rec.year && (
                      <span className="text-xs text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded">
                        {rec.year}
                      </span>
                    )}
                  </div>

                  <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                    {rec.title}
                  </h3>

                  {rec.journal && (
                    <p className="text-sm text-primary-700 font-medium mb-2">
                      {rec.journal}
                    </p>
                  )}

                  {rec.authors && rec.authors.length > 0 && (
                    <p className="text-sm text-gray-600 mb-3">
                      <span className="font-medium">Authors:</span>{" "}
                      {Array.isArray(rec.authors)
                        ? rec.authors.slice(0, 3).join(", ") + (rec.authors.length > 3 ? " et al." : "")
                        : rec.authors}
                    </p>
                  )}

                  {rec.reason && (
                    <div className="bg-blue-50 p-3 rounded-md mb-4">
                      <p className="text-xs font-bold text-blue-800 uppercase tracking-wide mb-1">
                        Quality Indicators
                      </p>
                      <p className="text-sm text-blue-700">
                        {rec.reason}
                      </p>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 pt-4 border-t border-gray-100">
                  <Button
                    onClick={() => navigate(`/library/article/${rec.article_id}`)}
                    variant="primary"
                    size="sm"
                    fullWidth
                  >
                    <BookOpenIcon className="h-4 w-4 mr-2" />
                    Read Now
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
                Load More Analysis
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
