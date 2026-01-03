# UI - AI-BOS Design System

**Standard UI components for Lynx AI Dashboard**

---

## 📦 Installed Package

**@aibos/design-system** v1.1.0

This is the standard UI design system for AI-BOS NexusCanon projects.

---

## 🚀 Usage

### Import Components

```typescript
import { ComponentName } from '@aibos/design-system';
```

### Example

```typescript
import { Button, Card, StatusBadge } from '@aibos/design-system';

function Dashboard() {
  return (
    <Card>
      <StatusBadge status="operational" />
      <Button onClick={handleClick}>Refresh</Button>
    </Card>
  );
}
```

---

## 📁 Project Structure

```
ui/
├── package.json          # npm dependencies
├── node_modules/         # Installed packages
│   └── @aibos/
│       └── design-system/  # Standard UI components
└── README.md            # This file
```

---

## 🔧 Next Steps

1. **Review Design System Components:**
   ```bash
   cd lynx-ai/ui
   ls node_modules/@aibos/design-system
   ```

2. **Check Documentation:**
   - Look for README.md in the package
   - Check for TypeScript definitions
   - Review component examples

3. **Integrate with Dashboard:**
   - Update `lynx-ai/lynx/api/dashboard.py` to use design system
   - Or create a separate frontend app using the components

---

## 📝 Notes

- Design system is installed as npm package
- Components can be used in React, Vue, or other frameworks
- Check package documentation for framework-specific usage

---

**Last Updated:** 2026-01-27

