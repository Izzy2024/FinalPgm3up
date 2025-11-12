import { useState, useEffect, useMemo } from "react";
import {
  MagnifyingGlassIcon,
  TrashIcon,
  EyeIcon,
  PlusIcon,
  XMarkIcon,
  SparklesIcon,
  BeakerIcon,
} from "@heroicons/react/24/outline";
import { StarIcon as StarSolidIcon } from "@heroicons/react/24/solid";
import { libraryAPI, articlesAPI } from "../services/api";
import type {
  BatchSummaryResult,
  SummaryMethod,
  SummaryLevel,
  LibraryStats,
  UserIndex,
} from "../services/api";
import {
  Badge,
  Input,
  Button,
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Dropdown,
  ArticleDetailModal,
  BibliographyModal,
  BatchSummaryModal,
} from "../components/ui";

interface LibraryArticle {
  id: number;
  title: string;
  authors?: string[];
  abstract?: string;
  journal?: string;
  publication_year?: number;
  doi?: string;
  keywords?: string[];
  auto_topics?: string[];
}

interface LibraryItem {
  id: number;
  article_id: number;
  title: string;
  authors?: string[];
  status: "unread" | "reading" | "read";
  rating: number | null;
  notes: string | null;
  added_at: string;
  updated_at: string;
  topics?: string[];
  article?: LibraryArticle;
}

const STATUS_LABELS = {
  all: "All Articles",
  unread: "Unread",
  reading: "Reading",
  read: "Read",
};

const SORT_OPTIONS = [
  { value: "recent", label: "Newest first" },
  { value: "title", label: "Title A-Z" },
  { value: "rating", label: "Highest rated" },
] as const;

const DEFAULT_INDEX_COLOR = "#2563eb";

export default function Library() {
  const [items, setItems] = useState<LibraryItem[]>([]);
  const [stats, setStats] = useState<LibraryStats | null>(null);
  const [segments, setSegments] = useState<{ topic: string; count: number }[]>([]);
  const [indexes, setIndexes] = useState<UserIndex[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState<"all" | "unread" | "reading" | "read">("all");
  const [sortOption, setSortOption] = useState<"recent" | "title" | "rating">("recent");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [activeTopic, setActiveTopic] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [skip, setSkip] = useState(0);
  const [total, setTotal] = useState(0);
  const [selectedArticle, setSelectedArticle] = useState<LibraryItem | null>(null);
  const [showBibliography, setShowBibliography] = useState(false);
  const [bibliography, setBibliography] = useState<any>(null);
  const [selectedForSummary, setSelectedForSummary] = useState<number[]>([]);
  const [summaryMethod, setSummaryMethod] = useState<SummaryMethod>("groq");
  const [summaryLevel, setSummaryLevel] = useState<SummaryLevel>("detailed");
  const [combineSummaries, setCombineSummaries] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryResults, setSummaryResults] = useState<BatchSummaryResult[]>([]);
  const [combinedSummary, setCombinedSummary] = useState<string | null>(null);
  const [combinedMethod, setCombinedMethod] = useState<string | null>(null);
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [summaryError, setSummaryError] = useState("");
  const [creatingIndex, setCreatingIndex] = useState(false);
  const [newIndexName, setNewIndexName] = useState("");
  const [newIndexKeywords, setNewIndexKeywords] = useState("");
  const [newIndexColor, setNewIndexColor] = useState(DEFAULT_INDEX_COLOR);
  const limit = 10;

  useEffect(() => {
    const handler = setTimeout(() => setDebouncedSearch(searchQuery), 350);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  useEffect(() => {
    setSkip(0);
  }, [filter, activeTopic, activeIndex, debouncedSearch, sortOption]);

  useEffect(() => {
    fetchLibrary();
  }, [filter, skip, activeTopic, activeIndex, debouncedSearch, sortOption]);

  useEffect(() => {
    fetchStats();
    fetchIndexes();
  }, []);

  useEffect(() => {
    const currentIds = new Set(items.map((item) => item.article_id));
    setSelectedForSummary((prev) => prev.filter((id) => currentIds.has(id)));
  }, [items]);

  const fetchLibrary = async () => {
    try {
      setLoading(true);
      setError("");
      const status = filter === "all" ? undefined : filter;
      const res = await libraryAPI.list({
        skip,
        limit,
        status,
        topic: activeTopic || undefined,
        search: debouncedSearch || undefined,
        index_id: activeIndex || undefined,
        sort: sortOption,
      });
      setItems(res.data.items);
      setTotal(res.data.total);
      fetchStats();
    } catch (err: any) {
      setError("Failed to load library");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await libraryAPI.getStats();
      setStats(res.data);
      setSegments(res.data.default_segments || []);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchIndexes = async () => {
    try {
      const res = await libraryAPI.listIndexes();
      setIndexes(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemove = async (articleId: number) => {
    if (!confirm("Remove this article from your library?")) return;

    try {
      await libraryAPI.remove(articleId);
      await Promise.all([fetchLibrary(), fetchStats()]);
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
      setItems((prev) =>
        prev.map((item) =>
          item.article_id === articleId ? { ...item, status: newStatus } : item
        )
      );
      if (selectedArticle && selectedArticle.article_id === articleId) {
        setSelectedArticle({ ...selectedArticle, status: newStatus });
      }
      fetchStats();
    } catch (err) {
      setError("Failed to update article status");
    }
  };

  const handleRatingChange = async (articleId: number, rating: number) => {
    try {
      await libraryAPI.update(articleId, undefined, rating);
      setItems((prev) =>
        prev.map((item) =>
          item.article_id === articleId ? { ...item, rating } : item
        )
      );
      if (selectedArticle && selectedArticle.article_id === articleId) {
        setSelectedArticle({ ...selectedArticle, rating });
      }
      fetchStats();
    } catch (err) {
      setError("Failed to update article rating");
    }
  };

  const handleSetTopic = async (articleId: number, topic: string) => {
    try {
      await libraryAPI.update(articleId, undefined, undefined, undefined, [topic]);
      setItems((prev) =>
        prev.map((it) =>
          it.article_id === articleId ? { ...it, topics: [topic] } : it
        )
      );
      fetchStats();
    } catch (err) {
      setError("Failed to update topic");
    }
  };

  const handleViewDetails = (item: LibraryItem) => {
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
        } catch {
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

  const toggleArticleSelection = (articleId: number) => {
    setSelectedForSummary((prev) =>
      prev.includes(articleId)
        ? prev.filter((id) => id !== articleId)
        : [...prev, articleId]
    );
  };

  const toggleSelectAllVisible = () => {
    const visibleIds = items.map((item) => item.article_id);
    if (visibleIds.length === 0) return;
    const allSelected = visibleIds.every((id) => selectedForSummary.includes(id));
    if (allSelected) {
      setSelectedForSummary((prev) => prev.filter((id) => !visibleIds.includes(id)));
    } else {
      const merged = new Set([...selectedForSummary, ...visibleIds]);
      setSelectedForSummary(Array.from(merged));
    }
  };

  const handleSummarizeSelected = async () => {
    if (selectedForSummary.length === 0) return;
    setSummaryLoading(true);
    setSummaryError("");
    try {
      const res = await articlesAPI.summarize({
        article_ids: selectedForSummary,
        method: summaryMethod,
        level: summaryLevel,
        combined: combineSummaries,
      });
      setSummaryResults(res.data.results);
      setCombinedSummary(res.data.combined_summary || null);
      setCombinedMethod(res.data.combined_method || null);
      setShowSummaryModal(true);
    } catch (err: any) {
      const detail =
        err?.response?.data?.detail || "Unable to summarize the selected articles.";
      setSummaryError(detail);
    } finally {
      setSummaryLoading(false);
    }
  };

  const handleCreateIndex = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!newIndexName.trim() || !newIndexKeywords.trim()) return;

    try {
      const keywords = newIndexKeywords.split(",").map((kw) => kw.trim());
      await libraryAPI.createIndex({
        name: newIndexName.trim(),
        keywords,
        color: newIndexColor,
      });
      setNewIndexName("");
      setNewIndexKeywords("");
      setNewIndexColor(DEFAULT_INDEX_COLOR);
      setCreatingIndex(false);
      fetchIndexes();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || "Unable to create index.";
      setError(detail);
    }
  };

  const handleDeleteIndex = async (indexId: number) => {
    if (!confirm("Delete this custom index?")) return;
    try {
      await libraryAPI.deleteIndex(indexId);
      if (activeIndex === indexId) {
        setActiveIndex(null);
      }
      fetchIndexes();
    } catch (err) {
      setError("Unable to delete index.");
    }
  };

  const summarySelectedCount = selectedForSummary.length;
  const summarySuccessCount = summaryResults.filter((result) => result.success).length;
  const summaryFailedCount = summaryResults.length - summarySuccessCount;
  const allVisibleSelected =
    items.length > 0 && items.every((item) => selectedForSummary.includes(item.article_id));

  const activeSegmentLabel = useMemo(() => {
    if (!activeTopic) return "All topics";
    const segment = segments.find((seg) => seg.topic === activeTopic);
    return segment ? `${segment.topic} (${segment.count})` : activeTopic;
  }, [activeTopic, segments]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">My Library</h1>
          <p className="text-gray-600 mt-1">
            {total} article{total !== 1 ? "s" : ""} in your collection
          </p>
        </div>
        <Button
          variant="primary"
          size="md"
          onClick={() => {
            setActiveTopic(null);
            setActiveIndex(null);
            setFilter("all");
            setSearchQuery("");
            setSortOption("recent");
          }}
        >
          Clear Filters
        </Button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-4">
        <Input
          type="text"
          placeholder="Search by title, author, or keyword..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          icon={MagnifyingGlassIcon}
        />
        <div className="flex gap-2 flex-wrap">
          {(["all", "unread", "reading", "read"] as const).map((status) => (
            <Badge
              key={status}
              variant={filter === status ? "primary" : "default"}
              active={filter === status}
              clickable
              onClick={() => {
                setFilter(status);
              }}
            >
              {STATUS_LABELS[status]}
            </Badge>
          ))}
        </div>
        <Dropdown
          label={SORT_OPTIONS.find((opt) => opt.value === sortOption)?.label || "Sort"}
          value={sortOption}
          options={SORT_OPTIONS.map((opt) => ({ value: opt.value, label: opt.label }))}
          onChange={(value) => setSortOption(value as typeof sortOption)}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900">Auto Segments</h3>
            <p className="text-xs text-gray-500">{activeSegmentLabel}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {segments.map((segment) => (
              <button
                key={segment.topic}
                onClick={() => {
                  setActiveIndex(null);
                  setActiveTopic((prev) =>
                    prev === segment.topic ? null : segment.topic
                  );
                }}
                className={`px-3 py-1 text-sm rounded-full border ${
                  activeTopic === segment.topic
                    ? "bg-blue-600 text-white border-blue-600"
                    : "bg-gray-100 text-gray-700 border-transparent hover:bg-gray-200"
                }`}
              >
                {segment.topic} ({segment.count})
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900">Custom Indexes</h3>
            <Button
              size="sm"
              variant={creatingIndex ? "secondary" : "primary"}
              onClick={() => setCreatingIndex((prev) => !prev)}
            >
              {creatingIndex ? (
                <>
                  <XMarkIcon className="h-4 w-4 mr-2" />
                  Cancel
                </>
              ) : (
                <>
                  <PlusIcon className="h-4 w-4 mr-2" />
                  New Index
                </>
              )}
            </Button>
          </div>
          {creatingIndex && (
            <form className="space-y-3" onSubmit={handleCreateIndex}>
              <Input
                type="text"
                placeholder="Name"
                value={newIndexName}
                onChange={(e) => setNewIndexName(e.target.value)}
                required
              />
              <Input
                type="text"
                placeholder="Keywords (comma separated)"
                value={newIndexKeywords}
                onChange={(e) => setNewIndexKeywords(e.target.value)}
                required
              />
              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-600">Color</label>
                <input
                  type="color"
                  value={newIndexColor}
                  onChange={(e) => setNewIndexColor(e.target.value)}
                  className="h-8 w-12 border border-gray-200 rounded"
                />
              </div>
              <div className="flex gap-2">
                <Button type="submit" variant="primary" size="sm">
                  Save Index
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setCreatingIndex(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
          <div className="flex flex-wrap gap-2">
            {indexes.length === 0 && !creatingIndex ? (
              <p className="text-sm text-gray-500">Create your first index to group articles.</p>
            ) : (
              indexes.map((index) => (
                <div
                  key={index.id}
                  className={`flex items-center gap-2 px-3 py-1 rounded-full border ${
                    activeIndex === index.id ? "border-blue-600 bg-blue-50" : "border-gray-200"
                  }`}
                  style={{ backgroundColor: activeIndex === index.id ? undefined : index.color + "20" }}
                >
                  <button
                    onClick={() => {
                      setActiveTopic(null);
                      setActiveIndex((prev) => (prev === index.id ? null : index.id));
                    }}
                    className="text-sm font-medium text-gray-800"
                  >
                    {index.name}
                  </button>
                  <button
                    onClick={() => handleDeleteIndex(index.id)}
                    className="text-xs text-gray-500 hover:text-red-600"
                    title="Delete index"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {items.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
          <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex flex-wrap gap-3 items-center">
              <div>
                <p className="text-xs uppercase text-gray-500 font-semibold">Summary Method</p>
                <div className="mt-2 flex items-center gap-2">
                  <Button
                    variant={summaryMethod === 'groq' ? 'neon' : 'secondary'}
                    size="sm"
                    onClick={() => setSummaryMethod('groq')}
                    title="AI-powered summary (Groq)"
                  >
                    <SparklesIcon className="h-4 w-4 mr-2" />
                    IA (Groq)
                  </Button>
                  <Button
                    variant={summaryMethod === 'local' ? 'neonGreen' : 'secondary'}
                    size="sm"
                    onClick={() => setSummaryMethod('local')}
                    title="Local Python extractive summary"
                  >
                    <BeakerIcon className="h-4 w-4 mr-2" />
                    Python Local
                  </Button>
                </div>
              </div>

              <div>
                <p className="text-xs uppercase text-gray-500 font-semibold">Summary Level</p>
                <div className="mt-2 flex items-center gap-2">
                  <Button
                    variant={summaryLevel === 'executive' ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setSummaryLevel('executive')}
                    title="Ejecutivo: 1 página (~500 palabras)"
                  >
                    📄 Ejecutivo
                  </Button>
                  <Button
                    variant={summaryLevel === 'detailed' ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setSummaryLevel('detailed')}
                    title="Detallado: 3-4 páginas (~1,800 palabras)"
                  >
                    📋 Detallado
                  </Button>
                  <Button
                    variant={summaryLevel === 'exhaustive' ? 'primary' : 'secondary'}
                    size="sm"
                    onClick={() => setSummaryLevel('exhaustive')}
                    title="Exhaustivo: 8-10 páginas (~4,000 palabras)"
                  >
                    📚 Exhaustivo
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {summaryLevel === 'executive' && '1 pág (~500 palabras, 5 min)'}
                  {summaryLevel === 'detailed' && '3-4 págs (~1,800 palabras, 15 min)'}
                  {summaryLevel === 'exhaustive' && '8-10 págs (~4,000 palabras, 40 min)'}
                </p>
              </div>
              <label className="flex items-center gap-2 text-sm text-gray-600 mt-4 lg:mt-0">
                <input
                  type="checkbox"
                  className="form-checkbox h-4 w-4 text-primary-600"
                  checked={combineSummaries}
                  onChange={(e) => setCombineSummaries(e.target.checked)}
                />
                Generate combined summary
              </label>
              <p className="text-sm text-gray-500 mt-4 lg:mt-0">
                Selected: <span className="font-semibold">{summarySelectedCount}</span>
              </p>
            </div>
            <Button
              variant="neon"
              size="sm"
              disabled={summarySelectedCount === 0 || summaryLoading}
              onClick={handleSummarizeSelected}
            >
              {summaryLoading
                ? "Summarizing..."
                : `Summarize${summarySelectedCount > 0 ? ` (${summarySelectedCount})` : ""}`}
            </Button>
          </div>
          {summaryError && (
            <p className="text-sm text-red-600 mt-3">{summaryError}</p>
          )}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading library...</p>
          </div>
        </div>
      ) : items.length === 0 ? (
        <div className="bg-white p-12 rounded-lg shadow text-center">
          <p className="text-gray-600 text-lg">
            {debouncedSearch
              ? "No articles match your search."
              : "No articles yet. Start by uploading or searching for articles."}
          </p>
        </div>
      ) : (
        <>
          <Table>
            <TableHeader>
              <TableColumn className="w-12">
                <input
                  type="checkbox"
                  className="form-checkbox h-4 w-4 text-primary-600"
                  onChange={toggleSelectAllVisible}
                  checked={allVisibleSelected}
                  disabled={items.length === 0}
                />
              </TableColumn>
              <TableColumn>Title</TableColumn>
              <TableColumn>Authors & Topics</TableColumn>
              <TableColumn>Status</TableColumn>
              <TableColumn>Rating</TableColumn>
              <TableColumn>Actions</TableColumn>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow key={`${item.id}-${item.article_id}`}>
                  <TableCell className="w-12">
                    <input
                      type="checkbox"
                      className="form-checkbox h-4 w-4 text-primary-600"
                      checked={selectedForSummary.includes(item.article_id)}
                      onChange={() => toggleArticleSelection(item.article_id)}
                    />
                  </TableCell>
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
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(item.topics || item.article?.auto_topics || []).map((topic) => (
                      <span
                        key={`${item.article_id}-${topic}`}
                        className="inline-flex text-xs px-2 py-0.5 rounded-full bg-blue-50 text-blue-700"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                  <div className="mt-2">
                    <Dropdown
                      label="Set Topic"
                      value=""
                      options={
                        (segments || []).map((s) => ({ value: s.topic, label: s.topic }))
                      }
                      onChange={(val) => handleSetTopic(item.article_id, val as string)}
                    />
                  </div>
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
                      onChange={(newStatus) =>
                        handleStatusChange(item.article_id, newStatus as "unread" | "reading" | "read")
                      }
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
                              onClick={() => handleRatingChange(item.article_id, i + 1)}
                            />
                          ))}
                        </>
                      ) : (
                        <span
                          className="text-gray-400 text-sm cursor-pointer"
                          onClick={() => handleRatingChange(item.article_id, 3)}
                        >
                          Not rated
                        </span>
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

      {showSummaryModal && (
        <BatchSummaryModal
          isOpen={showSummaryModal}
          onClose={() => setShowSummaryModal(false)}
          results={summaryResults}
          total={summaryResults.length}
          successful={summarySuccessCount}
          failed={summaryFailedCount}
          combinedSummary={combinedSummary}
          combinedMethod={combinedMethod}
        />
      )}
    </div>
  );
}
