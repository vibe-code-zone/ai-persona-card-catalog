<!-- Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions -->

# Testing Template

## Test Structure
Based on configurations in [../config.yaml](../config.yaml)

## pytest Best Practices
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Use fixtures for common setup

## Code Style
Tests should follow the same style guide: [../style_guide.md](../style_guide.md)

## Example Test Structure
```python
def test_function_should_return_expected_result():
    # Arrange
    input_data = "test"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == "expected"
```

## More Examples
See complete testing examples in [../usage_examples.md](../usage_examples.md)