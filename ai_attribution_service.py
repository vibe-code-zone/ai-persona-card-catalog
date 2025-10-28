"""
AI Attribution Service

Handles loading AI attribution configuration and applying template variable replacement
during persona extraction. Supports auto-generation of CLAUDE.md files and attribution
injection into README.md files.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class AIAttributionService:
    """Service for handling AI attribution during persona extraction"""

    def __init__(self, attribution_file: Path = None):
        if attribution_file is None:
            attribution_file = Path("AI-ATTRIBUTION.md")
        self.attribution_file = attribution_file
        self.config = {}
        self.selected_standard = ""  # Track which attribution standard is selected
        self.load_config()

    def set_selected_standard(self, standard: str):
        """Set the selected attribution standard"""
        self.selected_standard = standard

    def get_selected_standard(self) -> str:
        """Get the currently selected attribution standard"""
        return self.selected_standard

    def load_config(self):
        """Load AI attribution configuration from AI-ATTRIBUTION.md"""
        try:
            if self.attribution_file.exists():
                with open(self.attribution_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract YAML section
                if "```yaml" in content:
                    yaml_start = content.find("```yaml") + 7
                    yaml_end = content.find("```", yaml_start)
                    if yaml_end > yaml_start:
                        yaml_content = content[yaml_start:yaml_end].strip()
                        self.config = yaml.safe_load(yaml_content) or {}
                    else:
                        self.config = {}
                else:
                    self.config = {}
            else:
                # Create default configuration if file doesn't exist
                self.config = self._default_config()
                self._create_default_file()
        except Exception as e:
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default AI attribution configuration"""
        return {
            "attribution": {
                "standard": "AIA",
                "model": "claude-sonnet-4@20250514",
                "human_role": "Human-initiated",
                "generation_type": "New content",
                "review_status": "Reviewed",
                "tool": "Claude Code v1.0",
            },
            "aia_code": "AIA PAI Nc Hin R Claude Code v1.0",
            "templates": {
                "claude_md": """# AI Assistant Configuration

## Attribution Standards

This project follows [AI Attribution Initiative](https://aiattribution.github.io/) standards.

**AIA Code:** {aia_code}

**Model:** {model}
**Generated Content:** {generation_type}
**Human Role:** {human_role}
**Review Status:** {review_status}

## Project-Specific Instructions

{persona_instructions}

---

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>""",
                "ai_instructions": """
## AI Attribution Instructions

When working on projects using this persona, follow these attribution standards:

**Standard:** AIA (AI Attribution Initiative)
**Reference:** https://aiattribution.github.io/interpret-attribution

**For code contributions:**
```
# AI-generated code following AIA standards
# AIA Code: {aia_code}
# Model: {model}
# Human Role: {human_role}
```

**For documentation updates:**
- Add "🤖 Generated with [Claude Code](https://claude.ai/code)" to modified sections
- Include "Co-Authored-By: Claude <noreply@anthropic.com>" in commits

**For README.md additions:**
Include this attribution block for any AI-generated content:
```markdown
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**AIA Code:** {aia_code}
**Current Model:** {model}
**Attribution Guidelines:** https://aiattribution.github.io/interpret-attribution

Apply these standards to maintain consistent AI attribution across the project.""",
            },
            "extraction": {
                "auto_add_ai_instructions": True,
                "preserve_existing_attribution": True,
                "template_variable_replacement": True,
            },
        }

    def _create_default_file(self):
        """Create default AI-ATTRIBUTION.md file"""
        try:
            content = (
                """# AI Attribution Configuration

This file configures automatic AI attribution for all persona extractions from this catalog.

## Attribution Standard

**Selected Standard:** AIA (AI Attribution Initiative)
**Reference:** https://aiattribution.github.io/interpret-attribution

## Current Session Configuration

```yaml
"""
                + yaml.dump(self.config, default_flow_style=False, sort_keys=False)
                + """```

## Usage

When personas are extracted from this catalog, attribution is automatically applied based on these settings.

Template variables like {aia_code}, {model}, etc. are replaced with current values during extraction.
"""
            )
            with open(self.attribution_file, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass  # Silently fail if we can't create the file

    def get_template_variables(self, persona_instructions: str = "") -> Dict[str, str]:
        """Get template variables for replacement"""
        attribution = self.config.get("attribution", {})
        return {
            "aia_code": self.config.get("aia_code", "AIA PAI Nc Hin R Claude Code v1.0"),
            "model": attribution.get("model", "claude-sonnet-4"),
            "generation_type": attribution.get("generation_type", "New content"),
            "human_role": attribution.get("human_role", "Human-initiated"),
            "review_status": attribution.get("review_status", "Reviewed"),
            "tool": attribution.get("tool", "Claude Code v1.0"),
            "persona_instructions": persona_instructions,
        }

    def replace_template_variables(self, content: str, variables: Dict[str, str]) -> str:
        """Replace template variables in content"""
        if not self.config.get("extraction", {}).get("template_variable_replacement", True):
            return content

        for key, value in variables.items():
            # Replace {key} patterns
            content = content.replace(f"{{{key}}}", str(value))

        return content

    def generate_claude_md(self, persona_instructions: str = "") -> str:
        """Generate CLAUDE.md content with attribution"""
        template = self.config.get("templates", {}).get("claude_md", "")
        if not template:
            template = self._default_config()["templates"]["claude_md"]

        variables = self.get_template_variables(persona_instructions)
        return self.replace_template_variables(template, variables)

    def generate_ai_instructions(self) -> str:
        """Generate AI attribution instructions section"""
        template = self.config.get("templates", {}).get("ai_instructions", "")
        if not template:
            template = self._default_config()["templates"]["ai_instructions"]

        variables = self.get_template_variables()
        return self.replace_template_variables(template, variables)

    def should_auto_create_claude_md(self) -> bool:
        """Check if CLAUDE.md should be auto-created - DEPRECATED"""
        # We no longer auto-create separate CLAUDE.md files
        # Instead we update the main persona file
        return False

    def should_auto_add_ai_instructions(self) -> bool:
        """Check if AI instructions should be auto-added to instruction files"""
        return self.config.get("extraction", {}).get("auto_add_ai_instructions", True)

    def should_preserve_existing_attribution(self) -> bool:
        """Check if existing attribution should be preserved"""
        return self.config.get("extraction", {}).get("preserve_existing_attribution", True)

    def process_file_content(self, file_path: Path, content: str, is_main_persona_file: bool = False) -> str:
        """Process file content and apply attribution if needed"""
        if not self.config.get("extraction", {}).get("template_variable_replacement", True):
            return content

        # For main persona/context files, add AI instructions if enabled
        if is_main_persona_file and self.should_auto_add_ai_instructions():
            if not self._has_attribution(content):
                ai_instructions = self.generate_ai_instructions()
                # Add AI instructions at the end of the file
                return content + "\n\n" + ai_instructions

        # For all files, replace template variables if they exist
        variables = self.get_template_variables()
        return self.replace_template_variables(content, variables)

    def _has_attribution(self, content: str) -> bool:
        """Check if content already has AI attribution"""
        attribution_indicators = [
            "AI Attribution",
            "AIA Code:",
            "aiattribution.github.io",
            "Generated with [Claude Code]",
            "Co-Authored-By: Claude",
        ]

        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in attribution_indicators)

    def create_claude_md_for_persona(self, persona_name: str, persona_description: str = "") -> str:
        """Create CLAUDE.md content for a specific persona"""
        persona_instructions = f"Persona: {persona_name}\n\n{persona_description}"
        return self.generate_claude_md(persona_instructions)

    def get_files_to_auto_create(self, dest_path: Path) -> List[tuple]:
        """Get list of files that should be auto-created during extraction"""
        # We no longer auto-create separate files
        # Attribution is added directly to the main persona file during extraction
        return []
