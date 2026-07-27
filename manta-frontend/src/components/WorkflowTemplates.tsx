/**
 * Workflow templates gallery component.
 *
 * Provides pre-built workflow templates for common patterns:
 * sequential, parallel, branching, and feedback loops.
 */

import React, { useState, useCallback } from 'react';
import { WorkflowDefinition } from '../hooks/useWorkflowBuilder';
import '../styles/WorkflowTemplates.css';

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'sequential' | 'parallel' | 'branching' | 'feedback' | 'research' | 'analysis' | 'decision';
  useCase: string;
  thumbnail?: string;
  definition: WorkflowDefinition;
}

interface WorkflowTemplatesProps {
  onTemplateSelect: (definition: WorkflowDefinition) => void;
  onClose?: () => void;
}

/**
 * Pre-built workflow templates.
 */
const TEMPLATES: WorkflowTemplate[] = [
  {
    id: 'sequential-analysis',
    name: 'Sequential Analysis',
    description: 'Process data through multiple analysis steps in sequence',
    category: 'sequential',
    useCase: 'Data analysis pipeline',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 50 },
        },
        {
          id: 'extract',
          type: 'agent',
          agent_id: 'extractor',
          label: 'Data Extractor',
          position: { x: 250, y: 50 },
          config: { timeout: 300 },
        },
        {
          id: 'transform',
          type: 'agent',
          agent_id: 'transformer',
          label: 'Data Transformer',
          position: { x: 450, y: 50 },
          config: { timeout: 300 },
        },
        {
          id: 'analyze',
          type: 'agent',
          agent_id: 'analyzer',
          label: 'Data Analyzer',
          position: { x: 650, y: 50 },
          config: { timeout: 500 },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 850, y: 50 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'extract' },
        { id: 'e2', source: 'extract', target: 'transform' },
        { id: 'e3', source: 'transform', target: 'analyze' },
        { id: 'e4', source: 'analyze', target: 'end' },
      ],
      metadata: { category: 'sequential', complexity: 'low' },
    },
  },

  {
    id: 'parallel-research',
    name: 'Parallel Research',
    description: 'Research multiple topics in parallel, then synthesize results',
    category: 'parallel',
    useCase: 'Multi-topic research and synthesis',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 150 },
        },
        {
          id: 'research-1',
          type: 'agent',
          agent_id: 'researcher',
          label: 'Research Topic A',
          position: { x: 250, y: 50 },
          config: { research_depth: 'deep' },
        },
        {
          id: 'research-2',
          type: 'agent',
          agent_id: 'researcher',
          label: 'Research Topic B',
          position: { x: 250, y: 150 },
          config: { research_depth: 'deep' },
        },
        {
          id: 'research-3',
          type: 'agent',
          agent_id: 'researcher',
          label: 'Research Topic C',
          position: { x: 250, y: 250 },
          config: { research_depth: 'deep' },
        },
        {
          id: 'merger',
          type: 'merger',
          label: 'Merge Results',
          position: { x: 450, y: 150 },
        },
        {
          id: 'synthesize',
          type: 'agent',
          agent_id: 'synthesizer',
          label: 'Synthesize Findings',
          position: { x: 650, y: 150 },
          config: { style: 'comprehensive' },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 850, y: 150 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'research-1' },
        { id: 'e2', source: 'start', target: 'research-2' },
        { id: 'e3', source: 'start', target: 'research-3' },
        { id: 'e4', source: 'research-1', target: 'merger' },
        { id: 'e5', source: 'research-2', target: 'merger' },
        { id: 'e6', source: 'research-3', target: 'merger' },
        { id: 'e7', source: 'merger', target: 'synthesize' },
        { id: 'e8', source: 'synthesize', target: 'end' },
      ],
      metadata: { category: 'parallel', complexity: 'medium' },
    },
  },

  {
    id: 'decision-tree',
    name: 'Decision Tree',
    description: 'Route to different agents based on data classification',
    category: 'branching',
    useCase: 'Conditional logic and routing',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 150 },
        },
        {
          id: 'classify',
          type: 'agent',
          agent_id: 'classifier',
          label: 'Classify Input',
          position: { x: 250, y: 150 },
          config: { num_classes: 3 },
          handoff_conditions: [
            {
              id: 'cond-1',
              label: 'Type A',
              targetNodeId: 'process-a',
              condition: { type: 'equals', value: 'A' },
            },
            {
              id: 'cond-2',
              label: 'Type B',
              targetNodeId: 'process-b',
              condition: { type: 'equals', value: 'B' },
            },
            {
              id: 'cond-3',
              label: 'Type C',
              targetNodeId: 'process-c',
              condition: { type: 'equals', value: 'C' },
              isDefault: true,
            },
          ],
        },
        {
          id: 'process-a',
          type: 'agent',
          agent_id: 'processor-a',
          label: 'Process Type A',
          position: { x: 450, y: 50 },
        },
        {
          id: 'process-b',
          type: 'agent',
          agent_id: 'processor-b',
          label: 'Process Type B',
          position: { x: 450, y: 150 },
        },
        {
          id: 'process-c',
          type: 'agent',
          agent_id: 'processor-c',
          label: 'Process Type C',
          position: { x: 450, y: 250 },
        },
        {
          id: 'merger',
          type: 'merger',
          label: 'Consolidate',
          position: { x: 650, y: 150 },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 850, y: 150 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'classify' },
        { id: 'e2', source: 'classify', target: 'process-a', label: 'Type A' },
        { id: 'e3', source: 'classify', target: 'process-b', label: 'Type B' },
        { id: 'e4', source: 'classify', target: 'process-c', label: 'Type C' },
        { id: 'e5', source: 'process-a', target: 'merger' },
        { id: 'e6', source: 'process-b', target: 'merger' },
        { id: 'e7', source: 'process-c', target: 'merger' },
        { id: 'e8', source: 'merger', target: 'end' },
      ],
      metadata: { category: 'branching', complexity: 'medium' },
    },
  },

  {
    id: 'feedback-loop',
    name: 'Feedback Loop',
    description: 'Iterative refinement with quality checks and loops',
    category: 'feedback',
    useCase: 'Iterative improvement and refinement',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 150 },
        },
        {
          id: 'generate',
          type: 'agent',
          agent_id: 'generator',
          label: 'Generate Content',
          position: { x: 250, y: 150 },
          config: { style: 'creative' },
        },
        {
          id: 'evaluate',
          type: 'agent',
          agent_id: 'evaluator',
          label: 'Evaluate Quality',
          position: { x: 450, y: 150 },
          config: { criteria: ['clarity', 'accuracy', 'completeness'] },
          handoff_conditions: [
            {
              id: 'cond-pass',
              label: 'Quality OK',
              targetNodeId: 'end',
              condition: { quality_score: { min: 0.8 } },
              isDefault: false,
            },
            {
              id: 'cond-refine',
              label: 'Needs Refinement',
              targetNodeId: 'refine',
              condition: { quality_score: { max: 0.8 } },
              isDefault: true,
            },
          ],
        },
        {
          id: 'refine',
          type: 'agent',
          agent_id: 'refiner',
          label: 'Refine Content',
          position: { x: 450, y: 300 },
          config: { iterations: 3 },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 650, y: 150 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'generate' },
        { id: 'e2', source: 'generate', target: 'evaluate' },
        { id: 'e3', source: 'evaluate', target: 'end', label: 'Quality OK' },
        { id: 'e4', source: 'evaluate', target: 'refine', label: 'Needs Refinement' },
        { id: 'e5', source: 'refine', target: 'evaluate' },
      ],
      metadata: { category: 'feedback', complexity: 'high' },
    },
  },

  {
    id: 'claim-analysis',
    name: 'Claim Analysis',
    description: 'Specialized workflow for insurance claims assessment',
    category: 'analysis',
    useCase: 'Claims processing and evaluation',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 150 },
        },
        {
          id: 'intake',
          type: 'agent',
          agent_id: 'claims-intake',
          label: 'Claims Intake',
          position: { x: 250, y: 150 },
          config: { extract_fields: true },
        },
        {
          id: 'validate',
          type: 'agent',
          agent_id: 'validator',
          label: 'Validate Claim',
          position: { x: 450, y: 150 },
          config: { check_coverage: true, check_limits: true },
        },
        {
          id: 'assess',
          type: 'agent',
          agent_id: 'assessor',
          label: 'Assess Damages',
          position: { x: 650, y: 150 },
          config: { method: 'expert_system' },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 850, y: 150 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'intake' },
        { id: 'e2', source: 'intake', target: 'validate' },
        { id: 'e3', source: 'validate', target: 'assess' },
        { id: 'e4', source: 'assess', target: 'end' },
      ],
      metadata: { category: 'analysis', domain: 'insurance', complexity: 'medium' },
    },
  },

  {
    id: 'decision-support',
    name: 'Decision Support System',
    description: 'Multi-perspective analysis for complex decisions',
    category: 'decision',
    useCase: 'Strategic decision making',
    definition: {
      nodes: [
        {
          id: 'start',
          type: 'start',
          label: 'Start',
          position: { x: 50, y: 200 },
        },
        {
          id: 'frame',
          type: 'agent',
          agent_id: 'problem-framer',
          label: 'Frame Problem',
          position: { x: 250, y: 200 },
        },
        {
          id: 'analyze-financial',
          type: 'agent',
          agent_id: 'financial-analyst',
          label: 'Financial Analysis',
          position: { x: 450, y: 50 },
        },
        {
          id: 'analyze-risks',
          type: 'agent',
          agent_id: 'risk-analyst',
          label: 'Risk Analysis',
          position: { x: 450, y: 150 },
        },
        {
          id: 'analyze-impact',
          type: 'agent',
          agent_id: 'impact-analyst',
          label: 'Impact Analysis',
          position: { x: 450, y: 250 },
        },
        {
          id: 'synthesize',
          type: 'agent',
          agent_id: 'decision-synthesizer',
          label: 'Synthesize Options',
          position: { x: 650, y: 150 },
        },
        {
          id: 'recommend',
          type: 'agent',
          agent_id: 'recommender',
          label: 'Generate Recommendations',
          position: { x: 850, y: 150 },
        },
        {
          id: 'end',
          type: 'end',
          label: 'End',
          position: { x: 1050, y: 150 },
        },
      ],
      edges: [
        { id: 'e1', source: 'start', target: 'frame' },
        { id: 'e2', source: 'frame', target: 'analyze-financial' },
        { id: 'e3', source: 'frame', target: 'analyze-risks' },
        { id: 'e4', source: 'frame', target: 'analyze-impact' },
        { id: 'e5', source: 'analyze-financial', target: 'synthesize' },
        { id: 'e6', source: 'analyze-risks', target: 'synthesize' },
        { id: 'e7', source: 'analyze-impact', target: 'synthesize' },
        { id: 'e8', source: 'synthesize', target: 'recommend' },
        { id: 'e9', source: 'recommend', target: 'end' },
      ],
      metadata: { category: 'decision', complexity: 'high' },
    },
  },
];

/**
 * Workflow templates gallery component.
 */
export const WorkflowTemplates: React.FC<WorkflowTemplatesProps> = ({
  onTemplateSelect,
  onClose,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    { value: 'sequential', label: 'Sequential' },
    { value: 'parallel', label: 'Parallel' },
    { value: 'branching', label: 'Branching' },
    { value: 'feedback', label: 'Feedback Loops' },
    { value: 'research', label: 'Research' },
    { value: 'analysis', label: 'Analysis' },
    { value: 'decision', label: 'Decision Support' },
  ];

  const filteredTemplates = TEMPLATES.filter((template) => {
    const matchesCategory = !selectedCategory || template.category === selectedCategory;
    const matchesSearch =
      !searchQuery ||
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.useCase.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleSelectTemplate = useCallback(
    (template: WorkflowTemplate) => {
      onTemplateSelect(template.definition);
      onClose?.();
    },
    [onTemplateSelect, onClose]
  );

  return (
    <div className="workflow-templates-modal">
      <div className="templates-overlay" onClick={onClose} />

      <div className="templates-container">
        <div className="templates-header">
          <h2>Workflow Templates</h2>
          <button onClick={onClose} className="close-btn">
            ×
          </button>
        </div>

        {/* Search and Filter */}
        <div className="templates-controls">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search templates..."
            className="search-input"
          />

          <div className="category-filter">
            <button
              onClick={() => setSelectedCategory(null)}
              className={`filter-btn ${!selectedCategory ? 'active' : ''}`}
            >
              All
            </button>
            {categories.map((cat) => (
              <button
                key={cat.value}
                onClick={() => setSelectedCategory(cat.value)}
                className={`filter-btn ${selectedCategory === cat.value ? 'active' : ''}`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Templates Grid */}
        <div className="templates-grid">
          {filteredTemplates.length > 0 ? (
            filteredTemplates.map((template) => (
              <div key={template.id} className="template-card">
                {template.thumbnail && (
                  <div className="template-thumbnail">
                    <img src={template.thumbnail} alt={template.name} />
                  </div>
                )}

                <div className="template-content">
                  <h3>{template.name}</h3>
                  <p className="template-description">{template.description}</p>
                  <p className="template-usecase">Use case: {template.useCase}</p>

                  <div className="template-meta">
                    <span className="badge category">{template.category}</span>
                    <span className="badge complexity">
                      {template.definition.metadata?.complexity || 'medium'}
                    </span>
                  </div>

                  <button
                    onClick={() => handleSelectTemplate(template)}
                    className="btn btn-primary btn-block"
                  >
                    Use Template
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="no-templates">
              <p>No templates found matching your search.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowTemplates;
