/**
 * Next.js API Proxy Route - Chat Query
 * 
 * ✅ Proxies to FastAPI /api/chat/query
 * ✅ Same-origin (no CORS issues)
 * ✅ Forwards auth cookies automatically
 * ✅ Thin proxy (no business logic)
 */

import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const requestId = crypto.randomUUID(); // ✅ Request ID for debugging
    
    // ✅ Forward to FastAPI
    const res = await fetch(`${FASTAPI_URL}/api/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward auth headers
        'Authorization': request.headers.get('Authorization') || '',
        'Cookie': request.headers.get('Cookie') || '',
        'X-Request-ID': requestId, // ✅ Request ID
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({
        error: `HTTP ${res.status}: ${res.statusText}`,
        request_id: requestId,
      }));
      return NextResponse.json(error, { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        request_id: crypto.randomUUID() 
      },
      { status: 500 }
    );
  }
}

