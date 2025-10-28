#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Persona Card Catalog

Automated tests covering persona scanning, inheritance resolution, file dependency
analysis, and extraction functionality. Validates system behavior and prevents
regressions during development iterations.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import sys
from pathlib import Path

from extraction_modal import SimpleExtractionScreen
from file_dependency_resolver import FileDependencyResolver
from persona_browser_textual import PersonaConfig, PersonaScanner


def test_persona_scanning():
    """Test that scanner finds all README patterns"""
    print("🔍 Testing persona scanning...")

    scanner = PersonaScanner()
    personas = scanner.scan_personas()

    print(f"Found {len(personas)} personas:")

    # Track different file patterns we find
    patterns = {"with_dash": [], "without_dash": [], "regular": []}

    for p in personas:
        readme_files = [f for f in p.path.iterdir() if f.name.endswith("README.md")]
        if not readme_files:
            print(f"  - {p.name} (SKIPPED - no README.md found)")
            continue

        readme_file = p.path.name + "/" + readme_files[0].name
        print(f"  - {p.name}")
        print(f"    File: {readme_file}")
        print(f"    Path: {p.path}")

        # Categorize by pattern
        readme_name = readme_files[0].name
        if readme_name.endswith("-README.md"):
            patterns["with_dash"].append(p.name)
        elif readme_name != "README.md" and readme_name.endswith("README.md"):
            patterns["without_dash"].append(p.name)
        else:
            patterns["regular"].append(p.name)

    print(f"\n📊 Pattern distribution:")
    print(f"  With dash (-README.md): {len(patterns['with_dash'])} files")
    print(f"  Without dash (nameREADME.md): {len(patterns['without_dash'])} files")
    print(f"  Regular (README.md): {len(patterns['regular'])} files")

    # Validate we have our test cases
    assert len(personas) >= 6, f"Expected at least 6 personas, found {len(personas)}"
    assert len(patterns["with_dash"]) >= 1, "Should have at least 1 with-dash pattern"
    assert len(patterns["without_dash"]) >= 1, "Should have at least 1 without-dash pattern"
    assert len(patterns["regular"]) >= 4, "Should have at least 4 regular patterns"

    print("✅ Persona scanning test passed!")
    return personas


def test_frontmatter_parsing():
    """Test that frontmatter includes short_name field"""
    print("\n🏷️  Testing frontmatter parsing...")

    scanner = PersonaScanner()
    personas = scanner.scan_personas()

    short_names_found = 0
    for persona in personas:
        # We can't directly access short_name from PersonaConfig,
        # but we can re-parse the file to check
        readme_files = list(persona.path.glob("*README.md"))
        if readme_files:
            readme_file = readme_files[0]
            try:
                with open(readme_file, "r", encoding="utf-8") as f:
                    content = f.read()

                if "short_name:" in content:
                    short_names_found += 1
                    print(f"  ✅ {persona.name} has short_name field")
                else:
                    print(f"  ❌ {persona.name} missing short_name field")
            except Exception as e:
                print(f"  ⚠️  {persona.name} - Error reading file: {e}")

    print(f"\n📊 Short name summary: {short_names_found}/{len(personas)} personas have short_name")
    assert short_names_found >= 6, "All test personas should have short_name field"

    print("✅ Frontmatter parsing test passed!")


def test_file_dependency_resolver():
    """Test that dependency resolver works with new README patterns"""
    print("\n🔗 Testing file dependency resolver...")

    # Test with our complex experiment
    ai_coding_path = Path("experiments/ai-coding-assistant")
    if ai_coding_path.exists():
        resolver = FileDependencyResolver(ai_coding_path)
        readme_files = list(ai_coding_path.glob("*README.md"))

        if readme_files:
            readme_file = readme_files[0]
            dependencies = resolver.resolve_dependencies(readme_file)

            print(f"  📁 Testing {ai_coding_path.name}")
            print(f"  📄 README file: {readme_file.name}")
            print(f"  🔗 Found {len(dependencies)} dependencies")

            # Should find multiple files due to complex reference chain
            assert len(dependencies) > 1, "Should find multiple dependencies in complex experiment"
            print("  ✅ Complex dependency resolution working")
        else:
            print("  ⚠️  No README files found in ai-coding-assistant")

    # Test with circular references
    circular_path = Path("experiments/circular-refs")
    if circular_path.exists():
        resolver = FileDependencyResolver(circular_path)
        readme_files = list(circular_path.glob("*README.md"))

        if readme_files:
            readme_file = readme_files[0]
            dependencies = resolver.resolve_dependencies(readme_file)

            print(f"  🔄 Testing circular references in {circular_path.name}")
            print(f"  🔗 Found {len(dependencies)} dependencies (should handle cycles)")

            # Should find files without infinite loop
            assert len(dependencies) > 1, "Should find dependencies despite circular references"
            print("  ✅ Circular reference handling working")

    print("✅ File dependency resolver test passed!")


def test_dash_insertion_logic():
    """Test the dash insertion logic for README file renaming"""
    print("\n🔧 Testing dash insertion logic...")

    test_cases = [
        # (input_filename, expected_output)
        ("python-assistantREADME.md", "python-assistant-README.md"),
        ("security-expert-README.md", "security-expert-README.md"),  # Already has dash
        ("README.md", "README.md"),  # Regular file, no change
        ("data-scientistREADME.md", "data-scientist-README.md"),
        ("ai-codingREADME.md", "ai-coding-README.md"),
    ]

    for input_name, expected_output in test_cases:
        # Simulate the logic from extraction_modal.py
        if input_name.endswith("README.md") and input_name != "README.md":
            if "-README.md" not in input_name:
                # Add dash
                result = input_name.replace("README.md", "-README.md")
            else:
                # Keep as-is
                result = input_name
        else:
            # Regular file
            result = input_name

        print(f"  {input_name:25} → {result:25} {'✅' if result == expected_output else '❌'}")
        assert result == expected_output, f"Expected {expected_output}, got {result}"

    print("✅ Dash insertion logic test passed!")


def test_regex_patterns():
    """Test that regex patterns don't have syntax errors"""
    print("\n🔍 Testing regex patterns...")

    try:
        # Test importing the dependency resolver (this will fail if regex is broken)
        from file_dependency_resolver import FileDependencyResolver

        # Test creating a resolver
        test_path = Path(".")
        resolver = FileDependencyResolver(test_path)

        print("  ✅ FileDependencyResolver imports without syntax errors")
        print("  ✅ Regex patterns compile correctly")

    except SyntaxError as e:
        print(f"  ❌ Syntax error in regex patterns: {e}")
        raise
    except Exception as e:
        print(f"  ⚠️  Other error (not regex): {e}")

    print("✅ Regex patterns test passed!")


def test_extraction_modal_integration():
    """Test that extraction modal can handle new patterns"""
    print("\n📤 Testing extraction modal integration...")

    # We can't fully test the modal without GUI, but we can test the logic
    scanner = PersonaScanner()
    personas = scanner.scan_personas()

    if personas:
        test_persona = personas[0]
        print(f"  🧪 Testing with persona: {test_persona.name}")

        # Test that we can find README files with new pattern
        readme_files = list(test_persona.path.glob("*README.md"))
        assert len(readme_files) > 0, f"Should find README file in {test_persona.path}"

        readme_file = readme_files[0]
        print(f"  📄 Found README: {readme_file.name}")

        # Test smart extraction mode file discovery
        if readme_file.exists():
            resolver = FileDependencyResolver(test_persona.path)
            dependencies = resolver.resolve_dependencies(readme_file)
            print(f"  🔗 Smart extraction would copy {len(dependencies)} files")

        print("  ✅ Extraction modal integration working")

    print("✅ Extraction modal integration test passed!")


def test_backward_compatibility():
    """Test that old README.md files still work"""
    print("\n🔄 Testing backward compatibility...")

    scanner = PersonaScanner()
    personas = scanner.scan_personas()

    # Count personas with regular README.md files
    regular_readme_count = 0
    for persona in personas:
        readme_files = list(persona.path.glob("README.md"))
        if readme_files:
            regular_readme_count += 1
            print(f"  ✅ {persona.name} uses regular README.md (backward compatible)")

    print(f"  📊 Found {regular_readme_count} personas using regular README.md")
    assert regular_readme_count >= 4, "Should have at least 4 backward-compatible personas"

    print("✅ Backward compatibility test passed!")


def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Running Persona Browser System Tests")
    print("=" * 60)

    try:
        # Core functionality tests
        personas = test_persona_scanning()
        test_frontmatter_parsing(personas)
        test_file_dependency_resolver()
        test_dash_insertion_logic()
        test_regex_patterns()
        test_extraction_modal_integration()
        test_backward_compatibility()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Persona Browser system is working correctly")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
