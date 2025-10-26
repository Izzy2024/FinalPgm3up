import { useState } from "react";
import { XMarkIcon, CheckIcon, DocumentDuplicateIcon } from "@heroicons/react/24/outline";
import { Button } from "./Button";

interface BibliographyModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  bibliography: {
    apa: string;
    mla: string;
    chicago: string;
    bibtex: string;
    ris: string;
  };
}

type Format = "apa" | "mla" | "chicago" | "bibtex" | "ris";

export function BibliographyModal({ isOpen, onClose, title, bibliography }: BibliographyModalProps) {
  const [activeFormat, setActiveFormat] = useState<Format>("apa");
  const [copied, setCopied] = useState(false);

  const formats: Format[] = ["apa", "mla", "chicago", "bibtex", "ris"];

  const handleCopy = () => {
    const text = bibliography[activeFormat];
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Citation Formats</h2>
            <p className="text-gray-600 text-sm mt-1">{title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="flex gap-2 flex-wrap">
            {formats.map((format) => (
              <button
                key={format}
                onClick={() => setActiveFormat(format)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  activeFormat === format
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {format.toUpperCase()}
              </button>
            ))}
          </div>

          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <pre className="text-sm text-gray-800 whitespace-pre-wrap break-words font-mono">
              {bibliography[activeFormat]}
            </pre>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={handleCopy}
              variant="primary"
              className="flex items-center gap-2"
            >
              <DocumentDuplicateIcon className="h-4 w-4" />
              {copied ? (
                <>
                  <CheckIcon className="h-4 w-4" />
                  Copied!
                </>
              ) : (
                "Copy to Clipboard"
              )}
            </Button>
            <Button
              onClick={onClose}
              variant="secondary"
            >
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
