/**
 * Cowork Adapter
 * MVP integration with Cowork API with mock support and webhook infrastructure
 */

/**
 * Interface para resposta estruturada do adapter
 */
export interface AdapterResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: string;
  };
  timestamp: string;
}

/**
 * Task priority levels
 */
export enum TaskPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * Task status values
 */
export enum TaskStatus {
  OPEN = 'open',
  IN_PROGRESS = 'in_progress',
  BLOCKED = 'blocked',
  REVIEW = 'review',
  DONE = 'done',
  CANCELLED = 'cancelled',
}

/**
 * Interface para Comment
 */
export interface Comment {
  id: string;
  taskId: string;
  authorId: string;
  authorName: string;
  content: string;
  createdAt: string;
  updatedAt?: string;
  attachments?: string[];
  mentions?: string[];
}

/**
 * Interface para Task
 */
export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  assigneeId?: string;
  assigneeName?: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
  dueDate?: string;
  labels?: string[];
  comments?: Comment[];
  attachments?: string[];
  relatedTasks?: string[];
  customFields?: Record<string, unknown>;
  estimatedHours?: number;
  actualHours?: number;
}

/**
 * Interface para webhook payload
 */
export interface WebhookPayload {
  event: WebhookEventType;
  timestamp: string;
  data: Task | Comment | WebhookMetadata;
  retryCount?: number;
  deliveryId: string;
}

/**
 * Webhook event types (preparado para F2+)
 */
export enum WebhookEventType {
  TASK_CREATED = 'task.created',
  TASK_UPDATED = 'task.updated',
  TASK_STATUS_CHANGED = 'task.status_changed',
  TASK_ASSIGNED = 'task.assigned',
  TASK_DELETED = 'task.deleted',
  COMMENT_ADDED = 'comment.added',
  COMMENT_UPDATED = 'comment.updated',
  COMMENT_DELETED = 'comment.deleted',
}

/**
 * Interface para webhook metadata
 */
export interface WebhookMetadata {
  eventType: WebhookEventType;
  aggregateId: string;
  aggregateType: 'task' | 'comment';
  changes?: Record<string, { from: unknown; to: unknown }>;
}

/**
 * Interface para webhook subscription (F2+)
 */
export interface WebhookSubscription {
  id: string;
  url: string;
  events: WebhookEventType[];
  active: boolean;
  createdAt: string;
  lastDeliveryAt?: string;
  failureCount: number;
  maxRetries: number;
}

/**
 * Interface para webhook delivery result (F2+)
 */
export interface WebhookDeliveryResult {
  subscriptionId: string;
  deliveryId: string;
  statusCode: number;
  responseTime: number;
  success: boolean;
  retries: number;
  nextRetryAt?: string;
}

/**
 * Interface para opções de listagem
 */
export interface ListTasksOptions {
  status?: TaskStatus | TaskStatus[];
  priority?: TaskPriority | TaskPriority[];
  assigneeId?: string;
  labels?: string[];
  limit?: number;
  offset?: number;
  sortBy?: 'createdAt' | 'updatedAt' | 'dueDate' | 'priority';
  sortOrder?: 'asc' | 'desc';
}

/**
 * Interface para opções de criação de task
 */
export interface CreateTaskOptions {
  title: string;
  description?: string;
  priority?: TaskPriority;
  assigneeId?: string;
  assigneeName?: string;
  dueDate?: string;
  labels?: string[];
  estimatedHours?: number;
  customFields?: Record<string, unknown>;
  relatedTasks?: string[];
}

/**
 * Interface para opções de comentário
 */
export interface PostCommentOptions {
  taskId: string;
  content: string;
  authorId: string;
  authorName: string;
  mentions?: string[];
  attachments?: string[];
}

/**
 * Mock storage para MVP
 */
class CoworkMockStorage {
  private tasks: Map<string, Task> = new Map();
  private comments: Map<string, Comment> = new Map();
  private webhookSubscriptions: Map<string, WebhookSubscription> = new Map();
  private deliveryLog: WebhookDeliveryResult[] = [];

  /**
   * Inicializa dados mock
   */
  constructor() {
    this.initializeMockData();
  }

  /**
   * Inicializa dados mock para desenvolvimento
   */
  private initializeMockData(): void {
    const mockTasks: Task[] = [
      {
        id: 'task-001',
        title: 'Setup Cowork API Integration',
        description: 'Implement MVP integration with Cowork API',
        status: TaskStatus.IN_PROGRESS,
        priority: TaskPriority.HIGH,
        assigneeId: 'user-001',
        assigneeName: 'Alice Engineer',
        createdBy: 'user-admin',
        createdAt: new Date(Date.now() - 86400000).toISOString(),
        updatedAt: new Date(Date.now() - 3600000).toISOString(),
        dueDate: new Date(Date.now() + 604800000).toISOString(),
        labels: ['integration', 'api', 'mvp'],
        estimatedHours: 16,
        actualHours: 8,
        comments: [],
      },
      {
        id: 'task-002',
        title: 'Implement webhook support',
        description: 'Add webhook infrastructure for real-time updates (F2+)',
        status: TaskStatus.OPEN,
        priority: TaskPriority.MEDIUM,
        assigneeId: 'user-002',
        assigneeName: 'Bob Developer',
        createdBy: 'user-admin',
        createdAt: new Date(Date.now() - 172800000).toISOString(),
        updatedAt: new Date(Date.now() - 172800000).toISOString(),
        dueDate: new Date(Date.now() + 1209600000).toISOString(),
        labels: ['webhooks', 'async', 'feature'],
        estimatedHours: 24,
        comments: [],
      },
      {
        id: 'task-003',
        title: 'Write integration tests',
        description: 'Unit and integration tests for CoworkAdapter',
        status: TaskStatus.OPEN,
        priority: TaskPriority.MEDIUM,
        createdBy: 'user-admin',
        createdAt: new Date(Date.now() - 259200000).toISOString(),
        updatedAt: new Date(Date.now() - 259200000).toISOString(),
        labels: ['testing', 'quality'],
        estimatedHours: 12,
        comments: [],
      },
    ];

    mockTasks.forEach(task => {
      this.tasks.set(task.id, task);
    });

    const mockComments: Comment[] = [
      {
        id: 'comment-001',
        taskId: 'task-001',
        authorId: 'user-001',
        authorName: 'Alice Engineer',
        content: 'Started working on the API integration. The SDK looks straightforward.',
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        mentions: [],
      },
      {
        id: 'comment-002',
        taskId: 'task-001',
        authorId: 'user-003',
        authorName: 'Charlie Reviewer',
        content: '@Alice could you also document the error handling patterns?',
        createdAt: new Date(Date.now() - 1800000).toISOString(),
        mentions: ['user-001'],
      },
    ];

    mockComments.forEach(comment => {
      this.comments.set(comment.id, comment);
    });
  }

  /**
   * Obtém todas as tasks com filtros opcionais
   */
  listTasks(options?: ListTasksOptions): Task[] {
    let filtered = Array.from(this.tasks.values());

    if (options) {
      // Filtro de status
      if (options.status) {
        const statuses = Array.isArray(options.status) ? options.status : [options.status];
        filtered = filtered.filter(t => statuses.includes(t.status));
      }

      // Filtro de prioridade
      if (options.priority) {
        const priorities = Array.isArray(options.priority) ? options.priority : [options.priority];
        filtered = filtered.filter(t => priorities.includes(t.priority));
      }

      // Filtro de assignee
      if (options.assigneeId) {
        filtered = filtered.filter(t => t.assigneeId === options.assigneeId);
      }

      // Filtro de labels
      if (options.labels && options.labels.length > 0) {
        filtered = filtered.filter(t =>
          t.labels && t.labels.some(label => options.labels!.includes(label))
        );
      }

      // Ordenação
      const sortBy = options.sortBy || 'createdAt';
      const sortOrder = options.sortOrder || 'desc';
      filtered.sort((a, b) => {
        const aValue = a[sortBy as keyof Task] as unknown;
        const bValue = b[sortBy as keyof Task] as unknown;

        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return sortOrder === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        }

        return sortOrder === 'asc'
          ? (aValue as number) - (bValue as number)
          : (bValue as number) - (aValue as number);
      });

      // Paginação
      const offset = options.offset || 0;
      const limit = options.limit || 20;
      filtered = filtered.slice(offset, offset + limit);
    }

    return filtered;
  }

  /**
   * Obtém uma task pelo ID
   */
  getTask(taskId: string): Task | undefined {
    return this.tasks.get(taskId);
  }

  /**
   * Cria uma nova task
   */
  createTask(options: CreateTaskOptions, userId: string): Task {
    const taskId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();

    const task: Task = {
      id: taskId,
      title: options.title,
      description: options.description,
      status: TaskStatus.OPEN,
      priority: options.priority || TaskPriority.MEDIUM,
      assigneeId: options.assigneeId,
      assigneeName: options.assigneeName,
      createdBy: userId,
      createdAt: now,
      updatedAt: now,
      dueDate: options.dueDate,
      labels: options.labels,
      estimatedHours: options.estimatedHours,
      customFields: options.customFields,
      relatedTasks: options.relatedTasks,
      comments: [],
    };

    this.tasks.set(taskId, task);
    return task;
  }

  /**
   * Atualiza uma task
   */
  updateTask(taskId: string, updates: Partial<Task>): Task | null {
    const task = this.tasks.get(taskId);
    if (!task) {
      return null;
    }

    const updated: Task = {
      ...task,
      ...updates,
      updatedAt: new Date().toISOString(),
    };

    this.tasks.set(taskId, updated);
    return updated;
  }

  /**
   * Adiciona um comentário a uma task
   */
  addComment(options: PostCommentOptions): Comment {
    const commentId = `comment-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const now = new Date().toISOString();

    const comment: Comment = {
      id: commentId,
      taskId: options.taskId,
      authorId: options.authorId,
      authorName: options.authorName,
      content: options.content,
      createdAt: now,
      mentions: options.mentions,
      attachments: options.attachments,
    };

    this.comments.set(commentId, comment);

    // Adiciona o comentário à task
    const task = this.tasks.get(options.taskId);
    if (task) {
      if (!task.comments) {
        task.comments = [];
      }
      task.comments.push(comment);
      task.updatedAt = now;
    }

    return comment;
  }

  /**
   * Obtém comentários de uma task
   */
  getComments(taskId: string): Comment[] {
    const task = this.tasks.get(taskId);
    return task?.comments || [];
  }

  /**
   * Registra uma subscription de webhook (F2+)
   */
  registerWebhookSubscription(subscription: WebhookSubscription): void {
    this.webhookSubscriptions.set(subscription.id, subscription);
  }

  /**
   * Obtém webhooks ativos
   */
  getActiveWebhooks(eventType: WebhookEventType): WebhookSubscription[] {
    return Array.from(this.webhookSubscriptions.values()).filter(
      sub => sub.active && sub.events.includes(eventType)
    );
  }

  /**
   * Registra entrega de webhook (F2+)
   */
  logWebhookDelivery(result: WebhookDeliveryResult): void {
    this.deliveryLog.push(result);
  }

  /**
   * Obtém histórico de entregas (F2+)
   */
  getDeliveryHistory(subscriptionId: string, limit: number = 100): WebhookDeliveryResult[] {
    return this.deliveryLog
      .filter(r => r.subscriptionId === subscriptionId)
      .slice(-limit);
  }
}

/**
 * Classe para operações Cowork
 */
export class CoworkAdapter {
  private apiBaseUrl: string;
  private apiKey: string;
  private mockStorage: CoworkMockStorage;
  private useMock: boolean;
  private webhookCallbacks: Map<WebhookEventType, ((payload: WebhookPayload) => Promise<void>)[]> =
    new Map();

  constructor(apiBaseUrl: string = 'https://api.cowork.local', apiKey: string = '', useMock: boolean = true) {
    this.apiBaseUrl = apiBaseUrl;
    this.apiKey = apiKey;
    this.mockStorage = new CoworkMockStorage();
    this.useMock = useMock || !apiKey;
  }

  /**
   * Lista todas as tasks com filtros opcionais
   */
  async listTasks(options?: ListTasksOptions): Promise<AdapterResponse<Task[]>> {
    try {
      if (this.useMock) {
        const tasks = this.mockStorage.listTasks(options);
        return {
          success: true,
          data: tasks,
          timestamp: new Date().toISOString(),
        };
      }

      // Implementação real com API (quando houver credenciais)
      const params = new URLSearchParams();
      if (options?.status) {
        const statuses = Array.isArray(options.status) ? options.status : [options.status];
        params.append('status', statuses.join(','));
      }
      if (options?.priority) {
        const priorities = Array.isArray(options.priority) ? options.priority : [options.priority];
        params.append('priority', priorities.join(','));
      }
      if (options?.assigneeId) {
        params.append('assignee_id', options.assigneeId);
      }
      if (options?.limit) {
        params.append('limit', String(options.limit));
      }
      if (options?.offset) {
        params.append('offset', String(options.offset));
      }

      const response = await fetch(`${this.apiBaseUrl}/tasks?${params.toString()}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        return {
          success: false,
          error: {
            code: 'API_ERROR',
            message: `Failed to list tasks: HTTP ${response.status}`,
          },
          timestamp: new Date().toISOString(),
        };
      }

      const data = (await response.json()) as { tasks?: Task[] };
      return {
        success: true,
        data: data.tasks || [],
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'LIST_TASKS_ERROR',
          message: 'Failed to list tasks',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Cria uma nova task
   */
  async createTask(options: CreateTaskOptions, userId: string = 'system'): Promise<AdapterResponse<Task>> {
    try {
      // Validação
      if (!options.title || options.title.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_TITLE',
            message: 'Task title cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      if (this.useMock) {
        const task = this.mockStorage.createTask(options, userId);
        await this.emitWebhookEvent(WebhookEventType.TASK_CREATED, task);
        return {
          success: true,
          data: task,
          timestamp: new Date().toISOString(),
        };
      }

      // Implementação real com API
      const response = await fetch(`${this.apiBaseUrl}/tasks`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: options.title,
          description: options.description,
          priority: options.priority || TaskPriority.MEDIUM,
          assignee_id: options.assigneeId,
          assignee_name: options.assigneeName,
          due_date: options.dueDate,
          labels: options.labels,
          estimated_hours: options.estimatedHours,
          custom_fields: options.customFields,
          related_tasks: options.relatedTasks,
        }),
      });

      if (!response.ok) {
        const errorData = (await response.json()) as { error?: string };
        return {
          success: false,
          error: {
            code: 'API_ERROR',
            message: 'Failed to create task',
            details: errorData.error || `HTTP ${response.status}`,
          },
          timestamp: new Date().toISOString(),
        };
      }

      const task = (await response.json()) as Task;
      await this.emitWebhookEvent(WebhookEventType.TASK_CREATED, task);

      return {
        success: true,
        data: task,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'CREATE_TASK_ERROR',
          message: 'Failed to create task',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Posta um comentário em uma task
   */
  async postComment(options: PostCommentOptions): Promise<AdapterResponse<Comment>> {
    try {
      // Validação
      if (!options.taskId || options.taskId.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_TASK_ID',
            message: 'Task ID cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      if (!options.content || options.content.trim().length === 0) {
        return {
          success: false,
          error: {
            code: 'INVALID_CONTENT',
            message: 'Comment content cannot be empty',
          },
          timestamp: new Date().toISOString(),
        };
      }

      if (this.useMock) {
        const task = this.mockStorage.getTask(options.taskId);
        if (!task) {
          return {
            success: false,
            error: {
              code: 'TASK_NOT_FOUND',
              message: `Task ${options.taskId} not found`,
            },
            timestamp: new Date().toISOString(),
          };
        }

        const comment = this.mockStorage.addComment(options);
        await this.emitWebhookEvent(WebhookEventType.COMMENT_ADDED, comment);

        return {
          success: true,
          data: comment,
          timestamp: new Date().toISOString(),
        };
      }

      // Implementação real com API
      const response = await fetch(`${this.apiBaseUrl}/tasks/${options.taskId}/comments`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: options.content,
          author_id: options.authorId,
          author_name: options.authorName,
          mentions: options.mentions,
          attachments: options.attachments,
        }),
      });

      if (!response.ok) {
        const errorData = (await response.json()) as { error?: string };
        return {
          success: false,
          error: {
            code: 'API_ERROR',
            message: 'Failed to post comment',
            details: errorData.error || `HTTP ${response.status}`,
          },
          timestamp: new Date().toISOString(),
        };
      }

      const comment = (await response.json()) as Comment;
      await this.emitWebhookEvent(WebhookEventType.COMMENT_ADDED, comment);

      return {
        success: true,
        data: comment,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'POST_COMMENT_ERROR',
          message: 'Failed to post comment',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Registra um callback para um tipo de webhook event (F2+)
   */
  onWebhookEvent(eventType: WebhookEventType, callback: (payload: WebhookPayload) => Promise<void>): void {
    if (!this.webhookCallbacks.has(eventType)) {
      this.webhookCallbacks.set(eventType, []);
    }
    this.webhookCallbacks.get(eventType)!.push(callback);
  }

  /**
   * Emite um evento de webhook (F2+)
   */
  private async emitWebhookEvent(eventType: WebhookEventType, data: Task | Comment): Promise<void> {
    const callbacks = this.webhookCallbacks.get(eventType) || [];
    const payload: WebhookPayload = {
      event: eventType,
      timestamp: new Date().toISOString(),
      data,
      deliveryId: `delivery-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };

    for (const callback of callbacks) {
      try {
        await callback(payload);
      } catch (error) {
        console.error(`Error in webhook callback for ${eventType}:`, error);
      }
    }
  }

  /**
   * Registra uma subscription de webhook (F2+)
   */
  registerWebhookSubscription(url: string, events: WebhookEventType[]): AdapterResponse<WebhookSubscription> {
    try {
      const subscription: WebhookSubscription = {
        id: `sub-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        url,
        events,
        active: true,
        createdAt: new Date().toISOString(),
        failureCount: 0,
        maxRetries: 3,
      };

      this.mockStorage.registerWebhookSubscription(subscription);

      return {
        success: true,
        data: subscription,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'WEBHOOK_REGISTRATION_ERROR',
          message: 'Failed to register webhook subscription',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }

  /**
   * Obtém status da conexão
   */
  async getStatus(): Promise<AdapterResponse<{ connected: boolean; mode: 'mock' | 'api' }>> {
    try {
      if (this.useMock) {
        return {
          success: true,
          data: { connected: true, mode: 'mock' },
          timestamp: new Date().toISOString(),
        };
      }

      const response = await fetch(`${this.apiBaseUrl}/health`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
        },
      });

      return {
        success: response.ok,
        data: { connected: response.ok, mode: 'api' },
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'STATUS_CHECK_ERROR',
          message: 'Failed to check status',
          details: error instanceof Error ? error.message : String(error),
        },
        timestamp: new Date().toISOString(),
      };
    }
  }
}

/**
 * Funções exportadas para uso direto
 */

/**
 * Lista tasks com filtros opcionais
 */
export async function list_tasks(
  options?: ListTasksOptions,
  apiBaseUrl?: string,
  apiKey?: string
): Promise<AdapterResponse<Task[]>> {
  const adapter = new CoworkAdapter(apiBaseUrl, apiKey);
  return adapter.listTasks(options);
}

/**
 * Cria uma nova task
 */
export async function create_task(
  options: CreateTaskOptions,
  userId?: string,
  apiBaseUrl?: string,
  apiKey?: string
): Promise<AdapterResponse<Task>> {
  const adapter = new CoworkAdapter(apiBaseUrl, apiKey);
  return adapter.createTask(options, userId);
}

/**
 * Posta um comentário em uma task
 */
export async function post_comment(
  options: PostCommentOptions,
  apiBaseUrl?: string,
  apiKey?: string
): Promise<AdapterResponse<Comment>> {
  const adapter = new CoworkAdapter(apiBaseUrl, apiKey);
  return adapter.postComment(options);
}

/**
 * Registra uma subscription de webhook (F2+)
 */
export function register_webhook(
  url: string,
  events: WebhookEventType[],
  apiBaseUrl?: string,
  apiKey?: string
): AdapterResponse<WebhookSubscription> {
  const adapter = new CoworkAdapter(apiBaseUrl, apiKey);
  return adapter.registerWebhookSubscription(url, events);
}

/**
 * Obtém status da conexão
 */
export async function get_cowork_status(
  apiBaseUrl?: string,
  apiKey?: string
): Promise<AdapterResponse<{ connected: boolean; mode: 'mock' | 'api' }>> {
  const adapter = new CoworkAdapter(apiBaseUrl, apiKey);
  return adapter.getStatus();
}
