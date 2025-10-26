import { useState } from "react";
import { 
  DocumentArrowUpIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentTextIcon,
  LinkIcon 
} from "@heroicons/react/24/outline";
import { articlesAPI } from "../services/api";
import { Card, Button, ProgressItem, Input } from "../components/ui";
import clsx from "clsx";

interface UploadProgress {
  filename: string;
  progress: number;
  status: "pending" | "uploading" | "complete" | "error";
  error?: string;
}

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [uploadMode, setUploadMode] = useState<"file" | "url">("file");
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
    if (!file && !url) return;

    setUploading(true);
    const filename = uploadMode === "file" ? file!.name : url;
    const newProgress: UploadProgress = {
      filename,
      progress: 0,
      status: "pending",
    };

    setUploadProgress([newProgress]);

    try {
      setUploadProgress([{ ...newProgress, status: "uploading", progress: 10 }]);

      if (uploadMode === "file" && file) {
        await articlesAPI.upload(file);
      } else if (uploadMode === "url" && url) {
        await articlesAPI.uploadFromUrl(url);
      }

      setUploadProgress([
        {
          filename,
          progress: 100,
          status: "complete",
        },
      ]);

      setFile(null);
      setUrl("");
      setTimeout(() => {
        setUploadProgress([]);
      }, 2000);
    } catch (err: any) {
      setUploadProgress([
        {
          filename,
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
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Article</h1>
        <p className="text-gray-600 mt-1">Add academic articles to your library</p>
      </div>

      <div className="max-w-3xl mx-auto">
        <Card className="p-8">
          <div className="flex gap-2 mb-6">
            <Button
              type="button"
              variant={uploadMode === "file" ? "primary" : "secondary"}
              size="sm"
              onClick={() => setUploadMode("file")}
              fullWidth
            >
              <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
              Upload File
            </Button>
            <Button
              type="button"
              variant={uploadMode === "url" ? "primary" : "secondary"}
              size="sm"
              onClick={() => setUploadMode("url")}
              fullWidth
            >
              <LinkIcon className="h-4 w-4 mr-2" />
              From URL
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {uploadMode === "file" ? (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={clsx(
                  "relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer",
                  isDragActive
                    ? "border-primary-500 bg-primary-50 scale-[1.02]"
                    : "border-gray-300 hover:border-gray-400 bg-gray-50 hover:bg-gray-100"
                )}
              >
                <div className="space-y-4">
                  <div className="mx-auto w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
                    <CloudArrowUpIcon className="h-8 w-8 text-primary-600" />
                  </div>
                  
                  <div>
                    <p className="text-lg font-semibold text-gray-900">
                      Drop your PDF file here
                    </p>
                    <p className="text-gray-600 mt-1">or click to browse</p>
                  </div>

                  <div>
                    <input
                      id="file-input"
                      type="file"
                      accept=".pdf,.txt"
                      onChange={handleFileChange}
                      disabled={uploading}
                      className="hidden"
                    />
                    <label htmlFor="file-input">
                      <Button 
                        variant="primary" 
                        size="md" 
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          document.getElementById('file-input')?.click();
                        }}
                      >
                        <DocumentArrowUpIcon className="h-5 w-5 mr-2" />
                        Browse Files
                      </Button>
                    </label>
                  </div>

                  <p className="text-sm text-gray-500">
                    Supports: PDF, TXT • Max size: 10MB
                  </p>
                </div>

                {file && (
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <div className="flex items-center justify-center gap-3 p-4 bg-green-50 rounded-lg">
                      <DocumentTextIcon className="h-6 w-6 text-green-600 flex-shrink-0" />
                      <div className="flex-1 text-left">
                        <p className="text-green-900 font-medium">{file.name}</p>
                        <p className="text-sm text-green-600">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                      <CheckCircleIcon className="h-6 w-6 text-green-600" />
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <Input
                  type="url"
                  name="url"
                  label="Article URL"
                  placeholder="https://arxiv.org/abs/..."
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={uploading}
                  icon={LinkIcon}
                  helperText="Enter a URL to an article (ArXiv, PubMed, etc.)"
                  required
                />
                {url && (
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-start gap-3">
                      <LinkIcon className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
                      <div className="flex-1">
                        <p className="font-medium text-blue-900 text-sm">URL Ready</p>
                        <p className="text-sm text-blue-700 mt-1 break-all">{url}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {uploadProgress.length > 0 && (
              <div className="space-y-3 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-sm font-semibold text-gray-900">Upload Progress</h3>
                {uploadProgress.map((progress, idx) => (
                  <div key={idx}>
                    <ProgressItem
                      filename={progress.filename}
                      progress={progress.progress}
                      complete={progress.status === "complete"}
                    />
                    {progress.status === "error" && (
                      <div className="mt-2 flex items-start gap-2 text-sm text-red-600">
                        <XCircleIcon className="h-5 w-5 flex-shrink-0" />
                        <p>{progress.error}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            <Button
              type="submit"
              disabled={(!file && !url) || uploading}
              variant="primary"
              size="lg"
              fullWidth
              loading={uploading}
            >
              {uploading ? "Uploading..." : `Upload ${uploadMode === "file" ? "File" : "from URL"}`}
            </Button>
          </form>

          {uploadProgress.length > 0 &&
            uploadProgress[0].status === "complete" && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <p className="font-medium text-green-900">Upload successful!</p>
                    <p className="text-sm text-green-700 mt-1">
                      Your article is being processed and will appear in your library shortly.
                    </p>
                  </div>
                </div>
              </div>
            )}
        </Card>

        <Card className="mt-6 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            What happens after upload?
          </h3>
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-sm font-semibold text-primary-600">
                1
              </div>
              <div>
                <p className="font-medium text-gray-900">Metadata Extraction</p>
                <p className="text-sm text-gray-600">
                  We extract title, authors, abstract, and keywords from your article
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-sm font-semibold text-primary-600">
                2
              </div>
              <div>
                <p className="font-medium text-gray-900">Classification</p>
                <p className="text-sm text-gray-600">
                  The article is automatically categorized based on its content
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center text-sm font-semibold text-primary-600">
                3
              </div>
              <div>
                <p className="font-medium text-gray-900">Added to Library</p>
                <p className="text-sm text-gray-600">
                  The article appears in your library and recommendations are generated
                </p>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
