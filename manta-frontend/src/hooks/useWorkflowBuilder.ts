/**
 * React hook for workflow builder state management.
 *
 * Provides state management for workflow nodes, edges, and execution,
 * with auto-save and real-time execution tracking.
 */

import { useCallback, useState, useRef, useEffect } from 'react';
import { Node, Edge } from 'reactflow';
import axios, { AxiosError } from 'axios';

/**
 * Handoff condition for routing between nodes.
 */
export interface HandoffCondition {
  id: string;
  label: string;
  targetNodeId: string;
  condition?: Record<string, unknown>;
  isDefault?: boolean;
}

/**
 * Workflow node with configuration and handoff logic.
 */
export interface WorkflowNode extends Node {
  data: {
    label: string;
    agentId?: string;
    type: 'agent' | 'condition' | 'merger' | 'start' | 'end';
    config?: Record<string, unknown>;
    handoffConditions?: HandoffCondition[];
  };
}

/**
 * Workflow definition structure.
 */
export interface WorkflowDefinition {
  nodes: Array<{
    id: string;
    type: string;
    agent_id?: string;
    label: string;
    position: { x: number; y: number };
    config?: Record<string, unknown>;
    handoff_conditions?: HandoffCondition[];
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    label?: string;
    condition?: Record<string, unknown>;
    data?: Record<string, unknown>;
  }>;
  metadata?: Record<string, unknown>;
}

/**
 * Execution status and event tracking.
 */
export interface ExecutionState {
  id?: string;
  status: 'idle' | 'pending' | 'running' | 'completed' | 'failed';
  events: Array<{
    id: string;
    nodeId: string;
    type: string;
    timestamp: string;
    data?: Record<string, unknown>;
    error?: Record<string, unknown>;
  }>;
  output?: Record<string, unknown>;
  error?: string;
}

/**
 * Hook options for configuration.
 */
interface UseWorkflowBuilderOptions {
  workflowId?: string;
  autoSave?: boolean;
  autoSaveDelay?: number;
  onSaveSuccess?: (workflowId: string) => void;
  onExecutionComplete?: (output: Record<string, unknown>) => void;
  apiBaseUrl?: string;
}

/**
 * Hook return type.
 */
interface UseWorkflowBuilderReturn {
  // State
  nodes: WorkflowNode[];
  edges: Edge[];
  selectedNodeId: string | null;
  execution: ExecutionState;
  isDirty: boolean;
  isSaving: boolean;
  isLoading: boolean;
  error: string | null;

  // Node operations
  addNode: (type: 'agent' | 'condition' | 'merger' | 'start' | 'end', position?: { x: number; y: number }) => void;
  removeNode: (nodeId: string) => void;
  updateNode: (nodeId: string, updates: Partial<WorkflowNode>) => void;
  selectNode: (nodeId: string | null) => void;

  // Edge operations
  addEdge: (source: string, target: string, label?: string) => void;
  removeEdge: (edgeId: string) => void;
  updateEdge: (edgeId: string, updates: Partial<Edge>) => void;

  // Handoff conditions
  setHandoffCondition: (nodeId: string, condition: HandoffCondition) => void;
  removeHandoffCondition: (nodeId: string, conditionId: string) => void;

  // Workflow management
  saveWorkflow: (name: string, description?: string) => Promise<string>;
  loadWorkflow: (workflowId: string) => Promise<void>;
  newWorkflow: () => void;

  // Execution
  executeWorkflow: (inputData?: Record<string, unknown>) => Promise<void>;
  cancelExecution: () => void;
  streamExecutionEvents: (executionId: string) => void;

  // Auto-save
  markDirty: () => void;
  clearDirty: () => void;
}

const DEFAULT_AUTO_SAVE_DELAY = 3000; // 3 seconds
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Main hook for workflow builder state management.
 */
export function useWorkflowBuilder(
  options: UseWorkflowBuilderOptions = {}
): UseWorkflowBuilderReturn {
  const {
    workflowId,
    autoSave = true,
    autoSaveDelay = DEFAULT_AUTO_SAVE_DELAY,
    onSaveSuccess,
    onExecutionComplete,
    apiBaseUrl = API_BASE_URL,
  } = options;

  // State
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [execution, setExecution] = useState<ExecutionState>({ status: 'idle', events: [] });
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs
  const autoSaveTimerRef = useRef<NodeJS.Timeout | null>(null);
  const executionEventSourceRef = useRef<EventSource | null>(null);
  const currentWorkflowIdRef = useRef<string | undefined>(workflowId);

  // =========================================================================
  // Node Operations
  // =========================================================================

  const addNode = useCallback(
    (type: 'agent' | 'condition' | 'merger' | 'start' | 'end', position = { x: 100, y: 100 }) => {
      const nodeId = `node-${Date.now()}`;
      const newNode: WorkflowNode = {
        id: nodeId,
        data: { label: `${type.charAt(0).toUpperCase() + type.slice(1)} Node`, type },
        position,
        type: 'default',
      };
      setNodes((prev) => [...prev, newNode]);
      markDirty();
    },
    []
  );

  const removeNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
    setEdges((prev) =>
      prev.filter((e) => e.source !== nodeId && e.target !== nodeId)
    );
    if (selectedNodeId === nodeId) {
      setSelectedNodeId(null);
    }
    markDirty();
  }, [selectedNodeId]);

  const updateNode = useCallback((nodeId: string, updates: Partial<WorkflowNode>) => {
    setNodes((prev) =>
      prev.map((n) => (n.id === nodeId ? { ...n, ...updates } : n))
    );
    markDirty();
  }, []);

  const selectNode = useCallback((nodeId: string | null) => {
    setSelectedNodeId(nodeId);
  }, []);

  // =========================================================================
  // Edge Operations
  // =========================================================================

  const addEdge = useCallback((source: string, target: string, label?: string) => {
    const edgeId = `edge-${source}-${target}-${Date.now()}`;
    const newEdge: Edge = {
      id: edgeId,
      source,
      target,
      label,
      animated: true,
    };
    setEdges((prev) => [...prev, newEdge]);
    markDirty();
  }, []);

  const removeEdge = useCallback((edgeId: string) => {
    setEdges((prev) => prev.filter((e) => e.id !== edgeId));
    markDirty();
  }, []);

  const updateEdge = useCallback((edgeId: string, updates: Partial<Edge>) => {
    setEdges((prev) =>
      prev.map((e) => (e.id === edgeId ? { ...e, ...updates } : e))
    );
    markDirty();
  }, []);

  // =========================================================================
  // Handoff Conditions
  // =========================================================================

  const setHandoffCondition = useCallback((nodeId: string, condition: HandoffCondition) => {
    updateNode(nodeId, {
      data: {
        ...nodes.find((n) => n.id === nodeId)?.data,
        handoffConditions: [
          ...(nodes.find((n) => n.id === nodeId)?.data?.handoffConditions || []),
          condition,
        ],
      } as any,
    });
  }, [nodes, updateNode]);

  const removeHandoffCondition = useCallback(
    (nodeId: string, conditionId: string) => {
      const node = nodes.find((n) => n.id === nodeId);
      if (!node?.data?.handoffConditions) return;

      updateNode(nodeId, {
        data: {
          ...node.data,
          handoffConditions: node.data.handoffConditions.filter(
            (c) => c.id !== conditionId
          ),
        } as any,
      });
    },
    [nodes, updateNode]
  );

  // =========================================================================
  // Workflow Management
  // =========================================================================

  const buildDefinition = useCallback((): WorkflowDefinition => {
    return {
      nodes: nodes.map((n) => ({
        id: n.id,
        type: n.data.type,
        agent_id: n.data.agentId,
        label: n.data.label,
        position: n.position,
        config: n.data.config,
        handoff_conditions: n.data.handoffConditions,
      })),
      edges: edges.map((e) => ({
        id: e.id,
        source: e.source,
        target: e.target,
        label: e.label,
        condition: (e.data as any)?.condition,
        data: e.data,
      })),
      metadata: {},
    };
  }, [nodes, edges]);

  const saveWorkflow = useCallback(
    async (name: string, description?: string): Promise<string> => {
      setIsSaving(true);
      setError(null);

      try {
        const definition = buildDefinition();
        const payload = { name, description, definition };

        let response;
        if (currentWorkflowIdRef.current) {
          // Update existing
          response = await axios.put(
            `${apiBaseUrl}/workflows/${currentWorkflowIdRef.current}`,
            payload
          );
        } else {
          // Create new
          response = await axios.post(`${apiBaseUrl}/workflows`, payload);
        }

        const workflowId = response.data.id;
        currentWorkflowIdRef.current = workflowId;
        setIsDirty(false);

        onSaveSuccess?.(workflowId);
        return workflowId;
      } catch (err) {
        const message = err instanceof AxiosError ? err.response?.data?.detail : String(err);
        setError(message as string);
        throw err;
      } finally {
        setIsSaving(false);
      }
    },
    [buildDefinition, apiBaseUrl, onSaveSuccess]
  );

  const loadWorkflow = useCallback(
    async (id: string): Promise<void> => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.get(`${apiBaseUrl}/workflows/${id}`);
        const { definition } = response.data;

        setNodes(
          definition.nodes.map((n: any) => ({
            id: n.id,
            data: {
              label: n.label,
              type: n.type,
              agentId: n.agent_id,
              config: n.config,
              handoffConditions: n.handoff_conditions,
            },
            position: n.position,
            type: 'default',
          }))
        );

        setEdges(
          definition.edges.map((e: any) => ({
            id: e.id,
            source: e.source,
            target: e.target,
            label: e.label,
            animated: true,
            data: { condition: e.condition },
          }))
        );

        currentWorkflowIdRef.current = id;
        setIsDirty(false);
      } catch (err) {
        const message = err instanceof AxiosError ? err.response?.data?.detail : String(err);
        setError(message as string);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [apiBaseUrl]
  );

  const newWorkflow = useCallback(() => {
    setNodes([]);
    setEdges([]);
    setSelectedNodeId(null);
    setExecution({ status: 'idle', events: [] });
    currentWorkflowIdRef.current = undefined;
    setIsDirty(false);
    setError(null);
  }, []);

  // =========================================================================
  // Execution
  // =========================================================================

  const executeWorkflow = useCallback(
    async (inputData?: Record<string, unknown>) => {
      if (!currentWorkflowIdRef.current) {
        setError('Workflow must be saved before execution');
        return;
      }

      setExecution((prev) => ({ ...prev, status: 'pending' }));

      try {
        const response = await axios.post(
          `${apiBaseUrl}/workflows/${currentWorkflowIdRef.current}/execute`,
          { input_data: inputData || {} }
        );

        const executionId = response.data.id;
        setExecution((prev) => ({ ...prev, id: executionId, status: 'running' }));

        streamExecutionEvents(executionId);
      } catch (err) {
        const message = err instanceof AxiosError ? err.response?.data?.detail : String(err);
        setError(message as string);
        setExecution((prev) => ({ ...prev, status: 'failed', error: message as string }));
      }
    },
    [apiBaseUrl]
  );

  const cancelExecution = useCallback(() => {
    if (executionEventSourceRef.current) {
      executionEventSourceRef.current.close();
      executionEventSourceRef.current = null;
    }
    setExecution((prev) => ({ ...prev, status: 'idle' }));
  }, []);

  const streamExecutionEvents = useCallback(
    (executionId: string) => {
      // Close previous stream if exists
      if (executionEventSourceRef.current) {
        executionEventSourceRef.current.close();
      }

      const eventSource = new EventSource(
        `${apiBaseUrl}/workflows/executions/${executionId}/stream`
      );

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'status_update') {
            setExecution((prev) => ({ ...prev, status: data.status }));
          } else if (data.type === 'execution_complete') {
            setExecution((prev) => ({
              ...prev,
              status: data.status,
              output: data.output,
              error: data.error,
            }));
            onExecutionComplete?.(data.output);
            eventSource.close();
          } else {
            // Regular event (node execution)
            setExecution((prev) => ({
              ...prev,
              events: [
                ...prev.events,
                {
                  id: data.id,
                  nodeId: data.node_id,
                  type: data.event_type,
                  timestamp: data.timestamp,
                  data: data.data,
                  error: data.error,
                },
              ],
            }));
          }
        } catch (err) {
          console.error('Failed to parse event:', err);
        }
      };

      eventSource.onerror = () => {
        setError('Stream connection lost');
        setExecution((prev) => ({ ...prev, status: 'failed' }));
        eventSource.close();
      };

      executionEventSourceRef.current = eventSource;
    },
    [apiBaseUrl, onExecutionComplete]
  );

  // =========================================================================
  // Auto-save
  // =========================================================================

  const markDirty = useCallback(() => {
    setIsDirty(true);
  }, []);

  const clearDirty = useCallback(() => {
    setIsDirty(false);
  }, []);

  // Auto-save effect
  useEffect(() => {
    if (!autoSave || !isDirty || !currentWorkflowIdRef.current) {
      return;
    }

    if (autoSaveTimerRef.current) {
      clearTimeout(autoSaveTimerRef.current);
    }

    autoSaveTimerRef.current = setTimeout(() => {
      saveWorkflow('Auto-saved workflow').catch((err) => {
        console.error('Auto-save failed:', err);
      });
    }, autoSaveDelay);

    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
    };
  }, [isDirty, autoSave, autoSaveDelay, saveWorkflow]);

  // Load initial workflow if ID provided
  useEffect(() => {
    if (workflowId && !nodes.length) {
      loadWorkflow(workflowId).catch((err) => {
        console.error('Failed to load workflow:', err);
      });
    }
  }, [workflowId, loadWorkflow, nodes.length]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (autoSaveTimerRef.current) {
        clearTimeout(autoSaveTimerRef.current);
      }
      if (executionEventSourceRef.current) {
        executionEventSourceRef.current.close();
      }
    };
  }, []);

  return {
    // State
    nodes,
    edges,
    selectedNodeId,
    execution,
    isDirty,
    isSaving,
    isLoading,
    error,

    // Node operations
    addNode,
    removeNode,
    updateNode,
    selectNode,

    // Edge operations
    addEdge,
    removeEdge,
    updateEdge,

    // Handoff conditions
    setHandoffCondition,
    removeHandoffCondition,

    // Workflow management
    saveWorkflow,
    loadWorkflow,
    newWorkflow,

    // Execution
    executeWorkflow,
    cancelExecution,
    streamExecutionEvents,

    // Auto-save
    markDirty,
    clearDirty,
  };
}
