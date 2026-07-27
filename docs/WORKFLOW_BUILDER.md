# Workflow Builder User Guide

## Overview

The Workflow Builder is a visual tool for composing multi-agent workflows. It enables you to design complex agent interactions through a drag-and-drop interface, configure conditional routing, and monitor real-time execution.

**Key Features:**
- Drag-and-drop canvas for building workflows
- Conditional routing (if-then-else) between agents
- Parallel execution support
- Real-time execution monitoring via Server-Sent Events
- Pre-built workflow templates
- Auto-save with version history
- Dark mode support

---

## Quick Start

### 1. Open the Workflow Builder

Navigate to `/workflows` or click "Workflow Builder" in the main navigation.

### 2. Create Your First Workflow

1. Click **"+ Add Node"** to open the node menu
2. Select **"Agent"** to add an agent node
3. Click on the node to open the **Inspector Panel** (right side)
4. Assign an **Agent ID** (e.g., `researcher`, `analyzer`)
5. Add more nodes and connect them with click-and-drag

### 3. Configure Routing

For agent nodes that should route output to different agents:

1. Select the node
2. In the Inspector Panel, scroll to **"Handoff Conditions"**
3. Click **"+ Add Condition"** to define a routing rule
4. Specify:
   - **Label**: Display name for this route
   - **Target Node**: Which node handles this output
   - **Condition**: (Optional) When to take this route

Example:
```
Label: "Request Accepted"
Target: approval-agent
Condition: { status: "approved" }
```

### 4. Save & Execute

1. Enter a workflow name (top-left input)
2. Click **"Save"** to persist the workflow
3. Click **"Execute"** to run the workflow
4. Monitor execution in the **Execution Panel** (bottom-left)

---

## Node Types

### Agent Nodes
Invoke a specific agent to process data.

**Configuration:**
- `agent_id`: Required. ID of the agent to invoke
- `timeout`: Optional. Max execution time in seconds
- `config`: Optional. Agent-specific parameters

**Example:**
```json
{
  "type": "agent",
  "agent_id": "research-agent",
  "label": "Research Topic",
  "config": {
    "depth": "thorough",
    "include_sources": true
  }
}
```

### Condition Nodes
Evaluate input and route to different paths based on conditions.

**Configuration:**
- `config.num_classes`: Number of output paths
- `handoff_conditions`: Array of routing rules

**Example:**
```json
{
  "type": "condition",
  "label": "Classify Input",
  "config": { "num_classes": 3 },
  "handoff_conditions": [
    {
      "label": "Type A",
      "targetNodeId": "handler-a",
      "condition": { "classification": "A" }
    }
  ]
}
```

### Merger Nodes
Combine outputs from parallel branches.

**Use when:**
- Multiple agents run in parallel
- Results need consolidation before proceeding
- Different execution paths converge

### Start & End Nodes
Mark workflow boundaries.

- **Start**: Where the workflow begins
- **End**: Terminal node(s) for workflow completion

---

## Handoff Logic & Conditions

Handoff conditions define how output from one node routes to the next.

### Condition Structure

```typescript
interface HandoffCondition {
  id: string;                              // Unique ID
  label: string;                           // Display name
  targetNodeId: string;                    // Next node
  condition?: Record<string, unknown>;     // Routing logic (optional)
  isDefault?: boolean;                     // Default route if no match
}
```

### Condition Examples

**Exact Match:**
```json
{
  "label": "Status Approved",
  "condition": { "status": "approved" }
}
```

**Numeric Range:**
```json
{
  "label": "Score > 0.8",
  "condition": { "score": { "min": 0.8 } }
}
```

**Multiple Conditions (AND):**
```json
{
  "label": "High Confidence",
  "condition": {
    "confidence": { "min": 0.9 },
    "verified": true
  }
}
```

**Default Route:**
```json
{
  "label": "Fallback",
  "isDefault": true
}
```

### Setting Handoff Conditions

1. Select the agent node
2. Open the Inspector Panel
3. Click **"+ Add Condition"**
4. Configure:
   - Target node (click to select)
   - Condition expression (JSON editor)
   - Label for the route

---

## Workflow Patterns

### 1. Sequential Analysis Pipeline

Process data through multiple stages:

```
Start → Extract → Transform → Analyze → End
```

**Use Case:** Data processing, document analysis, claim assessment

**Template:** "Sequential Analysis"

### 2. Parallel Research

Research multiple topics simultaneously, then combine:

```
       ┌─ Research A ─┐
Start ─┤─ Research B ─├─ Merge ─ Synthesize ─ End
       └─ Research C ─┘
```

**Use Case:** Multi-topic research, competitive analysis, fact-checking

**Template:** "Parallel Research"

### 3. Decision Tree

Route to different processors based on classification:

```
Start ─ Classify ─┬─ Process A ─┐
                 ├─ Process B ─┤─ Consolidate ─ End
                 └─ Process C ─┘
```

**Use Case:** Claims routing, document classification, triage

**Template:** "Decision Tree"

### 4. Feedback Loop

Iteratively refine output until quality threshold:

```
Start ─ Generate ─ Evaluate ─┬─ (Good) ─ End
                             └─ (Refine) ─┘
                                   ↑
                                   └─ (Loop)
```

**Use Case:** Content generation, test case refinement, legal document drafting

**Template:** "Feedback Loop"

### 5. Multi-Perspective Decision Support

Analyze from multiple angles before deciding:

```
           ┌─ Financial Analysis ─┐
Start ─ Frame ─┤─ Risk Analysis ──┬─ Synthesize ─ Recommend ─ End
           └─ Impact Analysis ──┘
```

**Use Case:** Strategic decisions, M&A analysis, project evaluation

**Template:** "Decision Support System"

---

## Using Templates

Pre-built templates accelerate workflow creation:

### Loading a Template

1. Click **"+ Add Node"** → **"Load Template"** (or use Templates gallery)
2. Browse templates by category:
   - **Sequential**: Linear workflows
   - **Parallel**: Concurrent processing
   - **Branching**: Conditional routing
   - **Feedback Loops**: Iterative refinement
   - **Research**: Information gathering
   - **Analysis**: Data evaluation
   - **Decision**: Complex decision-making

3. Click **"Use Template"** to load into builder
4. Modify node IDs and configurations as needed

### Creating Custom Templates

To save your workflow as a reusable template:

1. Build and test your workflow
2. Click **"Save as Template"** (if available)
3. Provide:
   - Template name
   - Description
   - Use case tags
   - Category

Templates are stored in your organization's template library.

---

## Execution Monitoring

### Real-Time Execution

When you execute a workflow:

1. **Status Badge** shows current state:
   - `PENDING`: Queued for execution
   - `RUNNING`: Currently executing
   - `COMPLETED`: Finished successfully
   - `FAILED`: Error occurred

2. **Events Log** displays node-level activity:
   - `node_started`: Node began processing
   - `node_completed`: Node finished with output
   - `node_failed`: Node encountered error
   - `handoff_evaluated`: Routing condition evaluated

3. **Output Panel** shows final results (when completed)

### Execution Events

Each event includes:

```json
{
  "id": "evt-123",
  "nodeId": "agent-1",
  "type": "node_completed",
  "timestamp": "2026-07-27T14:30:00Z",
  "data": {
    "output": { /* agent output */ },
    "duration_ms": 2500
  }
}
```

### Troubleshooting Execution

**Workflow stuck on "RUNNING":**
- Click "Cancel" in Execution Panel
- Check agent logs for errors
- Review Agent configuration

**Output mismatch:**
- Verify handoff conditions in Inspector
- Check condition syntax in JSON editor
- Ensure target nodeId exists

**Missing events:**
- Increase polling interval in settings
- Check browser console for errors
- Verify workflow definition is valid

---

## API Reference

### REST Endpoints

#### Create Workflow

```bash
POST /api/workflows
Content-Type: application/json

{
  "name": "My Workflow",
  "description": "Description here",
  "definition": {
    "nodes": [...],
    "edges": [...],
    "metadata": {}
  }
}
```

**Response:** Workflow object with `id`

#### List Workflows

```bash
GET /api/workflows?page=1&page_size=20&search=query&is_active=true
```

**Parameters:**
- `page`: Page number (1-indexed)
- `page_size`: Results per page (1-100)
- `search`: Text search in name/description
- `is_active`: Filter by active status

**Response:** Paginated list with `total`, `page`, `page_size`, `items`

#### Get Workflow

```bash
GET /api/workflows/{workflow_id}
```

#### Update Workflow

```bash
PUT /api/workflows/{workflow_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "definition": { /* updated definition */ }
}
```

#### Execute Workflow

```bash
POST /api/workflows/{workflow_id}/execute
Content-Type: application/json

{
  "input_data": { "key": "value" },
  "metadata": {}
}
```

**Response:** Execution object with `id` (202 Accepted)

#### Track Execution

```bash
GET /api/workflows/executions/{execution_id}
```

**Response:** Execution status, events, output

#### Stream Execution (SSE)

```bash
GET /api/workflows/executions/{execution_id}/stream
Accept: text/event-stream
```

**Events:**
```
data: {"type": "node_started", "nodeId": "...", ...}
data: {"type": "status_update", "status": "running"}
data: {"type": "execution_complete", "status": "completed", ...}
```

---

## Best Practices

### Workflow Design

1. **Start Small**: Begin with sequential workflows, add complexity gradually
2. **Clear Naming**: Use descriptive labels for nodes (e.g., "Validate Claims" not "Agent1")
3. **Single Responsibility**: Each node should handle one logical task
4. **Explicit Routing**: Define all handoff conditions explicitly
5. **Default Fallback**: Always provide a default condition for error handling

### Performance

1. **Parallel Over Sequential**: Use parallel nodes for independent tasks
2. **Timeout Configuration**: Set reasonable timeouts per node
3. **Input Size**: Keep input data lean (compress if needed)
4. **Monitoring**: Use execution monitoring for long-running workflows

### Error Handling

1. **Validate Input**: First node should validate input format
2. **Error Conditions**: Create nodes to handle common error cases
3. **Retry Logic**: Use feedback loops for automatic retries
4. **Logging**: Review execution events for debugging

### Version Control

1. **Save Frequently**: Use auto-save during development
2. **Version History**: Access previous versions via the Versions menu
3. **Test Before Deploying**: Execute workflows in staging first
4. **Document Changes**: Add notes when saving updates

---

## Advanced Features

### Auto-Layout

Automatically arrange nodes with `dagre` graph layout:

1. Click **"+ Add Node"** → **"Auto Layout"**
2. Nodes reorganize into a readable hierarchy

### Node Configuration

Store agent-specific parameters in the `config` field:

```json
{
  "node_id": "analyzer",
  "type": "agent",
  "config": {
    "analysis_depth": "thorough",
    "include_citations": true,
    "max_length": 2000,
    "temperature": 0.7
  }
}
```

Agents receive these values during execution.

### Execution Metadata

Attach custom metadata to executions for tracking:

```bash
POST /api/workflows/{workflow_id}/execute
{
  "input_data": {...},
  "metadata": {
    "request_id": "REQ-2026-001",
    "priority": "high",
    "tags": ["claims", "urgent"]
  }
}
```

Metadata appears in execution logs.

---

## Troubleshooting

### Cannot Save Workflow

**Error:** "User must be associated with an organization"
- Solution: Ensure your account has an org_id set. Contact your admin.

**Error:** "Workflow not found"
- Solution: The workflow may have been deleted. Create a new one.

### Execution Fails

**Status: FAILED**
1. Check Execution Panel → Events for error details
2. Verify agent_ids are correct
3. Review agent logs in the Agents dashboard
4. Check input data format matches agent expectations

### Missing Events

**Only partial events visible:**
- Increase stream polling (check browser performance)
- Simplify workflow (too many nodes may overwhelm streaming)
- Check network connection stability

### Auto-Save Not Working

**Workflow changes not persisting:**
1. Verify you have WRITE permissions on the workflow
2. Check browser console for HTTP errors
3. Ensure network connection is stable
4. Try manual save with "Save" button

---

## FAQ

**Q: Can I use the same agent multiple times?**
A: Yes. You can add multiple agent nodes with the same agent_id. Each runs independently.

**Q: What's the maximum workflow size?**
A: No hard limit, but workflows with >50 nodes may have performance impact. Consider breaking into sub-workflows.

**Q: How long does execution take?**
A: Depends on agent processing time and workflow structure. Sequential workflows are slower than parallel. Typical range: 10 seconds to 10 minutes.

**Q: Can I share workflows with teammates?**
A: Yes. Workflows are org-scoped. Share the workflow_id with teammates who can then load it.

**Q: What if an agent fails mid-workflow?**
A: The entire execution fails and stops. Design error-handling branches using condition nodes.

**Q: Can I export workflows?**
A: Yes. Copy the JSON definition from the API response and store/version control it.

---

## Additional Resources

- [Agent Registry](./CLAUDE.md) — Available agents and capabilities
- [API Documentation](./API.md) — Complete endpoint reference
- [Agent Development](./AGENTS.md) — Building custom agents
- [MCP Tools](./MCP.md) — Tool integration guide

---

## Support

For issues or feature requests:
- File a ticket in the project tracker
- Contact your platform admin
- Review logs at `/logs/workflows`

Last updated: 2026-07-27
