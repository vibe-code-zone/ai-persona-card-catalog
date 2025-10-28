#!/usr/bin/env python3
"""
File Dependency Resolution System

Intelligent resolver that analyzes persona files for dependencies (markdown links,
file references) and recursively follows them with cycle detection. Ensures complete
extraction of all related files when extracting persona configurations.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import yaml


@dataclass
class FileReference:
    """Represents a file reference found during parsing"""

    source_file: Path
    referenced_file: Path
    reference_type: str  # 'markdown_link', 'relative_path', 'yaml_ref', etc.
    line_number: Optional[int] = None


class FileDependencyResolver:
    """Resolves file dependencies with cycle detection"""

    def __init__(self, base_path: Path):
        self.base_path = base_path.resolve()
        self.visited: Set[Path] = set()  # Files we've completely processed
        self.visiting: Set[Path] = set()  # Files currently in traversal stack
        self.dependencies: Dict[Path, List[FileReference]] = {}  # Cache of parsed dependencies

    def resolve_dependencies(self, start_file: Path) -> Set[Path]:
        """
        Resolve all file dependencies starting from a file.
        Returns set of all files that should be copied.
        """
        start_file = start_file.resolve()
        all_files = set()

        self._resolve_recursive(start_file, all_files)

        # Always include the starting file
        all_files.add(start_file)

        return all_files

    def _resolve_recursive(self, current_file: Path, collected_files: Set[Path]) -> None:
        """Recursively resolve dependencies with cycle detection"""
        current_file = current_file.resolve()

        # Cycle detection
        if current_file in self.visiting:
            # We've detected a cycle, but that's okay - just don't follow it
            return

        # Skip if already fully processed
        if current_file in self.visited:
            return

        # Skip if file doesn't exist or is outside base path
        if not current_file.exists() or not self._is_within_base_path(current_file):
            return

        # Mark as currently visiting (for cycle detection)
        self.visiting.add(current_file)

        try:
            # Parse file for references
            references = self._parse_file_references(current_file)
            self.dependencies[current_file] = references

            # Add current file to collection
            collected_files.add(current_file)

            # Recursively process referenced files
            for ref in references:
                self._resolve_recursive(ref.referenced_file, collected_files)

        finally:
            # Remove from visiting stack and mark as visited
            self.visiting.discard(current_file)
            self.visited.add(current_file)

    def _is_within_base_path(self, file_path: Path) -> bool:
        """Check if file is within the persona's base directory"""
        try:
            file_path.resolve().relative_to(self.base_path)
            return True
        except ValueError:
            return False

    def _parse_file_references(self, file_path: Path) -> List[FileReference]:
        """Parse a file and extract all file references"""
        references = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return references

        # Try different parsing strategies based on file type
        if file_path.suffix.lower() in [".md", ".markdown"]:
            references.extend(self._parse_markdown_references(file_path, content))
        elif file_path.suffix.lower() in [".yml", ".yaml"]:
            references.extend(self._parse_yaml_references(file_path, content))
        elif file_path.suffix.lower() == ".json":
            references.extend(self._parse_json_references(file_path, content))

        # Always check for generic file path patterns
        references.extend(self._parse_generic_path_references(file_path, content))

        return references

    def _parse_markdown_references(self, source_file: Path, content: str) -> List[FileReference]:
        """Parse markdown links and image references"""
        references = []

        # Markdown links: [text](path) and ![alt](path)
        link_pattern = r"!?\[([^\]]*)\]\(([^\)]+)\)"

        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_path = match.group(2)

            # Skip URLs (http, https, mailto, etc.)
            if "://" in link_path or link_path.startswith("mailto:"):
                continue

            # Resolve relative to source file's directory
            referenced_file = self._resolve_relative_path(source_file, link_path)
            if referenced_file:
                references.append(
                    FileReference(
                        source_file=source_file,
                        referenced_file=referenced_file,
                        reference_type="markdown_link",
                        line_number=content[: match.start()].count("\n") + 1,
                    )
                )

        return references

    def _parse_yaml_references(self, source_file: Path, content: str) -> List[FileReference]:
        """Parse YAML file references like $ref, include, extends"""
        references = []

        try:
            data = yaml.safe_load(content)
            self._extract_yaml_paths(source_file, data, references)
        except Exception:
            pass

        return references

    def _extract_yaml_paths(
        self,
        source_file: Path,
        data,
        references: List[FileReference],
        path_prefix: str = "",
    ) -> None:
        """Recursively extract file paths from YAML data"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key

                # Check for common reference keys
                if key in [
                    "$ref",
                    "include",
                    "extends",
                    "template",
                    "import",
                    "source",
                    "file",
                ]:
                    if isinstance(value, str) and not value.startswith(("http://", "https://")):
                        referenced_file = self._resolve_relative_path(source_file, value)
                        if referenced_file:
                            references.append(
                                FileReference(
                                    source_file=source_file,
                                    referenced_file=referenced_file,
                                    reference_type=f"yaml_{key}",
                                )
                            )
                else:
                    self._extract_yaml_paths(source_file, value, references, current_path)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                self._extract_yaml_paths(source_file, item, references, f"{path_prefix}[{i}]")

    def _parse_json_references(self, source_file: Path, content: str) -> List[FileReference]:
        """Parse JSON file references"""
        references = []

        try:
            data = json.loads(content)
            self._extract_json_paths(source_file, data, references)
        except Exception:
            pass

        return references

    def _extract_json_paths(self, source_file: Path, data, references: List[FileReference]) -> None:
        """Recursively extract file paths from JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                # Check for common reference keys
                if key in [
                    "$ref",
                    "include",
                    "extends",
                    "template",
                    "import",
                    "source",
                    "file",
                ]:
                    if isinstance(value, str) and not value.startswith(("http://", "https://")):
                        referenced_file = self._resolve_relative_path(source_file, value)
                        if referenced_file:
                            references.append(
                                FileReference(
                                    source_file=source_file,
                                    referenced_file=referenced_file,
                                    reference_type=f"json_{key}",
                                )
                            )
                else:
                    self._extract_json_paths(source_file, value, references)

        elif isinstance(data, list):
            for item in data:
                self._extract_json_paths(source_file, item, references)

    def _parse_generic_path_references(self, source_file: Path, content: str) -> List[FileReference]:
        """Parse generic file path patterns in any text file"""
        references = []

        # Look for relative path patterns like ./file, ../file, subdir/file
        path_pattern = r'(?:^|\s|["\'\`])(\.{0,2}/[^\s"\'\`<>|?*:]+(?:\.[a-zA-Z0-9]+)?)(?=\s|["\'\`]|$)'

        for match in re.finditer(path_pattern, content, re.MULTILINE):
            path_str = match.group(1)

            # Skip obvious non-file patterns
            if any(skip in path_str.lower() for skip in ["http", "https", "ftp", "://"]):
                continue

            referenced_file = self._resolve_relative_path(source_file, path_str)
            if referenced_file and referenced_file.exists():
                references.append(
                    FileReference(
                        source_file=source_file,
                        referenced_file=referenced_file,
                        reference_type="generic_path",
                        line_number=content[: match.start()].count("\n") + 1,
                    )
                )

        return references

    def _resolve_relative_path(self, source_file: Path, relative_path: str) -> Optional[Path]:
        """Resolve a relative path from a source file"""
        try:
            # Clean up the path
            relative_path = relative_path.strip().strip("\"\\'`")

            # Resolve relative to source file's directory
            resolved = (source_file.parent / relative_path).resolve()

            # Must be within base path and exist
            if self._is_within_base_path(resolved):
                return resolved

        except Exception:
            pass

        return None

    def get_dependency_tree(self) -> Dict[Path, List[FileReference]]:
        """Get the full dependency tree that was discovered"""
        return self.dependencies.copy()

    def print_dependency_tree(self) -> None:
        """Print a human-readable dependency tree"""
        for source_file, references in self.dependencies.items():
            rel_source = source_file.relative_to(self.base_path)
            print(f"📄 {rel_source}")

            for ref in references:
                try:
                    rel_ref = ref.referenced_file.relative_to(self.base_path)
                    print(f"  └─ {ref.reference_type}: {rel_ref}")
                except ValueError:
                    print(f"  └─ {ref.reference_type}: {ref.referenced_file}")
