'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import { Plus, Edit, Trash2, Download, Upload } from 'lucide-react';

interface Host {
  id: number;
  hostname: string;
  ip: string;
  os: string;
  environment: string;
  criticality: string;
  owner?: string;
  created_at: string;
}

export default function HostsPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: hosts = [], isLoading, refetch } = useQuery({
    queryKey: ['hosts'],
    queryFn: async () => {
      const response = await api.get('/hosts/');
      return response.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data: any) => api.post('/hosts', data),
    onSuccess: () => {
      refetch();
      setShowCreate(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (hostId: number) => api.delete(`/hosts/${hostId}`),
    onSuccess: () => refetch(),
  });

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <DashboardHeader title="Hosts" subtitle="Manage inventory" />
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="h-4 w-4" />
          Add Host
        </button>
      </div>

      {showCreate && (
        <div className="mb-8 bg-white rounded-lg shadow p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-4">Create New Host</h3>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              createMutation.mutate(Object.fromEntries(formData));
            }}
            className="grid grid-cols-2 gap-4"
          >
            <input name="hostname" placeholder="Hostname" className="input-field" required />
            <input name="ip" placeholder="IP Address" className="input-field" required />
            <select name="os" className="input-field" required>
              <option value="linux">Linux</option>
              <option value="windows">Windows</option>
              <option value="macos">macOS</option>
            </select>
            <select name="environment" className="input-field" required>
              <option value="dev">Development</option>
              <option value="stage">Staging</option>
              <option value="prod">Production</option>
            </select>
            <button type="submit" className="col-span-2 btn-primary">
              {createMutation.isPending ? 'Creating...' : 'Create Host'}
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-slate-500">Loading hosts...</div>
        ) : hosts.length === 0 ? (
          <div className="p-6 text-slate-500 text-center">No hosts found. Create one to get started.</div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Hostname</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">IP Address</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">OS</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Environment</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Criticality</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {hosts.map((host: Host) => (
                <tr key={host.id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-4 px-6 text-slate-900 font-medium">{host.hostname}</td>
                  <td className="py-4 px-6 text-slate-600 font-mono text-sm">{host.ip}</td>
                  <td className="py-4 px-6 capitalize text-slate-600">{host.os}</td>
                  <td className="py-4 px-6">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                      host.environment === 'prod' ? 'bg-red-50 text-red-700' :
                      host.environment === 'stage' ? 'bg-yellow-50 text-yellow-700' :
                      'bg-green-50 text-green-700'
                    }`}>
                      {host.environment}
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                      host.criticality === 'critical' ? 'bg-red-50 text-red-700' :
                      host.criticality === 'high' ? 'bg-orange-50 text-orange-700' :
                      host.criticality === 'medium' ? 'bg-yellow-50 text-yellow-700' :
                      'bg-slate-50 text-slate-600'
                    }`}>
                      {host.criticality}
                    </span>
                  </td>
                  <td className="py-4 px-6 flex gap-2">
                    <button className="p-1 hover:bg-slate-100 rounded" title="Edit">
                      <Edit className="h-4 w-4 text-slate-600" />
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(host.id)}
                      className="p-1 hover:bg-red-100 rounded"
                      title="Delete"
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
