"""
Persona Inheritance Resolution System

Handles persona inheritance through markdown links, resolving dependencies between
personas and ensuring complete extraction of inherited configurations. Provides
cycle detection and hierarchical persona management.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


@dataclass
class PersonaReference:
    """Represents a reference to another persona"""

    name: str
    path: Path
    relative_path: str


class PersonaInheritanceResolver:
    """Resolves persona inheritance chains and detects cycles"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.visited: Set[str] = set()
        self.visiting: Set[str] = set()

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

    def resolve_inheritance(self, persona_path: Path) -> List[Path]:
        """
        Resolve all inherited personas for a given persona.
        Returns list of all personas that should be included (including the original).
        """
        self.visited.clear()
        self.visiting.clear()

        all_personas = []
        # Ensure we start with an absolute path
        absolute_persona_path = persona_path.resolve()
        self._resolve_recursive(absolute_persona_path, all_personas)

        # Remove duplicates while preserving order
        seen = set()
        unique_personas = []
        for persona in all_personas:
            persona_str = str(persona)
            if persona_str not in seen:
                seen.add(persona_str)
                unique_personas.append(persona)

        return unique_personas

    def _resolve_recursive(self, persona_path: Path, all_personas: List[Path]) -> None:
        """Recursively resolve inheritance, detecting cycles"""
        persona_str = str(persona_path.resolve())

        # Check for cycles
        if persona_str in self.visiting:
            print(f"Warning: Circular inheritance detected involving {persona_path}")
            return

        if persona_str in self.visited:
            return

        self.visiting.add(persona_str)

        try:
            # Find persona file in the directory
            persona_file = self._find_persona_file(persona_path)
            if not persona_file:
                return
            inherits_from = self._extract_inheritance(persona_file)

            # First, resolve all inherited personas
            for inherit_path in inherits_from:
                inherited_persona_path = self._resolve_path(inherit_path, persona_path)
                if inherited_persona_path and inherited_persona_path.exists():
                    self._resolve_recursive(inherited_persona_path, all_personas)

            # Then add this persona
            all_personas.append(persona_path)

        except Exception as e:
            print(f"Warning: Error processing {persona_path}: {e}")
        finally:
            self.visiting.remove(persona_str)
            self.visited.add(persona_str)

    def _extract_inheritance(self, readme_file: Path) -> List[str]:
        """Extract inherits_from list from persona README"""
        try:
            with open(readme_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for YAML frontmatter
            if not content.startswith("---"):
                return []

            # Split frontmatter from content
            parts = content.split("---", 2)
            if len(parts) < 3:
                return []

            frontmatter = parts[1].strip()
            metadata = yaml.safe_load(frontmatter)

            if metadata and "inherits_from" in metadata:
                inherits_from = metadata["inherits_from"]
                if isinstance(inherits_from, list):
                    return inherits_from
                elif isinstance(inherits_from, str):
                    return [inherits_from]

            return []

        except Exception:
            return []

    def _resolve_path(self, inherit_path: str, current_persona_path: Path) -> Optional[Path]:
        """Resolve relative inheritance path to absolute path"""
        if inherit_path.startswith("../"):
            # Relative to current persona
            resolved = (current_persona_path / inherit_path).resolve()
        else:
            # Relative to base experiments directory
            resolved = (self.base_path / inherit_path).resolve()

        # Get the directory containing the README
        if resolved.name.endswith(".md"):
            return resolved.parent
        else:
            return resolved

    def get_inheritance_tree(self, persona_path: Path) -> Dict[str, List[str]]:
        """Get a tree representation of inheritance relationships"""
        all_personas = self.resolve_inheritance(persona_path)
        tree = {}

        for persona in all_personas:
            persona_name = persona.name
            persona_file = self._find_persona_file(persona)
            if persona_file:
                inherits_from = self._extract_inheritance(persona_file)
                tree[persona_name] = [self._get_persona_name_from_path(p, persona) for p in inherits_from]

        return tree

    def _get_persona_name_from_path(self, inherit_path: str, current_persona_path: Path) -> str:
        """Extract persona name from inheritance path"""
        resolved = self._resolve_path(inherit_path, current_persona_path)
        if resolved:
            return resolved.name
        return inherit_path.split("/")[-2] if "/" in inherit_path else inherit_path
