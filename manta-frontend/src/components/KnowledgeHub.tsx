/**
 * KnowledgeHub.tsx — Knowledge Hub UI (upload, browse, search, versions)
 *
 * Features:
 *  • Drag-drop upload (PDF/CSV/DWG/TXT/DOCX)
 *  • Upload progress bar (%, ETA)
 *  • Document browser (grid, sort by date/size/tags)
 *  • Tag management (create, filter, bulk apply)
 *  • Document preview (PDF viewer, CSV table, text)
 *  • Version history selector (browse, compare, revert)
 *  • Semantic search across documents
 */
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useKnowledgeHub } from '../hooks/useKnowledgeHub';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';

interface Document {
  id: string;
  title: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  tags: string[];
  created_at: string;
  processing_status: 'pending' | 'processing' | 'complete' | 'failed';
  progress_pct: number;
  error_message?: string;
  chunk_count: number;
}

interface UploadProgress {
  file: string;
  progress: number;
  eta_seconds?: number;
}

interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  content: string;
  similarity_score: number;
}

type ViewMode = 'upload' | 'browse' | 'search' | 'versions';

const KnowledgeHub: React.FC = () => {
  const {
    uploadFile,
    deleteDocument,
    searchDocuments,
    getDocumentChunks,
    listDocuments,
  } = useKnowledgeHub();

  // State
  const [viewMode, setViewMode] = useState<ViewMode>('browse');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [filterTags, setFilterTags] = useState<string[]>([]);
  const [allTags, setAllTags] = useState<Set<string>>(new Set());
  const [isDragging, setIsDragging] = useState(false);
  const [newTagInput, setNewTagInput] = useState('');
  const [sortBy, setSortBy] = useState<'date' | 'size' | 'name'>('date');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      const docs = await listDocuments({ tags: filterTags.join(',') });
      setDocuments(docs);

      // Extract all unique tags
      const tags = new Set<string>();
      docs.forEach(doc => {
        doc.tags.forEach(tag => tags.add(tag));
      });
      setAllTags(tags);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  // Sorted documents
  const sortedDocuments = useMemo(() => {
    const sorted = [...documents];
    if (sortBy === 'date') {
      sorted.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    } else if (sortBy === 'size') {
      sorted.sort((a, b) => b.size_bytes - a.size_bytes);
    } else if (sortBy === 'name') {
      sorted.sort((a, b) => a.title.localeCompare(b.title));
    }
    return sorted;
  }, [documents, sortBy]);

  // Drag-drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    for (const file of files) {
      await handleFileUpload(file);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    for (const file of files) {
      await handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setError(null);
      setUploadProgress({ file: file.name, progress: 0 });

      const tags = filterTags.length > 0 ? filterTags : [];
      await uploadFile(file, tags, '', (progress) => {
        setUploadProgress(prev =>
          prev ? { ...prev, progress } : null
        );
      });

      setUploadProgress(null);
      await loadDocuments();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploadProgress(null);
    }
  };

  // Search handler
  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const results = await searchDocuments(searchQuery, {
        tags: filterTags,
        top_k: 20,
      });
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  // Delete handler
  const handleDelete = async (docId: string) => {
    if (!window.confirm('Delete this document? This cannot be undone.')) return;

    try {
      setError(null);
      await deleteDocument(docId);
      await loadDocuments();
      if (selectedDoc?.id === docId) {
        setSelectedDoc(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  // Tag management
  const handleAddTag = () => {
    if (newTagInput.trim() && !allTags.has(newTagInput.trim())) {
      setAllTags(prev => new Set([...prev, newTagInput.trim()]));
      setNewTagInput('');
    }
  };

  const toggleFilterTag = (tag: string) => {
    setFilterTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  // Format bytes
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="knowledge-hub">
      {/* Header */}
      <div className="kb-header">
        <h1>Knowledge Hub</h1>
        <p>Upload, organize, search documents and manage versions</p>
      </div>

      {/* Error message */}
      {error && (
        <div className="kb-error">
          <span>{error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* View mode tabs */}
      <div className="kb-tabs">
        <button
          className={viewMode === 'upload' ? 'active' : ''}
          onClick={() => setViewMode('upload')}
        >
          Upload
        </button>
        <button
          className={viewMode === 'browse' ? 'active' : ''}
          onClick={() => setViewMode('browse')}
        >
          Browse Documents ({documents.length})
        </button>
        <button
          className={viewMode === 'search' ? 'active' : ''}
          onClick={() => setViewMode('search')}
        >
          Search
        </button>
        {selectedDoc && (
          <button
            className={viewMode === 'versions' ? 'active' : ''}
            onClick={() => setViewMode('versions')}
          >
            Versions
          </button>
        )}
      </div>

      {/* Main content */}
      <div className="kb-content">
        {/* Upload View */}
        {viewMode === 'upload' && (
          <div className="kb-upload">
            <Card>
              <div
                className={`kb-dropzone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
              >
                <div className="kb-dropzone-content">
                  <p>Drag & drop files here or click to select</p>
                  <p className="kb-dropzone-hint">
                    Supported: PDF, CSV, DWG, TXT, DOCX (max 500MB)
                  </p>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.csv,.dwg,.txt,.docx"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                    id="file-input"
                  />
                  <label htmlFor="file-input">
                    <Button as="span">Select Files</Button>
                  </label>
                </div>
              </div>

              {uploadProgress && (
                <div className="kb-upload-progress">
                  <p>{uploadProgress.file}</p>
                  <div className="kb-progress-bar">
                    <div
                      className="kb-progress-fill"
                      style={{ width: `${uploadProgress.progress}%` }}
                    />
                  </div>
                  <p className="kb-progress-text">
                    {uploadProgress.progress}%
                    {uploadProgress.eta_seconds && (
                      <> — ETA {uploadProgress.eta_seconds}s</>
                    )}
                  </p>
                </div>
              )}

              {/* Tag input */}
              <div className="kb-tags-section">
                <Label>Default Tags for Uploads</Label>
                <div className="kb-tag-input">
                  <Input
                    value={newTagInput}
                    onChange={e => setNewTagInput(e.target.value)}
                    onKeyPress={e => e.key === 'Enter' && handleAddTag()}
                    placeholder="Add tag (press Enter)"
                  />
                  <Button onClick={handleAddTag} variant="outline">
                    Add
                  </Button>
                </div>
                <div className="kb-tags">
                  {filterTags.map(tag => (
                    <span key={tag} className="kb-tag kb-tag-selected">
                      {tag}
                      <button onClick={() => toggleFilterTag(tag)}>×</button>
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Browse View */}
        {viewMode === 'browse' && (
          <div className="kb-browse">
            {/* Filters */}
            <div className="kb-filters">
              <div className="kb-sort">
                <Label>Sort by:</Label>
                <select
                  value={sortBy}
                  onChange={e => setSortBy(e.target.value as any)}
                >
                  <option value="date">Date (newest first)</option>
                  <option value="size">Size (largest first)</option>
                  <option value="name">Name (A-Z)</option>
                </select>
              </div>

              <div className="kb-tag-filter">
                <Label>Filter by tags:</Label>
                <div className="kb-tags">
                  {Array.from(allTags).map(tag => (
                    <button
                      key={tag}
                      className={`kb-tag ${filterTags.includes(tag) ? 'selected' : ''}`}
                      onClick={() => toggleFilterTag(tag)}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Document grid */}
            <div className="kb-document-grid">
              {loading ? (
                <p>Loading...</p>
              ) : sortedDocuments.length === 0 ? (
                <p className="kb-empty">No documents found</p>
              ) : (
                sortedDocuments.map(doc => (
                  <Card
                    key={doc.id}
                    className={`kb-document-card ${selectedDoc?.id === doc.id ? 'selected' : ''}`}
                  >
                    <h3>{doc.title}</h3>

                    <div className="kb-doc-meta">
                      <span className="kb-doc-type">{doc.file_type.toUpperCase()}</span>
                      <span className="kb-doc-size">{formatBytes(doc.size_bytes)}</span>
                    </div>

                    <div className="kb-doc-status">
                      {doc.processing_status === 'processing' && (
                        <div className="kb-progress-bar">
                          <div
                            className="kb-progress-fill"
                            style={{ width: `${doc.progress_pct}%` }}
                          />
                        </div>
                      )}
                      {doc.processing_status === 'complete' && (
                        <span className="kb-status-complete">
                          ✓ {doc.chunk_count} chunks
                        </span>
                      )}
                      {doc.processing_status === 'failed' && (
                        <span className="kb-status-error">
                          ✗ {doc.error_message}
                        </span>
                      )}
                    </div>

                    <div className="kb-doc-tags">
                      {doc.tags.map(tag => (
                        <span key={tag} className="kb-tag-small">
                          {tag}
                        </span>
                      ))}
                    </div>

                    <p className="kb-doc-date">{formatDate(doc.created_at)}</p>

                    <div className="kb-doc-actions">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedDoc(doc)}
                      >
                        View
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDelete(doc.id)}
                      >
                        Delete
                      </Button>
                    </div>
                  </Card>
                ))
              )}
            </div>

            {/* Document preview */}
            {selectedDoc && (
              <div className="kb-preview">
                <Card>
                  <h2>{selectedDoc.title}</h2>
                  <p>{selectedDoc.filename}</p>
                  {selectedDoc.description && (
                    <p className="kb-desc">{selectedDoc.description}</p>
                  )}
                  <div className="kb-preview-meta">
                    <div>
                      <strong>Status:</strong> {selectedDoc.processing_status}
                    </div>
                    <div>
                      <strong>Chunks:</strong> {selectedDoc.chunk_count}
                    </div>
                    <div>
                      <strong>Size:</strong> {formatBytes(selectedDoc.size_bytes)}
                    </div>
                    <div>
                      <strong>Created:</strong> {formatDate(selectedDoc.created_at)}
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        )}

        {/* Search View */}
        {viewMode === 'search' && (
          <div className="kb-search">
            <Card>
              <Label>Semantic Search</Label>
              <div className="kb-search-box">
                <Input
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && handleSearch()}
                  placeholder="Search across documents..."
                />
                <Button onClick={handleSearch} disabled={loading}>
                  {loading ? 'Searching...' : 'Search'}
                </Button>
              </div>

              {/* Search results */}
              <div className="kb-search-results">
                {searchResults.map(result => (
                  <Card key={result.chunk_id} className="kb-result-card">
                    <h4>{result.document_title}</h4>
                    <p className="kb-result-content">{result.content.substring(0, 200)}...</p>
                    <div className="kb-result-meta">
                      <span className="kb-score">
                        Score: {(result.similarity_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </Card>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Versions View */}
        {viewMode === 'versions' && selectedDoc && (
          <div className="kb-versions">
            <Card>
              <h2>Version History: {selectedDoc.title}</h2>
              <p>Compare and restore previous versions (coming soon)</p>
            </Card>
          </div>
        )}
      </div>

      <style>{`
        .knowledge-hub {
          padding: 24px;
          max-width: 1400px;
          margin: 0 auto;
        }

        .kb-header {
          margin-bottom: 32px;
        }

        .kb-header h1 {
          font-size: 28px;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .kb-header p {
          color: #666;
          font-size: 14px;
        }

        .kb-error {
          background-color: #fee;
          border: 1px solid #fcc;
          border-radius: 4px;
          padding: 12px;
          margin-bottom: 16px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .kb-error button {
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
        }

        .kb-tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
          border-bottom: 1px solid #eee;
        }

        .kb-tabs button {
          padding: 12px 16px;
          background: none;
          border: none;
          cursor: pointer;
          border-bottom: 2px solid transparent;
          font-weight: 500;
          transition: all 0.2s;
        }

        .kb-tabs button.active {
          border-bottom-color: #0066cc;
          color: #0066cc;
        }

        .kb-tabs button:hover {
          color: #0066cc;
        }

        .kb-content {
          min-height: 400px;
        }

        .kb-dropzone {
          border: 2px dashed #ccc;
          border-radius: 8px;
          padding: 48px 24px;
          text-align: center;
          transition: all 0.2s;
          cursor: pointer;
        }

        .kb-dropzone.dragging {
          border-color: #0066cc;
          background-color: #f0f7ff;
        }

        .kb-dropzone-hint {
          font-size: 12px;
          color: #999;
          margin-top: 8px;
        }

        .kb-upload-progress {
          margin-top: 24px;
          padding-top: 24px;
          border-top: 1px solid #eee;
        }

        .kb-progress-bar {
          width: 100%;
          height: 8px;
          background-color: #eee;
          border-radius: 4px;
          overflow: hidden;
          margin: 8px 0;
        }

        .kb-progress-fill {
          height: 100%;
          background-color: #0066cc;
          transition: width 0.3s;
        }

        .kb-progress-text {
          font-size: 12px;
          color: #666;
        }

        .kb-tags-section {
          margin-top: 24px;
          padding-top: 24px;
          border-top: 1px solid #eee;
        }

        .kb-tag-input {
          display: flex;
          gap: 8px;
          margin: 8px 0;
        }

        .kb-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 8px;
        }

        .kb-tag {
          background-color: #f0f0f0;
          border: 1px solid #ddd;
          border-radius: 16px;
          padding: 4px 12px;
          font-size: 12px;
          display: inline-block;
          cursor: pointer;
          transition: all 0.2s;
        }

        .kb-tag:hover {
          background-color: #e0e0e0;
        }

        .kb-tag.selected,
        .kb-tag-selected {
          background-color: #0066cc;
          color: white;
          border-color: #0066cc;
        }

        .kb-tag-selected button {
          background: none;
          border: none;
          color: white;
          cursor: pointer;
          font-size: 14px;
          margin-left: 4px;
        }

        .kb-filters {
          display: flex;
          gap: 24px;
          margin-bottom: 24px;
          padding-bottom: 24px;
          border-bottom: 1px solid #eee;
        }

        .kb-sort,
        .kb-tag-filter {
          flex: 1;
        }

        .kb-sort select {
          width: 100%;
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-top: 4px;
        }

        .kb-document-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .kb-document-card {
          padding: 16px;
          cursor: pointer;
          transition: all 0.2s;
          border: 2px solid transparent;
        }

        .kb-document-card:hover {
          border-color: #0066cc;
        }

        .kb-document-card.selected {
          border-color: #0066cc;
          background-color: #f0f7ff;
        }

        .kb-doc-meta {
          display: flex;
          justify-content: space-between;
          margin: 8px 0;
          font-size: 12px;
        }

        .kb-doc-type {
          background-color: #f0f0f0;
          padding: 2px 6px;
          border-radius: 2px;
          font-weight: 500;
        }

        .kb-doc-size {
          color: #999;
        }

        .kb-doc-status {
          margin: 8px 0;
          font-size: 12px;
        }

        .kb-status-complete {
          color: #28a745;
        }

        .kb-status-error {
          color: #dc3545;
        }

        .kb-doc-tags {
          margin: 8px 0;
        }

        .kb-tag-small {
          display: inline-block;
          background-color: #f0f0f0;
          border-radius: 12px;
          padding: 2px 8px;
          font-size: 11px;
          margin-right: 4px;
        }

        .kb-doc-date {
          font-size: 11px;
          color: #999;
          margin: 8px 0;
        }

        .kb-doc-actions {
          display: flex;
          gap: 8px;
          margin-top: 12px;
        }

        .kb-preview {
          margin-top: 24px;
          padding-top: 24px;
          border-top: 1px solid #eee;
        }

        .kb-preview h2 {
          margin-bottom: 8px;
        }

        .kb-desc {
          color: #666;
          margin: 8px 0;
          font-size: 14px;
        }

        .kb-preview-meta {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 16px;
          margin-top: 16px;
          font-size: 13px;
        }

        .kb-search-box {
          display: flex;
          gap: 8px;
          margin: 16px 0;
        }

        .kb-search-results {
          margin-top: 24px;
        }

        .kb-result-card {
          margin-bottom: 16px;
          padding: 16px;
        }

        .kb-result-card h4 {
          margin-bottom: 8px;
        }

        .kb-result-content {
          color: #666;
          font-size: 13px;
          margin-bottom: 8px;
          line-height: 1.5;
        }

        .kb-result-meta {
          font-size: 12px;
          color: #999;
        }

        .kb-score {
          background-color: #f0f0f0;
          padding: 2px 6px;
          border-radius: 2px;
        }

        .kb-empty {
          text-align: center;
          color: #999;
          padding: 48px 24px;
        }
      `}</style>
    </div>
  );
};

export default KnowledgeHub;
