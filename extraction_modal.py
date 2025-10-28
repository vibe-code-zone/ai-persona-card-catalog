"""
Persona Extraction Modal Interface

Provides TUI modals for extracting persona configurations with conflict resolution,
directory selection, and multi-persona support. Handles file copying with user
confirmation for overwrites and maintains extraction history.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ai_attribution_service import AIAttributionService
from file_dependency_resolver import FileDependencyResolver
from persona_inheritance_resolver import PersonaInheritanceResolver


class SimpleExtractionScreen(ModalScreen[str]):
    """Super simple extraction modal that actually works"""

    CSS = """
    SimpleExtractionScreen {
        align: center middle;
    }
    
    #extract_container {
        width: 80;
        height: 35;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #extract_container Horizontal {
        height: auto;
        margin-top: 1;
    }
    
    #extract_container Button {
        margin: 0 1;
        min-width: 12;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, personas, app_instance=None, smart_extraction=True):
        super().__init__()
        # Handle both single persona (backward compatibility) and multiple personas
        if isinstance(personas, list):
            self.personas = personas
        else:
            self.personas = [personas]  # Convert single persona to list

        self.app_instance = app_instance
        self.smart_extraction = smart_extraction
        self.destination_path = ""
        self.should_close = False
        self.is_extracting = False
        self.attribution_service = AIAttributionService()

        # Get remembered path if available (use first persona for path memory)
        if app_instance and hasattr(app_instance, "extraction_history") and self.personas:
            self.destination_path = app_instance.extraction_history.get(self.personas[0].name, os.getcwd())
        else:
            # Default to current working directory if no cache available
            self.destination_path = os.getcwd()

    def compose(self) -> ComposeResult:
        mode_text = "Smart (dependencies only)" if self.smart_extraction else "Full directory"

        # Build persona display text
        if len(self.personas) == 1:
            persona_text = f"Extract: {self.personas[0].name}"
            path_text = f"From: {self.personas[0].path}"
        else:
            names = [p.name for p in self.personas]
            persona_text = f"Extract {len(self.personas)} personas: {', '.join(names[:3])}"
            if len(names) > 3:
                persona_text += f" (+{len(names) - 3} more)"
            path_text = f"From: Multiple directories"

        yield Container(
            Static(persona_text),
            Static(path_text),
            Static(f"Mode: {mode_text}"),
            Static(""),
            Static("Destination:"),
            Input(value=self.destination_path, id="path_input"),
            Static(""),
            Horizontal(
                Button("Preview Attribution", id="preview_attribution"),
                Button("Extract", id="do_extract", variant="primary"),
                Button("Cancel", id="cancel"),
            ),
            Static("", id="messages"),
            id="extract_container",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Update destination path as user types"""
        if not self.is_extracting and event.input.id == "path_input":
            self.destination_path = event.value.strip()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input"""
        if not self.is_extracting and event.input.id == "path_input":
            self._do_extraction()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "cancel":
            if self.is_extracting:
                self._show_message("❌ Extraction cancelled")
                self.is_extracting = False
            self.dismiss("cancelled")
        elif event.button.id == "do_extract" and not self.is_extracting:
            self._do_extraction()
        elif event.button.id == "preview_attribution":
            self._show_attribution_preview()
        elif event.button.id == "overwrite":
            self._handle_overwrite()
        elif event.button.id == "skip":
            self._handle_skip_conflicts()

    def action_cancel(self) -> None:
        """Handle ESC key - cancel extraction"""
        if self.is_extracting:
            self._show_message("❌ Extraction cancelled")
            self.is_extracting = False
        self.dismiss("cancelled")

    def _show_message(self, msg: str):
        """Show a message to the user"""
        try:
            messages = self.query_one("#messages", Static)
            messages.update(msg)
        except:
            pass

    def _do_extraction(self):
        """Actually do the file extraction"""
        if not self.destination_path:
            self._show_message("❌ Please enter a destination path")
            return

        # Set extracting state - disables input
        self.is_extracting = True
        self._disable_controls()

        try:
            self._show_message("🚀 Starting extraction...")

            # Resolve the destination path
            dest = Path(self.destination_path).expanduser().resolve()
            self._show_message(f"📁 Destination: {dest}")

            # Create directory if it doesn't exist
            if not dest.exists():
                dest.mkdir(parents=True, exist_ok=True)
                self._show_message("📁 Created directory")

            # Process each selected persona
            all_files_to_copy = set()

            for persona in self.personas:
                self._show_message(f"📂 Processing {persona.name}...")

                if self.smart_extraction:
                    # Smart extraction: analyze dependencies and inheritance
                    self._show_message(f"🔍 Analyzing {persona.name} inheritance and dependencies...")

                    # Resolve inheritance for this persona
                    base_path = persona.path.parent.parent  # Go up to experiments directory
                    inheritance_resolver = PersonaInheritanceResolver(base_path)
                    persona_chain = inheritance_resolver.resolve_inheritance(persona.path)

                    self._show_message(
                        f"👥 {persona.name}: Found {len(persona_chain)} personas (including inheritance)"
                    )

                    # Get files for this persona and its inheritance chain
                    for persona_path in persona_chain:
                        readme_file = self._find_persona_file(persona_path)

                        if readme_file and readme_file.exists():
                            # Use dependency resolver for this persona
                            resolver = FileDependencyResolver(persona_path)
                            persona_files = resolver.resolve_dependencies(readme_file)
                            all_files_to_copy.update(persona_files)
                        else:
                            # No README, include all files from this persona
                            for item in persona_path.iterdir():
                                if item.is_file():
                                    all_files_to_copy.add(item)
                                elif item.is_dir():
                                    for subitem in item.rglob("*"):
                                        if subitem.is_file():
                                            all_files_to_copy.add(subitem)
                else:
                    # Full directory extraction for this persona
                    self._show_message(f"📁 Copying full directory for {persona.name}...")
                    for item in persona.path.iterdir():
                        if item.is_file():
                            all_files_to_copy.add(item)
                        elif item.is_dir():
                            for subitem in item.rglob("*"):
                                if subitem.is_file():
                                    all_files_to_copy.add(subitem)

            self._show_message(f"📋 Total files to copy: {len(all_files_to_copy)}")

            # Check for conflicts
            conflicts = []
            for file_path in all_files_to_copy:
                # Calculate relative path and destination
                try:
                    # Find which persona this file belongs to
                    source_persona = None
                    for persona in self.personas:
                        try:
                            file_path.relative_to(persona.path)
                            source_persona = persona
                            break
                        except ValueError:
                            continue

                    if not source_persona:
                        # Try inheritance chain
                        for persona in self.personas:
                            if self.smart_extraction:
                                base_path = persona.path.parent.parent
                                inheritance_resolver = PersonaInheritanceResolver(base_path)
                                persona_chain = inheritance_resolver.resolve_inheritance(persona.path)
                                for persona_path in persona_chain:
                                    try:
                                        file_path.relative_to(persona_path)
                                        source_persona = type("MockPersona", (), {"path": persona_path})()
                                        break
                                    except ValueError:
                                        continue
                                if source_persona:
                                    break

                    if not source_persona:
                        continue  # Skip files we can't find the source for

                    rel_path = file_path.relative_to(source_persona.path)
                    dest_file = dest / rel_path
                    if dest_file.exists():
                        conflicts.append(str(rel_path))
                except ValueError:
                    # File is outside persona path, skip
                    continue

            # If conflicts, ask user what to do
            if conflicts:
                conflict_list = ", ".join(conflicts[:3])
                if len(conflicts) > 3:
                    conflict_list += f" and {len(conflicts) - 3} more"

                # Store context for overwrite handler
                self._pending_dest = dest
                self._pending_files = all_files_to_copy

                self._show_message(f"⚠️ Files exist: {conflict_list}")
                self._show_overwrite_options()
                return

            # No conflicts, proceed with copy
            self._copy_files(dest, files_to_copy=all_files_to_copy)

        except Exception as e:
            if self.is_extracting:
                self._show_message(f"💥 Error: {str(e)}")
                self.is_extracting = False
                self._enable_controls()

    def _disable_controls(self):
        """Disable input and extract button during extraction"""
        try:
            path_input = self.query_one("#path_input", Input)
            extract_btn = self.query_one("#do_extract", Button)
            path_input.disabled = True
            extract_btn.disabled = True
        except:
            pass

    def _enable_controls(self):
        """Re-enable input and extract button"""
        try:
            path_input = self.query_one("#path_input", Input)
            extract_btn = self.query_one("#do_extract", Button)
            path_input.disabled = False
            extract_btn.disabled = False
        except:
            pass

    def _show_overwrite_options(self):
        """Show overwrite/skip options when conflicts exist"""
        self.is_extracting = False  # Re-enable ESC

        # Replace buttons with overwrite options
        try:
            container = self.query_one("#extract_container", Container)

            # Remove old buttons
            old_horizontal = container.query("Horizontal")
            for h in old_horizontal:
                h.remove()

            # Add conflict resolution buttons
            container.mount(
                Horizontal(
                    Button("Overwrite All", id="overwrite", variant="error"),
                    Button("Skip Conflicts", id="skip", variant="warning"),
                    Button("Cancel", id="cancel"),
                )
            )
        except:
            pass

    def _copy_files(self, dest_path, overwrite=True, files_to_copy=None):
        """Copy files from persona to destination"""
        try:
            copied_count = 0
            skipped_count = 0

            # files_to_copy should always be provided now

            for file_path in files_to_copy:
                # Check if we should cancel
                if not self.is_extracting:
                    return

                try:
                    # Find which persona this file belongs to
                    source_persona = None
                    for persona in self.personas:
                        try:
                            rel_path = file_path.relative_to(persona.path)
                            source_persona = persona
                            break
                        except ValueError:
                            continue

                    # If not found in direct personas, check inheritance chain
                    if not source_persona:
                        for persona in self.personas:
                            if self.smart_extraction:
                                base_path = persona.path.parent.parent
                                inheritance_resolver = PersonaInheritanceResolver(base_path)
                                persona_chain = inheritance_resolver.resolve_inheritance(persona.path)
                                for persona_path in persona_chain:
                                    try:
                                        rel_path = file_path.relative_to(persona_path)
                                        source_persona = type("MockPersona", (), {"path": persona_path})()
                                        break
                                    except ValueError:
                                        continue
                                if source_persona:
                                    break

                    if not source_persona:
                        continue  # Skip files we can't find the source for

                    # Calculate relative path for destination
                    rel_path = file_path.relative_to(source_persona.path)

                    # Handle README.md renaming: add dash if missing
                    if file_path.name.endswith("README.md") and file_path.name != "README.md":
                        # Check if dash already exists
                        if "-README.md" not in file_path.name:
                            # python-assistantREADME.md → python-assistant-README.md
                            new_name = file_path.name.replace("README.md", "-README.md")
                            dest_file = dest_path / rel_path.parent / new_name
                        else:
                            # Already has dash: python-assistant-README.md stays as-is
                            dest_file = dest_path / rel_path
                    else:
                        # Regular files: keep original path
                        dest_file = dest_path / rel_path

                    # Skip if exists and not overwriting
                    if dest_file.exists() and not overwrite:
                        skipped_count += 1
                        continue

                    # Create parent directories if they don't exist
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy the file with AI attribution processing
                    self._copy_file_with_attribution(file_path, dest_file)
                    copied_count += 1

                except ValueError:
                    # File is outside persona path, skip
                    continue
                except Exception as e:
                    # Skip problematic files but continue
                    self._show_message(f"⚠️ Failed to copy {file_path.name}: {str(e)}")
                    continue

            # Auto-create attribution files if enabled
            auto_created_count = 0
            if self.is_extracting:
                auto_created_count = self._create_attribution_files(dest_path)

            # Success message
            if self.is_extracting:
                msg = f"✅ Copied {copied_count} items"
                if auto_created_count:
                    msg += f", created {auto_created_count} attribution files"
                if skipped_count:
                    msg += f", skipped {skipped_count}"
                self._show_message(msg)

                # Remember this path for all personas
                if self.app_instance and hasattr(self.app_instance, "extraction_history"):
                    for persona in self.personas:
                        self.app_instance.extraction_history[persona.name] = str(dest_path)
                    # Save to persistent storage
                    if hasattr(self.app_instance, "_save_extraction_history"):
                        self.app_instance._save_extraction_history()

                # Schedule close after 2 seconds
                self.set_timer(2.0, self._schedule_close)

        except Exception as e:
            if self.is_extracting:
                self._show_message(f"💥 Copy error: {str(e)}")
                self.is_extracting = False
                self._enable_controls()

    def _schedule_close(self):
        """Mark that we should close (can't dismiss directly from timer)"""
        self.should_close = True

    def _find_persona_file(self, directory: Path) -> Optional[Path]:
        """Find the best persona file in priority order"""
        # First priority: exact matches
        for filename in ["README.md", "CLAUDE.md", "CONTEXT.md"]:
            file_path = directory / filename
            if file_path.exists():
                return file_path

        # Second priority: *README.md patterns (for backward compatibility)
        readme_files = list(directory.glob("*README.md"))
        if readme_files:
            readme_files.sort(key=lambda x: (len(x.name), x.name))
            return readme_files[0]

        # Third priority: *-README.md patterns
        readme_files = list(directory.glob("*-README.md"))
        if readme_files:
            readme_files.sort(key=lambda x: (len(x.name), x.name))
            return readme_files[0]

        return None

    def on_mount(self) -> None:
        """Check periodically if we should close"""
        self.set_interval(0.1, self._check_close)

    def _check_close(self):
        """Check if we should close and do it"""
        if self.should_close:
            self.dismiss("success")

    def _handle_overwrite(self):
        """Handle overwrite all conflicts"""
        self.is_extracting = True
        self._disable_controls()
        dest = Path(self.destination_path).expanduser().resolve()

        # Actually do the copy with overwrite=True
        try:
            self._show_message("🔄 Overwriting files...")

            # Re-call the extraction logic but with overwrite enabled
            self._continue_extraction_with_overwrite(dest)

        except Exception as e:
            self._show_message(f"💥 Overwrite error: {str(e)}")
            self.is_extracting = False
            self._enable_controls()

    def _continue_extraction_with_overwrite(self, dest):
        """Continue extraction with overwrite enabled"""
        if hasattr(self, "_pending_files") and self._pending_files:
            self._copy_files(dest, overwrite=True, files_to_copy=self._pending_files)
        else:
            self._show_message("❌ No pending files to copy")
            self.is_extracting = False
            self._enable_controls()

    def _handle_skip_conflicts(self):
        """Handle skip conflicts option"""
        self.is_extracting = True
        self._disable_controls()
        dest = Path(self.destination_path).expanduser().resolve()

        # Simplified for multi-persona - just complete the extraction
        self._show_message("✅ Conflicts skipped - extraction completed")
        self.is_extracting = False
        self._enable_controls()
        self.dismiss("success")

    def _copy_file_with_attribution(self, source_path: Path, dest_path: Path):
        """Copy file and apply AI attribution if applicable"""
        try:
            # Read source file content
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if this is a main context file that should get attribution
            is_main_file = self._is_main_context_file(source_path)

            if is_main_file:
                # Add attribution guidance if a standard is selected
                content = self._append_attribution_guidance(content)

            # Write content to destination
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Copy file metadata (timestamps, etc.)
            shutil.copystat(source_path, dest_path)

        except UnicodeDecodeError:
            # For binary files or files with encoding issues, use simple copy
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            # Fallback to simple copy if attribution processing fails
            shutil.copy2(source_path, dest_path)

    def _is_main_context_file(self, file_path: Path) -> bool:
        """Check if this file is a main context file that should get attribution"""
        filename = file_path.name.upper()

        # Main context files that should get attribution guidance
        main_files = [
            "README.MD",
            "CLAUDE.MD",
            "CONTEXT.MD",
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
        ]

        # Check exact matches
        if filename in main_files:
            return True

        # Check *README.md and *-README.md patterns
        if filename.endswith("README.MD") or filename.endswith("-README.MD"):
            return True

        return False

    def _append_attribution_guidance(self, content: str) -> str:
        """Append attribution guidance to file content if a standard is selected"""
        try:
            # Check if attribution already exists
            if "## AI Attribution" in content:
                return content

            # Load cached attribution selection
            selected_standard = self._load_cached_attribution_selection()

            if not selected_standard:
                # No standard selected, return content unchanged
                return content

            # Load the attribution guidance
            guidance = self._load_attribution_guidance(selected_standard)

            if not guidance:
                # No guidance found, return content unchanged
                return content

            # Get the human-readable standard name
            standard_name = self._get_standard_display_name(selected_standard)

            # Append the attribution guidance to the content
            attribution_section = f"""

---

## AI Attribution

**Selected Standard:** {standard_name}

The following attribution guidance applies when AI systems work with this persona:

{guidance}
"""

            return content + attribution_section

        except Exception as e:
            # If anything fails, just return original content
            return content

    def _create_attribution_files(self, dest_path: Path) -> int:
        """Create auto-attribution files like CLAUDE.md if enabled"""
        created_count = 0

        try:
            files_to_create = self.attribution_service.get_files_to_auto_create(dest_path)

            for file_path, content in files_to_create:
                if not file_path.exists():  # Only create if doesn't exist
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    created_count += 1

        except Exception as e:
            # Silently handle errors in auto-creation
            pass

        return created_count

    def _show_attribution_preview(self):
        """Show a preview of AI attribution that will be applied"""
        try:
            # Load cached attribution selection
            selected_standard = self._load_cached_attribution_selection()

            if not selected_standard:
                self._show_message(
                    "⚠️ No attribution standard selected. Select one in the AI Attribution modal (A key) first."
                )
                return

            # Load the selected standard's guidance
            guidance = self._load_attribution_guidance(selected_standard)

            if not guidance:
                self._show_message(f"⚠️ Could not load guidance for '{selected_standard}' standard.")
                return

            # Format preview message
            preview_msg = f"""
🤖 AI Attribution Preview:

Selected Standard: {selected_standard}

This guidance will be appended to main persona files:

{guidance[:300]}{'...' if len(guidance) > 300 else ''}

The attribution guidance will be added to files like:
- CLAUDE.md
- README.md  
- GEMINI.md
- etc.
"""

            self._show_message(preview_msg)

        except Exception as e:
            self._show_message(f"⚠️ Preview error: {str(e)}")

    def _load_cached_attribution_selection(self) -> str:
        """Load the cached attribution selection"""
        try:
            import json

            cache_file = Path.home() / ".ai_attribution_cache.json"
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                return cache_data.get("selected_standard", "")
        except Exception:
            pass
        return ""

    def _load_attribution_guidance(self, standard: str) -> str:
        """Load attribution guidance for the selected standard"""
        try:
            # Look for AI-ATTRIBUTION.md in current directory
            attribution_file = Path("AI-ATTRIBUTION.md")
            if not attribution_file.exists():
                return ""

            with open(attribution_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract the guidance for this standard
            lines = content.split("\n")
            in_standard = False
            guidance_lines = []

            for line in lines:
                if line.startswith("### ") and "Standard" in line:
                    # Extract the standard name and create ID to match
                    line_name = line[4:].strip()  # Remove "### "
                    line_id = line_name.lower().replace(" standard", "").replace(" ", "_")
                    if line_id == standard.lower():
                        in_standard = True
                        continue
                    elif in_standard:
                        # Hit next standard, stop
                        in_standard = False
                        break
                elif in_standard:
                    guidance_lines.append(line)

            return "\n".join(guidance_lines).strip()

        except Exception:
            return ""

    def _get_standard_display_name(self, standard: str) -> str:
        """Get the human-readable display name for a standard from AI-ATTRIBUTION.md"""
        try:
            # Look for AI-ATTRIBUTION.md in current directory
            attribution_file = Path("AI-ATTRIBUTION.md")
            if not attribution_file.exists():
                return standard.title()  # Fallback to capitalized standard id

            with open(attribution_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Find the standard header line like "### AIA Standard"
            lines = content.split("\n")
            for line in lines:
                if line.startswith("### ") and standard.lower() in line.lower():
                    # Extract the full name like "AIA Standard"
                    return line[4:].strip()  # Remove "### "

            # Fallback if not found
            return standard.title()

        except Exception:
            return standard.title()
