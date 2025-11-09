import { useState } from "react";
import { FunnelIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { Button } from "./Button";
import { Input } from "./Input";

export interface FilterOptions {
  keyword?: string;
  startYear?: number;
  endYear?: number;
  startDate?: string;
  endDate?: string;
  categoryId?: number;
}

interface AdvancedFilterProps {
  onFilterChange: (filters: FilterOptions) => void;
  categories?: Array<{ id: number; name: string }>;
}

export function AdvancedFilter({ onFilterChange, categories = [] }: AdvancedFilterProps) {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({});

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
  };

  const applyFilters = () => {
    onFilterChange(filters);
  };

  const clearFilters = () => {
    const emptyFilters = {};
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const hasActiveFilters = Object.keys(filters).some(
    (key) => filters[key as keyof FilterOptions] !== undefined && filters[key as keyof FilterOptions] !== ""
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Button
          variant={showFilters ? "primary" : "secondary"}
          size="sm"
          onClick={() => setShowFilters(!showFilters)}
        >
          <FunnelIcon className="h-4 w-4 mr-2" />
          Advanced Filters
          {hasActiveFilters && (
            <span className="ml-2 bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded-full">
              Active
            </span>
          )}
        </Button>

        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <XMarkIcon className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      {showFilters && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Keyword Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Keyword Search
              </label>
              <Input
                type="text"
                placeholder="Search in title, abstract, keywords, or authors..."
                value={filters.keyword || ""}
                onChange={(e) => handleFilterChange("keyword", e.target.value)}
              />
              <p className="mt-1 text-xs text-gray-500">
                Searches across article title, abstract, keywords, and author names
              </p>
            </div>

            {/* Publication Year Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Year
              </label>
              <Input
                type="number"
                placeholder="e.g., 2020"
                value={filters.startYear || ""}
                onChange={(e) => handleFilterChange("startYear", e.target.value ? parseInt(e.target.value) : undefined)}
                min="1900"
                max={new Date().getFullYear()}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Year
              </label>
              <Input
                type="number"
                placeholder="e.g., 2024"
                value={filters.endYear || ""}
                onChange={(e) => handleFilterChange("endYear", e.target.value ? parseInt(e.target.value) : undefined)}
                min="1900"
                max={new Date().getFullYear()}
              />
            </div>

            {/* Upload Date Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Start Date
              </label>
              <Input
                type="date"
                value={filters.startDate || ""}
                onChange={(e) => handleFilterChange("startDate", e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload End Date
              </label>
              <Input
                type="date"
                value={filters.endDate || ""}
                onChange={(e) => handleFilterChange("endDate", e.target.value)}
              />
            </div>

            {/* Category Filter */}
            {categories.length > 0 && (
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  value={filters.categoryId || ""}
                  onChange={(e) => handleFilterChange("categoryId", e.target.value ? parseInt(e.target.value) : undefined)}
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4 border-t border-gray-200">
            <Button variant="secondary" size="md" onClick={clearFilters}>
              Clear
            </Button>
            <Button variant="primary" size="md" onClick={applyFilters}>
              Apply Filters
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
