'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import DashboardHeader from '@/components/layout/dashboard-header';
import { Save, AlertCircle } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    prometheus_url: 'http://prometheus:9090',
    ssh_template: 'ssh {{user}}@{{host}} -p {{port}}',
    smb_template: '',
  });

  const { data: runtimeSettings } = useQuery({
    queryKey: ['settings/runtime'],
    queryFn: async () => {
      const response = await api.get('/settings/runtime');
      return response.data;
    },
  });

  const handleSave = async () => {
    try {
      await api.put('/settings/integrations', settings);
      alert('Settings saved successfully');
    } catch (error) {
      alert('Failed to save settings');
    }
  };

  return (
    <div className="p-8 max-w-4xl">
      <DashboardHeader title="Settings" subtitle="System configuration" />

      <div className="mt-8 space-y-6">
        {/* Runtime Information */}
        <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-blue-600" />
            Runtime Information
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">Environment</label>
              <div className="p-2 bg-slate-50 rounded border border-slate-200 text-slate-900">
                {runtimeSettings?.environment || 'development'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-2">Runtime Port</label>
              <div className="p-2 bg-slate-50 rounded border border-slate-200 text-slate-900 font-mono">
                {runtimeSettings?.runtime_port || 'N/A'}
              </div>
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-600 mb-2">Max Artifact Size</label>
              <div className="p-2 bg-slate-50 rounded border border-slate-200 text-slate-900">
                {runtimeSettings?.max_artifact_size_mb || 100} MB
              </div>
            </div>
          </div>
        </div>

        {/* Integration Settings */}
        <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-4">Integration Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Prometheus URL
              </label>
              <input
                type="text"
                value={settings.prometheus_url}
                onChange={(e) => setSettings({ ...settings, prometheus_url: e.target.value })}
                className="input-field"
                placeholder="http://prometheus:9090"
              />
              <p className="text-xs text-slate-500 mt-1">URL for metrics collection</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                SSH Command Template
              </label>
              <textarea
                value={settings.ssh_template}
                onChange={(e) => setSettings({ ...settings, ssh_template: e.target.value })}
                className="input-field font-mono text-sm"
                rows={3}
                placeholder='ssh {{user}}@{{host}} -p {{port}} -J {{bastion}}'
              />
              <p className="text-xs text-slate-500 mt-1">
                Template for SSH commands. Variables: {{'{user}'}} {{'{host}'}} {{'{port}'}} {{'{bastion}'}}
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                SMB/Download Template
              </label>
              <textarea
                value={settings.smb_template}
                onChange={(e) => setSettings({ ...settings, smb_template: e.target.value })}
                className="input-field font-mono text-sm"
                rows={3}
                placeholder='powershell -Command "New-PSDrive -Name X -PSProvider FileSystem -Root \\\\{{server}}\\share; Start-Process X:\\connector.exe"'
              />
              <p className="text-xs text-slate-500 mt-1">
                Template for initial host connection. Variables: {{'{server}'}} {{'{share}'}}
              </p>
            </div>

            <button
              onClick={handleSave}
              className="btn-primary flex items-center gap-2 mt-6"
            >
              <Save className="h-4 w-4" />
              Save Settings
            </button>
          </div>
        </div>

        {/* Security Settings */}
        <div className="bg-white rounded-lg shadow p-6 border border-slate-200">
          <h3 className="font-semibold text-slate-900 mb-4">Security</h3>
          <div className="space-y-4">
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <p className="text-sm text-slate-600">
                <strong>Password Policy:</strong> Minimum 8 characters, uppercase letter, digit required
              </p>
            </div>
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <p className="text-sm text-slate-600">
                <strong>JWT Expiration:</strong> 24 hours
              </p>
            </div>
            <div className="p-4 bg-slate-50 rounded border border-slate-200">
              <p className="text-sm text-slate-600">
                <strong>Rate Limiting:</strong> 5 requests per minute on auth endpoints
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
