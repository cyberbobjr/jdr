// === Types pour la racine ===
export interface HistoryResponse {
  history: ConversationMessage[];
}

// === Historique d'échanges ===
// HistoryItem est identique à ConversationMessage, donc on peut le typer comme un alias.
export type HistoryItem = ConversationMessage;

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

// ================================
// === INTERFACES API OPENAPI ===
// ================================

// === Modèles de base ===

/**
 * Interface pour un objet (item) dans l'inventaire
 */
export interface Item {
  id: string;
  name: string;
  weight: number;
  base_value: number;
}

/**
 * Interface pour un personnage
 */
export interface Character {
  id: string;
  name: string;
  race: string;
  culture: string;
  profession: string;
  caracteristiques: Record<string, number>;
  competences: Record<string, number>;
  hp: number;
  inventory: Item[];
  equipment: string[];
  spells: string[];
  equipment_summary?: Record<string, number> | null;
  culture_bonuses?: Record<string, number> | null;
}

/**
 * Interface pour la liste des personnages
 */
export interface CharacterList {
  characters: Character[];
}

/**
 * Interface pour le statut d'un scénario
 */
export interface ScenarioStatus {
  name: string;
  status: string;
  session_id?: string | null;
  scenario_name?: string | null;
  character_name?: string | null;
}

/**
 * Interface pour la liste des scénarios
 */
export interface ScenarioList {
  scenarios: ScenarioStatus[];
}

/**
 * Interface pour démarrer un scénario
 */
export interface StartScenarioRequest {
  scenario_name: string;
  character_id: string;
}

/**
 * Interface pour jouer un scénario
 */
export interface PlayScenarioRequest {
  message: string;
}

/**
 * Interface pour les erreurs de validation
 */
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

/**
 * Interface pour les erreurs HTTP de validation
 */
export interface HTTPValidationError {
  detail: ValidationError[];
}

// === Paramètres des endpoints ===

/**
 * Paramètres pour l'endpoint d'attaque de combat
 */
export interface AttackEndpointParams {
  attacker_id: string;
  target_id: string;
  attack_value: number;
}

/**
 * Corps de la requête pour l'endpoint d'attaque de combat
 */
export interface AttackEndpointBody {
  combat_state: Record<string, any>;
}

/**
 * Paramètres pour récupérer les détails d'un scénario
 */
export interface GetScenarioDetailsParams {
  scenario_file: string;
}

/**
 * Paramètres pour jouer un scénario
 */
export interface PlayScenarioParams {
  session_id: string;
}

/**
 * Paramètres pour récupérer l'historique d'un scénario
 */
export interface GetScenarioHistoryParams {
  session_id: string;
}

// === Réponses des endpoints ===

/**
 * Réponse de l'endpoint d'attaque de combat
 */
export interface AttackEndpointResponse {
  [key: string]: any; // État du combat mis à jour
}

/**
 * Réponse de l'endpoint pour démarrer un scénario
 */
export interface StartScenarioResponse {
  session_id: string;
  scenario_name: string;
  character_id: string;
  message: string;
  llm_response: string;
}

/**
 * Réponse de l'endpoint pour jouer un scénario
 */
export interface PlayScenarioResponse {
  response: ConversationMessage[];
}

/**
 * Réponse de l'endpoint pour récupérer l'historique d'un scénario
 */
export interface GetScenarioHistoryResponse {
  history: ConversationMessage[];
}

/**
 * Réponse de l'endpoint pour récupérer les détails d'un scénario
 */
export interface GetScenarioDetailsResponse {
  content: string;
}

// === Interfaces pour la conversation et les messages ===

/**
 * Interface pour une partie de message dans l'historique de conversation
 */
export interface MessagePart {
  content: string;
  timestamp: string;
  dynamic_ref?: string | null;
  part_kind: string; // ex: "system-prompt", "user-prompt", "text", "tool-call", "tool-return"
}

/**
 * Interface pour les informations d'usage des tokens
 */
export interface MessageUsage {
  requests: number;
  request_tokens: number;
  response_tokens: number;
  total_tokens: number;
  details?: Record<string, any> | null;
}

/**
 * Interface pour un message complet dans l'historique de conversation
 */
export interface ConversationMessage {
  parts: MessagePart[];
  instructions?: string | null;
  kind: string; // ex: "request", "response"
  usage?: MessageUsage | null;
  model_name?: string | null;
  timestamp?: string | null;
  vendor_details?: any | null;
  vendor_id?: string | null;
}

// === Types utilitaires ===

/**
 * Type pour les UUID
 */
export type UUID = string;

/**
 * Type pour les réponses d'erreur génériques
 */
export interface ApiErrorResponse {
  detail: string | ValidationError[];
}
