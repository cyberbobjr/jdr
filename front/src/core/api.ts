// Service API pour l'application JDR "Terres du Milieu"
// Gestion complète des appels backend FastAPI + PydanticAI
//
// Ce fichier utilise les interfaces définies dans interfaces.ts basées sur le fichier OpenAPI JSON
// Les seules interfaces définies ici sont spécifiques au frontend (GameSession, etc.)

import type {
  CharacterContext,
  Character,
  CharacterList,
  ScenarioStatus,
  ScenarioList,
  StartScenarioRequest,
  StartScenarioResponse,
  PlayScenarioRequest,
  PlayScenarioResponse,
  GetScenarioDetailsResponse,
  GetScenarioHistoryResponse,
  ApiErrorResponse,
  ConversationMessage,
  AllocateAttributesRequest,
  AllocateAttributesResponse,
  CheckAttributesRequest,
  CheckAttributesResponse,
  SaveCharacterRequest,
  SaveCharacterResponse,
  CheckSkillsRequest,
  CheckSkillsResponse,
  CreationStatusResponse,
  GeneratePhysicalDescriptionResponse,
  GenerateBackgroundResponse,
  GenerateNameResponse,
  SkillGroupsDict,
  RaceData
}

  from "./interfaces";

// ========================================
// Configuration et types API
// ========================================

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Types spécifiques au frontend (non présents dans l'OpenAPI)
export interface GameSession {
  session_id: string;
  scenario_name: string;
  character_name: string;
  status: "active" | "paused" | "completed";
  last_activity: string;
}

// Interface combinée pour les requêtes d'attaque de combat
export interface CombatAttackRequest {
  attacker_id: string;
  target_id: string;
  attack_value: number;
  combat_state: Record<string, any>;
}

// ========================================
// Classe de gestion des erreurs API
// ========================================

export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: any
  ) {
    super(message);
    this.name = "ApiError";
  }
}

// ========================================
// Utilitaires pour les appels HTTP
// ========================================

async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };

  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorDetails: ApiErrorResponse | undefined;

      try {
        errorDetails = (await response.json()) as ApiErrorResponse;
        if (errorDetails.detail) {
          errorMessage = Array.isArray(errorDetails.detail)
            ? errorDetails.detail.map((d) => d.msg).join(", ")
            : errorDetails.detail;
        }
      } catch {
        // Si on ne peut pas parser le JSON d'erreur, on garde le message HTTP
      }

      throw new ApiError(response.status, errorMessage, errorDetails);
    }

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return await response.json();
    } else {
      return (await response.text()) as unknown as T;
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }

    // Erreur de réseau ou autre
    throw new ApiError(
      0,
      `Erreur de connexion: ${
        error instanceof Error ? error.message : "Erreur inconnue"
      }`
    );
  }
}

// ========================================
// Service API principal
// ========================================

export class JdrApiService {
  // ========================================
  // Gestion des personnages
  // ========================================

  /**
   * Récupère la liste de tous les personnages disponibles
   */
  static async getCharacters(): Promise<Character[]> {
    try {
      const result = await makeRequest<CharacterList>("/api/characters/");
      console.log('getCharacters result:', result);
      return result.characters;
    } catch (error) {
      console.error('Erreur dans getCharacters:', error);
      return [];
    }
  }

  /**
   * Récupère un personnage par son ID en appelant l'endpoint spécifique
   */
  static async getCharacter(id: string): Promise<Character | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/characters/${id}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error(`Erreur HTTP: ${response.status}`);
      }
      
      const character = await response.json();
      return character;
    } catch (error) {
      console.error('Erreur dans getCharacter:', error);
      return null;
    }
  }

  // ========================================
  // Gestion des scénarios
  // ========================================

  /**
   * Récupère la liste de tous les scénarios avec leur statut
   */
  static async getScenarios(): Promise<ScenarioStatus[]> {
    const result = await makeRequest<ScenarioList>("/api/scenarios/");
    return result.scenarios;
  }
  /**
   * Récupère le contenu détaillé d'un scénario
   */
  static async getScenarioDetails(scenarioFile: string): Promise<string> {
    const result = await makeRequest<GetScenarioDetailsResponse>(
      `/api/scenarios/${encodeURIComponent(scenarioFile)}`
    );
    return result.content || (result as unknown as string); // Compatibilité avec l'ancien format
  }

  /**
   * Démarre un nouveau scénario avec un personnage
   */
  static async startScenario(
    request: StartScenarioRequest
  ): Promise<StartScenarioResponse> {
    return await makeRequest<StartScenarioResponse>("/api/scenarios/start", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
  /**
   * Envoie un message pour jouer le scénario
   */
  static async playScenario(
    sessionId: string,
    request: PlayScenarioRequest
  ): Promise<PlayScenarioResponse> {
    this.validateSessionParams(sessionId);
    const params = new URLSearchParams({ session_id: sessionId });
    return await makeRequest<PlayScenarioResponse>(
      `/api/scenarios/play?${params}`,
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }
  /**
   * Récupère l'historique complet d'une session de jeu
   */
  static async getScenarioHistory(sessionId: string): Promise<ConversationMessage[]> {
    this.validateSessionParams(sessionId);
    const result = await makeRequest<GetScenarioHistoryResponse>(
      `/api/scenarios/history/${sessionId}`
    );
    return result.history || [];
  }

  // ========================================
  // Gestion des sessions en cours
  // ========================================

  /**
   * Récupère la liste des sessions de jeu en cours (API REST)
   * Utilise l'endpoint /api/scenarios/sessions (voir openapi.json)
   * @returns {Promise<GameSession[]>} Liste des sessions actives
   */
  static async getActiveSessions(): Promise<GameSession[]> {
    const result = await makeRequest<{ sessions: any[] }>("/api/scenarios/sessions");
    // Adaptation du format backend -> frontend
    return result.sessions.map((s) => ({
      session_id: s.session_id,
      scenario_name: s.scenario_name,
      character_name: s.character_name,
      status: "active", // Le backend ne fournit pas de statut, on suppose "active"
      last_activity: new Date().toISOString(), // Optionnel, à améliorer si le backend fournit l'info
    }));
  }
  /**
   * Récupère une session spécifique par son ID
   */
  static async getSession(sessionId: string): Promise<GameSession | null> {
    if (!this.isValidUUID(sessionId)) {
      return null;
    }
    const sessions = await this.getActiveSessions();
    return sessions.find((session) => session.session_id === sessionId) || null;
  }


  // ========================================
  // Création de personnage (API REST)
  // ========================================

  /**
   * Alloue automatiquement les caractéristiques selon la race
   */
  static async allocateAttributes(
    request: AllocateAttributesRequest
  ): Promise<AllocateAttributesResponse> {
    return await makeRequest<AllocateAttributesResponse>(
      "/api/creation/allocate-attributes",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Vérifie la validité d'une répartition de caractéristiques
   */
  static async checkAttributes(
    request: CheckAttributesRequest
  ): Promise<CheckAttributesResponse> {
    return await makeRequest<CheckAttributesResponse>(
      "/api/creation/check-attributes",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Crée un nouveau personnage (état initial, id, date)
   */
  static async createNewCharacter(): Promise<CreationStatusResponse> {
    return await makeRequest<CreationStatusResponse>(
      "/api/creation/new",
      { method: "POST" }
    );
  }

  /**
   * Sauvegarde ou met à jour les données du personnage
   */
  static async saveCharacter(
    request: SaveCharacterRequest
  ): Promise<SaveCharacterResponse> {
    return await makeRequest<SaveCharacterResponse>(
      "/api/creation/save",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Vérifie la validité de la répartition des compétences
   */
  static async checkSkills(
    request: CheckSkillsRequest
  ): Promise<CheckSkillsResponse> {
    return await makeRequest<CheckSkillsResponse>(
      "/api/creation/check-skills",
      {
        method: "POST",
        body: JSON.stringify(request),
      }
    );
  }

  /**
   * Récupère le statut de création d'un personnage
   */
  static async getCreationStatus(
    characterId: string
  ): Promise<CreationStatusResponse> {
    return await makeRequest<CreationStatusResponse>(
      `/api/creation/status/${characterId}`
    );
  }

  /**
   * Récupère la liste brute des races (structure du JSON)
   */
  static async getRaces(): Promise<RaceData[]> {
    return await makeRequest<RaceData[]>("/api/creation/races");
  }

  /**
   * Récupère la structure complète des groupes de compétences (JSON brut)
   */
  static async getSkills(): Promise<SkillGroupsDict> {
    return await makeRequest<SkillGroupsDict>("/api/creation/skills");
  }

  /**
   * Récupère la liste des équipements disponibles
   */
  static async getEquipments(): Promise<string[]> {
    return await makeRequest<string[]>("/api/creation/equipments");
  }

  /**
   * Récupère la liste des sorts disponibles
   */
  static async getSpells(): Promise<string[]> {
    return await makeRequest<string[]>("/api/creation/spells");
  }

  // ========================================
  // Appels aux routes LLM (génération nom, background, description physique)
  // ========================================

  /**
   * Génère un nom de personnage via LLM à partir d'une fiche partielle
   */
  static async generateCharacterName(character: Partial<Character>): Promise<string> {
    const result = await makeRequest<GenerateNameResponse>(
      "/creation/generate-name",
      {
        method: "POST",
        body: JSON.stringify(character),
      }
    );
    return result.name;
  }

  /**
   * Génère un background d'histoire via LLM (character partiel accepté)
   */
  static async generateCharacterBackground(character: Partial<Character>): Promise<string> {
    const result = await makeRequest<GenerateBackgroundResponse>(
      "/creation/generate-background",
      {
        method: "POST",
        body: JSON.stringify(character),
      }
    );
    return result.background;
  }

  /**
   * Génère une description physique via LLM (character partiel accepté)
   */
  static async generateCharacterPhysicalDescription(character: Partial<Character>): Promise<string> {
    const result = await makeRequest<GeneratePhysicalDescriptionResponse>(
      "/creation/generate-physical-description",
      {
        method: "POST",
        body: JSON.stringify(character),
      }
    );
    return result.physical_description;
  }

  // ========================================
  // Utilitaires et helpers
  // ========================================

  /**
   * Vérifie si l'API backend est accessible
   */
  static async healthCheck(): Promise<boolean> {
    try {
      await this.getCharacters();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Formate un nom de scénario pour l'affichage
   */
  static formatScenarioName(name: string): string {
    return name
      .replace(/\.md$/, "") // Retire l'extension .md
      .replace(/_/g, " ") // Remplace les underscores par des espaces
      .replace(/\b\w/g, (l) => l.toUpperCase()); // Met en forme title case
  }
  /**
   * Convertit un Character en CharacterContext pour les interfaces existantes
   */
  static characterToContext(character: Character): CharacterContext {
    return {
      id: character.id,
      name: character.name,
      race: character.race.name,
      culture: character.culture.name,
      profession: character.profession,
      caracteristiques: character.caracteristiques,
      competences: character.competences,
      hp: character.hp,
      inventory: character.inventory?.map((item) => item.name) || [],
      equipment: character.equipment || [],
      spells: character.spells || [],
      equipment_summary: {
        total_cost: character.equipment_summary?.total_cost || 0,
        total_weight: character.equipment_summary?.total_weight || 0,
        remaining_money: character.equipment_summary?.remaining_money || 0,
        starting_money: character.equipment_summary?.starting_money || 0,
      },
      culture_bonuses: character.culture_bonuses || {},
    };
  }
  /**
   * Génère un ID de session temporaire (pour les tests ou fallback)
   */
  static generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Valide qu'une chaîne est un UUID valide
   */
  static isValidUUID(uuid: string): boolean {
    const uuidRegex =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  }

  /**
   * Valide les paramètres d'une session avant l'appel API
   */
  static validateSessionParams(sessionId: string): void {
    if (!sessionId) {
      throw new ApiError(400, "Session ID is required");
    }
    if (!this.isValidUUID(sessionId)) {
      throw new ApiError(400, "Invalid session ID format");
    }
  }

  /**
   * Gère les erreurs API de manière cohérente
   */
  static handleApiError(error: unknown): never {
    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      throw new ApiError(0, `Erreur inattendue: ${error.message}`);
    }

    throw new ApiError(0, "Erreur inconnue");
  }
}

// Export par défaut du service
export default JdrApiService;

// Re-export des types principaux de interfaces.ts pour une utilisation simplifiée
export type {
  Character,
  CharacterList,
  ScenarioStatus,
  ScenarioList,
  StartScenarioRequest,
  StartScenarioResponse,
  PlayScenarioRequest,
  PlayScenarioResponse,
} from './interfaces';

// Note: GameSession et CombatAttackRequest sont déjà exportés via leurs définitions d'interface ci-dessus
