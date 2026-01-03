# AI-BOS Design System Setup

**Date:** 2026-01-27  
**Status:** ✅ INSTALLED

---

## ✅ Installation Complete

**Package:** `@aibos/design-system` v1.1.0  
**Location:** `lynx-ai/ui/`  
**Repository:** https://github.com/pohlai88/AIBOS-DESIGN-SYSTEM

---

## 📦 What's Installed

### Design System Features

- ✅ **254 Design Tokens** - Colors, typography, spacing, shadows, motion
- ✅ **171 Semantic Classes** - Reusable `.na-*` component classes
- ✅ **React Components** - Button, Card, StatusIndicator
- ✅ **100% Figma Compliant** - Full alignment with design standards
- ✅ **Zero Framework Overhead** - Pure CSS/HTML implementation
- ✅ **TypeScript Support** - Full type definitions included

---

## 🚀 Usage

### Option 1: CSS Classes (Pure HTML)

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="node_modules/@aibos/design-system/style.css">
</head>
<body>
  <div class="na-card na-p-6">
    <h1 class="na-h1">Lynx AI Dashboard</h1>
    <button class="na-btn na-btn-primary">Refresh</button>
    <div class="na-status na-status-ok">Operational</div>
  </div>
</body>
</html>
```

### Option 2: React Components

```typescript
import { Button, Card, StatusIndicator } from '@aibos/design-system/react';
import '@aibos/design-system/css';

function Dashboard() {
  return (
    <Card>
      <StatusIndicator variant="operational" />
      <Button variant="primary" onClick={handleClick}>
        Refresh
      </Button>
    </Card>
  );
}
```

### Option 3: Design Tokens (TypeScript)

```typescript
import { tokens } from '@aibos/design-system/tokens';

const primaryColor = tokens.color.primary;
const spacing = tokens.spacing.md;
```

---

## 📋 Available Components

### React Components

1. **Button** (`@aibos/design-system/react`)
   - Variants: `primary`, `secondary`, `danger`
   - Full TypeScript support

2. **Card** (`@aibos/design-system/react`)
   - `CardHeader`, `CardBody`, `CardFooter`
   - Responsive and accessible

3. **StatusIndicator** (`@aibos/design-system/react`)
   - Variants: `operational`, `degraded`, `error`
   - Visual status badges

### CSS Classes

**Typography:**
- `.na-h1` - 32px bold (Page titles)
- `.na-h2` - 24px semibold (Section titles)
- `.na-h3` - 20px semibold (Subsections)
- `.na-h4` - 18px semibold (Card titles)
- `.na-data` - 14px monospace (Data values)
- `.na-data-large` - 30px serif (KPI values)
- `.na-metadata` - 11px uppercase (Labels)

**Components:**
- `.na-card` - Card container
- `.na-btn` - Button base
- `.na-btn-primary` - Primary button
- `.na-status` - Status indicator
- `.na-status-ok` - Operational status
- `.na-status-warning` - Warning status
- `.na-status-error` - Error status

**Spacing:**
- Use standard Tailwind classes: `p-4`, `p-6`, `p-8`
- Standard padding: `p-6` (24px)
- Standard gap: `gap-6` (24px)

---

## 📚 Documentation

### Package Documentation

Located in `node_modules/@aibos/design-system/docs/`:

1. **API_REFERENCE.md** - Complete API reference
2. **EXTERNAL_USAGE.md** - External usage guide
3. **INTEGRATION_GUIDE.md** - Integration instructions
4. **QUICK_REFERENCE.md** - Quick reference card

### Online Resources

- **Repository:** https://github.com/pohlai88/AIBOS-DESIGN-SYSTEM
- **Homepage:** https://github.com/pohlai88/AIBOS-DESIGN-SYSTEM#readme

---

## 🔧 Integration with Dashboard

### Current Dashboard

The current dashboard (`lynx-ai/lynx/api/dashboard.py`) uses inline HTML/CSS.

### Option 1: Update Existing Dashboard

Replace inline styles with design system classes:

```python
# Before
html = f"""
<div style="background: #1a1a1a; padding: 24px;">
  <h1 style="color: white;">Dashboard</h1>
</div>
"""

# After
html = f"""
<link rel="stylesheet" href="/static/design-system.css">
<div class="na-card na-p-6">
  <h1 class="na-h1">Dashboard</h1>
</div>
"""
```

### Option 2: Create Separate Frontend

Create a React/Next.js frontend using the design system:

```bash
cd lynx-ai/ui
npx create-next-app@latest dashboard --typescript
cd dashboard
npm install @aibos/design-system
```

---

## 📁 File Structure

```
lynx-ai/ui/
├── package.json                    # npm config
├── node_modules/
│   └── @aibos/
│       └── design-system/         # Design system package
│           ├── style.css          # Compiled CSS
│           ├── components/        # React components
│           ├── dist/              # Built assets
│           ├── docs/              # Documentation
│           └── types/             # TypeScript definitions
├── README.md                      # This file
└── DESIGN-SYSTEM-SETUP.md        # Setup guide
```

---

## 🎯 Next Steps

1. **Review Components:**
   ```bash
   cd lynx-ai/ui
   cat node_modules/@aibos/design-system/components/react/README.md
   ```

2. **Check Examples:**
   - Review React component source code
   - Check TypeScript definitions
   - Review API reference

3. **Integrate:**
   - Update dashboard HTML to use design system classes
   - Or create new frontend using React components
   - Copy `style.css` to static assets if needed

---

## ✅ Verification

**Installation verified:**
```bash
cd lynx-ai/ui
npm list @aibos/design-system
# Should show: @aibos/design-system@1.1.0
```

**Package contents:**
- ✅ CSS file: `style.css`
- ✅ React components: `components/react/`
- ✅ TypeScript types: `types/`
- ✅ Design tokens: `dist/tokens.json`
- ✅ Documentation: `docs/`

---

**Last Updated:** 2026-01-27  
**Status:** ✅ **READY TO USE**

