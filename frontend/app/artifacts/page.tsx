'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import { Download, Trash2 } from 'lucide-react';

interface Artifact {
  id: number;
  name: string;
  file_type: string;
  size_bytes: number;
  uploaded_at: string;
  host_id: number;
}

export default function ArtifactsPage() {
  const { data: artifacts = [], isLoading } = useQuery({
    queryKey: ['artifacts'],
    queryFn: async () => {
      // In a real app, this would be a paginated list endpoint
      return [];
    },
  });

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="p-8">
      <DashboardHeader title="Artifacts" subtitle="Collected data from hosts" />

      <div className="mt-8 bg-white rounded-lg shadow border border-slate-200 overflow-hidden">
        {isLoading ? (
          <div className="p-6 text-slate-500">Loading artifacts...</div>
        ) : artifacts.length === 0 ? (
          <div className="p-6 text-center">
            <div className="text-slate-500">No artifacts collected yet</div>
            <p className="text-slate-400 text-sm mt-2">Upload files on host detail pages</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Filename</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Type</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Size</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Uploaded</th>
                <th className="text-left py-3 px-6 font-semibold text-slate-600 text-sm">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {artifacts.map((artifact: Artifact) => (
                <tr key={artifact.id} className="hover:bg-slate-50">
                  <td className="py-4 px-6 text-slate-900 font-medium">{artifact.name}</td>
                  <td className="py-4 px-6 text-slate-600">
                    <span className="inline-block px-2 py-1 bg-slate-100 rounded text-xs font-semibold text-slate-600">
                      {artifact.file_type}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-slate-600 text-sm">{formatBytes(artifact.size_bytes)}</td>
                  <td className="py-4 px-6 text-slate-600 text-sm">
                    {new Date(artifact.uploaded_at).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-6 flex gap-2">
                    <button className="p-1 hover:bg-slate-100 rounded">
                      <Download className="h-4 w-4 text-slate-600" />
                    </button>
                    <button className="p-1 hover:bg-red-100 rounded">
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
