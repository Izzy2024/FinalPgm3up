import { CheckCircleIcon, ExclamationTriangleIcon } from "@heroicons/react/24/outline";

interface ClassificationResultProps {
  suggestedCategory: string | null;
  scores: Record<string, number>;
  isLoading?: boolean;
}

export function ClassificationResult({ suggestedCategory, scores, isLoading }: ClassificationResultProps) {
  if (isLoading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <div className="animate-spin">
            <div className="h-5 w-5 border-2 border-blue-600 border-t-transparent rounded-full" />
          </div>
          <p className="text-blue-800 font-medium">Classifying article...</p>
        </div>
      </div>
    );
  }

  if (!suggestedCategory) {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 flex-shrink-0" />
          <p className="text-amber-800 font-medium">Could not classify this article</p>
        </div>
      </div>
    );
  }

  const sortedScores = Object.entries(scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <CheckCircleIcon className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-green-900 font-medium">Article Classification</p>
          <div className="mt-3 space-y-2">
            <div className="bg-white rounded-lg p-3 border border-green-200">
              <p className="text-sm text-green-600">Suggested Category</p>
              <p className="text-lg font-bold text-green-900">{suggestedCategory}</p>
            </div>
            {sortedScores.length > 0 && (
              <div>
                <p className="text-sm text-green-600 mb-2">Category Scores</p>
                <div className="space-y-1.5">
                  {sortedScores.map(([category, score]) => (
                    <div key={category} className="flex items-center justify-between">
                      <span className="text-sm text-green-800">{category}</span>
                      <div className="w-32 bg-white rounded-full h-2 border border-green-200 overflow-hidden">
                        <div
                          className="h-full bg-green-600 transition-all"
                          style={{ width: `${Math.min(score * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-green-700 font-medium w-10 text-right">
                        {(score * 100).toFixed(0)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
