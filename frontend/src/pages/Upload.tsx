import { useState } from "react";
import { articlesAPI } from "../services/api";

interface UploadProgress {
  filename: string;
  progress: number;
  status: "pending" | "uploading" | "complete" | "error";
  error?: string;
}

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const newProgress: UploadProgress = {
      filename: file.name,
      progress: 0,
      status: "pending",
    };

    setUploadProgress([newProgress]);

    try {
      setUploadProgress([{ ...newProgress, status: "uploading", progress: 10 }]);

      await articlesAPI.upload(file);

      setUploadProgress([
        {
          filename: file.name,
          progress: 100,
          status: "complete",
        },
      ]);

      setFile(null);
      setTimeout(() => {
        setUploadProgress([]);
      }, 2000);
    } catch (err: any) {
      setUploadProgress([
        {
          filename: file.name,
          progress: 0,
          status: "error",
          error:
            err.response?.data?.detail ||
            "Upload failed. Please try again.",
        },
      ]);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-4xl font-bold">Upload Article</h1>
        <p className="text-gray-600 mt-2">Add academic articles to your library</p>
      </div>

      <div className="max-w-2xl mx-auto">
        <div className="bg-white p-8 rounded-lg shadow">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-12 text-center transition cursor-pointer ${
                isDragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-300 bg-gray-50"
              }`}
            >
              <div className="space-y-2">
                <p className="text-lg font-medium text-gray-900">
                  Drop your PDF file here
                </p>
                <p className="text-gray-600">or</p>
                <label className="inline-block">
                  <span className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer font-medium">
                    Browse Files
                  </span>
                  <input
                    type="file"
                    accept=".pdf,.txt"
                    onChange={handleFileChange}
                    disabled={uploading}
                    className="hidden"
                  />
                </label>
                <p className="text-xs text-gray-500">PDF or TXT files only</p>
              </div>

              {file && (
                <div className="mt-4 pt-4 border-t">
                  <p className="text-green-600 font-medium">✓ {file.name}</p>
                  <p className="text-xs text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>

            {uploadProgress.length > 0 && (
              <div className="space-y-3">
                {uploadProgress.map((progress, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {progress.filename}
                      </p>
                      <span className="text-xs text-gray-500">
                        {progress.progress}%
                      </span>
                    </div>
                    {progress.status === "error" && (
                      <p className="text-sm text-red-600">{progress.error}</p>
                    )}
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${
                          progress.status === "error"
                            ? "bg-red-500"
                            : progress.status === "complete"
                            ? "bg-green-500"
                            : "bg-blue-500"
                        }`}
                        style={{ width: `${progress.progress}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}

            <button
              type="submit"
              disabled={!file || uploading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 font-medium transition"
            >
              {uploading ? "Uploading..." : "Upload Article"}
            </button>
          </form>

          {uploadProgress.length > 0 &&
            uploadProgress[0].status === "complete" && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg text-sm">
                ✓ Article uploaded successfully! It will appear in your library shortly.
              </div>
            )}
        </div>
      </div>
    </div>
  );
}
