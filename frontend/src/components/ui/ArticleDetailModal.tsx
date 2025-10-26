import { useState } from "react";
import { XMarkIcon, DocumentDuplicateIcon } from "@heroicons/react/24/outline";
import { Button } from "./Button";

interface ArticleDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  article: {
    id: number;
    title: string;
    authors?: string[];
    abstract?: string;
    journal?: string;
    publication_year?: number;
    doi?: string;
    keywords?: string[];
    added_at?: string;
    status?: "unread" | "reading" | "read";
    rating?: number | null;
    notes?: string;
  };
  onStatusChange?: (status: "unread" | "reading" | "read") => Promise<void>;
  onRatingChange?: (rating: number) => Promise<void>;
  onBibliography?: () => void;
}

export function ArticleDetailModal({
  isOpen,
  onClose,
  article,
  onStatusChange,
  onRatingChange,
  onBibliography,
}: ArticleDetailModalProps) {
  const [updating, setUpdating] = useState(false);
  const [localRating, setLocalRating] = useState(article.rating || 0);

  const handleStatusChange = async (status: "unread" | "reading" | "read") => {
    if (!onStatusChange) return;
    setUpdating(true);
    try {
      await onStatusChange(status);
    } finally {
      setUpdating(false);
    }
  };

  const handleRatingChange = async (rating: number) => {
    setLocalRating(rating);
    if (!onRatingChange) return;
    setUpdating(true);
    try {
      await onRatingChange(rating);
    } finally {
      setUpdating(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Article Details</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">{article.title}</h3>
            {article.authors && article.authors.length > 0 && (
              <p className="text-sm text-gray-600">
                <span className="font-medium">Authors:</span> {article.authors.join(", ")}
              </p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            {article.journal && (
              <div>
                <p className="text-sm text-gray-500">Journal</p>
                <p className="text-sm font-medium text-gray-900">{article.journal}</p>
              </div>
            )}
            {article.publication_year && (
              <div>
                <p className="text-sm text-gray-500">Year</p>
                <p className="text-sm font-medium text-gray-900">{article.publication_year}</p>
              </div>
            )}
            {article.doi && (
              <div className="col-span-2">
                <p className="text-sm text-gray-500">DOI</p>
                <a
                  href={`https://doi.org/${article.doi}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-blue-600 hover:text-blue-800 break-all"
                >
                  {article.doi}
                </a>
              </div>
            )}
          </div>

          {article.abstract && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Abstract</p>
              <p className="text-sm text-gray-700 leading-relaxed">{article.abstract}</p>
            </div>
          )}

          {article.keywords && article.keywords.length > 0 && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Keywords</p>
              <div className="flex flex-wrap gap-2">
                {article.keywords.map((keyword) => (
                  <span
                    key={keyword}
                    className="inline-block px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {onStatusChange && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Status</p>
              <div className="flex gap-2">
                {(["unread", "reading", "read"] as const).map((status) => (
                  <button
                    key={status}
                    onClick={() => handleStatusChange(status)}
                    disabled={updating}
                    className={`px-3 py-2 rounded text-sm font-medium transition-all ${
                      article.status === status
                        ? "bg-blue-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {onRatingChange && (
            <div>
              <p className="text-sm text-gray-500 mb-2">Rating</p>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => handleRatingChange(star)}
                    disabled={updating}
                    className="focus:outline-none transition-transform hover:scale-110"
                  >
                    <span className={`text-2xl ${star <= localRating ? "text-yellow-400" : "text-gray-300"}`}>
                      ★
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {article.added_at && (
            <div className="text-xs text-gray-500">
              Added on {new Date(article.added_at).toLocaleDateString()}
            </div>
          )}

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            {onBibliography && (
              <Button onClick={onBibliography} variant="secondary" fullWidth>
                <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
                View Citations
              </Button>
            )}
            <Button onClick={onClose} variant="primary" fullWidth>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
