"""
Business logic for Knowledge Base service
"""

import logging
import re
import hashlib
from typing import List, Optional, Tuple, Dict
from datetime import datetime

from sqlalchemy.orm import Session
import httpx

from app.models.knowledge import KnowledgeDocument, KnowledgeCategory
from app.schemas.knowledge import KnowledgeDocumentCreate
from app.db import knowledge as knowledge_db

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manager for knowledge base operations"""

    def __init__(self, db: Session):
        self.db = db

    async def ingest_from_github(
        self,
        repo_owner: str,
        repo_name: str,
        paths: Optional[List[str]] = None,
        branch: str = "main",
    ) -> Dict:
        """
        Ingest documents from GitHub repository.

        Args:
            repo_owner: GitHub repository owner
            repo_name: GitHub repository name
            paths: Optional list of file paths to ingest (e.g., ["CLAUDE.md", "*.md"])
            branch: Branch name (default: main)

        Returns:
            Dictionary with ingestion results
        """
        ingested_count = 0
        failed_count = 0
        errors = []

        try:
            # Build GitHub API URL
            base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

            async with httpx.AsyncClient() as client:
                # Get repository contents
                try:
                    contents_response = await client.get(f"{base_url}/contents", params={"ref": branch})
                    contents_response.raise_for_status()
                    contents = contents_response.json()
                except httpx.HTTPError as e:
                    error_msg = f"Failed to fetch repository contents: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    return {
                        "status": "failed",
                        "ingested_count": 0,
                        "failed_count": 1,
                        "errors": errors,
                        "message": error_msg,
                    }

                # Process files
                for item in contents:
                    if item["type"] != "file":
                        continue

                    filename = item["name"]

                    # Apply path filter if specified
                    if paths:
                        if not any(self._matches_pattern(filename, p) for p in paths):
                            continue

                    # Skip files that are not documentation
                    if not self._is_documentation_file(filename):
                        continue

                    try:
                        # Download file content
                        file_url = item["download_url"]
                        file_response = await client.get(file_url)
                        file_response.raise_for_status()
                        content = file_response.text

                        # Parse and ingest document
                        await self._ingest_single_document(
                            doc_id=self._generate_doc_id(repo_owner, repo_name, filename),
                            title=filename,
                            content=content,
                            source_url=item["html_url"],
                            source_repo=f"{repo_owner}/{repo_name}",
                            source_path=item["path"],
                        )

                        ingested_count += 1
                        logger.info(f"Ingested {filename} from {repo_owner}/{repo_name}")

                    except Exception as e:
                        failed_count += 1
                        error_msg = f"Failed to ingest {filename}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)

        except Exception as e:
            error_msg = f"GitHub ingestion failed: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)

        return {
            "status": "success" if ingested_count > 0 else "partial",
            "ingested_count": ingested_count,
            "failed_count": failed_count,
            "errors": errors,
            "message": f"Ingested {ingested_count} documents, {failed_count} failed",
        }

    async def _ingest_single_document(
        self,
        doc_id: str,
        title: str,
        content: str,
        source_url: str,
        source_repo: str,
        source_path: str,
    ) -> KnowledgeDocument:
        """Ingest a single document with chunking"""
        # Determine category from content
        category = self._detect_category(title, content)

        # Extract eixo tags
        eixo_tags = self._extract_eixo_tags(content)

        # Extract agent IDs
        agent_ids = self._extract_agent_ids(content)

        # Create document
        doc_create = KnowledgeDocumentCreate(
            id=doc_id,
            title=title,
            content=content,
            summary=self._extract_summary(content),
            category=category,
            eixo_tags=eixo_tags,
            agent_ids=agent_ids,
            source_url=source_url,
            source_repo=source_repo,
            source_path=source_path,
            created_by="github-ingest",
        )

        try:
            document = knowledge_db.create_knowledge_document(self.db, doc_create)
            logger.info(f"Created document {doc_id}")
        except ValueError:
            # Document already exists, update it
            existing = knowledge_db.get_knowledge_document_by_id(self.db, doc_id)
            if existing:
                doc_update = doc_create.model_validate(doc_create)
                document = knowledge_db.update_knowledge_document(self.db, doc_id, doc_update)
                logger.info(f"Updated document {doc_id}")
            else:
                raise

        # Create chunks
        chunks = self.chunk_document(content)
        for chunk_index, chunk_data in enumerate(chunks):
            knowledge_db.create_knowledge_chunk(
                self.db,
                doc_id=document.id,
                chunk_text=chunk_data["text"],
                chunk_index=chunk_index,
                section_title=chunk_data.get("section"),
                token_count=self._estimate_token_count(chunk_data["text"]),
            )

        return document

    def chunk_document(self, content: str, chunk_size: int = 500) -> List[Dict]:
        """
        Chunk a document into manageable pieces.

        Args:
            content: Document content
            chunk_size: Target chunk size in words (approximate)

        Returns:
            List of chunks with text and optional section title
        """
        chunks = []

        # Split by markdown headings first
        sections = re.split(r"^(#{1,6}\s+.*?)$", content, flags=re.MULTILINE)

        current_section = None
        current_chunk = []
        current_chunk_size = 0

        for i, section in enumerate(sections):
            if not section.strip():
                continue

            # Check if this is a heading
            if re.match(r"^#{1,6}\s+", section):
                current_section = section.strip()
                if current_chunk:
                    # Save previous chunk
                    chunks.append({
                        "text": "\n".join(current_chunk),
                        "section": current_section if chunks else None,
                    })
                    current_chunk = []
                    current_chunk_size = 0
            else:
                # Add content to current chunk
                words = len(section.split())
                current_chunk.append(section)
                current_chunk_size += words

                # Create new chunk if size exceeded
                if current_chunk_size > chunk_size and current_chunk:
                    chunks.append({
                        "text": "\n".join(current_chunk),
                        "section": current_section,
                    })
                    current_chunk = []
                    current_chunk_size = 0

        # Add remaining chunk
        if current_chunk:
            chunks.append({
                "text": "\n".join(current_chunk),
                "section": current_section,
            })

        return chunks if chunks else [{"text": content, "section": None}]

    @staticmethod
    def _detect_category(title: str, content: str) -> KnowledgeCategory:
        """Detect document category based on title and content"""
        title_lower = title.lower()
        content_lower = content.lower()

        if "claude.md" in title_lower or "agent" in content_lower:
            return KnowledgeCategory.AGENT_PROFILE
        elif "skill" in title_lower or "skill" in content_lower:
            return KnowledgeCategory.SKILL
        elif "routing" in title_lower or "routing" in content_lower:
            return KnowledgeCategory.ROUTING_RULE
        elif "runbook" in title_lower or "runbook" in content_lower:
            return KnowledgeCategory.RUNBOOK
        elif "architecture" in title_lower or "architecture" in content_lower:
            return KnowledgeCategory.ARCHITECTURE
        else:
            return KnowledgeCategory.DOCUMENTATION

    @staticmethod
    def _extract_eixo_tags(content: str) -> List[str]:
        """Extract eixo tags from content"""
        tags = set()

        # Match S1-S10, Horizontal, Vertical, Lifecycle
        patterns = [
            r"S[1-9](?:\d)?",
            r"(Horizontal|Vertical|Lifecycle)",
            r"Manta\s+\d+(?:-[A-Z]\d+)?",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tags.update(matches)

        return sorted(list(tags))

    @staticmethod
    def _extract_agent_ids(content: str) -> List[str]:
        """Extract agent IDs from content"""
        agent_ids = set()

        # Match manta-## or Manta ## (including multi-segment IDs like manta-03-s1)
        patterns = [
            r"manta-[\w\d-]+",
            r"Manta\s+\d+(?:-[A-Z]\d+)?",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            agent_ids.update(m.lower() for m in matches)

        return sorted(list(agent_ids))

    @staticmethod
    def _extract_summary(content: str, max_length: int = 300) -> str:
        """Extract a summary from the first paragraph of content"""
        # Get first non-empty line
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        if lines:
            summary = lines[0]
            if len(summary) > max_length:
                summary = summary[:max_length] + "..."
            return summary
        return ""

    @staticmethod
    def _estimate_token_count(text: str) -> int:
        """Rough estimate of token count (words * 1.3)"""
        word_count = len(text.split())
        return int(word_count * 1.3)

    @staticmethod
    def _matches_pattern(filename: str, pattern: str) -> bool:
        """Check if filename matches a glob pattern"""
        import fnmatch
        return fnmatch.fnmatch(filename, pattern)

    @staticmethod
    def _is_documentation_file(filename: str) -> bool:
        """Check if file is a documentation file"""
        doc_extensions = {".md", ".txt", ".rst"}
        return any(filename.lower().endswith(ext) for ext in doc_extensions)

    @staticmethod
    def _generate_doc_id(repo_owner: str, repo_name: str, filename: str) -> str:
        """Generate a unique document ID"""
        base = f"{repo_owner}/{repo_name}/{filename}"
        return hashlib.md5(base.encode()).hexdigest()[:20]

    async def refresh_external_sources(self) -> Dict:
        """
        Refresh all external sources to check if they're still accessible.
        Phase 2 implementation - stub for now.
        """
        return {
            "status": "pending",
            "message": "External source refresh coming in Phase 2",
        }
