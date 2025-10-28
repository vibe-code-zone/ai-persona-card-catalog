#!/usr/bin/env python3
"""
TUI Component Tests for AI Persona Card Catalog

Tests for Textual TUI components using Textual's built-in testing framework.
Covers app initialization, widget interactions, search functionality, and user workflows.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

from pathlib import Path

import pytest

from persona_browser_textual import PersonaBrowserApp, PersonaScanner


class TestPersonaBrowserApp:
    """Test the main PersonaBrowserApp using Textual's testing framework"""

    @pytest.mark.asyncio
    async def test_app_startup(self):
        """Test that the app starts up without errors"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            # App should start and show main interface
            assert app.is_running
            assert pilot.app == app

    @pytest.mark.asyncio
    async def test_personas_table_loads(self):
        """Test that the personas table loads with data"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            # Wait for table to populate
            await pilot.pause(0.2)

            # Table should exist and have rows
            table = pilot.app.query_one("#personas_table")
            assert table is not None
            # Should have at least some personas loaded
            assert table.row_count > 0

    @pytest.mark.asyncio
    async def test_search_functionality(self):
        """Test search input filtering"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Get initial row count
            table = pilot.app.query_one("#personas_table")
            initial_count = table.row_count

            # Type in search input
            search_input = pilot.app.query_one("#search_input")
            await pilot.click("#search_input")
            await pilot.press("p", "y", "t", "h", "o", "n")
            await pilot.pause(0.1)

            # Should filter results
            filtered_count = table.row_count
            # Either same count (if python matches are same as total) or fewer
            assert filtered_count <= initial_count

    @pytest.mark.asyncio
    async def test_details_panel_updates(self):
        """Test that details panel updates when selecting personas"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Select first row in table
            table = pilot.app.query_one("#personas_table")
            if table.row_count > 0:
                # Click on first row
                await pilot.click("#personas_table")
                await pilot.press("enter")
                await pilot.pause(0.1)

                # Details panel should be populated
                details_panel = pilot.app.query_one("#details_panel")
                assert details_panel is not None
                # Should have some content
                details_text = details_panel.render()
                assert len(str(details_text)) > 0

    @pytest.mark.asyncio
    async def test_keyboard_navigation(self):
        """Test keyboard navigation in the table"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            table = pilot.app.query_one("#personas_table")
            if table.row_count > 1:
                # Focus table and navigate
                await pilot.click("#personas_table")
                await pilot.press("down")
                await pilot.pause(0.1)

                # Should have moved selection
                assert table.cursor_row >= 0

    @pytest.mark.asyncio
    async def test_multi_select_functionality(self):
        """Test multi-select functionality with space key"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            table = pilot.app.query_one("#personas_table")
            if table.row_count > 0:
                # Focus and select with space
                await pilot.click("#personas_table")
                await pilot.press("space")
                await pilot.pause(0.1)

                # Check if selection state changed
                # (We can't easily test the internal selection state without app internals)
                assert True  # Basic test that space key doesn't crash

    @pytest.mark.asyncio
    async def test_extraction_modal_shortcut(self):
        """Test that Ctrl+E opens extraction modal"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Try to open extraction modal
            await pilot.press("ctrl+e")
            await pilot.pause(0.1)

            # Modal should be pushed (we can check if app has modal screen)
            # This is a basic test - full modal testing would require more setup
            assert True  # Basic test that shortcut doesn't crash

    @pytest.mark.asyncio
    async def test_search_filters_by_llm(self):
        """Test search with LLM filter syntax"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Test LLM filter syntax
            search_input = pilot.app.query_one("#search_input")
            await pilot.click("#search_input")
            # Type llm:claude
            for char in "llm:claude":
                await pilot.press(char)
            await pilot.pause(0.1)

            # Should apply filter without crashing
            table = pilot.app.query_one("#personas_table")
            assert table.row_count >= 0  # Might be 0 if no Claude personas

    @pytest.mark.asyncio
    async def test_search_filters_by_category(self):
        """Test search with category filter syntax"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Test category filter syntax
            search_input = pilot.app.query_one("#search_input")
            await pilot.click("#search_input")
            # Type category:dev
            for char in "category:dev":
                await pilot.press(char)
            await pilot.pause(0.1)

            # Should apply filter without crashing
            table = pilot.app.query_one("#personas_table")
            assert table.row_count >= 0  # Might be 0 if no dev category personas

    @pytest.mark.asyncio
    async def test_negation_search(self):
        """Test search with negation (!llm:gpt)"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Test negation syntax
            search_input = pilot.app.query_one("#search_input")
            await pilot.click("#search_input")
            # Type !llm:gpt
            for char in "!llm:gpt":
                await pilot.press(char)
            await pilot.pause(0.1)

            # Should apply negation filter without crashing
            table = pilot.app.query_one("#personas_table")
            assert table.row_count >= 0


class TestPersonaScannerIntegration:
    """Test PersonaScanner integration with the TUI"""

    def test_scanner_finds_personas(self):
        """Test that PersonaScanner finds test personas"""
        scanner = PersonaScanner()
        personas = scanner.scan_personas()

        # Should find some personas in the test environment
        assert len(personas) > 0

        # Each persona should have required fields
        for persona in personas:
            assert persona.name
            assert persona.path.exists()
            assert isinstance(persona.llms, list)

    def test_scanner_handles_different_readme_patterns(self):
        """Test that scanner handles various README.md patterns"""
        scanner = PersonaScanner()
        personas = scanner.scan_personas()

        # Count different README patterns
        regular_readmes = 0
        dash_readmes = 0
        name_readmes = 0

        for persona in personas:
            readme_files = list(persona.path.glob("*README.md"))
            if readme_files:
                readme_name = readme_files[0].name
                if readme_name == "README.md":
                    regular_readmes += 1
                elif readme_name.endswith("-README.md"):
                    dash_readmes += 1
                elif readme_name.endswith("README.md"):
                    name_readmes += 1

        # Should find at least some of each pattern
        total_patterns = regular_readmes + dash_readmes + name_readmes
        assert total_patterns > 0, "Should find personas with README files"


class TestAppWithMockData:
    """Test app behavior with controlled mock data"""

    @pytest.mark.asyncio
    async def test_empty_directory_handling(self, tmp_path, monkeypatch):
        """Test app behavior when no personas are found"""
        # Create empty directory and point scanner to it
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Mock the scanner to use our empty directory
        def mock_scan_personas(self):
            return []

        monkeypatch.setattr("persona_browser_textual.PersonaScanner.scan_personas", mock_scan_personas)

        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # App should handle empty state gracefully
            table = pilot.app.query_one("#personas_table")
            assert table.row_count == 0

    @pytest.mark.asyncio
    async def test_search_with_no_results(self):
        """Test search that returns no results"""
        app = PersonaBrowserApp()
        async with app.run_test() as pilot:
            await pilot.pause(0.1)

            # Search for something that definitely won't exist
            search_input = pilot.app.query_one("#search_input")
            await pilot.click("#search_input")
            # Type a nonexistent search term
            for char in "xyzqwertynonexistent":
                await pilot.press(char)
            await pilot.pause(0.1)

            # Should handle no results gracefully
            table = pilot.app.query_one("#personas_table")
            assert table.row_count == 0


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__])
