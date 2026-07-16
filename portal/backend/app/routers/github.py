"""
FastAPI router for GitHub webhook integration.

Handles inbound GitHub webhooks for repository events:
- Push events (CLAUDE.md changes)
- Pull request events (validation)
- Issue events (knowledge base)
- Release events (version updates)
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.github_service import GitHubWebhookHandler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["Webhooks"])

# Initialize handler
_webhook_handler: Optional[GitHubWebhookHandler] = None


def get_webhook_handler() -> GitHubWebhookHandler:
    """Get or initialize webhook handler."""
    global _webhook_handler
    if _webhook_handler is None:
        _webhook_handler = GitHubWebhookHandler()
    return _webhook_handler


class WebhookResponse(BaseModel):
    """Webhook processing response."""

    success: bool = Field(..., description="Whether the webhook was processed successfully")
    message: str = Field(..., description="Processing message or error details")
    event_type: Optional[str] = Field(None, description="GitHub event type")


class WebhookErrorResponse(BaseModel):
    """Webhook error response."""

    success: bool = False
    error: str = Field(..., description="Error message")
    status_code: int = Field(..., description="HTTP status code")


@router.post(
    "/github",
    response_model=WebhookResponse,
    status_code=202,
    summary="GitHub Webhook Endpoint",
    description="Receive and process GitHub repository events"
)
async def receive_github_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> WebhookResponse:
    """
    Receive GitHub webhooks.

    GitHub sends webhooks to this endpoint with:
    - X-GitHub-Event: Event type (push, pull_request, issue, release)
    - X-Hub-Signature-256: HMAC SHA256 signature
    - X-GitHub-Delivery: Unique delivery ID

    The endpoint verifies the signature and dispatches to appropriate handler.

    Returns:
        WebhookResponse: Processing status and message
    """
    try:
        # Get event type
        event_type = request.headers.get("X-GitHub-Event")
        delivery_id = request.headers.get("X-GitHub-Delivery")
        signature = request.headers.get("X-Hub-Signature-256")

        logger.info(
            f"Received GitHub webhook: event={event_type}, "
            f"delivery={delivery_id}"
        )

        # Verify required headers
        if not event_type:
            logger.warning("Missing X-GitHub-Event header")
            raise HTTPException(
                status_code=400,
                detail="Missing X-GitHub-Event header"
            )

        if not signature:
            logger.warning("Missing X-Hub-Signature-256 header")
            raise HTTPException(
                status_code=400,
                detail="Missing X-Hub-Signature-256 header"
            )

        # Get raw body
        body = await request.body()

        # Verify signature
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        if not webhook_secret:
            logger.error("GITHUB_WEBHOOK_SECRET environment variable not set")
            raise HTTPException(
                status_code=500,
                detail="Webhook secret not configured"
            )

        handler = get_webhook_handler()
        if not await handler.verify_signature(body, signature, webhook_secret):
            logger.warning(
                f"Invalid signature for webhook delivery {delivery_id}"
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid webhook signature"
            )

        # Parse JSON payload
        import json
        payload = json.loads(body)

        # Dispatch to appropriate handler
        logger.info(f"Processing {event_type} event")

        if event_type == "push":
            background_tasks.add_task(
                _handle_push_webhook,
                payload,
                delivery_id
            )
            return WebhookResponse(
                success=True,
                message="Push event queued for processing",
                event_type="push"
            )

        elif event_type == "pull_request":
            background_tasks.add_task(
                _handle_pull_request_webhook,
                payload,
                delivery_id
            )
            return WebhookResponse(
                success=True,
                message="Pull request event queued for processing",
                event_type="pull_request"
            )

        elif event_type == "issues":
            background_tasks.add_task(
                _handle_issue_webhook,
                payload,
                delivery_id
            )
            return WebhookResponse(
                success=True,
                message="Issue event queued for processing",
                event_type="issues"
            )

        elif event_type == "release":
            background_tasks.add_task(
                _handle_release_webhook,
                payload,
                delivery_id
            )
            return WebhookResponse(
                success=True,
                message="Release event queued for processing",
                event_type="release"
            )

        else:
            logger.info(f"Ignoring unsupported event type: {event_type}")
            return WebhookResponse(
                success=True,
                message=f"Event type {event_type} not yet supported",
                event_type=event_type
            )

    except HTTPException:
        raise

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON payload: {e}")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON payload"
        )

    except Exception as e:
        logger.error(f"Unexpected error processing webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing webhook: {str(e)}"
        )


# Background task handlers
async def _handle_push_webhook(payload: dict, delivery_id: str) -> None:
    """Handle push event in background."""
    try:
        handler = get_webhook_handler()
        success, message = await handler.handle_push_event(payload)
        log_level = "info" if success else "warning"
        getattr(logger, log_level)(
            f"[{delivery_id}] Push event processed: {message}"
        )
    except Exception as e:
        logger.error(f"[{delivery_id}] Error in push handler: {e}")


async def _handle_pull_request_webhook(payload: dict, delivery_id: str) -> None:
    """Handle pull_request event in background."""
    try:
        handler = get_webhook_handler()
        success, message = await handler.handle_pull_request_event(payload)
        log_level = "info" if success else "warning"
        getattr(logger, log_level)(
            f"[{delivery_id}] PR event processed: {message}"
        )
    except Exception as e:
        logger.error(f"[{delivery_id}] Error in PR handler: {e}")


async def _handle_issue_webhook(payload: dict, delivery_id: str) -> None:
    """Handle issue event in background."""
    try:
        handler = get_webhook_handler()
        success, message = await handler.handle_issue_event(payload)
        log_level = "info" if success else "warning"
        getattr(logger, log_level)(
            f"[{delivery_id}] Issue event processed: {message}"
        )
    except Exception as e:
        logger.error(f"[{delivery_id}] Error in issue handler: {e}")


async def _handle_release_webhook(payload: dict, delivery_id: str) -> None:
    """Handle release event in background."""
    try:
        handler = get_webhook_handler()
        success, message = await handler.handle_release_event(payload)
        log_level = "info" if success else "warning"
        getattr(logger, log_level)(
            f"[{delivery_id}] Release event processed: {message}"
        )
    except Exception as e:
        logger.error(f"[{delivery_id}] Error in release handler: {e}")


@router.get(
    "/github/status",
    response_model=WebhookResponse,
    summary="Webhook Status Check",
    description="Check GitHub webhook integration status"
)
async def webhook_status() -> WebhookResponse:
    """
    Check webhook integration status.

    Returns:
        WebhookResponse: Current webhook configuration status
    """
    try:
        webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        portal_integration = os.getenv(
            "PORTAL_INTEGRATION_URL",
            "http://localhost:8016"
        )

        status = "configured" if webhook_secret else "not_configured"

        return WebhookResponse(
            success=True,
            message=f"Webhook integration status: {status}. "
            f"Integration URL: {portal_integration}",
            event_type="status"
        )

    except Exception as e:
        logger.error(f"Error checking webhook status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking status: {str(e)}"
        )
