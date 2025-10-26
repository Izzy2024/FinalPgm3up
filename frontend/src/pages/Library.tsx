import { useState, useEffect } from "react";
import { libraryAPI } from "../services/api";

interface LibraryItem {
  id: number;
  article_id: number;
  title: string;
  authors: string[];
  status: "unread" | "reading" | "read";
  rating: number | null;
  notes: string | null;
  added_at: string;
  updated_at: string;
}

export default function Library() {
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | "unread" | "reading" | "read">("all");
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const limit = 10;

  useEffect(() => {
    fetchLibrary();
  }, [filter, skip]);

  const fetchLibrary = async () => {
    try {
      setLoading(true);
      setError("");
      const status = filter === "all" ? undefined : filter;
      const res = await libraryAPI.list(skip, limit, status);
      setItems(res.data.items);
      setTotal(res.data.total);
    } catch (err: any) {
      setError("Failed to load library");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (articleId: number) => {
    if (!confirm("Remove this article from your library?")) return;

    try {
      await libraryAPI.remove(articleId);
      setItems(items.filter((item) => item.article_id !== articleId));
      setTotal(total - 1);
    } catch (err) {
      setError("Failed to remove article");
    }
  };

  const handleStatusChange = async (
    articleId: number,
    newStatus: "unread" | "reading" | "read"
  ) => {
    try {
      await libraryAPI.update(articleId, newStatus);
      setItems(
        items.map((item) =>
          item.article_id === articleId ? { ...item, status: newStatus } : item
        )
      );
    } catch (err) {
      setError("Failed to update article status");
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
        <h1 className="text-4xl font-bold">My Library</h1>
        <p className="text-gray-600 mt-2">
          Total articles: {total}
        </p>
      </div>

      <div className="mb-6 flex gap-4">
        {(["all", "unread", "reading", "read"] as const).map((status) => (
          <button
            key={status}
            onClick={() => {
              setFilter(status);
              setSkip(0);
            }}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              filter === status
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading library...</p>
        </div>
      ) : items.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow text-center">
          <p className="text-gray-600">
            No articles yet. Start by uploading or searching for articles.
          </p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Authors</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Rating</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm text-gray-900">{item.title}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {Array.isArray(item.authors) ? item.authors.join(", ") : "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <select
                        value={item.status}
                        onChange={(e) =>
                          handleStatusChange(item.article_id, e.target.value as any)
                        }
                        className="px-2 py-1 border rounded bg-white text-sm"
                      >
                        <option value="unread">Unread</option>
                        <option value="reading">Reading</option>
                        <option value="read">Read</option>
                      </select>
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {item.rating ? `${item.rating}/5` : "-"}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => handleRemove(item.article_id)}
                        className="text-red-600 hover:text-red-800 font-medium"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-6 flex justify-between items-center">
            <button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg disabled:opacity-50"
            >
              Previous
            </button>
            <p className="text-gray-600">
              Showing {skip + 1}-{Math.min(skip + limit, total)} of {total}
            </p>
            <button
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= total}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
