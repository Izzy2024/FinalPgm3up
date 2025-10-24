import { useState } from "react";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    // TODO: Implement file upload logic
    console.log("Upload file:", file);
  };

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">Upload Article</h1>
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center">
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileChange}
              className="w-full"
            />
            {file && <p className="mt-2 text-green-600">Selected: {file.name}</p>}
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
          >
            Upload
          </button>
        </form>
      </div>
    </div>
  );
}
