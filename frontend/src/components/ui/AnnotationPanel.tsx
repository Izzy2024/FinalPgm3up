import { useState } from "react";
import {
  PencilIcon,
  TrashIcon,
  PlusIcon,
  XMarkIcon,
  TagIcon,
} from "@heroicons/react/24/outline";
import { Button } from "./Button";
import { Input, Textarea } from "./Input";
import { Badge } from "./Badge";

export interface Annotation {
  id: number;
  article_id: number;
  highlighted_text: string;
  page_number?: number;
  position_data?: any;
  color: "yellow" | "green" | "blue" | "red" | "purple";
  note?: string;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

interface AnnotationPanelProps {
  annotations: Annotation[];
  onCreateAnnotation?: (annotation: Partial<Annotation>) => void;
  onUpdateAnnotation?: (id: number, annotation: Partial<Annotation>) => void;
  onDeleteAnnotation?: (id: number) => void;
  readOnly?: boolean;
}

const COLOR_OPTIONS = [
  { value: "yellow", label: "Yellow", color: "bg-yellow-200 border-yellow-400" },
  { value: "green", label: "Green", color: "bg-green-200 border-green-400" },
  { value: "blue", label: "Blue", color: "bg-blue-200 border-blue-400" },
  { value: "red", label: "Red", color: "bg-red-200 border-red-400" },
  { value: "purple", label: "Purple", color: "bg-purple-200 border-purple-400" },
] as const;

export function AnnotationPanel({
  annotations,
  onCreateAnnotation,
  onUpdateAnnotation,
  onDeleteAnnotation,
  readOnly = false,
}: AnnotationPanelProps) {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState<Partial<Annotation>>({
    highlighted_text: "",
    color: "yellow",
    note: "",
    tags: [],
    page_number: undefined,
  });
  const [newTag, setNewTag] = useState("");
  const [filterColor, setFilterColor] = useState<string | null>(null);
  const [filterTag, setFilterTag] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      onUpdateAnnotation?.(editingId, formData);
      setEditingId(null);
    } else {
      onCreateAnnotation?.(formData);
      setShowCreateForm(false);
    }
    resetForm();
  };

  const handleEdit = (annotation: Annotation) => {
    setEditingId(annotation.id);
    setFormData({
      highlighted_text: annotation.highlighted_text,
      color: annotation.color,
      note: annotation.note,
      tags: annotation.tags || [],
      page_number: annotation.page_number,
    });
    setShowCreateForm(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("Delete this annotation?")) {
      onDeleteAnnotation?.(id);
    }
  };

  const resetForm = () => {
    setFormData({
      highlighted_text: "",
      color: "yellow",
      note: "",
      tags: [],
      page_number: undefined,
    });
    setNewTag("");
    setEditingId(null);
  };

  const handleCancel = () => {
    setShowCreateForm(false);
    setEditingId(null);
    resetForm();
  };

  const addTag = () => {
    if (newTag && !formData.tags?.includes(newTag)) {
      setFormData({
        ...formData,
        tags: [...(formData.tags || []), newTag],
      });
      setNewTag("");
    }
  };

  const removeTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags?.filter((t) => t !== tag) || [],
    });
  };

  // Get all unique tags from annotations
  const allTags = Array.from(
    new Set(annotations.flatMap((a) => a.tags || []))
  );

  // Filter annotations
  const filteredAnnotations = annotations.filter((annotation) => {
    if (filterColor && annotation.color !== filterColor) return false;
    if (filterTag && !annotation.tags?.includes(filterTag)) return false;
    return true;
  });

  const getColorClass = (color: string) => {
    const colorOption = COLOR_OPTIONS.find((c) => c.value === color);
    return colorOption?.color || "bg-yellow-200 border-yellow-400";
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Annotations ({filteredAnnotations.length})
        </h3>
        {!readOnly && !showCreateForm && (
          <Button
            variant="primary"
            size="sm"
            onClick={() => setShowCreateForm(true)}
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            New Annotation
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Color:</span>
          <Badge
            variant={filterColor === null ? "primary" : "default"}
            clickable
            onClick={() => setFilterColor(null)}
          >
            All
          </Badge>
          {COLOR_OPTIONS.map((color) => (
            <div
              key={color.value}
              className={`px-3 py-1 rounded-full cursor-pointer border-2 ${
                filterColor === color.value ? "ring-2 ring-offset-2 ring-blue-500" : ""
              } ${color.color}`}
              onClick={() => setFilterColor(color.value)}
            >
              <span className="text-xs font-medium">{color.label}</span>
            </div>
          ))}
        </div>
      </div>

      {allTags.length > 0 && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-medium text-gray-700">Tags:</span>
          <Badge
            variant={filterTag === null ? "primary" : "default"}
            clickable
            onClick={() => setFilterTag(null)}
          >
            All
          </Badge>
          {allTags.map((tag) => (
            <Badge
              key={tag}
              variant={filterTag === tag ? "primary" : "default"}
              clickable
              onClick={() => setFilterTag(tag)}
            >
              {tag}
            </Badge>
          ))}
        </div>
      )}

      {/* Create/Edit Form */}
      {showCreateForm && !readOnly && (
        <form
          onSubmit={handleSubmit}
          className="bg-white p-4 rounded-lg border-2 border-primary-500 space-y-4"
        >
          <h4 className="font-medium text-gray-900">
            {editingId ? "Edit Annotation" : "New Annotation"}
          </h4>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Highlighted Text *
            </label>
            <Textarea
              value={formData.highlighted_text}
              onChange={(e) =>
                setFormData({ ...formData, highlighted_text: e.target.value })
              }
              placeholder="Paste or type the text you want to highlight..."
              rows={3}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Color
            </label>
            <div className="flex gap-2">
              {COLOR_OPTIONS.map((color) => (
                <button
                  key={color.value}
                  type="button"
                  className={`px-4 py-2 rounded-lg border-2 ${
                    formData.color === color.value
                      ? "ring-2 ring-offset-2 ring-blue-500"
                      : ""
                  } ${color.color}`}
                  onClick={() => setFormData({ ...formData, color: color.value })}
                >
                  {color.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Page Number (optional)
            </label>
            <Input
              type="number"
              value={formData.page_number || ""}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  page_number: e.target.value ? parseInt(e.target.value) : undefined,
                })
              }
              placeholder="e.g., 5"
              min={1}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Note (optional)
            </label>
            <Textarea
              value={formData.note}
              onChange={(e) => setFormData({ ...formData, note: e.target.value })}
              placeholder="Add your thoughts or comments..."
              rows={2}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tags
            </label>
            <div className="flex gap-2 mb-2">
              <Input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                placeholder="Add a tag..."
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    addTag();
                  }
                }}
              />
              <Button type="button" variant="secondary" size="sm" onClick={addTag}>
                Add
              </Button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.tags?.map((tag) => (
                <Badge key={tag} variant="primary">
                  {tag}
                  <button
                    type="button"
                    onClick={() => removeTag(tag)}
                    className="ml-2 text-primary-700 hover:text-primary-900"
                  >
                    <XMarkIcon className="h-3 w-3" />
                  </button>
                </Badge>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" size="md" onClick={handleCancel}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" size="md">
              {editingId ? "Update" : "Create"}
            </Button>
          </div>
        </form>
      )}

      {/* Annotations List */}
      <div className="space-y-3">
        {filteredAnnotations.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg">
            <p className="text-gray-500">
              {annotations.length === 0
                ? "No annotations yet. Create your first one!"
                : "No annotations match the selected filters."}
            </p>
          </div>
        ) : (
          filteredAnnotations.map((annotation) => (
            <div
              key={annotation.id}
              className={`p-4 rounded-lg border-2 ${getColorClass(annotation.color)}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 mb-1">
                    {annotation.page_number && (
                      <span className="text-gray-600 mr-2">
                        Page {annotation.page_number}
                      </span>
                    )}
                  </p>
                  <blockquote className="text-gray-800 italic border-l-4 border-gray-400 pl-3">
                    "{annotation.highlighted_text}"
                  </blockquote>
                </div>
                {!readOnly && (
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleEdit(annotation)}
                      className="text-blue-600 hover:text-blue-800"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(annotation.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                )}
              </div>

              {annotation.note && (
                <div className="mt-2 text-sm text-gray-700 bg-white bg-opacity-60 p-2 rounded">
                  <p className="font-medium text-gray-900 mb-1">Note:</p>
                  <p>{annotation.note}</p>
                </div>
              )}

              {annotation.tags && annotation.tags.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {annotation.tags.map((tag) => (
                    <Badge key={tag} variant="default">
                      <TagIcon className="h-3 w-3 mr-1" />
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}

              <div className="mt-2 text-xs text-gray-500">
                {new Date(annotation.created_at).toLocaleString()}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
