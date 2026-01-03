# UI PRD Requirements & Wireframe Plan

**Date:** 2026-01-27  
**Status:** ✅ **READY TO START** - Independent of design system  
**Focus:** PRD requirements, theme, direction, wireframes  
**Priority:** 🔴 **HIGH** - Critical for Phase 5 completion

---

## 🎯 Objective

Define UI requirements, theme, direction, and wireframes based on PRD-LYNX-003 Phase 5 requirements, **independent of design system implementation**.

**Key Principle:** Design and structure first, implementation later (when design system is ready).

---

## 📋 PRD Requirements (Phase 5)

### Required UI Components

1. **Global "Ask Lynx" Button**
   - Universal access from any page
   - Persistent in header/navigation
   - Opens chat interface

2. **Contextual "Ask Lynx about this" Buttons**
   - Context-aware queries
   - Appears on entity pages (documents, workflows, payments)
   - Pre-fills context

3. **Draft Review Interface**
   - List all drafts
   - View draft details
   - Approve/reject actions
   - Filter by status, type, date

4. **Execution Confirmation Dialogs**
   - Show before high-risk executions
   - Display execution details
   - Require explicit confirmation

5. **Basic Audit Trail Visibility**
   - List recent Lynx Runs
   - Show run details (query, response, tool calls)
   - Filter by date, tenant, user
   - Pagination

---

## 🎨 Theme & Direction

### Design Philosophy

**Theme:** **Neo-Analog Ops Console**

**Inspired by:** Existing dashboard (`lynx-ai/lynx/api/dashboard.py`)

**Key Characteristics:**
- Dark theme (void/paper palette)
- Serif fonts for data (Playfair Display)
- Monospace for technical data (JetBrains Mono)
- Sans-serif for UI (Inter)
- Gold accent color for highlights
- Minimal, functional, enterprise-grade

### Color Palette

```
--color-void: #09090b        (Background)
--color-paper: #121214       (Cards)
--color-paper-2: #18181b     (Elevated cards)
--color-lux: #f4f4f5         (Primary text)
--color-lux-dim: #a1a1aa     (Secondary text)
--color-clay: #71717a        (Metadata)
--color-gold: #eab308        (Accents, highlights)
--color-success: #10b981     (Success states)
--color-warning: #f59e0b     (Warning states)
--color-error: #f43f5e       (Error states)
```

### Typography

**Headings:**
- H1: Playfair Display, 32px, bold (Page titles)
- H2: Inter, 24px, semibold (Section titles)
- H3: Inter, 20px, semibold (Subsections)

**Data:**
- Large: Playfair Display, 42px, serif (KPI values)
- Regular: JetBrains Mono, 13px (Technical data)
- Metadata: Inter, 11px, uppercase (Labels)

### Spacing & Layout

- Standard padding: 24px (`p-6`)
- Standard gap: 24px (`gap-6`)
- Card radius: 12px
- Panel radius: 16px
- Max width: 1400px (centered)

---

## 📐 Wireframe Specifications

### 1. Global "Ask Lynx" Button

**Location:** Global header (persistent)

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  [Lynx Ops Console]  [Protocol v1.0]  [🔄]  [Ask Lynx] │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Position:** Right side of header, after refresh button
- **Style:** Button with gold accent border
- **Text:** "Ask Lynx" (or icon + text)
- **Action:** Opens chat interface (modal or new page)
- **State:** Always visible, persistent across pages

**Behavior:**
- Click → Opens chat interface
- Hover → Gold highlight
- Active → Shows chat is open

---

### 2. Chat Interface

**Location:** Modal overlay or dedicated page

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  Ask Lynx                                    [×]        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ You: What documents are pending approval?      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Lynx: You have 3 documents pending approval:    │    │
│  │                                                  │    │
│  │ • Document Request #123 (High priority)        │    │
│  │ • Workflow Proposal #456 (Medium priority)     │    │
│  │ • Payment Draft #789 (Low priority)            │    │
│  │                                                  │    │
│  │ [Tool: docs.domain.registry.read] ✓            │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Type your question...                    [Send]│    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Layout:** Vertical message list
- **User messages:** Right-aligned, blue background
- **Lynx responses:** Left-aligned, gray background
- **Tool calls:** Shown inline with status
- **Input:** Bottom fixed input bar
- **Scrolling:** Auto-scroll to latest message

**States:**
- Loading: Show spinner while processing
- Error: Show error message in red
- Tool call in progress: Show "Thinking..." indicator

---

### 3. Contextual "Ask Lynx about this" Button

**Location:** Entity detail pages (documents, workflows, payments)

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  Document Request #123                                   │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Title: New Vendor Onboarding Request                  │
│  Status: Pending Approval                                │
│  Created: 2026-01-27                                    │
│                                                          │
│  [Ask Lynx about this]  [Edit]  [Delete]                │
│                                                          │
│  Content:                                                │
│  ...                                                     │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Position:** Top-right of entity detail section
- **Style:** Secondary button (outline style)
- **Text:** "Ask Lynx about this"
- **Action:** Opens chat with pre-filled context
- **Context:** Includes entity_type, entity_id, entity_data

**Behavior:**
- Click → Opens chat with context
- Chat shows: "You asked about Document Request #123"
- Pre-fills query suggestions based on entity type

---

### 4. Draft Review Interface

**Location:** Dedicated drafts page (`/drafts`)

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  Draft Review                                            │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Filters: [All Status ▼] [All Types ▼] [Date Range]     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Document Draft #123                    [Medium]│    │
│  │ Type: Document Request                          │    │
│  │ Created: 2026-01-27 09:00                       │    │
│  │ Status: Draft                                    │    │
│  │                                                  │    │
│  │ [View Details]  [Approve]  [Reject]             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Workflow Draft #456                     [High]  │    │
│  │ Type: Workflow Proposal                         │    │
│  │ Created: 2026-01-27 08:00                       │    │
│  │ Status: Draft                                    │    │
│  │                                                  │    │
│  │ [View Details]  [Approve]  [Reject]             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  [← Previous]  [1] [2] [3]  [Next →]                   │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Layout:** Card-based list
- **Filters:** Status, type, date range
- **Cards:** Show draft summary, risk badge, actions
- **Pagination:** Bottom pagination controls
- **Actions:** View, Approve, Reject buttons per card

**Draft Detail View:**
```
┌─────────────────────────────────────────────────────────┐
│  Draft Details: Document Draft #123                     │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Type: Document Request                                  │
│  Status: Draft                                           │
│  Risk Level: Medium                                      │
│  Created: 2026-01-27 09:00 by user_123                  │
│                                                          │
│  Payload:                                                │
│  ┌────────────────────────────────────────────────┐    │
│  │ {                                               │    │
│  │   "document_type": "request",                  │    │
│  │   "title": "New Vendor Onboarding",            │    │
│  │   ...                                           │    │
│  │ }                                               │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  [← Back]  [Approve]  [Reject]                          │
└─────────────────────────────────────────────────────────┘
```

---

### 5. Execution Confirmation Dialog

**Location:** Modal overlay (triggered before high-risk execution)

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  ⚠️  Confirm Execution                                   │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  You are about to execute a HIGH-RISK action:            │
│                                                          │
│  Tool: vpm.cell.payment.execute                          │
│  Risk Level: HIGH                                        │
│                                                          │
│  Execution Details:                                       │
│  • Payment Amount: $10,000                                │
│  • Vendor: Acme Corp                                     │
│  • Account: Operating Account                            │
│                                                          │
│  This action cannot be undone.                           │
│                                                          │
│  [Cancel]                                    [Confirm]   │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Trigger:** Before high-risk Cell MCP execution
- **Style:** Modal overlay with warning styling
- **Content:** Tool name, risk level, execution details
- **Actions:** Cancel (secondary), Confirm (primary, red)
- **Requirement:** Explicit confirmation required

**States:**
- Pending: Show confirmation dialog
- Confirming: Show loading state
- Confirmed: Close dialog, show success message
- Error: Show error message, keep dialog open

---

### 6. Audit Trail Visibility

**Location:** Dedicated audit page (`/audit`)

**Wireframe:**
```
┌─────────────────────────────────────────────────────────┐
│  Audit Trail                                             │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  Filters: [All Tenants ▼] [All Users ▼] [Date Range]    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Run #xyz123                            [✓]     │    │
│  │ User: user_123 | Tenant: tenant_abc            │    │
│  │ Query: "What documents are pending?"           │    │
│  │ Created: 2026-01-27 10:00                       │    │
│  │                                                  │    │
│  │ Tool Calls:                                     │    │
│  │ • docs.domain.registry.read (150ms) ✓           │    │
│  │                                                  │    │
│  │ [View Details]                                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Run #abc456                            [✓]     │    │
│  │ User: user_456 | Tenant: tenant_abc            │    │
│  │ Query: "Show workflow status"                   │    │
│  │ Created: 2026-01-27 09:30                       │    │
│  │                                                  │    │
│  │ Tool Calls:                                     │    │
│  │ • workflow.domain.status.read (120ms) ✓         │    │
│  │                                                  │    │
│  │ [View Details]                                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  [← Previous]  [1] [2] [3]  [Next →]                   │
└─────────────────────────────────────────────────────────┘
```

**Specifications:**
- **Layout:** Card-based list
- **Filters:** Tenant, user, date range
- **Cards:** Show run summary, tool calls, status
- **Pagination:** Bottom pagination controls
- **Details:** Expandable or separate detail view

**Run Detail View:**
```
┌─────────────────────────────────────────────────────────┐
│  Run Details: #xyz123                                    │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  User: user_123                                          │
│  Tenant: tenant_abc                                       │
│  Created: 2026-01-27 10:00:00                            │
│  Completed: 2026-01-27 10:00:15 (15s)                    │
│                                                          │
│  Query: "What documents are pending approval?"           │
│                                                          │
│  Response: "You have 3 documents pending..."             │
│                                                          │
│  Tool Calls:                                             │
│  ┌────────────────────────────────────────────────┐    │
│  │ docs.domain.registry.read                       │    │
│  │ Status: Success                                 │    │
│  │ Duration: 150ms                                 │    │
│  │ Input: { "tenant_id": "tenant_abc" }           │    │
│  │ Output: { "documents": [...] }                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  [← Back]                                                │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 User Flows

### Flow 1: Global Chat Access

```
User clicks "Ask Lynx" button
  ↓
Chat interface opens (modal or page)
  ↓
User types query
  ↓
Lynx processes (shows "Thinking...")
  ↓
Response displayed with tool calls
  ↓
User can continue conversation
```

### Flow 2: Contextual Query

```
User views document detail page
  ↓
User clicks "Ask Lynx about this"
  ↓
Chat opens with context pre-filled
  ↓
Shows: "You asked about Document #123"
  ↓
User can ask contextual questions
  ↓
Lynx responds with document-specific info
```

### Flow 3: Draft Review & Approval

```
User navigates to /drafts
  ↓
Views list of drafts (filtered)
  ↓
Clicks "View Details" on a draft
  ↓
Reviews draft payload and metadata
  ↓
Clicks "Approve" or "Reject"
  ↓
If approve → Confirmation dialog (if high-risk)
  ↓
Draft status updated
  ↓
If execution required → Execution triggered
```

### Flow 4: High-Risk Execution

```
User approves high-risk draft
  ↓
Execution confirmation dialog appears
  ↓
User reviews execution details
  ↓
User clicks "Confirm"
  ↓
Execution proceeds
  ↓
Success/error message shown
  ↓
User redirected to execution status
```

---

## 📐 Component Specifications

### Component Hierarchy

```
App (Root)
├── Layout
│   ├── Header
│   │   ├── Logo/Title
│   │   ├── Status Indicators
│   │   └── AskLynxButton (Global)
│   └── Main Content
│       └── [Page Content]
│
├── ChatInterface (Modal/Page)
│   ├── MessageList
│   │   ├── UserMessage
│   │   └── LynxMessage
│   │       └── ToolCallIndicator
│   └── ChatInput
│
├── DraftReviewPage
│   ├── DraftFilters
│   ├── DraftList
│   │   └── DraftCard
│   └── DraftDetailView
│       └── DraftActions
│
├── ExecutionDialog (Modal)
│   ├── ExecutionDetails
│   └── ConfirmationActions
│
└── AuditTrailPage
    ├── AuditFilters
    ├── RunList
    │   └── RunCard
    └── RunDetailView
```

---

## 🎨 Design Tokens (Reference)

**Note:** These are for wireframe/structure planning. Actual implementation will use design system when available.

### Spacing Scale
- `xs`: 4px
- `sm`: 8px
- `md`: 16px
- `lg`: 24px
- `xl`: 32px
- `2xl`: 48px

### Border Radius
- `sm`: 4px
- `md`: 8px
- `lg`: 12px
- `xl`: 16px
- `full`: 9999px

### Shadows
- `sm`: 0 1px 2px rgba(0,0,0,0.1)
- `md`: 0 4px 6px rgba(0,0,0,0.2)
- `lg`: 0 10px 15px rgba(0,0,0,0.3)

---

## 📋 Implementation Checklist

### Phase 1: Wireframes & Specifications (Week 1)

- [ ] Create detailed wireframes for all 5 components
- [ ] Define component specifications
- [ ] Document user flows
- [ ] Define data structures
- [ ] Create component hierarchy diagram

### Phase 2: PRD Alignment (Week 1)

- [ ] Review PRD-LYNX-003 Phase 5 requirements
- [ ] Map wireframes to PRD requirements
- [ ] Identify any gaps
- [ ] Document theme and direction decisions

### Phase 3: Structure Planning (Week 1)

- [ ] Define file structure
- [ ] Define component props/interfaces
- [ ] Define state management approach
- [ ] Define routing structure

### Phase 4: Ready for Implementation (When Design System Available)

- [ ] Wireframes complete
- [ ] Specifications documented
- [ ] PRD requirements mapped
- [ ] Ready to implement with design system

---

## 📚 PRD Requirements Mapping

| PRD Requirement | Wireframe | Component | Status |
|-----------------|-----------|-----------|--------|
| Global "Ask Lynx" button | ✅ Defined | AskLynxButton | 📋 Specified |
| Contextual buttons | ✅ Defined | ContextualButton | 📋 Specified |
| Draft review interface | ✅ Defined | DraftReviewPage | 📋 Specified |
| Execution dialogs | ✅ Defined | ExecutionDialog | 📋 Specified |
| Audit trail visibility | ✅ Defined | AuditTrailPage | 📋 Specified |

---

## 🎯 Success Criteria

### Wireframe Completeness
- [ ] All 5 components wireframed
- [ ] All user flows documented
- [ ] All states defined (loading, error, success)
- [ ] All interactions specified

### PRD Alignment
- [ ] All PRD Phase 5 requirements covered
- [ ] Theme and direction aligned with PRD
- [ ] Component specifications match PRD

### Implementation Readiness
- [ ] Wireframes ready for design system integration
- [ ] Component structure defined
- [ ] Data structures specified
- [ ] API contracts documented

---

## 📝 Next Steps

### Immediate (This Week)
1. **Create detailed wireframes** - Use tools like Figma, Excalidraw, or Mermaid
2. **Document component specs** - Props, states, behaviors
3. **Define data structures** - Request/response formats
4. **Map to PRD** - Ensure all requirements covered

### Short-term (Next Week)
1. **Review wireframes** - Get feedback, refine
2. **Create component hierarchy** - Define React component structure
3. **Document user flows** - Complete flow diagrams
4. **Prepare for implementation** - When design system available

---

**Status:** ✅ **READY TO START**  
**Estimated Completion:** 1 week (wireframes & specs)  
**Priority:** 🔴 **HIGH** - Critical for Phase 5  
**Dependency:** None - Can proceed independently

