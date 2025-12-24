'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import { Download } from 'lucide-react';

interface AuditEvent {
  id: number;
  action: string;
  entity_type: string;
  actor_user_id?: number;
  created_at: string;
  ip_address?: string;
}

export default function AuditPage() {
  const [actionFilter, setActionFilter] = useState('');
  const { data: events = [], isLoading } = useQuery({
    queryKey: ['audit', actionFilter],
    queryFn: async () => {
      const response = await api.get('/audit/', {
        params: actionFilter ? { action: actionFilter } : {},
      });
      return response.data;
    },
  });

  const actions = [
    'LOGIN',
    'LOGOUT',
    'HOST_CREATED',
    'HOST_UPDATED',
    'HOST_DELETED',
    'ARTIFACT_UPLOADED',
    'ARTIFACT_DOWNLOADED',
    'METRICS_COLLECTED',
    'SSH_COMMAND_COPIED',
  ];

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <DashboardHeader title="Audit Logs" subtitle="System activity and access" />
        <button className="btn-primary flex items-center gap-2">
          <Download className="h-4 w-4" />
          Export CSV
        </button>
      </div>

      <div className="mb-6 flex gap-4">
        <input
          type="text"
          placeholder="Search by IP or action..."
          className="input-field flex-1"
        />
        <select
          value={actionFilter}
          onChange={(e) => setActionFilter(e.target.value)}
          className="input-field w-48"
        >
          <option value="">All Actions</option>
          {actions.map((action) => (
            <option key={action} value={action}>
              {action.replace(/_/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-slate-500">Loading audit logs...</div>
        ) : events.length === 0 ? (
          <div className="p-6 text-slate-500 text-center">No events found</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left py-3 px-6 font-semibold text-slate-600">Timestamp</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600">Action</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600">Entity</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600">User</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {events.map((event: AuditEvent) => (
                <tr key={event.id} className="hover:bg-slate-50">
                  <td className="py-3 px-6 text-slate-600">
                    {new Date(event.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-6">
                    <span className="inline-block px-2 py-1 bg-indigo-50 text-indigo-700 rounded text-xs font-semibold">
                      {event.action}
                    </span>
                  </td>
                  <td className="py-3 px-6 text-slate-600">{event.entity_type}</td>
                  <td className="py-3 px-6 text-slate-600">User {event.actor_user_id}</td>
                  <td className="py-3 px-6 text-slate-600 font-mono">{event.ip_address || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
