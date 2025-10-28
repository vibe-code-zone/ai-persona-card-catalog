# AI Attribution Guidance

This file provides guidance for AI systems on how to attribute their contributions to work based on this persona configuration.

**Purpose**: When an AI system (LLM) reads this persona configuration, it should follow the selected attribution standard for any work it produces.

## Attribution Standards

### AIA Standard
When using this standard, the AI should include AIA-compliant attribution in any code, documentation, or content it generates.

**For Code Files:**
```
# AI-generated code following AIA standards
# AIA Code: AIA PAI Nc Hin R Claude Code v1.0
# Model: claude-3.5-sonnet
# Human Role: Human-initiated
# Generated: 2024-01-15
```

**For Documentation:**
```markdown
## AI Attribution
This work was developed with AI assistance following AIA standards.
**AIA Code:** AIA PAI Nc Hin R Claude Code v1.0
**Model:** claude-3.5-sonnet
**Human Role:** Human-initiated
**Reference:** https://aiattribution.github.io/interpret-attribution
```

### Academic Standard  
When using this standard, the AI should include academic-style citations and methodology disclosure.

**For Code Files:**
```
# AI-assisted development
# Tool: Claude Code, accessed 2024-01-15
# Model: claude-3.5-sonnet
# Methodology: Interactive prompting with human oversight
```

**For Documentation:**
```markdown
## AI Attribution
This document was developed with AI assistance.
**Citation:** Claude Code (claude-3.5-sonnet). Accessed 2024-01-15.
**Methodology:** Interactive prompting with human review
**Human Role:** Conceptual guidance and review
```

### Corporate Standard
When using this standard, the AI should include corporate compliance attribution.

**For Code Files:**
```
# AI Development Disclosure
# Tool: Claude Code
# Review Status: Human-reviewed
# Compliance: Corporate AI Policy v2.1
```

**For Documentation:**
```markdown
## Development Disclosure
**AI Tools Used:** Claude Code  
**Review Status:** Human-reviewed and approved
**Policy Compliance:** Corporate AI Policy v2.1
```

### Open Source Standard
When using this standard, the AI should include attribution compatible with open source practices.

**For Code Files:**
```
# AI-assisted code - see project ATTRIBUTION for details
# Generated with: Claude Code
# Human contribution: Architecture design and review
# License: Compatible with project license
```

**For Documentation:**
```markdown
## AI Attribution
This project uses AI-assisted development.
**Tool:** Claude Code
**Human Contribution:** Architecture, design, and review
**License:** Content compatible with project license
```

### Minimal Standard
When using this standard, the AI should include basic, unobtrusive acknowledgment.

**For Code Files:**
```
# AI-assisted development with Claude Code - human reviewed
```

**For Documentation:**
```markdown
*AI-assisted development with Claude Code. Human reviewed and approved.*
```

## Usage Notes

- The AI should automatically apply the selected standard when working with this persona
- Code examples should use the appropriate comment syntax for the file type
- Documentation examples should use markdown format
- All placeholder values (dates, tool names, etc.) should be replaced with actual values
