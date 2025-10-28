# Markdown Attribution Block Template

## Template for README.md and other markdown files

```markdown
<!-- AI Attribution Block -->
<!-- Reference: https://aiattribution.github.io/interpret-attribution -->
<!-- AIA Code: [AIA_CODE_HERE] -->
<!-- Model: [MODEL_NAME_HERE] -->
<!-- Generated: [GENERATION_TYPE_HERE] -->
<!-- Human Role: [HUMAN_ROLE_HERE] -->
<!-- Reviewed: [REVIEW_STATUS_HERE] -->

## AI Attribution

This work was primarily AI-generated. AI was used to make new content, such as text, images, analysis, and ideas.
AI was prompted for its contributions, or AI assistance was enabled. AI-generated content was reviewed and approved.
The following model(s) or application(s) were used: [MODEL_NAME_HERE].

**AIA Code:** [AIA_CODE_HERE]

([AIA_CODE_HERE])[https://aiattribution.github.io/interpret-attribution]

[https://aiattribution.github.io/]
```

## Usage Options

### 1. HTML Comment Header (Invisible)
Use the HTML comment block at the top of markdown files for machine-readable attribution.

### 2. Visible Attribution Section
Include the "AI Attribution" section for human-readable attribution.

### 3. Both
Use both for complete compliance - machine and human readable.

## Template Variables

- `AIA_CODE_HERE` - Full AIA code (e.g., "AIA PAI Nc Hin R Claude Code v1.0")
- `MODEL_NAME_HERE` - Specific model used
- `GENERATION_TYPE_HERE` - Content type (documentation, analysis, etc.)
- `HUMAN_ROLE_HERE` - Human involvement level
- `REVIEW_STATUS_HERE` - Review and approval status