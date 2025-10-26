import { useState, useEffect } from "react";
import { 
  MagnifyingGlassIcon,
  TrashIcon,
  EyeIcon
} from "@heroicons/react/24/outline";
import { StarIcon as StarSolidIcon } from "@heroicons/react/24/solid";
import { libraryAPI, articlesAPI } from "../services/api";
import { Badge, Input, Button, Table, TableHeader, TableColumn, TableBody, TableRow, TableCell, Dropdown, ArticleDetailModal, BibliographyModal } from "../components/ui";

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
  article?: {
    abstract?: string;
    journal?: string;
    publication_year?: number;
    doi?: string;
    keywords?: string[];
  };
}

const STATUS_LABELS = {
  all: "All Articles",
  unread: "Unread",
  reading: "Reading",
  read: "Read",
};

export default function Library() {
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | "unread" | "reading" | "read">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [selectedArticle, setSelectedArticle] = useState<LibraryItem | null>(null);
  const [showBibliography, setShowBibliography] = useState(false);
  const [bibliography, setBibliography] = useState<any>(null);
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
      if (selectedArticle && selectedArticle.article_id === articleId) {
        setSelectedArticle({ ...selectedArticle, status: newStatus });
      }
    } catch (err) {
      setError("Failed to update article status");
    }
  };

  const handleRatingChange = async (articleId: number, rating: number) => {
    try {
      await libraryAPI.update(articleId, undefined, rating);
      setItems(
        items.map((item) =>
          item.article_id === articleId ? { ...item, rating } : item
        )
      );
      if (selectedArticle && selectedArticle.article_id === articleId) {
        setSelectedArticle({ ...selectedArticle, rating });
      }
    } catch (err) {
      setError("Failed to update article rating");
    }
  };

  const handleViewDetails = async (item: LibraryItem) => {
    setSelectedArticle(item);
  };

  const handleViewBibliography = async () => {
    if (!selectedArticle) return;

    try {
      const formats = ["apa", "mla", "chicago", "bibtex", "ris"] as const;
      const bib: any = {};

      for (const format of formats) {
        try {
          const res = await articlesAPI.getBibliography(selectedArticle.article_id, format);
          bib[format] = res.data.bibliography;
        } catch (err) {
          bib[format] = "Unable to generate citation";
        }
      }

      setBibliography({
        title: selectedArticle.title,
        bibliography: bib,
      });
      setShowBibliography(true);
    } catch (err) {
      setError("Failed to load bibliography");
    }
  };

  const filteredItems = items.filter((item) =>
    searchQuery === "" ||
    item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.authors.some((author) => author.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Library</h1>
          <p className="text-gray-600 mt-1">
            {total} article{total !== 1 ? "s" : ""} in your collection
          </p>
        </div>
        <Button variant="primary" size="md">
          Import Articles
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            type="text"
            placeholder="Search by title or author..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            icon={MagnifyingGlassIcon}
          />
        </div>
        
        <div className="flex gap-2 flex-wrap">
          {(["all", "unread", "reading", "read"] as const).map((status) => (
            <Badge
              key={status}
              variant={filter === status ? "primary" : "default"}
              active={filter === status}
              clickable
              onClick={() => {
                setFilter(status);
                setSkip(0);
              }}
            >
              {STATUS_LABELS[status]}
            </Badge>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading library...</p>
          </div>
        </div>
      ) : filteredItems.length === 0 ? (
        <div className="bg-white p-12 rounded-lg shadow text-center">
          <p className="text-gray-600 text-lg">
            {searchQuery
              ? "No articles match your search."
              : "No articles yet. Start by uploading or searching for articles."}
          </p>
        </div>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableColumn>Title</TableColumn>
              <TableColumn>Authors</TableColumn>
              <TableColumn>Status</TableColumn>
              <TableColumn>Rating</TableColumn>
              <TableColumn>Actions</TableColumn>
            </TableHeader>
            <TableBody>
              {filteredItems.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium text-gray-900">{item.title}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Added {new Date(item.added_at).toLocaleDateString()}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <p className="text-gray-600">
                      {Array.isArray(item.authors) && item.authors.length > 0
                        ? item.authors.join(", ")
                        : "-"}
                    </p>
                  </TableCell>
                  <TableCell>
                    <Dropdown
                      label={`${item.status.charAt(0).toUpperCase()}${item.status.slice(1)}`}
                      value={item.status}
                      options={[
                        { value: "unread", label: "Unread" },
                        { value: "reading", label: "Reading" },
                        { value: "read", label: "Read" },
                      ]}
                      onChange={(newStatus) => handleStatusChange(item.article_id, newStatus as "unread" | "reading" | "read")}
                    />
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {item.rating ? (
                        <>
                          {[...Array(5)].map((_, i) => (
                            <StarSolidIcon
                              key={i}
                              className={`h-4 w-4 ${
                                i < item.rating! ? "text-yellow-400" : "text-gray-300"
                              }`}
                            />
                          ))}
                        </>
                      ) : (
                        <span className="text-gray-400 text-sm">Not rated</span>
                      )}
                    </div>
                  </TableCell>
                   <TableCell>
                     <div className="flex gap-2">
                       <Button
                         variant="ghost"
                         size="sm"
                         onClick={() => handleViewDetails(item)}
                       >
                         <EyeIcon className="h-4 w-4 text-blue-600" />
                       </Button>
                       <Button
                         variant="ghost"
                         size="sm"
                         onClick={() => handleRemove(item.article_id)}
                       >
                         <TrashIcon className="h-4 w-4 text-red-600" />
                       </Button>
                     </div>
                   </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between">
            <Button
              onClick={() => setSkip(Math.max(0, skip - limit))}
              disabled={skip === 0}
              variant="secondary"
              size="sm"
            >
              Previous
            </Button>
            <p className="text-sm text-gray-600">
              Showing {skip + 1}-{Math.min(skip + limit, total)} of {total}
            </p>
            <Button
              onClick={() => setSkip(skip + limit)}
              disabled={skip + limit >= total}
              variant="secondary"
              size="sm"
            >
              Next
            </Button>
          </div>
        </>
      )}

      {selectedArticle && (
        <ArticleDetailModal
          isOpen={!!selectedArticle}
          onClose={() => setSelectedArticle(null)}
          article={{
            id: selectedArticle.article_id,
            title: selectedArticle.title,
            authors: selectedArticle.authors,
            abstract: selectedArticle.article?.abstract,
            journal: selectedArticle.article?.journal,
            publication_year: selectedArticle.article?.publication_year,
            doi: selectedArticle.article?.doi,
            keywords: selectedArticle.article?.keywords,
            added_at: selectedArticle.added_at,
            status: selectedArticle.status,
            rating: selectedArticle.rating,
            notes: selectedArticle.notes || undefined,
          }}
          onStatusChange={(status) => handleStatusChange(selectedArticle.article_id, status)}
          onRatingChange={(rating) => handleRatingChange(selectedArticle.article_id, rating)}
          onBibliography={handleViewBibliography}
        />
      )}

      {bibliography && (
        <BibliographyModal
          isOpen={showBibliography}
          onClose={() => setShowBibliography(false)}
          title={bibliography.title}
          bibliography={bibliography.bibliography}
        />
      )}
    </div>
  );
}
