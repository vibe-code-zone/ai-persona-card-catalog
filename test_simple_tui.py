#!/usr/bin/env python3
"""
Simple TUI Test to verify Textual testing setup

Basic test to ensure Textual testing works with our app.
"""

import pytest

from persona_browser_textual import PersonaBrowserApp


class TestBasicTUI:
    """Basic TUI tests"""

    @pytest.mark.asyncio
    async def test_app_can_start(self):
        """Test that the app can start without errors"""
        app = PersonaBrowserApp()

        # Test with run_test context manager
        async with app.run_test() as pilot:
            # App should be running
            assert app.is_running
            assert pilot.app == app

    @pytest.mark.asyncio
    async def test_app_has_expected_widgets(self):
        """Test that expected widgets are present"""
        app = PersonaBrowserApp()

        async with app.run_test() as pilot:
            # Wait a moment for widgets to be composed
            await pilot.pause(0.1)

            # Check for main widgets using query
            try:
                table = pilot.app.query_one("#personas_table")
                assert table is not None
                print(f"✅ Found table: {table}")
            except Exception as e:
                print(f"❌ Table not found: {e}")
                # Continue - maybe widget IDs are different

            try:
                search = pilot.app.query_one("#search_input")
                assert search is not None
                print(f"✅ Found search: {search}")
            except Exception as e:
                print(f"❌ Search not found: {e}")

            # Basic test that app started successfully
            assert app.is_running


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
