/**
 * Visual workflow builder component using React Flow.
 *
 * Provides a drag-and-drop canvas for composing agent workflows,
 * with node configuration, edge routing, and execution monitoring.
 */

import React, { useCallback, useState, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Connection,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
  useReactFlow,
  MiniMap,
  Controls,
  Background,
  BackgroundVariant,
} from 'reactflow';
import { useWorkflowBuilder, WorkflowNode, HandoffCondition } from '../hooks/useWorkflowBuilder';
import 'reactflow/dist/style.css';
import '../styles/WorkflowBuilder.css';

interface WorkflowBuilderProps {
  workflowId?: string;
  onSave?: (workflowId: string) => void;
  onExecute?: () => void;
  readOnly?: boolean;
}

interface SelectedNodeData {
  nodeId: string | null;
  agentId?: string;
  config?: Record<string, unknown>;
  handoffConditions?: HandoffCondition[];
}

/**
 * Main workflow builder component.
 */
export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  workflowId,
  onSave,
  onExecute,
  readOnly = false,
}) => {
  // Hook setup
  const {
    nodes: hookNodes,
    edges: hookEdges,
    selectedNodeId,
    execution,
    isDirty,
    isSaving,
    isLoading,
    error,
    addNode,
    removeNode,
    updateNode,
    selectNode,
    addEdge: hookAddEdge,
    removeEdge,
    updateEdge,
    setHandoffCondition,
    removeHandoffCondition,
    saveWorkflow,
    executeWorkflow,
    cancelExecution,
  } = useWorkflowBuilder({ workflowId, onSaveSuccess: onSave });

  // Local state for React Flow
  const [rfNodes, setRfNodes, onNodesChange] = useNodesState(
    hookNodes.map((n) => ({
      ...n,
      selected: n.id === selectedNodeId,
    }))
  );

  const [rfEdges, setRfEdges, onEdgesChange] = useEdgesState(hookEdges);
  const { getNode, setCenter } = useReactFlow();

  // UI state
  const [workflowName, setWorkflowName] = useState('My Workflow');
  const [showNodePanel, setShowNodePanel] = useState(false);
  const [selectedNodeData, setSelectedNodeData] = useState<SelectedNodeData>({ nodeId: null });
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [showExecutionPanel, setShowExecutionPanel] = useState(false);

  // =========================================================================
  // Sync hooks with React Flow
  // =========================================================================

  React.useEffect(() => {
    setRfNodes(
      hookNodes.map((n) => ({
        ...n,
        selected: n.id === selectedNodeId,
      }))
    );
  }, [hookNodes, selectedNodeId, setRfNodes]);

  React.useEffect(() => {
    setRfEdges(hookEdges);
  }, [hookEdges, setRfEdges]);

  // =========================================================================
  // Event Handlers
  // =========================================================================

  const onConnect = useCallback(
    (connection: Connection) => {
      if (connection.source && connection.target) {
        hookAddEdge(connection.source, connection.target);
      }
    },
    [hookAddEdge]
  );

  const onNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      selectNode(node.id);
      const workflowNode = hookNodes.find((n) => n.id === node.id);
      if (workflowNode) {
        setSelectedNodeData({
          nodeId: node.id,
          agentId: workflowNode.data.agentId,
          config: workflowNode.data.config,
          handoffConditions: workflowNode.data.handoffConditions,
        });
        setShowNodePanel(true);
      }
    },
    [selectNode, hookNodes]
  );

  const onNodesDelete = useCallback(
    (nodesToDelete: Node[]) => {
      nodesToDelete.forEach((node) => removeNode(node.id));
    },
    [removeNode]
  );

  const onEdgesDelete = useCallback(
    (edgesToDelete: Edge[]) => {
      edgesToDelete.forEach((edge) => removeEdge(edge.id));
    },
    [removeEdge]
  );

  const handleAddAgentNode = useCallback(() => {
    addNode('agent', { x: 250, y: 100 });
    setIsMenuOpen(false);
  }, [addNode]);

  const handleAddConditionNode = useCallback(() => {
    addNode('condition', { x: 250, y: 100 });
    setIsMenuOpen(false);
  }, [addNode]);

  const handleAddStartNode = useCallback(() => {
    addNode('start', { x: 100, y: 50 });
    setIsMenuOpen(false);
  }, [addNode]);

  const handleAutoLayout = useCallback(() => {
    // Simplified auto-layout (dagre-based layout)
    // In production, use @dagrejs/dagre or react-flow-dagre
    const layoutedNodes = rfNodes.map((node, index) => ({
      ...node,
      position: {
        x: (index % 3) * 300,
        y: Math.floor(index / 3) * 200,
      },
    }));
    setRfNodes(layoutedNodes);
  }, [rfNodes, setRfNodes]);

  const handleSave = useCallback(async () => {
    try {
      const id = await saveWorkflow(workflowName);
      // Success handled by onSaveSuccess callback
    } catch (err) {
      console.error('Save failed:', err);
    }
  }, [saveWorkflow, workflowName]);

  const handleExecute = useCallback(async () => {
    try {
      await executeWorkflow({ nodes: hookNodes, edges: hookEdges });
      setShowExecutionPanel(true);
      onExecute?.();
    } catch (err) {
      console.error('Execution failed:', err);
    }
  }, [executeWorkflow, hookNodes, hookEdges, onExecute]);

  const handleAgentIdChange = useCallback(
    (agentId: string) => {
      if (selectedNodeData.nodeId) {
        updateNode(selectedNodeData.nodeId, {
          data: {
            ...rfNodes.find((n) => n.id === selectedNodeData.nodeId)?.data,
            agentId,
          } as any,
        });
        setSelectedNodeData((prev) => ({ ...prev, agentId }));
      }
    },
    [selectedNodeData.nodeId, rfNodes, updateNode]
  );

  const handleAddHandoffCondition = useCallback(
    (condition: HandoffCondition) => {
      if (selectedNodeData.nodeId) {
        setHandoffCondition(selectedNodeData.nodeId, condition);
        setSelectedNodeData((prev) => ({
          ...prev,
          handoffConditions: [...(prev.handoffConditions || []), condition],
        }));
      }
    },
    [selectedNodeData.nodeId, setHandoffCondition]
  );

  const handleRemoveHandoffCondition = useCallback(
    (conditionId: string) => {
      if (selectedNodeData.nodeId) {
        removeHandoffCondition(selectedNodeData.nodeId, conditionId);
        setSelectedNodeData((prev) => ({
          ...prev,
          handoffConditions: prev.handoffConditions?.filter((c) => c.id !== conditionId),
        }));
      }
    },
    [selectedNodeData.nodeId, removeHandoffCondition]
  );

  // =========================================================================
  // Render
  // =========================================================================

  const isDarkMode = useMemo(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }, []);

  return (
    <div className={`workflow-builder ${isDarkMode ? 'dark' : 'light'}`}>
      {/* Error Display */}
      {error && (
        <div className="workflow-error-toast">
          <span>{error}</span>
          <button onClick={() => {}} className="close-btn">
            ×
          </button>
        </div>
      )}

      {/* Main Canvas */}
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onNodesDelete={onNodesDelete}
        onEdgesDelete={onEdgesDelete}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Controls />
        <MiniMap />

        {/* Top Toolbar */}
        <Panel position="top-left" className="workflow-toolbar">
          <div className="toolbar-section">
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              placeholder="Workflow name"
              className="workflow-name-input"
              disabled={readOnly}
            />
            {isDirty && <span className="dirty-indicator">*</span>}
          </div>

          <div className="toolbar-buttons">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="btn btn-add"
              title="Add node"
              disabled={readOnly}
            >
              + Add Node
            </button>

            {isMenuOpen && (
              <div className="dropdown-menu">
                <button onClick={handleAddStartNode}>Start</button>
                <button onClick={handleAddAgentNode}>Agent</button>
                <button onClick={handleAddConditionNode}>Condition</button>
                <button onClick={handleAutoLayout}>Auto Layout</button>
              </div>
            )}

            <button
              onClick={handleSave}
              className="btn btn-primary"
              title="Save workflow"
              disabled={readOnly || isSaving}
            >
              {isSaving ? 'Saving...' : 'Save'}
            </button>

            <button
              onClick={handleExecute}
              className="btn btn-execute"
              title="Execute workflow"
              disabled={readOnly || !hookNodes.length}
            >
              Execute
            </button>
          </div>
        </Panel>

        {/* Right Panel - Node Inspector */}
        {showNodePanel && selectedNodeData.nodeId && (
          <Panel position="top-right" className="workflow-inspector-panel">
            <div className="inspector-header">
              <h3>Node Configuration</h3>
              <button
                onClick={() => setShowNodePanel(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>

            <div className="inspector-content">
              <div className="form-group">
                <label>Node ID</label>
                <input
                  type="text"
                  value={selectedNodeData.nodeId}
                  disabled
                  className="input-disabled"
                />
              </div>

              <div className="form-group">
                <label>Agent ID</label>
                <input
                  type="text"
                  value={selectedNodeData.agentId || ''}
                  onChange={(e) => handleAgentIdChange(e.target.value)}
                  placeholder="Select agent"
                  disabled={readOnly}
                />
              </div>

              {/* Handoff Conditions */}
              <div className="form-group">
                <label>Handoff Conditions</label>
                <div className="handoff-list">
                  {selectedNodeData.handoffConditions?.map((condition) => (
                    <div key={condition.id} className="handoff-item">
                      <div className="handoff-label">
                        {condition.label} → {condition.targetNodeId}
                      </div>
                      {!readOnly && (
                        <button
                          onClick={() => handleRemoveHandoffCondition(condition.id)}
                          className="remove-btn"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                {!readOnly && (
                  <button
                    onClick={() => {
                      const newCondition: HandoffCondition = {
                        id: `condition-${Date.now()}`,
                        label: 'New condition',
                        targetNodeId: 'target-node',
                      };
                      handleAddHandoffCondition(newCondition);
                    }}
                    className="btn btn-small"
                  >
                    + Add Condition
                  </button>
                )}
              </div>

              {/* Node Actions */}
              {!readOnly && (
                <div className="inspector-actions">
                  <button
                    onClick={() => {
                      removeNode(selectedNodeData.nodeId!);
                      setShowNodePanel(false);
                    }}
                    className="btn btn-danger"
                  >
                    Delete Node
                  </button>
                </div>
              )}
            </div>
          </Panel>
        )}

        {/* Execution Panel */}
        {showExecutionPanel && execution.status !== 'idle' && (
          <Panel position="bottom-left" className="workflow-execution-panel">
            <div className="execution-header">
              <h3>Execution Status</h3>
              <button
                onClick={() => setShowExecutionPanel(false)}
                className="close-btn"
              >
                ×
              </button>
            </div>

            <div className="execution-content">
              <div className="status-badge" data-status={execution.status}>
                {execution.status.toUpperCase()}
              </div>

              {execution.events.length > 0 && (
                <div className="events-log">
                  <h4>Events</h4>
                  <div className="events-list">
                    {execution.events.slice(-5).map((event) => (
                      <div
                        key={event.id}
                        className={`event-item event-${event.type}`}
                      >
                        <div className="event-type">{event.type}</div>
                        <div className="event-node">Node: {event.nodeId}</div>
                        {event.error && (
                          <div className="event-error">{event.error.message}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {execution.status === 'running' && (
                <button
                  onClick={cancelExecution}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              )}

              {execution.output && (
                <div className="execution-output">
                  <h4>Output</h4>
                  <pre>{JSON.stringify(execution.output, null, 2)}</pre>
                </div>
              )}
            </div>
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
};

export default WorkflowBuilder;
