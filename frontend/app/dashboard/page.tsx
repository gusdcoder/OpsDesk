'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import StatsCard from '@/components/common/stats-card';
import { BarChart3, Cpu, HardDrive, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const { data: hosts = [], isLoading } = useQuery({
    queryKey: ['hosts'],
    queryFn: async () => {
      const response = await api.get('/hosts/');
      return response.data;
    },
  });

  const hostCount = hosts.length;
  const criticalCount = hosts.filter((h: any) => h.criticality === 'critical').length;
  const prodCount = hosts.filter((h: any) => h.environment === 'prod').length;

  return (
    <div className="p-8">
      <DashboardHeader title="Dashboard" subtitle="System Overview" />
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
        <StatsCard 
          title="Total Hosts" 
          value={hostCount} 
          icon={<BarChart3 className="h-5 w-5" />}
          color="blue"
        />
        <StatsCard 
          title="Production" 
          value={prodCount} 
          icon={<Cpu className="h-5 w-5" />}
          color="slate"
        />
        <StatsCard 
          title="Critical" 
          value={criticalCount} 
          icon={<AlertCircle className="h-5 w-5" />}
          color="red"
        />
        <StatsCard 
          title="Metrics Updated" 
          value="0" 
          icon={<HardDrive className="h-5 w-5" />}
          color="indigo"
        />
      </div>
      
      <div className="mt-8 bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4">Recent Hosts</h2>
        {isLoading ? (
          <div className="text-slate-500">Loading...</div>
        ) : hosts.length === 0 ? (
          <div className="text-slate-500">No hosts found. Create one to get started.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200">
                <tr>
                  <th className="text-left py-2 px-4 font-semibold text-slate-600">Hostname</th>
                  <th className="text-left py-2 px-4 font-semibold text-slate-600">IP</th>
                  <th className="text-left py-2 px-4 font-semibold text-slate-600">OS</th>
                  <th className="text-left py-2 px-4 font-semibold text-slate-600">Environment</th>
                </tr>
              </thead>
              <tbody>
                {hosts.slice(0, 5).map((host: any) => (
                  <tr key={host.id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="py-2 px-4 text-slate-900">{host.hostname}</td>
                    <td className="py-2 px-4 text-slate-600">{host.ip}</td>
                    <td className="py-2 px-4 text-slate-600 capitalize">{host.os}</td>
                    <td className="py-2 px-4">
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${
                        host.environment === 'prod' ? 'bg-red-50 text-red-700' :
                        host.environment === 'stage' ? 'bg-yellow-50 text-yellow-700' :
                        'bg-green-50 text-green-700'
                      }`}>
                        {host.environment}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
