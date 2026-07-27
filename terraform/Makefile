.PHONY: help init validate plan apply destroy fmt clean debug state

TERRAFORM := terraform
TFVARS := terraform.tfvars
PLAN_FILE := tfplan

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Display this help menu
	@echo "$(BLUE)Manta Platform Terraform - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

init: ## Initialize Terraform (must run first)
	@echo "$(BLUE)Initializing Terraform...$(NC)"
	$(TERRAFORM) init
	@echo "$(GREEN)✓ Terraform initialized$(NC)"

validate: ## Validate Terraform configuration
	@echo "$(BLUE)Validating Terraform configuration...$(NC)"
	$(TERRAFORM) validate
	@echo "$(GREEN)✓ Configuration is valid$(NC)"

fmt: ## Format Terraform files
	@echo "$(BLUE)Formatting Terraform files...$(NC)"
	$(TERRAFORM) fmt -recursive
	@echo "$(GREEN)✓ Files formatted$(NC)"

fmt-check: ## Check Terraform formatting without applying
	@echo "$(BLUE)Checking Terraform formatting...$(NC)"
	$(TERRAFORM) fmt -recursive -check
	@echo "$(GREEN)✓ Formatting check passed$(NC)"

plan: validate ## Create Terraform plan (no changes)
	@echo "$(BLUE)Creating Terraform plan...$(NC)"
	$(TERRAFORM) plan -out=$(PLAN_FILE)
	@echo "$(GREEN)✓ Plan created: $(PLAN_FILE)$(NC)"

plan-destroy: validate ## Create plan for destroying resources
	@echo "$(RED)Creating destroy plan...$(NC)"
	$(TERRAFORM) plan -destroy -out=$(PLAN_FILE)
	@echo "$(RED)✓ Destroy plan created: $(PLAN_FILE)$(NC)"

apply: ## Apply Terraform plan (use with caution)
	@if [ ! -f $(PLAN_FILE) ]; then \
		echo "$(RED)Error: Plan file not found. Run 'make plan' first.$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)About to apply changes...$(NC)"
	@echo "$(YELLOW)Press Ctrl+C to cancel, or wait 10 seconds to continue...$(NC)"
	@sleep 10
	$(TERRAFORM) apply $(PLAN_FILE)
	@echo "$(GREEN)✓ Terraform apply completed$(NC)"
	@rm -f $(PLAN_FILE)

apply-auto-approve: ## Apply without plan (dangerous!)
	@echo "$(RED)WARNING: Applying without plan review!$(NC)"
	@echo "$(YELLOW)Press Ctrl+C within 10 seconds to cancel...$(NC)"
	@sleep 10
	$(TERRAFORM) apply -auto-approve
	@echo "$(GREEN)✓ Applied$(NC)"

destroy: ## Destroy all infrastructure (use with EXTREME caution)
	@echo "$(RED)WARNING: This will destroy ALL infrastructure!$(NC)"
	@echo "$(RED)Type 'destroy-prod' to confirm destruction of production...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(TERRAFORM) destroy -auto-approve; \
		echo "$(RED)✓ Destroyed$(NC)"; \
	else \
		echo "$(GREEN)Cancelled$(NC)"; \
	fi

destroy-prod: ## Destroy production (requires confirmation)
	@echo "$(RED)PRODUCTION DESTRUCTION CONFIRMED$(NC)"
	$(TERRAFORM) destroy -auto-approve
	@echo "$(RED)✓ Production destroyed$(NC)"

output: ## Display Terraform outputs
	@echo "$(BLUE)Terraform Outputs:$(NC)"
	$(TERRAFORM) output

output-json: ## Display outputs as JSON
	@$(TERRAFORM) output -json | jq .

refresh: ## Refresh Terraform state
	@echo "$(BLUE)Refreshing Terraform state...$(NC)"
	$(TERRAFORM) refresh
	@echo "$(GREEN)✓ State refreshed$(NC)"

state-list: ## List all resources in state
	@echo "$(BLUE)Resources in state:$(NC)"
	$(TERRAFORM) state list

state-show: ## Show state of specific resource
	@echo "$(YELLOW)Usage: make state-show RESOURCE=resource.name$(NC)"
	@if [ -z "$(RESOURCE)" ]; then \
		echo "$(RED)Error: RESOURCE not specified$(NC)"; \
		exit 1; \
	fi
	$(TERRAFORM) state show $(RESOURCE)

state-rm: ## Remove resource from state (DANGEROUS!)
	@echo "$(RED)WARNING: Removing from state without destroying resource!$(NC)"
	@echo "$(YELLOW)Usage: make state-rm RESOURCE=resource.name$(NC)"
	@if [ -z "$(RESOURCE)" ]; then \
		echo "$(RED)Error: RESOURCE not specified$(NC)"; \
		exit 1; \
	fi
	@read -p "Remove $(RESOURCE) from state? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(TERRAFORM) state rm $(RESOURCE); \
		echo "$(YELLOW)✓ Removed from state$(NC)"; \
	fi

state-backup: ## Backup Terraform state locally
	@echo "$(BLUE)Backing up Terraform state...$(NC)"
	@mkdir -p .backups
	@cp terraform.tfstate .backups/terraform-$(shell date +%Y%m%d-%H%M%S).tfstate || true
	@echo "$(GREEN)✓ State backed up to .backups/$(NC)"

lock-list: ## List Terraform locks (if using DynamoDB)
	@echo "$(BLUE)Checking Terraform locks...$(NC)"
	@aws dynamodb scan --table-name terraform-locks --region $(shell grep 'region' terraform.tfvars | head -1 | cut -d'"' -f2) 2>/dev/null || echo "$(YELLOW)DynamoDB lock table not found$(NC)"

clean: ## Clean local Terraform files (keeps state)
	@echo "$(YELLOW)Cleaning local Terraform cache...$(NC)"
	@rm -rf .terraform
	@rm -f .terraform.lock.hcl
	@rm -f $(PLAN_FILE)
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: ## Remove ALL Terraform files (DANGEROUS!)
	@echo "$(RED)WARNING: This will remove .terraform directory and lock files!$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf .terraform .terraform.lock.hcl $(PLAN_FILE); \
		echo "$(RED)✓ Cleaned all$(NC)"; \
	fi

lint: fmt-check validate ## Run linting checks

debug: ## Print debug information
	@echo "$(BLUE)Debug Information:$(NC)"
	@echo "Terraform version:"
	@$(TERRAFORM) version
	@echo ""
	@echo "AWS region (from tfvars):"
	@grep 'aws_region' $(TFVARS) || echo "Not set"
	@echo ""
	@echo "Environment:"
	@grep 'environment' $(TFVARS) || echo "Not set"
	@echo ""
	@echo "Current AWS account:"
	@aws sts get-caller-identity --output table || echo "AWS CLI not configured"

cost: ## Estimate infrastructure costs (requires Infracost)
	@echo "$(BLUE)Estimating costs with Infracost...$(NC)"
	@which infracost > /dev/null || { echo "$(RED)Infracost not installed$(NC)"; exit 1; }
	infracost breakdown --path .

logs-fastapi: ## Tail FastAPI logs
	@echo "$(BLUE)FastAPI Logs (last 50 lines):$(NC)"
	@aws logs tail /ecs/manta-platform --follow --log-stream-name-prefix fastapi || echo "$(RED)Error fetching logs$(NC)"

logs-react: ## Tail React logs
	@echo "$(BLUE)React Logs (last 50 lines):$(NC)"
	@aws logs tail /ecs/manta-platform --follow --log-stream-name-prefix react || echo "$(RED)Error fetching logs$(NC)"

logs-all: ## Tail all logs
	@echo "$(BLUE)All Application Logs:$(NC)"
	@aws logs tail /ecs/manta-platform --follow || echo "$(RED)Error fetching logs$(NC)"

alarms: ## List CloudWatch alarms
	@echo "$(BLUE)CloudWatch Alarms:$(NC)"
	@aws cloudwatch describe-alarms --query "MetricAlarms[*].[AlarmName,StateValue]" --output table --region $$(grep 'aws_region' $(TFVARS) | cut -d'"' -f2)

health-check: ## Check infrastructure health
	@echo "$(BLUE)Infrastructure Health Check:$(NC)"
	@echo ""
	@echo "ALB Status:"
	@aws elbv2 describe-load-balancers --query "LoadBalancers[?contains(LoadBalancerName, 'manta-platform')].[LoadBalancerName,State.Code]" --output table || true
	@echo ""
	@echo "RDS Status:"
	@aws rds describe-db-instances --query "DBInstances[?contains(DBInstanceIdentifier, 'manta-platform')].[DBInstanceIdentifier,DBInstanceStatus]" --output table || true
	@echo ""
	@echo "ECS Cluster Status:"
	@aws ecs describe-clusters --clusters manta-platform-cluster --query "clusters[0].[clusterName,status,registeredContainerInstancesCount]" --output table || true

upgrade: ## Check for Terraform provider updates
	@echo "$(BLUE)Checking for provider updates...$(NC)"
	$(TERRAFORM) init -upgrade
	@echo "$(GREEN)✓ Providers upgraded$(NC)"

workspace-list: ## List Terraform workspaces
	@echo "$(BLUE)Terraform Workspaces:$(NC)"
	$(TERRAFORM) workspace list

workspace-new: ## Create new workspace (e.g., make workspace-new ENV=staging)
	@if [ -z "$(ENV)" ]; then \
		echo "$(RED)Error: ENV not specified$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Creating workspace: $(ENV)$(NC)"
	$(TERRAFORM) workspace new $(ENV)
	@echo "$(GREEN)✓ Workspace created$(NC)"

workspace-select: ## Select workspace (e.g., make workspace-select ENV=staging)
	@if [ -z "$(ENV)" ]; then \
		echo "$(RED)Error: ENV not specified$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Selecting workspace: $(ENV)$(NC)"
	$(TERRAFORM) workspace select $(ENV)
	@echo "$(GREEN)✓ Workspace selected$(NC)"

check-resources: ## List planned resource changes
	@echo "$(BLUE)Checking planned resource changes...$(NC)"
	@$(TERRAFORM) plan -json 2>/dev/null | grep -o '"type":"[^"]*"' | sort -u || true

docs: ## Generate documentation (requires terraform-docs)
	@echo "$(BLUE)Generating documentation...$(NC)"
	@which terraform-docs > /dev/null || { echo "$(RED)terraform-docs not installed$(NC)"; exit 1; }
	@terraform-docs markdown . > DOCS.md
	@echo "$(GREEN)✓ Documentation generated: DOCS.md$(NC)"

.DEFAULT_GOAL := help
