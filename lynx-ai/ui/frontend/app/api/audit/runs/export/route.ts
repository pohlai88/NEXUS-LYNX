/**
 * Next.js API Proxy Route - Export Audit Logs
 * 
 * ✅ Proxies to FastAPI /api/audit/runs/export
 * ✅ Returns file download (CSV or JSON)
 */

import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const requestId = crypto.randomUUID();
    
    // Forward query params to FastAPI
    const queryString = searchParams.toString();
    const url = `${FASTAPI_URL}/api/audit/runs/export${queryString ? `?${queryString}` : ''}`;
    
    const res = await fetch(url, {
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
    
    // Get content type and filename from headers
    const contentType = res.headers.get('Content-Type') || 'application/octet-stream';
    const contentDisposition = res.headers.get('Content-Disposition') || '';
    
    // Get file content
    const blob = await res.blob();
    const buffer = await blob.arrayBuffer();
    
    // Return file download
    return new NextResponse(buffer, {
      status: 200,
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': contentDisposition,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error', request_id: crypto.randomUUID() },
      { status: 500 }
    );
  }
}

