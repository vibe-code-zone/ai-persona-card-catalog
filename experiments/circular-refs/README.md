---
name: "Circular Reference Test"
description: "Test experiment with intentional circular file references to validate cycle detection"
llms: ["claude-3.5-sonnet"]
contact: "test@example.com"
project: "Cycle Detection Testing"
category: "Testing"
short_name: "circular-refs"
---
<!-- Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions -->

# Circular Reference Test

This experiment intentionally creates circular references to test our cycle detection system.

## The Cycle

This README references [file_a.md](./file_a.md), which starts a reference chain:

README.md → file_a.md → file_b.md → file_c.md → file_a.md

The system should detect this cycle and include all files without getting stuck in an infinite loop.

## Additional Files

We also have some non-circular references:
- [standalone.md](./standalone.md) - No references to other files
- [config.json](./config.json) - JSON configuration with references