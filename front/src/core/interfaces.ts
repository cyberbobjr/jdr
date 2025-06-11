// === Types pour la racine ===
export interface Root {
  history: HistoryItem[];
}

// === Historique d'échanges ===
export interface HistoryItem {
  parts: Part[];
  instructions?: string | null;
  kind: string;
  usage?: Usage;
  model_name?: string;
  timestamp: string;
  vendor_details?: VendorDetails | null;
  vendor_id?: string;
}

// === Une partie (part) d'un échange ===
export interface Part {
  content?: string;
  timestamp?: string;
  dynamic_ref?: string | null;
  part_kind: string;
  tool_name?: string;
  args?: string;
  tool_call_id?: string;
}

// === Utilisation des tokens ===
export interface Usage {
  requests: number;
  request_tokens: number;
  response_tokens: number;
  total_tokens: number;
  details: {
    cached_tokens?: number;
  };
}

// === VendorDetails (optionnel) ===
export interface VendorDetails {
  // Ajoute des propriétés ici si ton JSON en contient
}

// === Contexte du personnage (string encodé JSON) ===
export interface CharacterContext {
  id: string;
  name: string;
  race: string;
  culture: string;
  profession: string;
  caracteristiques: Record<string, number>;
  competences: Record<string, number>;
  hp: number;
  inventory: string[];
  equipment: string[];
  spells: string[];
  equipment_summary: EquipmentSummary;
  culture_bonuses: Record<string, number>;
}

export interface EquipmentSummary {
  total_cost: number;
  total_weight: number;
  remaining_money: number;
  starting_money: number;
}
