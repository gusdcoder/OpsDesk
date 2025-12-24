'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import LoginForm from '@/components/auth/login-form';
import { api } from '@/lib/api';

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = React.useState('');

  const loginMutation = useMutation({
    mutationFn: async (credentials: { email: string; password: string }) => {
      return api.post('/auth/login', credentials);
    },
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.data.access_token);
      router.push('/dashboard');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Login failed');
    },
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">OpsDesk</h1>
          <p className="text-slate-600 mb-8">Enterprise Host Management</p>
          
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}
          
          <LoginForm isLoading={loginMutation.isPending} onSubmit={(data) => loginMutation.mutate(data)} />
        </div>
      </div>
    </div>
  );
}
