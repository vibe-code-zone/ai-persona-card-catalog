---
name: "Kubernetes DevOps Best Practices"
description: "DevOps patterns and configurations based on official Kubernetes documentation"
llms: ["claude-3.5-sonnet", "gpt-4"]
contact: "devops@example.com"
project: "Cloud Native Computing Foundation"
category: "DevOps"
short_name: "k8s-devops"
external_references:
  - url: "https://kubernetes.io/docs/concepts/"
    type: "documentation"
    description: "Official Kubernetes concepts documentation"
  - url: "https://kubernetes.io/docs/tasks/"
    type: "tasks"
    description: "Kubernetes task-based documentation"
  - url: "https://kubernetes.io/docs/reference/config-file/"
    type: "reference"
    description: "Configuration file reference"
  - url: "https://helm.sh/docs/"
    type: "tooling"
    description: "Helm package manager documentation"
tool_adapters:
  - "docker-compose.yml"
  - "kubernetes-manifests"
  - "helm-charts"
  - "ci-cd-pipelines"
---

# Kubernetes DevOps Best Practices

This persona provides DevOps patterns and configurations based on official Kubernetes and CNCF documentation.

## External Documentation Reference

This persona implements patterns from official Kubernetes documentation:
**Primary Reference:** [Kubernetes Documentation](https://kubernetes.io/docs/)

Rather than duplicating K8s docs, this persona:
1. **References** official Kubernetes documentation
2. **Generates** project-specific manifests and configurations  
3. **Applies** CNCF best practices to deployment workflows

## Configuration Templates

Based on official Kubernetes patterns and best practices:

### Core Kubernetes Resources
- [templates/deployment.yaml](./templates/deployment.yaml) - Standard deployment configuration
- [templates/service.yaml](./templates/service.yaml) - Service definitions with best practices
- [templates/configmap.yaml](./templates/configmap.yaml) - Configuration management patterns
- [templates/secret.yaml](./templates/secret.yaml) - Secret management templates

### Helm Chart Patterns
- [templates/helm-chart-structure.md](./templates/helm-chart-structure.md) - Standard Helm chart layout
- [templates/values-schema.yaml](./templates/values-schema.yaml) - Values.yaml schema template

### CI/CD Integration
- [templates/github-actions-k8s.yml](./templates/github-actions-k8s.yml) - GitHub Actions for K8s deployment
- [templates/gitlab-ci-k8s.yml](./templates/gitlab-ci-k8s.yml) - GitLab CI/CD for Kubernetes

### Security & Compliance
- [templates/pod-security-standards.yaml](./templates/pod-security-standards.yaml) - Pod Security Standards
- [templates/network-policies.yaml](./templates/network-policies.yaml) - Network policy templates
- [templates/rbac.yaml](./templates/rbac.yaml) - Role-based access control

## Real-World Application

**Problem Solved:** Consistent Kubernetes deployment patterns across teams

**Use Case:** Any project deploying to Kubernetes clusters with CNCF best practices

**Value:** External reference ensures alignment with official K8s documentation and evolving best practices

## Documentation Links Integration

This persona demonstrates how external references can be:
- **Contextual**: Links to specific documentation sections relevant to each template
- **Versioned**: References to specific K8s API versions
- **Authoritative**: Direct links to official CNCF/K8s sources
- **Actionable**: Templates that implement documented patterns

## Implementation Pattern

```yaml
# Example: Each template includes reference to source documentation
# Reference: https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
apiVersion: apps/v1
kind: Deployment
metadata:
  name: [APP_NAME_HERE]
# ... rest of template
```

This creates a direct link between generated configurations and authoritative documentation.
