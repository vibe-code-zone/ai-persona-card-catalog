<!-- Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions -->

# Usage Examples

## Configuration
Examples based on [config.yaml](./config.yaml) settings

## Code Style Examples
Following guidelines from [style_guide.md](./style_guide.md):

```python
def calculate_average(numbers: list[float]) -> float:
    """Calculate the arithmetic mean of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

## Testing Examples  
Using patterns from [templates/testing_template.md](./templates/testing_template.md):

```python
def test_calculate_average_returns_correct_result():
    # Arrange
    numbers = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected = 3.0
    
    # Act
    result = calculate_average(numbers)
    
    # Assert
    assert result == expected
```

## Best Practices
All examples follow the standards defined in [style_guide.md](./style_guide.md)