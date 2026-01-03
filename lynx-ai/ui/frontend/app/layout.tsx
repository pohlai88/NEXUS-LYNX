'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState } from 'react';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // ✅ QueryClientProvider at root (required for React Query)
  // Must be created inside component for 'use client' directive
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: 1,
        staleTime: 30000, // 30 seconds
      },
    },
  }));

  return (
    <html lang="en">
      <head>
        <title>Lynx AI Dashboard</title>
        <meta name="description" content="Enterprise-grade monitoring for Lynx AI" />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  );
}

