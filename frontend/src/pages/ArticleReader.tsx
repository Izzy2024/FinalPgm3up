import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";
import { articlesAPI } from "../services/api";
import { Button } from "../components/ui";

export default function ArticleReader() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [article, setArticle] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        if (id) {
            fetchArticle(parseInt(id));
        }
    }, [id]);

    const fetchArticle = async (articleId: number) => {
        try {
            setLoading(true);
            const res = await articlesAPI.get(articleId);
            setArticle(res.data);
        } catch (err) {
            setError("Failed to load article details");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const [pdfUrl, setPdfUrl] = useState<string>("");

    useEffect(() => {
        const loadPdf = async () => {
            if (!id) return;
            try {
                const token = localStorage.getItem("access_token");
                const response = await fetch(`${(import.meta as any).env.VITE_API_URL}/api/articles/${id}/view`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) throw new Error('Failed to load PDF');

                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                setPdfUrl(url);
            } catch (err) {
                console.error("Error loading PDF:", err);
                setError("Failed to load PDF document");
            }
        };

        loadPdf();

        return () => {
            if (pdfUrl) URL.revokeObjectURL(pdfUrl);
        };
    }, [id]);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
            </div>
        );
    }

    if (error || !article) {
        return (
            <div className="p-8 text-center">
                <p className="text-red-600 mb-4">{error || "Article not found"}</p>
                <Button onClick={() => navigate(-1)} variant="secondary">
                    Go Back
                </Button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)]">
            <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-4">
                    <Button onClick={() => navigate(-1)} variant="ghost" size="sm">
                        <ArrowLeftIcon className="h-5 w-5 mr-1" />
                        Back
                    </Button>
                    <div>
                        <h1 className="text-lg font-bold text-gray-900 line-clamp-1">
                            {article.title}
                        </h1>
                        {article.authors && (
                            <p className="text-xs text-gray-500 line-clamp-1">
                                {article.authors.join(", ")}
                            </p>
                        )}
                    </div>
                </div>
                <div className="flex gap-2">
                    {/* Future: Add annotation tools here */}
                </div>
            </div>

            <div className="flex-1 bg-gray-100 p-4 overflow-hidden">
                {pdfUrl ? (
                    <iframe
                        src={pdfUrl}
                        className="w-full h-full rounded-lg shadow-lg border border-gray-200 bg-white"
                        title="PDF Viewer"
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-600"></div>
                    </div>
                )}
            </div>
        </div>
    );
}
