# Lynx AI Frontend

Next.js frontend for Lynx AI Dashboard - Neo-Analog Ops Console.

## Setup

### 1. Install Dependencies

```bash
cd ui/frontend
npm install
```

### 2. Configure Environment

Create `.env.local` from `.env.local.example`:

```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`.

## Architecture

### API Client

All API calls use `apiFetch()` from `lib/apiClient.ts`:
- ✅ Same-origin (calls Next.js proxy routes)
- ✅ Automatically includes auth cookies
- ✅ Preserves request_id for debugging

### Proxy Routes

Next.js proxy routes forward to FastAPI:
- `/api/chat/*` → FastAPI `/api/chat/*`
- `/api/drafts/*` → FastAPI `/api/drafts/*`
- `/api/audit/*` → FastAPI `/api/audit/*`

### Security

- ✅ **Tenant Absolutism:** No `tenant_id` in client code (backend derives from session)
- ✅ **Thin Client:** UI only renders backend flags (no inference)

## Development

### Project Structure

```
app/
├── layout.tsx          # Root layout with QueryClientProvider
├── globals.css         # Neo-Analog theme CSS variables
├── api/                # Next.js proxy routes
│   ├── chat/
│   ├── drafts/
│   └── audit/
└── [pages]/            # UI pages (to be implemented)

lib/
├── apiClient.ts        # API fetch wrapper
└── types.ts            # TypeScript types (to be generated)

components/             # React components (to be implemented)
```

## Next Steps

1. Implement Step A: Chat Page
2. Implement Step D: Audit Page (with export)
3. Implement Step B: Draft List
4. Implement Step C: Execution Dialog

