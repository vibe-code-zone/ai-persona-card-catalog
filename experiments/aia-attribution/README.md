---
name: "AIA Code Attribution Standards"
description: "AI Attribution standards for code projects with external reference linking"
llms: ["claude-3.5-sonnet", "gpt-4", "gemini-pro"]
contact: "contact@example.com"
project: "AI Attribution Initiative"
category: "Standards"
short_name: "aia-attribution"
external_references:
  - url: "https://aiattribution.github.io/interpret-attribution"
    type: "standard"
    description: "Official AIA interpretation guidelines"
  - url: "https://aiattribution.github.io/"
    type: "documentation"
    description: "AI Attribution Initiative homepage"
tool_adapters:
  - "CLAUDE.md"
  - ".copilot-config"
  - "package.json"
  - "README.md"
---

# AIA Code Attribution Standards

This persona provides standardized AI attribution patterns that reference the official [AI Attribution Initiative](https://aiattribution.github.io/) guidelines.

## External Standards Reference

This persona implements the official AIA interpretation standard:
**Primary Reference:** [AIA Attribution - Interpret Attribution](https://aiattribution.github.io/interpret-attribution)

Rather than duplicating the standard, this persona:
1. **Links** to authoritative external sources
2. **Generates** tool-specific templates
3. **Applies** consistent attribution across projects

## Template Generation

The persona includes templates for different file types and comment styles:

### Code Attribution Templates
- [templates/claude-md.md](./templates/claude-md.md) - CLAUDE.md file template
- [templates/go-header.md](./templates/go-header.md) - Go source file headers (`//`)
- [templates/bash-header.md](./templates/bash-header.md) - Shell script headers (`#`)
- [templates/markdown-attribution.md](./templates/markdown-attribution.md) - Markdown attribution blocks

### Tool-Specific Adapters
- [templates/package-json.md](./templates/package-json.md) - npm package.json fields
- [templates/copilot-config.md](./templates/copilot-config.md) - GitHub Copilot configuration

## Real-World Application

**Problem Solved:** Consistent AI attribution across projects without manual setup

**Use Case:** Any project using AI coding tools needs proper attribution according to AIA standards

**Value:** External reference ensures accuracy and consistency with evolving standards

## Implementation Notes

This persona demonstrates the "package manager for AI personas" concept:
- External reference management
- Template engine for multiple formats  
- Tool adapter patterns
- Standards compliance automation
