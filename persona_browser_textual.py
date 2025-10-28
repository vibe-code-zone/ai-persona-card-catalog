#!/usr/bin/env python3
"""
AI Persona Card Catalog - Main TUI Application

A comprehensive Terminal User Interface for browsing, searching, filtering, and extracting
AI persona configurations stored as README.md files with YAML frontmatter. Features include
multi-select extraction, inheritance resolution, smart dependency handling, and extensive
keyboard-driven navigation.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import argparse
import hashlib
import importlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    DirectoryTree,
    Footer,
    Header,
    Input,
    Label,
    Static,
)

from ai_attribution_modal_v2 import AIAttributionScreen
from extraction_modal import SimpleExtractionScreen
from file_dependency_resolver import FileDependencyResolver
from persona_inheritance_resolver import PersonaInheritanceResolver

# Constants
PREVIEW_LENGTH = 300  # Maximum length for README preview in details panel
MAX_FILES_DISPLAY = 15  # Maximum number of files to show in details panel


@dataclass
class PersonaConfig:
    """Represents a persona configuration with metadata"""

    name: str
    description: str
    llms: List[str]
    contact: str
    project: str
    category: str
    path: Path
    readme_content: str
    file_type: str = "README"  # README, CLAUDE, or CONTEXT
    inherits_from: List[str] = field(default_factory=list)  # List of paths to inherited personas
    smart_file_count: int = 0  # Files in smart extraction mode
    directory_file_count: int = 0  # Files in directory extraction mode
    smart_files: List[Path] = field(default_factory=list)  # List of files for smart extraction
    directory_files: List[Path] = field(default_factory=list)  # List of files for directory extraction
    frontmatter_data: Optional[Dict] = None  # Raw YAML frontmatter data for README viewer


class PersonaScanner:
    """Scans directories for persona configurations"""

    def __init__(self, directories: List[str] = None):
        if directories is None:
            directories = ["."]
        self.root_paths = [Path(directory).resolve() for directory in directories]

    def scan_personas(self) -> List[PersonaConfig]:
        """Scan for persona files (README.md, CLAUDE.md, CONTEXT.md) and extract metadata"""
        personas = []
        seen_content = set()  # Track content hashes to skip duplicates
        processed_dirs = set()  # Track directories we've already processed

        for root_path in self.root_paths:
            # First check the root directory itself for persona files
            root_persona_file = self._find_persona_file(root_path)
            if root_persona_file:
                try:
                    persona = self._parse_persona(root_persona_file)
                    if persona:
                        # Calculate content hash for duplicate detection
                        with open(root_persona_file, "r", encoding="utf-8") as f:
                            content_hash = hashlib.md5(f.read().encode()).hexdigest()

                        # Skip content duplicates
                        if content_hash not in seen_content:
                            seen_content.add(content_hash)
                            # Store source path for key and source column
                            persona._source_path = root_persona_file
                            personas.append(persona)
                            processed_dirs.add(root_path)
                except Exception as e:
                    # Skip problematic persona files but continue scanning
                    continue

            # Then find all subdirectories that might contain personas
            for item in root_path.rglob("*"):
                if item.is_dir() and item != root_path and item not in processed_dirs:
                    persona_file = self._find_persona_file(item)
                    if persona_file:
                        try:
                            persona = self._parse_persona(persona_file)
                            if persona:
                                # Calculate content hash for duplicate detection
                                with open(persona_file, "r", encoding="utf-8") as f:
                                    content_hash = hashlib.md5(f.read().encode()).hexdigest()

                                # Skip content duplicates
                                if content_hash in seen_content:
                                    continue
                                seen_content.add(content_hash)

                                # Store source path for key and source column
                                persona._source_path = persona_file
                                personas.append(persona)
                                processed_dirs.add(item)
                        except Exception:
                            continue

        return personas

    def _find_persona_file(self, directory: Path) -> Optional[Path]:
        """Find the best persona file in priority order"""
        # First priority: exact matches
        for filename in [
            "README.md",
            "CLAUDE.md",
            "CONTEXT.md",
            "GEMINI.md",
            "GPT.md",
            "ANTHROPIC.md",
            "COPILOT.md",
            "OPENAI.md",
            "LLAMA.md",
            "MISTRAL.md",
            "CURSOR.md",
            "AI.md",
            "PROMPT.md",
            "SYSTEM.md",
            "PERPLEXITY.md",
            "COHERE.md",
            "CODEIUM.md",
            "TABNINE.md",
        ]:
            file_path = directory / filename
            if file_path.exists():
                return file_path

        # Second priority: *README.md patterns (for backward compatibility)
        readme_files = list(directory.glob("*README.md"))
        if readme_files:
            # Sort to get consistent ordering, prefer shorter names
            readme_files.sort(key=lambda x: (len(x.name), x.name))
            return readme_files[0]

        # Third priority: *-README.md patterns
        readme_files = list(directory.glob("*-README.md"))
        if readme_files:
            readme_files.sort(key=lambda x: (len(x.name), x.name))
            return readme_files[0]

        return None

    def _determine_file_type(self, file_path: Path) -> str:
        """Determine the file type for emoji display"""
        filename = file_path.name.upper()

        if filename == "README.MD":
            return "README"
        elif filename == "CLAUDE.MD":
            return "CLAUDE"
        elif filename == "CONTEXT.MD":
            return "CONTEXT"
        elif filename in [
            "GEMINI.MD",
            "GPT.MD",
            "ANTHROPIC.MD",
            "COPILOT.MD",
            "OPENAI.MD",
            "LLAMA.MD",
            "MISTRAL.MD",
            "CURSOR.MD",
            "AI.MD",
            "PROMPT.MD",
            "SYSTEM.MD",
            "PERPLEXITY.MD",
            "COHERE.MD",
            "CODEIUM.MD",
            "TABNINE.MD",
        ]:
            return "AI_INSTRUCTION"
        elif filename.endswith("README.MD"):
            return "README"  # For *README.md and *-README.md patterns
        else:
            return "README"  # Default fallback

    def _parse_persona(self, file_path: Path) -> Optional[PersonaConfig]:
        """Parse a persona file and extract metadata (with or without frontmatter)"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for YAML frontmatter
            if content.startswith("---"):
                return self._parse_with_frontmatter(file_path, content)
            else:
                return self._parse_without_frontmatter(file_path, content)

        except Exception:
            return None

    def _parse_with_frontmatter(self, file_path: Path, content: str) -> Optional[PersonaConfig]:
        """Parse a file with YAML frontmatter"""
        try:
            # Split frontmatter from content
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()
            readme_content = parts[2].strip()

            # Parse YAML
            metadata = yaml.safe_load(frontmatter)
            frontmatter_data = metadata
            if not metadata:
                return None

            # Calculate file counts and lists for both extraction modes
            persona_path = file_path.parent
            smart_count, directory_count, smart_files, directory_files = self._calculate_file_counts(
                persona_path, file_path
            )

            # Extract required fields with defaults
            return PersonaConfig(
                name=metadata.get("name", file_path.parent.name),
                description=metadata.get("description", ""),
                llms=metadata.get("llms", []),
                contact=metadata.get("contact", ""),
                project=metadata.get("project", ""),
                category=metadata.get("category", "General"),
                path=file_path.parent,
                readme_content=readme_content,
                file_type=self._determine_file_type(file_path),
                inherits_from=metadata.get("inherits_from", []),
                smart_file_count=smart_count,
                directory_file_count=directory_count,
                smart_files=smart_files,
                directory_files=directory_files,
                frontmatter_data=frontmatter_data,
            )
        except Exception:
            return None

    def _parse_without_frontmatter(self, file_path: Path, content: str) -> Optional[PersonaConfig]:
        """Parse a file without frontmatter, extracting metadata from content"""
        try:
            # Extract name from first heading or directory name
            name = self._extract_name_from_content(content, file_path)

            # Extract description from first paragraph
            description = self._extract_description_from_content(content)

            # Try to infer LLMs from content
            llms = self._extract_llms_from_content(content)

            # Use directory name as project
            project = file_path.parent.name

            # Try to infer category from directory structure or content
            category = self._extract_category_from_path(file_path)

            # Calculate file counts
            persona_path = file_path.parent
            smart_count, directory_count, smart_files, directory_files = self._calculate_file_counts(
                persona_path, file_path
            )

            return PersonaConfig(
                name=name,
                description=description,
                llms=llms,
                contact="",
                project=project,
                category=category,
                path=file_path.parent,
                readme_content=content,
                file_type=self._determine_file_type(file_path),
                inherits_from=[],
                smart_file_count=smart_count,
                directory_file_count=directory_count,
                smart_files=smart_files,
                directory_files=directory_files,
                frontmatter_data={},
            )
        except Exception:
            return None

    def _extract_name_from_content(self, content: str, file_path: Path) -> str:
        """Extract name from first heading or use directory name"""
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                return line[2:].strip()
        return file_path.parent.name

    def _extract_description_from_content(self, content: str) -> str:
        """Extract description from first paragraph"""
        lines = content.split("\n")
        description_lines = []
        in_description = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_description:
                    break
                continue
            if line.startswith("#"):
                in_description = True
                continue
            if in_description:
                description_lines.append(line)
                if len(" ".join(description_lines)) > 200:  # Limit description length
                    break

        description = " ".join(description_lines)
        return description[:200] + "..." if len(description) > 200 else description

    def _extract_llms_from_content(self, content: str) -> List[str]:
        """Try to detect LLM mentions in content"""
        content_lower = content.lower()
        llms = []

        # Common LLM patterns
        if "claude" in content_lower or "anthropic" in content_lower:
            llms.append("claude")
        if "gpt" in content_lower or "openai" in content_lower:
            llms.append("gpt-4")
        if "gemini" in content_lower or "google" in content_lower:
            llms.append("gemini")

        return llms if llms else ["claude"]  # Default to claude

    def _extract_category_from_path(self, file_path: Path) -> str:
        """Try to infer category from directory structure"""
        path_str = str(file_path).lower()

        # Common category patterns
        if any(word in path_str for word in ["dev", "code", "programming", "software"]):
            return "Development"
        if any(word in path_str for word in ["data", "analysis", "science"]):
            return "Data Science"
        if any(word in path_str for word in ["write", "content", "blog"]):
            return "Writing"
        if any(word in path_str for word in ["research", "academic"]):
            return "Research"

        return "General"

    def _calculate_file_counts(self, persona_path: Path, readme_path: Path) -> tuple[int, int, List[Path], List[Path]]:
        """Calculate file counts and lists for smart extraction and directory extraction modes"""
        try:
            # Directory extraction - collect all files in the directory
            directory_files = []
            for item in persona_path.iterdir():
                if item.is_file():
                    directory_files.append(item)
                elif item.is_dir():
                    for subitem in item.rglob("*"):
                        if subitem.is_file():
                            directory_files.append(subitem)
            directory_count = len(directory_files)

            # Smart extraction count - dependencies + inheritance
            smart_count = 0
            try:
                # Resolve inheritance chain first
                base_path = persona_path.parent.parent  # Go up to experiments directory
                inheritance_resolver = PersonaInheritanceResolver(base_path)
                persona_chain = inheritance_resolver.resolve_inheritance(persona_path)

                # Collect files from entire inheritance chain
                all_files = set()
                for chain_persona_path in persona_chain:
                    chain_readme = self._find_persona_file(chain_persona_path)

                    if chain_readme and chain_readme.exists():
                        # Use dependency resolver for this persona
                        resolver = FileDependencyResolver(chain_persona_path)
                        persona_files = resolver.resolve_dependencies(chain_readme)
                        all_files.update(persona_files)
                    else:
                        # No README, include all files from this persona
                        for item in chain_persona_path.iterdir():
                            if item.is_file():
                                all_files.add(item)
                            elif item.is_dir():
                                for subitem in item.rglob("*"):
                                    if subitem.is_file():
                                        all_files.add(subitem)

                smart_files = list(all_files)
                smart_count = len(smart_files)

            except Exception:
                # If smart extraction fails, fall back to directory files
                smart_files = directory_files[:]
                smart_count = directory_count

            return smart_count, directory_count, smart_files, directory_files

        except Exception:
            return 0, 0, [], []


class ExtractionScreen(ModalScreen[str]):
    """Modal screen for extracting persona files"""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancel"),
    ]

    def __init__(self, persona: PersonaConfig, app_instance=None):
        super().__init__()
        self.persona = persona
        self.app_instance = app_instance
        self.destination = ""
        self.conflicts = []
        self.overwrite_mode = False

        # Initialize destination from history if available
        if self.app_instance and hasattr(self.app_instance, "extraction_history"):
            self.destination = self.app_instance.extraction_history.get(self.persona.name, "")

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Extract Persona: {self.persona.name}", classes="title"),
            Static(f"Source: {self.persona.path}"),
            Label("Destination directory:"),
            Input(
                placeholder="Enter destination path...",
                value=self.destination,
                id="dest_input",
            ),
            Horizontal(
                Button(
                    "Extract",
                    id="extract_btn",
                    disabled=not self.destination.strip(),
                    variant="primary",
                ),
                Button("Cancel", id="cancel_btn"),
            ),
            Static("", id="status"),
            id="extraction_dialog",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "dest_input":
            self.destination = event.value
            try:
                extract_btn = self.query_one("#extract_btn", Button)
                extract_btn.disabled = not self.destination.strip()
            except:
                # Button might not exist if dialog has changed state
                pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        if event.input.id == "dest_input":
            # Force update destination from input value
            self.destination = event.value

            try:
                status = self.query_one("#status", Static)
                status.update(f"🔍 DEBUG: destination='{self.destination}', len={len(self.destination)}")

                if self.destination.strip():
                    status.update("🚀 Starting extraction...")
                    self._perform_extraction()
                else:
                    status.update("❌ Please enter a destination path")
            except Exception as e:
                # Show the actual error
                try:
                    status = self.query_one("#status", Static)
                    status.update(f"💥 Error in submit: {str(e)}")
                except:
                    pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel_btn":
            self.dismiss(None)
        elif event.button.id == "extract_btn":
            status = self.query_one("#status", Static)
            status.update("🚀 Starting extraction via button...")
            self._perform_extraction()
        elif event.button.id == "create_btn":
            self._create_directory_and_extract()
        elif event.button.id == "overwrite_btn":
            self._copy_files_with_overwrite()
        elif event.button.id == "skip_btn":
            self._copy_files_skip_conflicts()

    def _perform_extraction(self) -> None:
        """Perform the actual file extraction"""
        try:
            # Show immediate feedback
            try:
                status = self.query_one("#status", Static)
                status.update(f"📁 Processing extraction to: {self.destination}")
            except:
                pass

            dest_path = Path(self.destination).expanduser().resolve()

            try:
                status = self.query_one("#status", Static)
                status.update(f"🔍 Resolved path: {dest_path}")
            except:
                pass

            # Check if destination exists, prompt to create if not
            if not dest_path.exists():
                try:
                    status = self.query_one("#status", Static)
                    status.update(f"📁 Directory doesn't exist, creating: {dest_path}")
                except:
                    pass
                self._prompt_create_directory(dest_path)
                return

            # Check for conflicts
            conflicts = []
            for item in self.persona.path.iterdir():
                dest_item = dest_path / item.name
                if dest_item.exists():
                    conflicts.append(item.name)

            if conflicts:
                try:
                    status = self.query_one("#status", Static)
                    status.update(f"⚠️ Found {len(conflicts)} conflicts")
                except:
                    pass
                self._show_conflicts(conflicts, dest_path)
            else:
                try:
                    status = self.query_one("#status", Static)
                    status.update("✅ No conflicts, copying files...")
                except:
                    pass
                self._copy_files(dest_path)

        except Exception as e:
            try:
                status = self.query_one("#status", Static)
                status.update(f"💥 MAJOR ERROR: {str(e)}")
            except:
                pass

    def _show_conflicts(self, conflicts: List[str], dest_path: Path) -> None:
        """Show conflict resolution dialog"""
        status = self.query_one("#status", Static)
        conflict_text = ", ".join(conflicts[:3])
        if len(conflicts) > 3:
            conflict_text += f" and {len(conflicts) - 3} more"

        status.update(f"⚠️  File conflicts found: {conflict_text}")

        # Add overwrite options
        container = self.query_one("#extraction_dialog", Container)

        # Remove existing buttons
        old_buttons = container.query("#extract_btn, #cancel_btn")
        for btn in old_buttons:
            btn.remove()

        # Add new conflict resolution buttons
        container.mount(
            Horizontal(
                Button("Overwrite All", id="overwrite_btn", variant="error"),
                Button("Skip Conflicts", id="skip_btn", variant="warning"),
                Button("Cancel", id="cancel_btn"),
            )
        )

        self.dest_path = dest_path

    def _prompt_create_directory(self, dest_path: Path) -> None:
        """Prompt user to create directory"""
        status = self.query_one("#status", Static)
        status.update(f"📁 Directory doesn't exist: {dest_path}")

        # Add create directory options
        container = self.query_one("#extraction_dialog", Container)

        # Remove existing buttons
        old_buttons = container.query("#extract_btn, #cancel_btn")
        for btn in old_buttons:
            btn.remove()

        # Add directory creation buttons
        container.mount(
            Horizontal(
                Button("Create & Extract", id="create_btn", variant="primary"),
                Button("Cancel", id="cancel_btn"),
            )
        )

        self.dest_path = dest_path

    def _create_directory_and_extract(self) -> None:
        """Create directory and proceed with extraction"""
        try:
            self.dest_path.mkdir(parents=True, exist_ok=True)

            # Check for conflicts (should be none in new directory)
            conflicts = []
            for item in self.persona.path.iterdir():
                dest_item = self.dest_path / item.name
                if dest_item.exists():
                    conflicts.append(item.name)

            if conflicts:
                self._show_conflicts(conflicts, self.dest_path)
            else:
                self._copy_files(self.dest_path)

        except Exception as e:
            status = self.query_one("#status", Static)
            status.update(f"❌ Error creating directory: {str(e)}")

    def _copy_files_with_overwrite(self) -> None:
        """Copy files with overwrite permission"""
        self._copy_files(self.dest_path, overwrite=True)

    def _copy_files_skip_conflicts(self) -> None:
        """Copy files but skip conflicts"""
        self._copy_files(self.dest_path, overwrite=False)

    def _copy_files(self, dest_path: Path, overwrite: bool = True) -> None:
        """Copy persona files to destination"""
        try:
            copied = 0
            skipped = 0

            for item in self.persona.path.iterdir():
                dest_item = dest_path / item.name

                if dest_item.exists() and not overwrite:
                    skipped += 1
                    continue

                if item.is_file():
                    shutil.copy2(item, dest_item)
                    copied += 1
                elif item.is_dir():
                    shutil.copytree(item, dest_item, dirs_exist_ok=overwrite)
                    copied += 1

            status = self.query_one("#status", Static)
            message = f"✅ Copied {copied} items to {dest_path}"
            if skipped:
                message += f" (skipped {skipped} conflicts)"
            status.update(message)

            # Save successful extraction directory to history
            if self.app_instance and hasattr(self.app_instance, "extraction_history"):
                self.app_instance.extraction_history[self.persona.name] = str(dest_path)
                self.app_instance._save_extraction_history()

            # Auto-close after success
            self.set_timer(3.0, lambda: self.dismiss("success"))

        except Exception as e:
            status = self.query_one("#status", Static)
            status.update(f"❌ Error copying files: {str(e)}")


class ReadmeViewerScreen(ModalScreen[str]):
    """Modal screen for viewing full README content"""

    CSS = """
    ReadmeViewerScreen {
        align: center middle;
    }
    
    #readme_container {
        width: 90%;
        height: 85%;
        border: solid $primary;
        background: $surface;
        padding: 1;
    }
    
    #frontmatter_display {
        background: $panel;
        border: solid $primary;
        padding: 1;
        margin-bottom: 1;
    }
    
    #readme_scroll {
        height: 1fr;
        scrollbar-gutter: stable;
        border: solid $primary;
        padding: 1;
    }
    
    #readme_content {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("w", "dismiss", "Close"),  # Allow W to close README viewer
        Binding("ctrl+q", "quit_app", "Quit App"),
        Binding("p", "prev_persona", "Previous README"),
        Binding("n", "next_persona", "Next README"),
        Binding("space", "toggle_selection", "Toggle Selection"),
    ]

    def __init__(
        self,
        persona: PersonaConfig,
        persona_list: List[PersonaConfig],
        current_index: int,
        app_instance=None,
    ):
        super().__init__()
        self.persona = persona
        self.persona_list = persona_list
        self.current_index = current_index
        self.app_instance = app_instance

    def compose(self) -> ComposeResult:
        persona_counter = f"({self.current_index + 1} of {len(self.persona_list)})"
        yield Container(
            Static(
                f"[bold]{self.persona.name}[/bold] - README {persona_counter}",
                id="readme_header",
            ),
            Static("", id="frontmatter_display"),
            ScrollableContainer(Static("", id="readme_content"), id="readme_scroll"),
            Static(
                "[dim]ESC/Q: close | P/N: prev/next README | Space: select | Arrows: scroll[/dim]",
                id="readme_footer",
            ),
            id="readme_container",
        )

    def on_mount(self) -> None:
        """Load and display the README content"""
        self._update_content()

    def _update_content(self) -> None:
        """Update the displayed content for current persona"""
        content_widget = self.query_one("#readme_content", Static)
        frontmatter_widget = self.query_one("#frontmatter_display", Static)

        # Update header with selection status
        self._update_header_with_selection()

        # Update frontmatter display
        frontmatter_text = self._format_frontmatter(self.persona)
        frontmatter_widget.update(frontmatter_text)

        # Update README content
        try:
            content_widget.update(self.persona.readme_content)
        except Exception as e:
            content_widget.update(f"Error loading README: {str(e)}")

        # Scroll to top when switching personas
        scroll_container = self.query_one("#readme_scroll", ScrollableContainer)
        scroll_container.scroll_home()

        # Update the background table selection to match current persona
        if self.app_instance:
            self.app_instance._update_background_selection(self.persona)

    def _format_frontmatter(self, persona: PersonaConfig) -> str:
        """Format persona frontmatter data for display"""
        if not persona.frontmatter_data:
            return "[dim]No frontmatter data available[/dim]"

        data = persona.frontmatter_data
        lines = []

        # Description (prominent)
        if data.get("description"):
            lines.append(f"[bold]{data['description']}[/bold]")
            lines.append("")

        # Core metadata in organized layout
        if data.get("llms"):
            llms_list = data["llms"] if isinstance(data["llms"], list) else [data["llms"]]
            lines.append(f"[dim]LLMs:[/dim] {', '.join(llms_list)}")

        if data.get("contact"):
            lines.append(f"[dim]Contact:[/dim] {data['contact']}")

        if data.get("project"):
            lines.append(f"[dim]Project:[/dim] {data['project']}")

        if data.get("category"):
            lines.append(f"[dim]Category:[/dim] {data['category']}")

        if data.get("short_name"):
            lines.append(f"[dim]Short Name:[/dim] {data['short_name']}")

        # Add inheritance info if present
        if persona.inherits_from:
            inheritance_list = []
            for inherit_path in persona.inherits_from:
                persona_name = inherit_path.split("/")[-2] if "/" in inherit_path else inherit_path
                inheritance_list.append(persona_name)
            lines.append(f"[dim]Inherits From:[/dim] {', '.join(inheritance_list)}")

        return "\n".join(lines) if lines else "[dim]No metadata available[/dim]"

    def action_prev_persona(self) -> None:
        """Navigate to previous persona's README (wraps to end)"""
        if self.current_index > 0:
            self.current_index -= 1
        else:
            # Wrap to last persona
            self.current_index = len(self.persona_list) - 1

        self.persona = self.persona_list[self.current_index]
        self._update_content()

    def action_next_persona(self) -> None:
        """Navigate to next persona's README (wraps to beginning)"""
        if self.current_index < len(self.persona_list) - 1:
            self.current_index += 1
        else:
            # Wrap to first persona
            self.current_index = 0

        self.persona = self.persona_list[self.current_index]
        self._update_content()

    def action_quit_app(self) -> None:
        """Quit the entire application from README viewer"""
        if self.app_instance:
            self.app_instance.exit()

    def action_toggle_selection(self) -> None:
        """Toggle selection of current persona in README viewer"""
        if self.app_instance:
            # Toggle selection in the main app
            file_path = str(self.persona._source_path)
            if file_path in self.app_instance.selected_personas:
                self.app_instance.selected_personas.remove(file_path)
            else:
                self.app_instance.selected_personas.add(file_path)

            # Update the background table to reflect the selection change (preserve cursor)
            current_persona = self.app_instance.selected_persona
            self.app_instance._setup_table()
            # Restore cursor position to match the selected persona
            if current_persona:
                self.app_instance._update_background_selection(current_persona)

            # Update the header to show selection status
            self._update_header_with_selection()

    def _update_header_with_selection(self) -> None:
        """Update header to show current persona and selection status"""
        header_widget = self.query_one("#readme_header", Static)
        persona_counter = f"({self.current_index + 1} of {len(self.persona_list)})"

        # Add selection indicator
        selection_indicator = ""
        if self.app_instance and str(self.persona._source_path) in self.app_instance.selected_personas:
            selection_indicator = " ✅"

        header_widget.update(f"[bold]{self.persona.name}[/bold]{selection_indicator} - README {persona_counter}")


class PersonaBrowserApp(App):
    """Main TUI application for browsing personas"""

    CSS = """
    #personas_table {
        height: 1fr;
        min-height: 10;
    }
    
    #search_input {
        margin: 1;
    }
    
    #details_panel {
        width: 40%;
        border: solid $primary;
        padding: 1;
        min-width: 30;
    }
    
    ExtractionScreen {
        align: center middle;
    }
    
    #extraction_dialog {
        width: 70;
        height: 15;
        border: solid $primary;
        background: $surface;
        padding: 1;
        margin: 2;
    }
    
    #extraction_dialog Button {
        margin: 1;
        min-width: 12;
        height: 3;
    }
    
    #extraction_dialog Horizontal {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    
    #extraction_dialog Label {
        margin-bottom: 1;
    }
    
    #extraction_dialog Input {
        margin-bottom: 1;
    }
    
    .title {
        text-style: bold;
        margin-bottom: 1;
    }
    
    #status {
        margin-top: 1;
        text-wrap: wrap;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("f5", "refresh", "Refresh", show=True),
        Binding("ctrl+e", "extract", "Multi-Extract", show=True),
        Binding("ctrl+f", "search", "Search", show=True),
        Binding("d", "toggle_details", "Details", show=True),
        Binding("w", "view_readme", "View README", show=True),
        Binding("a", "ai_attribution", "AI Attribution", show=True),
        Binding("f3", "toggle_smart_extraction", "Smart Extraction"),
        Binding("s", "cycle_sort", "Sort", show=True),
        Binding("r", "reverse_sort", "Reverse", show=True),
        Binding("space", "toggle_selection", "Select", show=True),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("escape", "focus_table", "Focus Table"),
    ]

    def __init__(
        self, development_mode: bool = False, directories: List[str] = None, attribution_files: List[str] = None
    ):
        super().__init__()
        if directories is None:
            directories = ["."]
        self.attribution_files = attribution_files or ["AI-ATTRIBUTION.md"]
        self.scanner = PersonaScanner(directories)
        self.personas: List[PersonaConfig] = []
        self.filtered_personas: List[PersonaConfig] = []
        self.selected_persona: Optional[PersonaConfig] = None
        self.selected_personas: Set[str] = set()  # Track multi-selected persona file paths
        self.smart_extraction_enabled = True  # Smart extraction feature toggle
        self.details_visible = False  # Details panel visibility toggle
        self.development_mode = development_mode
        self.sort_field = "name"  # Current sort field: name, category, project
        self.sort_reverse = False  # Sort direction
        self.code_changed = False
        self.file_mtime = {}
        self.extraction_history = {}  # persona_name -> last_directory
        self.history_file = Path.home() / ".persona_browser_history.json"

        # Load persistent extraction history
        self._load_extraction_history()

        if self.development_mode:
            self._check_file_changes()
            # Add F6 code reload binding only in development mode
            self.bind("f6", "reload_code")

    def on_exit(self) -> None:
        """Save extraction history when app exits"""
        self._save_extraction_history()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Input(
                placeholder="Search or use category:dev, llm:claude... (Ctrl+F to focus)",
                id="search_input",
            ),
            Horizontal(
                DataTable(id="personas_table", zebra_stripes=True),
                Container(
                    Static("Select a persona to view details", id="details_content"),
                    Button(
                        "Extract Selected",
                        id="extract_btn",
                        disabled=True,
                        variant="primary",
                    ),
                    id="details_panel",
                ),
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application"""
        self._load_personas()
        self._setup_table()

        # Hide details panel initially
        details_panel = self.query_one("#details_panel")
        details_panel.display = False

        # Focus the table on startup
        table = self.query_one("#personas_table", DataTable)
        table.focus()

        # Start file watcher in development mode
        if self.development_mode:
            self.set_interval(1.0, self._check_file_changes)

        # Show initial status
        if not self.personas:
            details_content = self.query_one("#details_content", Static)
            details_content.update("No personas found. Add some README.md files in subdirectories!")

        # Update title with initial count
        self._update_title()

    def _load_personas(self) -> None:
        """Load all personas from the filesystem"""
        self.personas = self.scanner.scan_personas()
        self.filtered_personas = self.personas[:]
        self._sort_personas()
        self._update_title()

    def _setup_table(self) -> None:
        """Setup the personas data table"""
        table = self.query_one("#personas_table", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Category", "Project", "Source", "LLMs", "SE", "D", "Description")
        table.cursor_type = "row"  # Enable row selection

        for persona in self.filtered_personas:
            llms_str = ", ".join(persona.llms[:2]) if persona.llms else "N/A"
            if len(persona.llms) > 2:
                llms_str += f" (+{len(persona.llms) - 2})"

            desc = persona.description[:80] + "..." if len(persona.description) > 80 else persona.description

            # Add file type, selection and inheritance indicators to name
            name_display = persona.name

            # Add file type marker
            if persona.file_type == "README":
                name_display = "⭐ " + name_display
            elif persona.file_type == "CLAUDE":
                name_display = "📘 " + name_display
            elif persona.file_type == "CONTEXT":
                name_display = "📋 " + name_display
            elif persona.file_type == "AI_INSTRUCTION":
                name_display = "🤖 " + name_display

            # Add selection indicator
            if str(persona._source_path) in self.selected_personas:
                name_display = "✅ " + name_display

            # Add inheritance indicator
            if persona.inherits_from:
                name_display += " 🔗"

            # Create source display from path
            path_parts = persona._source_path.parts[-3:-1]  # Last 2 dirs before file
            source_display = "/".join(path_parts) if len(path_parts) > 0 else persona._source_path.parent.name

            table.add_row(
                name_display,
                persona.category or "General",
                persona.project or "N/A",
                source_display,
                llms_str,
                str(persona.smart_file_count),
                str(persona.directory_file_count),
                desc or "No description",
                key=str(persona._source_path),
            )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        if event.input.id == "search_input":
            self._filter_personas(event.value)

    def _filter_personas(self, search_term: str) -> None:
        """Filter personas based on search term with support for category: and llm: filters"""
        if not search_term:
            self.filtered_personas = self.personas[:]
        else:
            term = search_term.lower()

            # Parse multiple filters and regular search terms
            category_filters = []
            llm_filters = []
            not_category_filters = []
            not_llm_filters = []
            regular_terms = []
            not_regular_terms = []

            # Split by spaces and process each part
            parts = term.split()
            for part in parts:
                if part.startswith("!category:"):
                    not_category_filters.append(part[10:].strip())
                elif part.startswith("!llm:"):
                    not_llm_filters.append(part[5:].strip())
                elif part.startswith("category:"):
                    category_filters.append(part[9:].strip())
                elif part.startswith("llm:"):
                    llm_filters.append(part[4:].strip())
                elif part.startswith("!"):
                    not_regular_terms.append(part[1:].strip())
                else:
                    regular_terms.append(part)

            # Filter personas based on all criteria
            self.filtered_personas = []
            for persona in self.personas:
                matches = True

                # Check category filters (all must match)
                for cat_filter in category_filters:
                    if cat_filter and cat_filter not in persona.category.lower():
                        matches = False
                        break

                # Check negated category filters (all must NOT match)
                if matches:
                    for not_cat_filter in not_category_filters:
                        if not_cat_filter and not_cat_filter in persona.category.lower():
                            matches = False
                            break

                # Check LLM filters (all must match)
                if matches:
                    for llm_filter in llm_filters:
                        if llm_filter and not any(llm_filter in llm.lower() for llm in persona.llms):
                            matches = False
                            break

                # Check negated LLM filters (all must NOT match)
                if matches:
                    for not_llm_filter in not_llm_filters:
                        if not_llm_filter and any(not_llm_filter in llm.lower() for llm in persona.llms):
                            matches = False
                            break

                # Check regular search terms (all must match somewhere in the persona)
                if matches:
                    for regular_term in regular_terms:
                        if regular_term and not (
                            regular_term in persona.name.lower()
                            or regular_term in persona.description.lower()
                            or regular_term in persona.project.lower()
                            or regular_term in persona.contact.lower()
                            or regular_term in persona.category.lower()
                            or any(regular_term in llm.lower() for llm in persona.llms)
                        ):
                            matches = False
                            break

                # Check negated regular search terms (all must NOT match anywhere in the persona)
                if matches:
                    for not_regular_term in not_regular_terms:
                        if not_regular_term and (
                            not_regular_term in persona.name.lower()
                            or not_regular_term in persona.description.lower()
                            or not_regular_term in persona.project.lower()
                            or not_regular_term in persona.contact.lower()
                            or not_regular_term in persona.category.lower()
                            or any(not_regular_term in llm.lower() for llm in persona.llms)
                        ):
                            matches = False
                            break

                if matches:
                    self.filtered_personas.append(persona)

        # Apply sorting
        self._sort_personas()

        # Refresh table
        self._setup_table()
        self._update_title()

    def _sort_personas(self) -> None:
        """Sort filtered personas based on current sort field and direction"""
        if self.sort_field == "name":
            self.filtered_personas.sort(key=lambda p: p.name.lower(), reverse=self.sort_reverse)
        elif self.sort_field == "category":
            self.filtered_personas.sort(
                key=lambda p: (p.category.lower(), p.name.lower()),
                reverse=self.sort_reverse,
            )
        elif self.sort_field == "project":
            self.filtered_personas.sort(
                key=lambda p: ((p.project or "").lower(), p.name.lower()),
                reverse=self.sort_reverse,
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle persona selection - Enter key triggers extraction"""
        if event.row_key is None:
            return

        file_path = event.row_key.value
        clicked_persona = next((p for p in self.filtered_personas if str(p._source_path) == file_path), None)

        if clicked_persona:
            # Extract the selected persona
            def on_extraction_complete(result):
                if result == "success":
                    self._set_status_message(f"✅ Extracted {clicked_persona.name} successfully!")

            self.push_screen(
                SimpleExtractionScreen(
                    clicked_persona,
                    self,
                    smart_extraction=self.smart_extraction_enabled,
                ),
                on_extraction_complete,
            )

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """Handle row highlighting (cursor movement) - always show highlighted persona"""
        if event.row_key is None:
            return

        # Always show the highlighted persona in details
        file_path = event.row_key.value
        highlighted_persona = next((p for p in self.filtered_personas if str(p._source_path) == file_path), None)

        if highlighted_persona:
            self.selected_persona = highlighted_persona
            self._update_details_panel()

    def _update_details_panel(self) -> None:
        """Update the details panel with selected persona info"""
        if not self.selected_persona or not self.details_visible:
            return

        p = self.selected_persona
        llms_text = ", ".join(p.llms) if p.llms else "Not specified"

        # Format inheritance information
        inheritance_text = ""
        if p.inherits_from:
            inheritance_list = []
            for inherit_path in p.inherits_from:
                # Extract persona name from path
                persona_name = inherit_path.split("/")[-2] if "/" in inherit_path else inherit_path
                inheritance_list.append(persona_name)
            inheritance_text = f"\n[dim]Inherits From:[/dim] {', '.join(inheritance_list)}"

        # Generate file list based on current extraction mode
        if self.smart_extraction_enabled:
            current_files = p.smart_files or []
            mode_name = "Smart Extraction"
            file_count = p.smart_file_count
        else:
            current_files = p.directory_files or []
            mode_name = "Directory Mode"
            file_count = p.directory_file_count

        # Create relative file paths for display
        file_list_text = ""
        if current_files:
            # Show first few files, truncate if more
            display_files = current_files[:MAX_FILES_DISPLAY]
            file_paths = []
            for file_path in display_files:
                try:
                    # Show path relative to persona directory
                    rel_path = file_path.relative_to(p.path)
                    file_paths.append(f"  • {rel_path}")
                except ValueError:
                    # For inherited files, show full relative path from current directory
                    try:
                        rel_path = file_path.relative_to(Path.cwd())
                        file_paths.append(f"  • {rel_path} [dim](inherited)[/dim]")
                    except ValueError:
                        file_paths.append(f"  • {file_path.name}")

            file_list_text = "\n" + "\n".join(file_paths)
            if len(current_files) > MAX_FILES_DISPLAY:
                file_list_text += f"\n  [dim]... and {len(current_files) - MAX_FILES_DISPLAY} more files[/dim]"

        details = f"""[bold]{p.name}[/bold]

[dim]Category:[/dim] {p.category or 'General'}
[dim]Project:[/dim] {p.project or 'Not specified'}
[dim]Contact:[/dim] {p.contact or 'Not specified'}
[dim]LLMs:[/dim] {llms_text}
[dim]Path:[/dim] {p.path}
[dim]Main Persona File:[/dim] {p._source_path.name if hasattr(p, '_source_path') else 'Not found'}{inheritance_text}

[dim]File Counts:[/dim]
[dim]  Smart Extraction (SE):[/dim] {p.smart_file_count} files
[dim]  Directory Mode (D):[/dim] {p.directory_file_count} files

[dim]Files for {mode_name} ({file_count} total):[/dim]{file_list_text}

[dim]Description:[/dim]
{p.description or 'No description provided'}

[dim]README Preview:[/dim]
{p.readme_content[:PREVIEW_LENGTH]}{'...' if len(p.readme_content) > PREVIEW_LENGTH else ''}
"""

        details_content = self.query_one("#details_content", Static)
        details_content.update(details)

        extract_btn = self.query_one("#extract_btn", Button)
        extract_btn.disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "extract_btn" and self.selected_persona:

            def on_extraction_complete(result):
                if result == "success":
                    self._set_status_message(f"✅ Extracted {self.selected_persona.name} successfully!")

            self.push_screen(
                SimpleExtractionScreen(
                    self.selected_persona,
                    self,
                    smart_extraction=self.smart_extraction_enabled,
                ),
                on_extraction_complete,
            )

    def action_refresh(self) -> None:
        """Refresh personas list"""
        old_count = len(self.personas)
        self._load_personas()
        self._filter_personas("")
        search_input = self.query_one("#search_input", Input)
        search_input.value = ""

        # Show refresh feedback
        new_count = len(self.personas)
        if new_count != old_count:
            self._set_status_message(f"📁 Refreshed! Found {new_count} personas ({new_count - old_count:+d})")
        else:
            self._set_status_message(f"📁 Refreshed! {new_count} personas found")

    def action_extract(self) -> None:
        """Extract selected personas"""
        if not self.selected_personas:
            self._set_status_message("❌ No personas selected. Use Space to select personas.")
            return

        # Get the actual persona objects for selected file paths
        personas_to_extract = [p for p in self.filtered_personas if str(p._source_path) in self.selected_personas]

        if not personas_to_extract:
            self._set_status_message("❌ Selected personas not found.")
            return

        def on_extraction_complete(result):
            if result == "success":
                count = len(personas_to_extract)
                names = ", ".join([p.name for p in personas_to_extract])
                self._set_status_message(f"✅ Extracted {count} personas: {names}")

        self.push_screen(
            SimpleExtractionScreen(
                personas_to_extract,
                self,
                smart_extraction=self.smart_extraction_enabled,
            ),
            on_extraction_complete,
        )

    def action_search(self) -> None:
        """Focus search input"""
        search_input = self.query_one("#search_input", Input)
        search_input.focus()

    def action_select_persona(self) -> None:
        """Extract the highlighted persona (single extraction)"""
        table = self.query_one("#personas_table", DataTable)
        if table.cursor_row is not None and self.filtered_personas:
            row_index = table.cursor_row
            if 0 <= row_index < len(self.filtered_personas):
                highlighted_persona = self.filtered_personas[row_index]
                personas_to_extract = [highlighted_persona]

                def on_extraction_complete(result):
                    if result == "success":
                        self._set_status_message(f"✅ Extracted {highlighted_persona.name} successfully!")

                self.push_screen(
                    SimpleExtractionScreen(
                        personas_to_extract,
                        self,
                        smart_extraction=self.smart_extraction_enabled,
                    ),
                    on_extraction_complete,
                )

    def action_focus_table(self) -> None:
        """Focus the personas table (escape from search) or hide details if shown"""
        table = self.query_one("#personas_table", DataTable)

        # If details panel is visible, hide it with ESC
        if self.details_visible:
            self.details_visible = False
            details_panel = self.query_one("#details_panel")
            details_panel.display = False
            self._set_status_message("📋 Details panel hidden (D to show)")
            return

        # Otherwise just focus the table (escape from search)
        table.focus()

    def action_toggle_smart_extraction(self) -> None:
        """Toggle smart extraction feature"""
        self.smart_extraction_enabled = not self.smart_extraction_enabled
        status = "ON" if self.smart_extraction_enabled else "OFF"

        mode_desc = "Smart (dependencies only)" if self.smart_extraction_enabled else "Full directory"
        self._set_status_message(f"🔧 Extraction mode: {mode_desc} (F3 to toggle)")

        # Update details panel to show files for new mode
        if self.details_visible and self.selected_persona:
            self._update_details_panel()

    def action_toggle_details(self) -> None:
        """Toggle details panel visibility"""
        self.details_visible = not self.details_visible
        details_panel = self.query_one("#details_panel")

        if self.details_visible:
            details_panel.display = True
            # Update details if we have a selected persona
            if self.selected_persona:
                self._update_details_panel()
            self._set_status_message("📋 Details panel shown (D to toggle)")
        else:
            details_panel.display = False
            self._set_status_message("📋 Details panel hidden (D to toggle)")

    def action_view_readme(self) -> None:
        """View full README content for selected persona"""
        if not self.selected_persona:
            self._set_status_message("⚠️ No persona selected - select a persona first")
            return

        # Find the index of the selected persona in the filtered list
        try:
            current_index = next(
                i for i, p in enumerate(self.filtered_personas) if p.name == self.selected_persona.name
            )
        except StopIteration:
            current_index = 0

        def on_readme_close(result):
            # Focus back on table when README viewer closes
            table = self.query_one("#personas_table", DataTable)
            table.focus()

        self.push_screen(
            ReadmeViewerScreen(self.selected_persona, self.filtered_personas, current_index, self),
            on_readme_close,
        )

    def action_ai_attribution(self) -> None:
        """Open AI Attribution configuration modal"""

        def on_attribution_close(result):
            # Focus back on table when attribution modal closes
            table = self.query_one("#personas_table", DataTable)
            table.focus()

            # Show status message based on result
            if result == "saved":
                self._set_status_message("✅ AI Attribution configuration saved")
            elif result == "cancelled":
                self._set_status_message("🚫 AI Attribution configuration cancelled")

        self.push_screen(AIAttributionScreen(attribution_files=self.attribution_files), on_attribution_close)

    def _update_background_selection(self, persona: PersonaConfig) -> None:
        """Update table selection to match persona being viewed in README modal"""
        try:
            table = self.query_one("#personas_table", DataTable)
            # Find the row with this persona and move cursor to it
            for i, row_persona in enumerate(self.filtered_personas):
                if row_persona.name == persona.name:
                    table.move_cursor(row=i)
                    # Update selected persona state
                    self.selected_persona = persona
                    # Update details panel if visible
                    if self.details_visible:
                        self._update_details_panel()
                    break
        except Exception:
            # Silently fail if table access fails
            pass

    def action_cycle_sort(self) -> None:
        """Cycle through sort fields: name -> category -> project"""
        sort_fields = ["name", "category", "project"]

        if self.sort_field in sort_fields:
            current_index = sort_fields.index(self.sort_field)
            self.sort_field = sort_fields[(current_index + 1) % len(sort_fields)]
        else:
            self.sort_field = "name"

        # Re-apply filter and sort
        search_input = self.query_one("#search_input", Input)
        self._filter_personas(search_input.value)

        direction = "↓" if self.sort_reverse else "↑"
        self._set_status_message(f"📊 Sorted by {self.sort_field} {direction} (S to cycle, R to reverse)")

    def action_reverse_sort(self) -> None:
        """Reverse the current sort direction"""
        self.sort_reverse = not self.sort_reverse

        # Re-apply filter and sort
        search_input = self.query_one("#search_input", Input)
        self._filter_personas(search_input.value)

        direction = "↓" if self.sort_reverse else "↑"
        self._set_status_message(f"📊 Sorted by {self.sort_field} {direction} (S to cycle, R to reverse)")

    def action_toggle_selection(self) -> None:
        """Toggle selection of currently highlighted persona"""
        table = self.query_one("#personas_table", DataTable)

        if table.cursor_row is None or not self.filtered_personas:
            return

        if table.cursor_row >= len(self.filtered_personas):
            return

        # Get the highlighted persona
        highlighted_persona = self.filtered_personas[table.cursor_row]
        file_path = str(highlighted_persona._source_path)

        # Toggle selection
        if file_path in self.selected_personas:
            self.selected_personas.remove(file_path)
            self._set_status_message(f"❌ Deselected {highlighted_persona.name}")
        else:
            self.selected_personas.add(file_path)
            self._set_status_message(f"✅ Selected {highlighted_persona.name}")

        # Update extract button state
        extract_btn = self.query_one("#extract_btn", Button)
        extract_btn.disabled = len(self.selected_personas) == 0

        # Refresh table to show selection indicators while preserving cursor position
        current_cursor = table.cursor_row
        self._setup_table()
        if current_cursor is not None and current_cursor < len(self.filtered_personas):
            table.move_cursor(row=current_cursor)

    def _check_file_changes(self) -> None:
        """Check if source files have been modified"""
        current_file = Path(__file__)
        try:
            current_mtime = current_file.stat().st_mtime

            if current_file not in self.file_mtime:
                self.file_mtime[current_file] = current_mtime
                return

            if current_mtime > self.file_mtime[current_file]:
                self.file_mtime[current_file] = current_mtime
                if not self.code_changed:
                    self.code_changed = True
                    self._update_footer_notification()
        except Exception:
            pass  # Ignore file access errors

    def _update_footer_notification(self) -> None:
        """Update footer to show reload notification"""
        if self.code_changed and self.development_mode:
            self.sub_title = "Code Changes Detected - F6 to reload"
        else:
            self.sub_title = ""

    def action_reload_code(self) -> None:
        """Reload the application code"""
        if not self.development_mode:
            self._set_status_message("Reload only available in development mode", duration=2.0)
            return

        try:
            # Save current state
            current_search = ""
            current_selected = None

            try:
                search_input = self.query_one("#search_input", Input)
                current_search = search_input.value
            except:
                pass

            if self.selected_persona:
                current_selected = self.selected_persona.name

            # Reload modules
            module_name = __name__
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])

            # Restart the app with preserved state
            self.code_changed = False
            self._update_footer_notification()

            # Quick visual feedback
            self._set_status_message("Code reloaded! 🔄", duration=2.0)

        except Exception as e:
            self._set_status_message(f"Reload failed: {str(e)}")

    def _clear_subtitle_to_default(self) -> None:
        """Clear subtitle back to default state"""
        if self.development_mode and self.code_changed:
            self._update_footer_notification()
        else:
            self.sub_title = ""

    def _set_status_message(self, message: str, duration: float = 3.0) -> None:
        """Set a status message with automatic dismissal, replacing any existing timer"""
        # Textual timers can't be cancelled, but we can track if we should ignore old timers
        # by incrementing a counter and checking it in the callback
        if not hasattr(self, "_status_timer_id"):
            self._status_timer_id = 0

        self._status_timer_id += 1
        current_timer_id = self._status_timer_id

        # Set the new message
        self.sub_title = message

        # Set new timer with ID checking
        def clear_if_current():
            if hasattr(self, "_status_timer_id") and self._status_timer_id == current_timer_id:
                self._clear_subtitle_to_default()

        self.set_timer(duration, clear_if_current)

    def _update_title(self) -> None:
        """Update the application title with persona count"""
        total_count = len(self.personas)
        filtered_count = len(self.filtered_personas)

        if filtered_count == total_count:
            self.title = f"AI Persona Card Catalog ({total_count} personas)"
        else:
            self.title = f"AI Persona Card Catalog ({filtered_count}/{total_count} personas)"

    def _load_extraction_history(self) -> None:
        """Load extraction history from persistent storage"""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.extraction_history = json.load(f)
        except Exception:
            # If loading fails, start with empty history
            self.extraction_history = {}

    def _save_extraction_history(self) -> None:
        """Save extraction history to persistent storage"""
        try:
            # Ensure the parent directory exists
            self.history_file.parent.mkdir(parents=True, exist_ok=True)

            # Create a temporary file first, then rename for atomic write
            temp_file = self.history_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.extraction_history, f, indent=2)

            # Atomic rename to prevent corruption
            temp_file.replace(self.history_file)
        except Exception:
            # Silently ignore save errors to prevent disrupting the UX
            pass


def main():
    parser = argparse.ArgumentParser(description="Persona Browser TUI")
    parser.add_argument(
        "--development",
        action="store_true",
        help="Enable development mode with hot-reload functionality",
    )
    parser.add_argument(
        "--directory",
        "-d",
        action="append",
        help="Directory to scan for persona configurations (can be used multiple times, default: current directory)",
    )
    parser.add_argument(
        "--attribution-file",
        "-a",
        action="append",
        help="Path to AI attribution configuration file(s) (can be used multiple times, default: AI-ATTRIBUTION.md)",
    )
    args = parser.parse_args()

    # Default to current directory if no directories specified
    directories = args.directory if args.directory else ["."]

    # Default attribution files if not specified
    attribution_files = args.attribution_file if args.attribution_file else ["AI-ATTRIBUTION.md"]

    app = PersonaBrowserApp(
        development_mode=args.development, directories=directories, attribution_files=attribution_files
    )
    try:
        app.run()
    except Exception:
        # Save history even if app crashes
        app._save_extraction_history()
        raise


if __name__ == "__main__":
    main()
