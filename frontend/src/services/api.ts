import { JobCreatePayload, JobStatusResponse, ManifestData, TimelineData } from '../types';

const API_BASE = '/api/v1';

export async function createJob(payload: JobCreatePayload, idempotencyKey?: string): Promise<JobStatusResponse> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }

  const response = await fetch(`${API_BASE}/broll/jobs`, {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || `Job creation failed with status ${response.status}`);
  }
  return data;
}

export async function uploadAudioJob(
  file: File,
  options: { voice?: string; aspect_ratios?: string[]; style?: string; avoid?: string[] },
  idempotencyKey?: string
): Promise<JobStatusResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (options.voice) formData.append('voice', options.voice);
  if (options.aspect_ratios) formData.append('aspect_ratios', JSON.stringify(options.aspect_ratios));
  if (options.style) formData.append('style', options.style);
  if (options.avoid) formData.append('avoid', JSON.stringify(options.avoid));

  const headers: Record<string, string> = {};
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }

  const response = await fetch(`${API_BASE}/broll/jobs/upload`, {
    method: 'POST',
    headers,
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || `Upload failed with status ${response.status}`);
  }
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || `Failed to fetch status for job ${jobId}`);
  }
  return data;
}

export async function listJobs(statusFilter?: string): Promise<{ total: number; jobs: JobStatusResponse[] }> {
  const url = statusFilter ? `${API_BASE}/jobs?status=${encodeURIComponent(statusFilter)}` : `${API_BASE}/jobs`;
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error('Failed to list jobs');
  }
  return data;
}

export async function getJobResult(jobId: string): Promise<{
  job_id: string;
  status: string;
  aspect_ratios: string[];
  artifacts: Record<string, string>;
  manifest?: ManifestData;
  timeline?: TimelineData;
  cost_estimate_usd: number;
  processing_duration_sec: number;
}> {
  const response = await fetch(`${API_BASE}/broll/jobs/${jobId}/result`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || 'Failed to retrieve job results');
  }
  return data;
}

export async function swapSceneClip(
  jobId: string,
  sceneIndex: number,
  options: { new_clip_id?: string; new_visual_hint?: string }
): Promise<any> {
  const response = await fetch(`${API_BASE}/broll/jobs/${jobId}/scenes/${sceneIndex}/swap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scene_index: sceneIndex, ...options }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error?.message || 'Failed to swap clip');
  }
  return data;
}

export async function checkHealth(): Promise<{ status: string; app: string; version: string }> {
  const response = await fetch('/health');
  return response.json();
}
