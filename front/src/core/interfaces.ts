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
  caracteristiques: Record<string, number>;
  competences: Record<string, number>;
  hp: number;
  inventory: string[];
  spells: string[];
  gold: number; // Or possédé par le personnage
  culture_bonuses: Record<string, number>;
}

// Interfaces pour les équipements détaillés
export interface EquipmentItem {
  type: string;
  weight: number;
  cost: number; // Coût en pièces d'or
  description: string;
}

export interface WeaponItem extends EquipmentItem {
  category: "mêlée" | "distance";
  damage: string;
  range?: number;
}

export interface ArmorItem extends EquipmentItem {
  protection: number;
}

export interface EquipmentData {
  weapons: Record<string, WeaponItem>;
  armor: Record<string, ArmorItem>;
  items: Record<string, EquipmentItem>;
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
  status: string;
  name: string;
  race: RaceData;
  culture: CultureData;
  caracteristiques: Record<string, number>;
  competences: Record<string, number>;
  hp: number;
  inventory: Item[];
  spells: string[];
  gold: number; // Or possédé par le personnage
  culture_bonuses?: Record<string, number> | null;
  background?: string; // Histoire du personnage
  physical_description?: string; // Description physique
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

// === Création de personnage (API /api/creation) ===

export interface AllocateAttributesRequest {
  race: string;
}

export interface AllocateAttributesResponse {
  attributes: Record<string, number>;
}

export interface CheckAttributesRequest {
  attributes: Record<string, number>;
}

export interface CheckAttributesResponse {
  valid: boolean;
}

export interface SaveCharacterRequest {
  character_id: string;
  character: Record<string, any>;
}

export interface SaveCharacterResponse {
  status: string;
}

export interface CheckSkillsRequest {
  skills: Record<string, number>;
}

export interface CheckSkillsResponse {
  valid: boolean;
  cost: number;
}

export interface CreationStatusResponse {
  id: string;
  status: string;
  created_at?: string;
}

// === Création de personnage (LLM) ===

// Les routes de génération LLM utilisent Partial<Character> comme type d'entrée.
// Utiliser ce type pour définir les entrées attendues par les routes de création de personnage.
// Exemple :
// export interface GenerateCharacterRequest {
//   character: Partial<Character>;
// }

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

export interface GeneratePhysicalDescriptionResponse {
  physical_description:string;
}

export interface GenerateBackgroundResponse {
  backgrounds: string[];
}

export interface GenerateNameResponse {
  names: string[];
}

export interface GeneratePhysicalDescriptionResponse {
  physical_descriptions: string[];
}

// === Groupes de compétences (structure du JSON) ===
export interface SkillGroup {
  name: string;
  description: string;
}

export type SkillGroupsDict = Record<string, SkillGroup[]>;

// === Nouvelles interfaces pour les données JSON refactorisées ===

/**
 * Interface pour les données de caractéristique depuis characteristics.json
 */
export interface CharacteristicData {
  short_name: string;
  category: 'physical' | 'mental';
  description: string;
  examples: string[];
}

/**
 * Interface pour les données complètes des caractéristiques
 */
export interface CharacteristicsData {
  characteristics: Record<string, CharacteristicData>;
  bonus_table: Record<string, number>;
  cost_table: Record<string, number>;
  starting_points: number;
  maximum_starting_value: number;
}

/**
 * Interface pour les données de compétence depuis skills_for_llm.json
 */
export interface SkillDataLLM {
  name: string;
  group: string;
  description: string;
  primary_characteristic: string;
  difficulty_levels: {
    facile: string;
    moyenne: string;
    difficile: string;
    tres_difficile: string;
  };
}

/**
 * Interface pour les groupes de compétences organisés pour l'LLM
 */
export interface SkillGroupsLLM {
  [groupName: string]: SkillDataLLM[];
}

/**
 * Interface pour les données de culture depuis races_and_cultures.json
 */
export interface CultureData {
  name: string;
  description?: string;
  skill_bonuses?: Record<string, number>;
  characteristic_bonuses?: Record<string, number>;
  free_skill_points?: number;
  special_traits?: Record<string, any>;
}

/**
 * Interface pour les données de race depuis races_and_cultures.json
 */
export interface RaceData {
  name: string;
  characteristic_bonuses: Record<string, number>;
  destiny_points: number;
  special_abilities: string[];
  base_languages: string[];
  optional_languages: string[];
  cultures?: CultureData[]; // Optionnel pour éviter de l'envoyer lors de la sauvegarde
}

/**
 * Interface pour les données de sort depuis spells.json
 */
export interface SpellData {
  name: string;
  power_cost: number;
  description: string;
}

/**
 * Interface pour les sphères de magie avec leurs sorts
 */
export interface MagicSpheres {
  [sphereName: string]: SpellData[];
}

/**
 * Interface pour les données d'équipement depuis equipment.json
 */
export interface EquipmentData {
  type: string;
  weight: number;
  cost: number; // Coût en pièces d'or
  description: string;
  // Propriétés spécifiques selon le type
  damage?: string;
  category?: string;
  range?: number;
  protection?: number;
}

/**
 * Interface pour les catégories d'équipement
 */
export interface EquipmentCategories {
  weapons: Record<string, EquipmentData>;
  armor: Record<string, EquipmentData>;
  items: Record<string, EquipmentData>;
}

/**
 * Interface pour les données de système de combat depuis combat_system.json
 */
export interface CombatSystemData {
  initiative: {
    base_formula: string;
    tie_breaker: string;
    description: string;
  };
  turn_structure: {
    action_points: number;
    phases: string[];
  };
  actions: Record<string, {
    name: string;
    cost: number;
    description: string;
  }>;
  difficulty_modifiers: Record<string, number>;
  damage_types?: Record<string, any>;
  armor_types?: Record<string, any>;
}

// === Interfaces pour les réponses d'équipement ===

/**
 * Interface pour la réponse d'ajout d'équipement
 */
export interface AddEquipmentResponse {
  status: string;
  gold: number;
  total_weight: number;
  equipment_added: {
    type: string;
    category: string;
    damage?: string;
    weight: number;
    cost: number;
    description: string;
  };
}

/**
 * Interface pour la réponse de suppression d'équipement
 */
export interface RemoveEquipmentResponse {
  status: string;
  gold: number;
  total_weight: number;
  equipment_removed: {
    type: string;
    category: string;
    damage?: string;
    weight: number;
    cost: number;
    description: string;
  };
}

// === Mise à jour des interfaces existantes pour compatibilité ===