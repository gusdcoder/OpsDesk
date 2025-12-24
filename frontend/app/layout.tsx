'use client';

import type { Metadata } from 'next';
import React from 'react';
import '../styles/globals.css';
import Sidebar from '@/components/layout/sidebar';
import TopBar from '@/components/layout/topbar';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from '@/lib/queryClient';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isAuthenticated, setIsAuthenticated] = React.useState(false);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  if (isLoading) {
    return (
      <html lang="en">
        <body className="bg-slate-50">
          <div className="flex h-screen items-center justify-center">
            <div className="text-slate-600">Loading...</div>
          </div>
        </body>
      </html>
    );
  }

  return (
    <html lang="en">
      <head>
        <title>OpsDesk - Enterprise Host Management</title>
      </head>
      <body className="bg-slate-50">
        <QueryClientProvider client={queryClient}>
          {isAuthenticated ? (
            <div className="flex h-screen bg-slate-50">
              <Sidebar />
              <div className="flex flex-1 flex-col overflow-hidden">
                <TopBar />
                <main className="flex-1 overflow-auto">
                  {children}
                </main>
              </div>
            </div>
          ) : (
            <div>
              {children}
            </div>
          )}
        </QueryClientProvider>
      </body>
    </html>
  );
}
