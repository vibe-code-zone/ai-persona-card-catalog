"""
Clean AI Attribution Modal - Simple Selection Only

Provides a simple dropdown to select from available attribution standards.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import json
from pathlib import Path
from typing import List, Optional, Tuple

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Select, Static


class AIAttributionScreen(ModalScreen[str]):
    """Simple modal for selecting AI attribution standard"""

    CSS = """
    AIAttributionScreen {
        align: center middle;
    }
    
    #attribution_container {
        width: 90;
        height: 40;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #standard_select {
        width: 100%;
        margin: 1 0;
    }
    
    #selected_preview {
        height: 20;
        border: solid $secondary;
        padding: 1;
        margin: 1 0;
        background: $panel;
        scrollbar-gutter: stable;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    def __init__(self, attribution_files: List[str] = None):
        super().__init__()
        self.attribution_files = attribution_files or ["AI-ATTRIBUTION.md"]
        self.available_standards: List[Tuple[str, str]] = []
        self.selected_standard = ""
        self.cache_file = Path.home() / ".ai_attribution_cache.json"
        self.load_standards()
        self.load_cached_selection()

    def load_standards(self):
        """Load attribution standards from all attribution files"""
        self.available_standards = []

        for file_path in self.attribution_files:
            path = Path(file_path)
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    standards = self._parse_standards(content)
                    self.available_standards.extend(standards)
                except Exception:
                    continue

        # Remove duplicates while preserving order
        seen = set()
        unique_standards = []
        for std_id, std_name in self.available_standards:
            if std_id not in seen:
                seen.add(std_id)
                unique_standards.append((std_id, std_name))
        self.available_standards = unique_standards

    def _parse_standards(self, content: str) -> List[Tuple[str, str]]:
        """Parse attribution standards from file content"""
        standards = []
        lines = content.split("\n")

        for line in lines:
            if line.startswith("### ") and "Standard" in line:
                # Extract standard name like "### AIA Standard" -> ("aia", "AIA Standard")
                name = line[4:].strip()  # Remove "### "
                if name:
                    std_id = name.lower().replace(" standard", "").replace(" ", "_")
                    standards.append((std_id, name))
        return standards

    def load_cached_selection(self):
        """Load cached selection if available and valid"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                cached_standard = cache_data.get("selected_standard", "")
                # Only use if it exists in available standards
                if cached_standard and any(std[0] == cached_standard for std in self.available_standards):
                    self.selected_standard = cached_standard
        except Exception:
            pass

    def save_cached_selection(self):
        """Save current selection to cache"""
        try:
            cache_data = {"selected_standard": self.selected_standard}
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(cache_data, f)
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        """Create the attribution selection modal with preview"""
        with Container(id="attribution_container"):
            yield Static("🤖 AI Attribution Standard")

            if not self.available_standards:
                yield Static("⚠️ No attribution standards found!")
                yield Static(f"Looking for files: {', '.join(self.attribution_files)}")
                yield Static("Extractions will proceed without attribution.")
            else:
                yield Static("Select attribution standard for extractions:")
                yield Select(
                    options=self.available_standards,
                    allow_blank=True,
                    prompt="Choose standard...",
                    id="standard_select",
                )

                # Preview area
                from textual.containers import ScrollableContainer

                with ScrollableContainer(id="selected_preview"):
                    yield Static(self._get_preview_text(), id="preview_text")

            with Horizontal():
                if self.available_standards:
                    yield Button("Apply", id="apply", variant="primary")
                yield Button("Close", id="close")

    def on_mount(self) -> None:
        """Set initial selection after mounting"""
        if not self.available_standards:
            return

        try:
            # Use a timer to set selection after widget is fully ready
            self.set_timer(0.1, self._set_initial_selection)
        except Exception:
            pass

    def _set_initial_selection(self) -> None:
        """Set the initial selection from cache"""
        try:
            if self.selected_standard and self.available_standards:
                # Find the display name for this ID
                display_name = None
                for std_id, std_name in self.available_standards:
                    if std_id == self.selected_standard:
                        display_name = std_name
                        break

                if display_name:
                    select_widget = self.query_one("#standard_select", Select)
                    select_widget.value = display_name
                    # Also update the preview immediately
                    self._update_preview()
        except Exception:
            pass

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle selection change"""
        if event.select.id == "standard_select":
            # Convert display name back to ID
            display_name = event.value or ""
            # Find the ID for this display name
            for std_id, std_name in self.available_standards:
                if std_name == display_name:
                    self.selected_standard = std_id
                    break
            else:
                self.selected_standard = ""

            self._update_preview()

    def _update_preview(self) -> None:
        """Update the preview text"""
        try:
            preview_widget = self.query_one("#preview_text", Static)
            preview_widget.update(self._get_preview_text())
        except Exception:
            pass

    def _get_preview_text(self) -> str:
        """Get preview text for selected standard"""
        if not self.selected_standard:
            return "Select a standard above to see preview..."

        # Load guidance for selected standard
        guidance = self._load_attribution_guidance(self.selected_standard)

        if not guidance:
            return f"No guidance found for '{self.selected_standard}'"

        # Show selected standard and preview
        standard_name = next(
            (name for id, name in self.available_standards if id == self.selected_standard), self.selected_standard
        )

        return f"""Selected: {standard_name}

Preview of guidance that will be appended to context files:

{guidance[:400]}{'...' if len(guidance) > 400 else ''}"""

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
                if line.startswith("### ") and standard.lower() in line.lower():
                    in_standard = True
                    continue
                elif line.startswith("### ") and in_standard:
                    # Hit next standard, stop
                    break
                elif in_standard:
                    guidance_lines.append(line)

            return "\n".join(guidance_lines).strip()

        except Exception:
            return ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "apply":
            if self.selected_standard:
                self.save_cached_selection()
                self.dismiss("saved")
            else:
                self.dismiss("no_selection")
        elif event.button.id == "close":
            self.dismiss("cancelled")
