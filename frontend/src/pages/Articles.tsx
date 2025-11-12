import { useEffect, useMemo, useState } from "react";
import { articlesAPI, libraryAPI } from "../services/api";
import { Button, Input, Table, TableHeader, TableColumn, TableBody, TableRow, TableCell, Badge, Card } from "../components/ui";

interface ArticleRow {
  id: number;
  title: string;
  authors?: string[];
  journal?: string;
  publication_year?: number;
  doi?: string;
  keywords?: string[];
}

export default function Articles() {
  const [items, setItems] = useState<ArticleRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [skip, setSkip] = useState(0);
  const limit = 20;
  const [pageCount, setPageCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [inLibraryIds, setInLibraryIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    const h = setTimeout(() => setDebouncedSearch(search), 350);
    return () => clearTimeout(h);
  }, [search]);

  useEffect(() => {
    fetchData();
  }, [debouncedSearch, skip]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError("");
      const [articlesRes, libRes] = await Promise.all([
        articlesAPI.list({ skip, limit, keyword: debouncedSearch || undefined }),
        libraryAPI.list({ skip: 0, limit: 1000 }),
      ]);
      const data = articlesRes.data as ArticleRow[];
      const list = Array.isArray(data) ? data : [];
      setItems(list);
      setPageCount(list.length);
      setHasMore(list.length === limit);

      const inLib = new Set<number>();
      const libItems = libRes.data.items || [];
      for (const it of libItems) inLib.add(it.article_id);
      setInLibraryIds(inLib);
    } catch (e) {
      setError("Failed to load articles");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const visible = useMemo(() => items, [items]);

  const addToLibrary = async (articleId: number) => {
    try {
      await libraryAPI.add(articleId);
      const next = new Set(inLibraryIds);
      next.add(articleId);
      setInLibraryIds(next);
    } catch (e) {
      console.error(e);
      setError("Unable to add to library");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">All Articles</h1>
          <p className="text-gray-600">Browse database and add to your library</p>
        </div>
        <div className="w-full sm:w-80">
          <Input placeholder="Search title/keywords" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-700 border border-red-200 rounded-lg">{error}</div>
      )}

      <Card>
        <Table>
          <TableHeader>
            <TableColumn>Title</TableColumn>
            <TableColumn>Year</TableColumn>
            <TableColumn>DOI</TableColumn>
            <TableColumn>Keywords</TableColumn>
            <TableColumn>Action</TableColumn>
          </TableHeader>
          <TableBody loading={loading} emptyMessage={loading ? "" : "No articles found"}>
            {visible.map((a) => (
              <TableRow key={a.id}>
                <TableCell>
                  <div className="font-medium text-gray-900">{a.title}</div>
                  {a.authors && a.authors.length > 0 && (
                    <div className="text-sm text-gray-600 truncate max-w-xl">{a.authors.join(", ")}</div>
                  )}
                  {a.journal && (
                    <div className="text-xs text-gray-500">{a.journal}</div>
                  )}
                </TableCell>
                <TableCell className="w-24">{a.publication_year || "—"}</TableCell>
                <TableCell className="w-64 truncate">{a.doi || "—"}</TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1 max-w-lg">
                    {(a.keywords || []).slice(0, 5).map((k, i) => (
                      <Badge key={i} variant="secondary">{k}</Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell className="w-40">
                  {inLibraryIds.has(a.id) ? (
                    <Badge variant="success">In Library</Badge>
                  ) : (
                    <Button size="sm" onClick={() => addToLibrary(a.id)}>Add to Library</Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <div className="flex items-center justify-between mt-4">
          <Button
            onClick={() => setSkip(Math.max(0, skip - limit))}
            disabled={skip === 0}
            variant="secondary"
            size="sm"
          >
            Previous
          </Button>
          <p className="text-sm text-gray-600">Showing {pageCount} items</p>
          <Button
            onClick={() => setSkip(skip + limit)}
            disabled={!hasMore}
            variant="secondary"
            size="sm"
          >
            Next
          </Button>
        </div>
      </Card>
    </div>
  );
}
