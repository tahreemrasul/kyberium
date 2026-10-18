// Mirrors backend/app/schemas.py — keep in sync.

export type Category = "top" | "bottom" | "outerwear" | "dress" | "shoes" | "accessory";
export type Formality = "casual" | "smart_casual" | "formal";
export type Layer = "base" | "mid" | "outer" | "none";
export type Occasion = "work" | "everyday" | "event" | "travel";
export type Fidelity = "close" | "aesthetic" | "creative";
export type Shopping = "wardrobe_first" | "secondhand_rental" | "open_to_new";
export type Strategy = "closest" | "creative" | "alternative";

export const CATEGORIES: Category[] = ["top", "bottom", "outerwear", "dress", "shoes", "accessory"];
export const OCCASIONS: Occasion[] = ["work", "everyday", "event", "travel"];

export interface GarmentAttributes {
  name: string;
  category: Category;
  subcategory?: string | null;
  colors: string[];
  silhouette?: string | null;
  pattern?: string | null;
  formality: Formality;
  layer: Layer;
  style_tags: string[];
  occasions: Occasion[];
  material_appearance?: string | null;
}

export interface GarmentDraft extends GarmentAttributes {
  is_garment: boolean;
  low_confidence_fields: string[];
  notes?: string | null;
}

export interface GarmentAnalysis {
  upload_id: string;
  image_url: string;
  /** Garment cut out/cropped and placed at a standard scale on the studio background. */
  display_url?: string | null;
  draft: GarmentDraft | null;
  engine: "gemini" | "none";
  cached: boolean;
  message?: string | null;
}

export interface Garment extends GarmentAttributes {
  id: string;
  image_url: string;
  image_kind: "photo" | "cutout" | "illustration";
  source: "upload" | "sample";
  verified_by_user: boolean;
  created_at: string;
  updated_at: string;
}

export interface InspirationPiece {
  slot_id: string;
  category: Category;
  description: string;
  subcategory?: string | null;
  colors: string[];
  silhouette?: string | null;
  pattern?: string | null;
  formality: Formality;
  layer: Layer;
  style_tags: string[];
  visibility: "clear" | "partial" | "obscured";
  importance: "key" | "supporting";
  material_appearance?: string | null;
  fit_volume?: string | null;
  styling_details?: string[];
}

export interface InspirationAnalysis {
  is_outfit: boolean;
  summary: string;
  aesthetic: string[];
  palette: string[];
  proportions?: string | null;
  layering?: string | null;
  formality: Formality;
  occasions: Occasion[];
  pieces: InspirationPiece[];
  ambiguities: string[];
  // Outfit DNA
  essential_traits?: string[];
  flexible_traits?: string[];
  waist_definition?: string | null;
  volume_balance?: string | null;
  color_contrast?: string | null;
  materials?: string[];
  styling_details?: string[];
}

export interface Inspiration {
  id: string;
  image_url: string;
  analysis: InspirationAnalysis;
  engine: "gemini" | "cached_sample";
  sample_id?: string | null;
  created_at: string;
}

export interface SampleInspiration {
  id: string;
  title: string;
  image_url: string;
  scenario: string;
}

export interface StylePreferences {
  occasion: Occasion;
  fidelity: Fidelity;
  shopping: Shopping;
  keep_garment_ids: string[];
  exclude_garment_ids: string[];
  notes?: string | null;
}

export interface CandidateMatch {
  garment_id: string;
  slot_id: string;
  /** Relative ranking value — not a probability. */
  score: number;
  reasons: string[];
  matching_attributes?: string[];
  differences?: string[];
  styling_considerations?: string[];
}

export interface LookItem {
  garment_id: string;
  garment: Garment;
  replaces_slot_id: string | null;
  replaces_description: string | null;
  explanation: string;
  preserved: string[];
  changed: string[];
  role?: string | null;
}

export interface LookGap {
  slot_id: string;
  description: string;
  category: Category;
  reason: string;
  essential: boolean;
  sourcing_hint?: string | null;
}

export interface ImpactSummary {
  owned_count: number;
  total_pieces: number;
  gap_count: number;
  essential_gap_count: number;
  purchase_needed: boolean;
  potential_purchases_avoided: number;
  headline: string;
}

export interface Look {
  id: string;
  strategy: Strategy;
  title: string;
  items: LookItem[];
  gaps: LookGap[];
  why_it_works: string[];
  styling_tip?: string | null;
  impact: ImpactSummary;
  warnings: string[];
  coherence?: string | null;
  styling_instructions?: string[];
  preserved_traits?: string[];
  deviations?: string[];
  review?: LookReview | null;
}

/** The critic's verdict as shown to users — a judgment, not an objective score. */
export interface LookReview {
  verdict: "approve" | "revise" | "reject";
  strengths: string[];
  notes: string[];
  rounds: number;
}

export interface TraceStep {
  step: string;
  round: number;
  summary: string;
  details: string[];
  latency_ms?: number | null;
  tokens?: number | null;
}

export interface StylingTrace {
  engine: string;
  rounds: number;
  steps: TraceStep[];
  total_latency_ms?: number | null;
  total_tokens?: number | null;
  final_decision?: string | null;
}

export interface KnowledgeHitRef {
  id: string;
  text: string;
  source_title?: string | null;
  source_url?: string | null;
}

export interface Generation {
  id: string;
  inspiration_id: string;
  inspiration_image_url: string;
  analysis: InspirationAnalysis;
  preferences: StylePreferences;
  looks: Look[];
  candidates: Record<string, CandidateMatch[]>;
  engine: "agentic" | "gemini" | "rules";
  engine_note?: string | null;
  no_match_reason?: string | null;
  knowledge: KnowledgeHitRef[];
  trace?: StylingTrace | null;
  created_at: string;
}

export interface SavedLook {
  id: string;
  generation_id: string;
  inspiration_image_url: string;
  preferences: StylePreferences;
  look: Look;
  created_at: string;
}

export interface Health {
  status: "ok";
  version: string;
  ai_enabled: boolean;
  ai_model: string | null;
  storage_backend: string;
  knowledge_backend: string;
}

export interface ErrorBody {
  code: string;
  message: string;
  retryable: boolean;
  details?: Record<string, unknown> | null;
}

export const DEFAULT_PREFERENCES: StylePreferences = {
  occasion: "work",
  fidelity: "aesthetic",
  shopping: "wardrobe_first",
  keep_garment_ids: [],
  exclude_garment_ids: [],
  notes: null,
};
