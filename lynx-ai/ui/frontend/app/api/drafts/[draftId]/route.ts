/**
 * Next.js API Proxy Route - Draft Detail
 * 
 * ✅ Proxies to FastAPI /api/drafts/{draftId}
 */

import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { draftId: string } }
) {
  try {
    const requestId = crypto.randomUUID();
    
    const res = await fetch(`${FASTAPI_URL}/api/drafts/${params.draftId}`, {
      method: 'GET',
      headers: {
        'Authorization': request.headers.get('Authorization') || '',
        'Cookie': request.headers.get('Cookie') || '',
        'X-Request-ID': requestId,
      },
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
      { error: 'Internal server error', request_id: crypto.randomUUID() },
      { status: 500 }
    );
  }
}

