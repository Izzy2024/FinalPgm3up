import { XMarkIcon, CheckCircleIcon, XCircleIcon, DocumentDuplicateIcon } from "@heroicons/react/24/outline";
import { Button } from "./Button";
import type { BatchSummaryResult } from "../../services/api";

interface BatchSummaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: BatchSummaryResult[];
  total: number;
  successful: number;
  failed: number;
  combinedSummary?: string | null;
  combinedMethod?: string | null;
}

export function BatchSummaryModal({
  isOpen,
  onClose,
  results,
  total,
  successful,
  failed,
  combinedSummary,
  combinedMethod,
}: BatchSummaryModalProps) {
  if (!isOpen) return null;

  const copyAllSummaries = () => {
    const blocks: string[] = [];
    if (combinedSummary) {
      blocks.push(`## Combined Summary\n\n${combinedSummary}`);
    }
    const successfulSummaries = results
      .filter(r => r.success && r.summary)
      .map(r => `### ${r.title}\n\n${r.summary}\n\n`)
      .join('\n---\n\n');
    if (successfulSummaries) {
      blocks.push(successfulSummaries);
    }
    if (blocks.length === 0) {
      alert("No summaries available to copy.");
      return;
    }
    const payload = blocks.join('\n\n');

    navigator.clipboard.writeText(payload);
    alert("Summaries copied to clipboard!");
  };

  const copySummary = (summary: string) => {
    navigator.clipboard.writeText(summary);
    alert("Summary copied to clipboard!");
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Batch Summary Results</h2>
            <p className="text-sm text-gray-600 mt-1">
              {successful} of {total} articles summarized successfully
              {failed > 0 && ` (${failed} failed)`}
            </p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* Action Buttons */}
          {(successful > 0 || combinedSummary) && (
            <div className="flex justify-end mb-4">
              <Button
                variant="secondary"
                size="sm"
                onClick={copyAllSummaries}
              >
                <DocumentDuplicateIcon className="h-4 w-4 mr-2" />
                Copy Available Summaries
              </Button>
            </div>
          )}

          {combinedSummary && (
            <div className="border rounded-lg p-4 bg-blue-50 border-blue-200">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-gray-900">Combined Summary</h3>
                  {combinedMethod && (
                    <p className="text-xs text-gray-500 mt-1">Method: {combinedMethod}</p>
                  )}
                </div>
                <button
                  onClick={() => copySummary(combinedSummary)}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Copy
                </button>
              </div>
              <p className="text-sm text-gray-700 whitespace-pre-wrap">{combinedSummary}</p>
            </div>
          )}

          {/* Results List */}
          {results.map((result, index) => (
            <div
              key={result.article_id}
              className={`border rounded-lg p-4 ${
                result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-start gap-3 flex-1">
                  {result.success ? (
                    <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  ) : (
                    <XCircleIcon className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{result.title}</h3>
                    {result.method && (
                      <p className="text-xs text-gray-500 mt-1">
                        Method: {result.method}
                      </p>
                    )}
                  </div>
                </div>
                {result.success && result.summary && (
                  <button
                    onClick={() => copySummary(result.summary!)}
                    className="text-xs text-blue-600 hover:text-blue-800 ml-2"
                  >
                    Copy
                  </button>
                )}
              </div>

              {result.success && result.summary ? (
                <div className="ml-8 mt-2">
                  <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {result.summary}
                  </p>
                </div>
              ) : result.error ? (
                <div className="ml-8 mt-2">
                  <p className="text-sm text-red-600">
                    Error: {result.error}
                  </p>
                </div>
              ) : null}
            </div>
          ))}
        </div>

        <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6">
          <Button onClick={onClose} variant="primary" fullWidth>
            Close
          </Button>
        </div>
      </div>
    </div>
  );
}
