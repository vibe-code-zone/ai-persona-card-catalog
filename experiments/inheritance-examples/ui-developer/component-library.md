<!-- Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions -->

# Component Library Guidelines

## Reusable Components

### Button Component
```jsx
export const Button = ({ variant, size, children, ...props }) => {
  return (
    <button 
      className={`btn btn-${variant} btn-${size}`}
      {...props}
    >
      {children}
    </button>
  );
};
```

### Input Component
```jsx
export const Input = ({ label, error, ...props }) => {
  return (
    <div className="input-group">
      <label>{label}</label>
      <input {...props} />
      {error && <span className="error">{error}</span>}
    </div>
  );
};
```

## Design Tokens
- Primary: #007bff
- Secondary: #6c757d
- Success: #28a745
- Danger: #dc3545