export interface SceneInputItem {
  text: string;
  visual_hint?: string;
}

export interface CaptionsConfig {
  burn_in: boolean;
  srt: boolean;
}

export interface JobCreatePayload {
  audio_url?: string;
  script?: string;
  scenes?: Array<{ text: string; visual_hint?: string }>;
  voice?: string;
  aspect_ratios?: string[];
  style?: string;
  avoid?: string[];
  captions?: CaptionsConfig;
}

export interface JobResultLinks {
  video_16_9?: string;
  video_9_16?: string;
  video_1_1?: string;
  captions_srt?: string;
  timeline_json?: string;
  manifest_json?: string;
  audio_narration?: string;
}

export interface ErrorInfo {
  code: string;
  message: string;
  retryable?: boolean;
  details?: Record<string, any>;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'queued' | 'running' | 'succeeded' | 'failed';
  progress: number;
  current_stage: string;
  created_at: string;
  updated_at: string;
  result?: JobResultLinks;
  error?: ErrorInfo;
}

export interface TimelineScene {
  scene_index: number;
  scene_id: string;
  narration_text: string;
  start_time: number;
  end_time: number;
  duration: number;
  visual_intent: string;
  category: string;
  selected_clip: {
    clip_id: string;
    provider: string;
    title: string;
    source_url: string;
    download_url: string;
    license_name: string;
    license_url: string;
    attribution: string;
    rights_verification_status: string;
    is_ai_generated: boolean;
  };
  selection_decision: {
    selection_reason: string;
    relevance_score: number;
    vlm_score: number;
    human_rating_estimate: number;
    fallback_used: boolean;
  };
  safety_and_warnings: string[];
}

export interface TimelineData {
  schema_version: string;
  job_id: string;
  generated_at: string;
  total_narration_duration_sec: number;
  scene_count: number;
  scenes: TimelineScene[];
}

export interface ManifestData {
  manifest_version: string;
  job_id: string;
  application: {
    name: string;
    version: string;
    environment: string;
  };
  models_and_providers: Record<string, any>;
  rendering_settings: {
    aspect_ratios: string[];
    fps: number;
    crf: number;
    codec_video: string;
    codec_audio: string;
    pixel_format: string;
  };
  stage_timings_seconds: Record<string, number>;
  total_processing_duration_seconds: number;
  cost_estimate: {
    total_usd: number;
    currency: string;
    breakdown: Record<string, number>;
    assumptions: string;
  };
  media_licensing_summary: {
    all_clips_commercial_use: boolean;
    watermarked_footage: boolean;
    ai_generated_clips_count: number;
    stock_clips_count: number;
  };
  output_artifacts: Record<string, string>;
  warnings: string[];
}
