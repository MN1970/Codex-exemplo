# GitHub Webhook Integration

Portal Master GitHub webhook integration for Manta Maestro agent registry synchronization.

## Overview

The GitHub webhook system handles inbound webhooks from GitHub repositories and processes events to:

1. **Extract and sync agent metadata** from CLAUDE.md changes
2. **Validate agent metadata** in pull requests
3. **Index knowledge content** from issue discussions
4. **Trigger version releases** and agent updates

## Architecture

### Components

#### `app/services/github_service.py`
Core business logic for webhook processing:

- **`GitHubWebhookHandler`** - Main handler class with async methods:
  - `verify_signature()` - HMAC-SHA256 signature verification
  - `parse_claude_md()` - Extract agent metadata from CLAUDE.md
  - `extract_knowledge_urls()` - Find external knowledge sources
  - `trigger_sync_event()` - Notify Portal Integration service
  - `handle_push_event()` - Process repository push events
  - `handle_pull_request_event()` - Validate PR changes
  - `handle_issue_event()` - Index knowledge from issues
  - `handle_release_event()` - Handle version releases

#### `app/routers/github.py`
FastAPI endpoints:

- `POST /api/webhooks/github` - Main webhook receiver (202 Accepted)
  - Verifies X-Hub-Signature-256
  - Dispatches to background handlers
  - Returns immediately with delivery ID
  
- `GET /api/webhooks/github/status` - Webhook integration status

#### `app/main.py`
Main application updates:

- Import and include GitHub router
- Add webhook configuration endpoint: `GET /api/config/webhooks`

## Configuration

### Environment Variables

```bash
# GitHub webhook secret (from repository settings)
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Portal Integration service URL (default: http://localhost:8016)
PORTAL_INTEGRATION_URL=http://localhost:8016
```

### GitHub Repository Setup

1. Go to repository Settings → Webhooks
2. Create a new webhook:
   - **Payload URL:** `https://your-domain/api/webhooks/github`
   - **Content type:** `application/json`
   - **Secret:** Generate and set `GITHUB_WEBHOOK_SECRET`
   - **Events:** Select "Let me select individual events"
   - **Selected events:**
     - Push
     - Pull requests
     - Issues
     - Releases

## Event Handling

### Push Events
Triggered when code is pushed to the repository.

**Processing:**
- Detects if `CLAUDE.md` was modified
- If modified, triggers `agent_metadata_updated` sync event
- Extracts new agent metadata from updated file
- Notifies Portal Integration service

**Example payload sent to integration service:**
```json
{
  "event_type": "agent_metadata_updated",
  "timestamp": "2026-07-16T10:30:00Z",
  "payload": {
    "repository": "manta/Codex-exemplo",
    "branch": "main",
    "event": "claude_md_updated",
    "modified_files": ["CLAUDE.md", "some_other_file.py"]
  }
}
```

### Pull Request Events
Triggered when a PR is opened, synchronized, or updated.

**Processing:**
- Triggers `pull_request_validation` sync event
- Portal Integration can perform validations on agent metadata changes
- Validates routing rules syntax
- Ensures backwards compatibility

**Example payload:**
```json
{
  "event_type": "pull_request_validation",
  "timestamp": "2026-07-16T10:30:00Z",
  "payload": {
    "repository": "manta/Codex-exemplo",
    "pull_request": 42,
    "action": "opened",
    "title": "Update agent metadata"
  }
}
```

### Issue Events
Triggered when issues are opened or edited.

**Processing:**
- Filters by `documentation` or `knowledge` labels
- Only labeled issues trigger sync
- Triggers `knowledge_content_indexed` sync event
- Builds knowledge base from issue discussions

**Filtered by labels:** `documentation`, `knowledge`

### Release Events
Triggered when a new release is published.

**Processing:**
- Triggers `agent_version_released` sync event
- Portal Integration can update agent version information
- Enables semantic versioning tracking

## CLAUDE.md Parsing

The parser extracts:

### 1. Version
```
Versão: **v4.2** (2026-07-05)
```

### 2. Agents (from tables)
```
| Código | Agente | Aliases | Tier default | Status |
|--------|--------|---------|--------------|--------|
| Manta 00 | maestro | maestro, manta-router | Haiku→Sonnet | ✅ Operacional |
```

Extracts: code, name, aliases, tier, status

### 3. Routing Rules (from code blocks)
```
IF menção a saneamento|ETA|ETE → agente-saneamento
IF menção a transmissão|LT|subestação → agente-energia
```

Extracts: keywords, target agent, rule type

### 4. RAG Collections (from tables)
```
| Coleção | Prefixo storage | Fontes iniciais | Status |
|---------|-----------------|-----------------|--------|
| saneamento | san: | SNIS, IWA, NBR 12211-12218 | 🆕 v4.2 |
```

Extracts: name, prefix, sources list, status

### 5. SharePoint Routing (from tables)
```
| Agente | Pasta SP sugerida | Pattern |
|--------|-------------------|---------|
| agente-saneamento | 03_Projetos/Saneamento/* | *.pdf, *.dwg, *.xlsx |
```

Extracts: agent, folder path, file patterns

## Knowledge URL Extraction

The extractor finds and normalizes:

1. **Markdown links:** `[Title](https://url.com)`
2. **Bare URLs:** `https://example.com/path`
3. **Common sources:** SNIS, ANTAQ, ANEEL, ICOLD, CBDB, etc.

Returns list with format, title, and source type.

## Signature Verification

Uses HMAC-SHA256 constant-time comparison:

```python
# GitHub sends: X-Hub-Signature-256: sha256=<hex_digest>
# We verify: HMAC_SHA256(secret, body) == provided_signature
```

**Security:**
- Uses `hmac.compare_digest()` to prevent timing attacks
- Validates signature before processing any payload
- Rejects unsigned or tampered requests (401 Unauthorized)

## Testing

### Running Tests

```bash
cd portal/backend
pytest tests/test_github_webhooks.py -v
pytest tests/test_github_webhooks.py::TestGitHubWebhookSignature -v
pytest tests/test_github_webhooks.py::TestClaudeMdParsing -v
```

### Test Coverage

- ✅ Signature verification (valid, invalid, tampered)
- ✅ CLAUDE.md parsing (agents, routing, RAG, SharePoint)
- ✅ Knowledge URL extraction (markdown, bare, sources)
- ✅ Event handlers (push, PR, issue, release)
- ✅ Sync event triggering (success, retry, timeout)
- ⏳ Integration tests (Phase 2)

### Mock Testing

Tests use `unittest.mock` for:
- HTTP requests (httpx mocking)
- Portal Integration service responses
- Async operations

Example:
```python
with patch.object(handler, "trigger_sync_event", new_callable=AsyncMock) as mock_sync:
    mock_sync.return_value = True
    success, message = await handler.handle_push_event(payload)
```

## Phase 2: Implementation Roadmap

### Planned Features

1. **Webhook Persistence**
   - Store webhook deliveries in database
   - Track delivery status and retry history
   - Enable re-delivery of failed events

2. **Portal Integration Service**
   - Implement `POST /api/sync/webhook` endpoint in Portal Integration
   - Handle agent metadata updates
   - Validate and merge metadata changes
   - Update agent registry

3. **Full Integration Tests**
   - End-to-end webhook processing
   - Database state verification
   - Portal Integration interaction validation

4. **Advanced Parsing**
   - Support multiple CLAUDE.md formats
   - Incremental parsing (track deltas)
   - Conflict detection and resolution

5. **Knowledge Base Indexing**
   - Vector embeddings for knowledge sources
   - Semantic search integration
   - Automatic knowledge discovery

6. **Validation & Enforcement**
   - CLAUDE.md schema validation
   - Routing rule consistency checks
   - Agent metadata completeness checks
   - CI/CD integration (GitHub Actions)

7. **Observability**
   - Webhook event logging and analytics
   - Metrics: processing time, success rate, retries
   - Structured logging with correlation IDs
   - Alerts for failures

## Error Handling

### Retry Strategy

For server errors (5xx):
- Automatic retry with exponential backoff
- Max 3 retries (configurable via `max_retries`)
- Sleep pattern: 2^retry_count seconds

For client errors (4xx):
- No retry
- Log warning with details
- Return failure status

### Timeout Handling

- HTTP timeout: 30 seconds (configurable)
- Triggers retry on timeout
- Graceful degradation

## Logging

All operations logged with:
- Event type and repository
- Processing status (success/failure)
- Delivery ID for tracing
- Extracted metadata summaries

Example:
```
Processing push event for manta/Codex-exemplo on branch main with 3 commits
CLAUDE.md was modified, triggering metadata sync
Extracted 5 agents, 3 routing rules, 2 RAG collections
Successfully triggered sync event: agent_metadata_updated (status: 200)
```

## Future Integration Points

### MCP Server
When Portal Master exposes MCP interface:
- Tools to manually trigger webhook processing
- Tools to query webhook delivery history
- Tools to validate agent metadata

### Dashboard
Future Portal dashboard features:
- Webhook delivery visualization
- Agent metadata sync status
- Validation error reports
- Knowledge base indexing progress

## References

- [GitHub Webhooks Documentation](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [GitHub Security](https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks)
- [HMAC-SHA256 in Python](https://docs.python.org/3/library/hmac.html)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## Support

For issues or questions:
1. Check test cases for usage examples
2. Review event payload structures in router
3. Consult CLAUDE.md format in Codex-exemplo repo
4. See Portal Integration service documentation
