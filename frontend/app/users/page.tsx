'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import { Plus, Edit, Trash2 } from 'lucide-react';

interface User {
  id: number;
  email: string;
  role: string;
  mfa_enabled: boolean;
  created_at: string;
}

export default function UsersPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: users = [], isLoading, refetch } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await api.get('/users/');
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/users', data),
    onSuccess: () => {
      refetch();
      setShowCreate(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (userId: number) => api.delete(`/users/${userId}`),
    onSuccess: () => refetch(),
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <DashboardHeader title="Users" subtitle="User accounts and roles" />
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add User
        </button>
      </div>

      {showCreate && (
        <div className="mb-8 bg-white rounded-lg shadow p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-4">Create New User</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              createMutation.mutate(Object.fromEntries(formData));
            }}
            className="grid grid-cols-2 gap-4"
          >
            <input type="email" name="email" placeholder="Email" className="input-field" required />
            <input type="password" name="password" placeholder="Password" className="input-field" required />
            <select name="role" className="input-field" required>
              <option value="admin">Admin</option>
              <option value="operator">Operator</option>
              <option value="auditor">Auditor</option>
              <option value="viewer">Viewer</option>
            </select>
            <button type="submit" className="btn-primary">
              {createMutation.isPending ? 'Creating...' : 'Create User'}
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-slate-500">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="p-6 text-slate-500 text-center">No users found</div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Email</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Role</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">MFA</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Created</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {users.map((user: User) => (
                <tr key={user.id} className="hover:bg-slate-50">
                  <td className="py-4 px-6 text-slate-900 font-medium">{user.email}</td>
                  <td className="py-4 px-6">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                      user.role === 'admin' ? 'bg-red-50 text-red-700' :
                      user.role === 'operator' ? 'bg-blue-50 text-blue-700' :
                      user.role === 'auditor' ? 'bg-green-50 text-green-700' :
                      'bg-slate-50 text-slate-600'
                    }`}>
                      {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-sm">
                    {user.mfa_enabled ? (
                      <span className="inline-block px-2 py-1 bg-green-50 text-green-700 rounded text-xs font-semibold">
                        Enabled
                      </span>
                    ) : (
                      <span className="inline-block px-2 py-1 bg-slate-50 text-slate-600 rounded text-xs font-semibold">
                        Disabled
                      </span>
                    )}
                  </td>
                  <td className="py-4 px-6 text-slate-600 text-sm">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-6 flex gap-2">
                    <button className="p-1 hover:bg-slate-100 rounded">
                      <Edit className="h-4 w-4 text-slate-600" />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(user.id)}
                      className="p-1 hover:bg-red-100 rounded"
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
