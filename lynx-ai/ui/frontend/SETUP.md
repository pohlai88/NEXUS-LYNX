# Frontend Setup - Quick Start

## ✅ Dependencies Installed

All npm packages have been installed successfully.

## 🚀 Start Development Server

From the `ui/frontend` directory:

```bash
npm run dev
```

The Next.js app will start at `http://localhost:3000`.

## ⚙️ Environment Configuration

**Important:** Create `.env.local` file before running:

```bash
# Copy example file
cp .env.local.example .env.local
```

Edit `.env.local`:
```bash
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 📋 Prerequisites

1. **FastAPI Backend Running**
   - Backend should be running on `http://localhost:8000` (or update `FASTAPI_URL`)
   - Start backend: `cd lynx-ai && python -m lynx.api.dashboard` (or `uvicorn lynx.api.dashboard:app`)

2. **Environment Variables**
   - Create `.env.local` with `FASTAPI_URL` pointing to your FastAPI server

## 🐛 Troubleshooting

### "Command 'dev' not found"
- ✅ **Fixed:** Dependencies are now installed
- Run `npm run dev` from `ui/frontend` directory

### "Cannot connect to FastAPI"
- Check that FastAPI is running on the port specified in `FASTAPI_URL`
- Verify `FASTAPI_URL` in `.env.local` matches your backend URL

### "Module not found"
- Run `npm install` again in `ui/frontend` directory
- Check that `node_modules` exists

## 📁 Project Structure

```
ui/frontend/
├── app/
│   ├── layout.tsx      # Root layout (QueryClientProvider)
│   ├── globals.css     # Theme CSS variables
│   └── api/            # Next.js proxy routes
├── lib/
│   └── apiClient.ts    # API fetch wrapper
└── package.json        # Dependencies
```

## ✅ Next Steps

1. Create `.env.local` with `FASTAPI_URL`
2. Start FastAPI backend (if not running)
3. Run `npm run dev` to start Next.js
4. Open `http://localhost:3000` in browser

