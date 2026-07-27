/**
 * useKnowledgeHub.ts — React hook for Knowledge Hub operations
 *
 * Provides:
 *  • uploadFile(file, tags, description, onProgress)
 *  • deleteDocument(id)
 *  • searchDocuments(query, filters)
 *  • getDocumentChunks(id)
 *  • listDocuments(filters)
 *  • updateDocument(id, updates)
 *
 * Handles:
 *  • Multipart upload with progress tracking
 *  • Error handling and retry logic
 *  • Polling for async processing status
 */
import { useCallback, useState } from 'react';
import axios, { AxiosProgressEvent } from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || '/api';

interface ListDocumentsFilters {
  tags?: string;
  status?: string;
  created_after?: string;
  created_before?: string;
  org_id?: string;
  page?: number;
  page_size?: number;
}

interface SearchFilters {
  tags?: string[];
  org_ids?: string[];
  top_k?: number;
}

interface Document {
  id: string;
  org_id: string;
  title: string;
  filename: string;
  file_type: string;
  source_url?: string;
  size_bytes: number;
  tags: string[];
  description?: string;
  created_by?: string;
  processing_status: 'pending' | 'processing' | 'complete' | 'failed';
  progress_pct: number;
  error_message?: string;
  chunk_count: number;
  created_at: string;
  updated_at: string;
  deleted_at?: string;
}

interface DocumentChunk {
  id: string;
  chunk_index: number;
  content: string;
  content_tokens: number;
  metadata: Record<string, any>;
  created_at: string;
}

interface DocumentDetail extends Document {
  chunks: DocumentChunk[];
}

interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  content: string;
  content_tokens: number;
  similarity_score: number;
  page_num?: number;
  tags: string[];
  metadata: Record<string, any>;
}

interface UploadResponse {
  id: string;
  processing_status: string;
}

export const useKnowledgeHub = () => {
  const [uploading, setUploading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Upload file with multipart form data
   * Supports progress tracking and polling for async processing
   */
  const uploadFile = useCallback(
    async (
      file: File,
      tags: string[] = [],
      description: string = '',
      onProgress?: (progress: number) => void
    ): Promise<Document> => {
      try {
        setUploading(true);
        setError(null);

        // Validate file type
        const allowedTypes = ['pdf', 'csv', 'dwg', 'txt', 'docx'];
        const fileExt = file.name.split('.').pop()?.toLowerCase();
        if (!fileExt || !allowedTypes.includes(fileExt)) {
          throw new Error(
            `File type ${fileExt} not supported. Allowed: ${allowedTypes.join(', ')}`
          );
        }

        // Validate file size (500MB)
        const maxSize = 500 * 1024 * 1024;
        if (file.size > maxSize) {
          throw new Error(`File size exceeds 500MB limit`);
        }

        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name);
        formData.append('tags', JSON.stringify(tags));
        formData.append('description', description);

        // Upload
        const uploadResponse = await axios.post<UploadResponse>(
          `${API_BASE}/knowledge/upload`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent: AxiosProgressEvent) => {
              if (progressEvent.total) {
                const progress = Math.round(
                  (progressEvent.loaded / progressEvent.total) * 100
                );
                onProgress?.(progress);
              }
            },
          }
        );

        const docId = uploadResponse.data.id;
        onProgress?.(100);

        // Poll for processing completion
        const maxAttempts = 60; // 5 minutes with 5s intervals
        let attempts = 0;
        let doc: Document | null = null;

        while (attempts < maxAttempts) {
          const response = await axios.get<Document>(
            `${API_BASE}/knowledge/documents/${docId}`
          );
          doc = response.data;

          if (doc.processing_status === 'complete' || doc.processing_status === 'failed') {
            break;
          }

          attempts++;
          await new Promise(resolve => setTimeout(resolve, 5000));
        }

        if (!doc) {
          throw new Error('Document upload polling timeout');
        }

        if (doc.processing_status === 'failed') {
          throw new Error(`Processing failed: ${doc.error_message}`);
        }

        return doc;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Upload failed';
        setError(message);
        throw err;
      } finally {
        setUploading(false);
      }
    },
    []
  );

  /**
   * Delete document (soft-delete)
   */
  const deleteDocument = useCallback(async (docId: string): Promise<void> => {
    try {
      setError(null);
      await axios.delete(`${API_BASE}/knowledge/documents/${docId}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Delete failed';
      setError(message);
      throw err;
    }
  }, []);

  /**
   * Semantic search across documents
   */
  const searchDocuments = useCallback(
    async (query: string, filters?: SearchFilters): Promise<SearchResult[]> => {
      try {
        setSearching(true);
        setError(null);

        const response = await axios.post(`${API_BASE}/knowledge/semantic-search`, {
          query,
          top_k: filters?.top_k || 10,
          tags: filters?.tags || [],
          org_ids: filters?.org_ids || [],
        });

        return response.data.results || [];
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Search failed';
        setError(message);
        throw err;
      } finally {
        setSearching(false);
      }
    },
    []
  );

  /**
   * Get document with chunks
   */
  const getDocumentChunks = useCallback(
    async (docId: string): Promise<DocumentDetail> => {
      try {
        setError(null);
        const response = await axios.get<DocumentDetail>(
          `${API_BASE}/knowledge/documents/${docId}`
        );
        return response.data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to fetch document';
        setError(message);
        throw err;
      }
    },
    []
  );

  /**
   * List documents with optional filters
   */
  const listDocuments = useCallback(
    async (filters?: ListDocumentsFilters): Promise<Document[]> => {
      try {
        setError(null);

        const params = new URLSearchParams();
        if (filters?.tags) params.append('tags', filters.tags);
        if (filters?.status) params.append('status_filter', filters.status);
        if (filters?.created_after) params.append('created_after', filters.created_after);
        if (filters?.created_before) params.append('created_before', filters.created_before);
        if (filters?.org_id) params.append('org_id', filters.org_id);
        if (filters?.page) params.append('page', filters.page.toString());
        if (filters?.page_size) params.append('page_size', filters.page_size.toString());

        const response = await axios.get(`${API_BASE}/knowledge/documents`, {
          params,
        });

        return response.data.documents || [];
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to list documents';
        setError(message);
        throw err;
      }
    },
    []
  );

  /**
   * Update document metadata
   */
  const updateDocument = useCallback(
    async (
      docId: string,
      updates: {
        title?: string;
        tags?: string[];
        description?: string;
      }
    ): Promise<Document> => {
      try {
        setError(null);

        const response = await axios.put<Document>(
          `${API_BASE}/knowledge/documents/${docId}`,
          updates
        );

        return response.data;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Update failed';
        setError(message);
        throw err;
      }
    },
    []
  );

  /**
   * Get document versions
   */
  const getDocumentVersions = useCallback(async (docId: string) => {
    try {
      setError(null);

      const response = await axios.get(
        `${API_BASE}/knowledge/documents/${docId}/versions`
      );

      return response.data || [];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch versions';
      setError(message);
      throw err;
    }
  }, []);

  return {
    uploadFile,
    deleteDocument,
    searchDocuments,
    getDocumentChunks,
    listDocuments,
    updateDocument,
    getDocumentVersions,
    uploading,
    searching,
    error,
    setError,
  };
};
