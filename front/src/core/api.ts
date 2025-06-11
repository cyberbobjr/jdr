// Service API pour l'application JDR "Terres du Milieu"
// Gestion complète des appels backend FastAPI + PydanticAI

import type { CharacterContext } from './interfaces';

// ========================================
// Configuration et types API
// ========================================

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types pour les requêtes et réponses API
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

export interface Item {
  id: string;
  name: string;
  weight: number;
  base_value: number;
}

export interface CharacterList {
  characters: Character[];
}

export interface ScenarioStatus {
  name: string;
  status: string;
  session_id?: string | null;
  scenario_name?: string | null;
  character_name?: string | null;
}

export interface ScenarioList {
  scenarios: ScenarioStatus[];
}

export interface StartScenarioRequest {
  scenario_name: string;
  character_id: string;
}

export interface StartScenarioResponse {
  session_id: string;
  scenario_name: string;
  character_id: string;
  message: string;
  initial_response: string;
}

export interface PlayScenarioRequest {
  message: string;
}

export interface PlayScenarioResponse {
  response: string;
  tool_calls?: any[];
}

export interface GameSession {
  session_id: string;
  scenario_name: string;
  character_name: string;
  status: 'active' | 'paused' | 'completed';
  last_activity: string;
}

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
    this.name = 'ApiError';
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
    'Content-Type': 'application/json',
    'Accept': 'application/json',
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
      let errorDetails;

      try {
        errorDetails = await response.json();
        if (errorDetails.detail) {
          errorMessage = Array.isArray(errorDetails.detail) 
            ? errorDetails.detail.map((d: any) => d.msg).join(', ')
            : errorDetails.detail;
        }
      } catch {
        // Si on ne peut pas parser le JSON d'erreur, on garde le message HTTP
      }

      throw new ApiError(response.status, errorMessage, errorDetails);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    } else {
      return await response.text() as unknown as T;
    }
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Erreur de réseau ou autre
    throw new ApiError(0, `Erreur de connexion: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
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
    const result = await makeRequest<CharacterList>('/api/characters/');
    return result.characters;
  }

  /**
   * Récupère un personnage par son ID
   */
  static async getCharacter(id: string): Promise<Character | null> {
    const characters = await this.getCharacters();
    return characters.find(char => char.id === id) || null;
  }

  // ========================================
  // Gestion des scénarios
  // ========================================

  /**
   * Récupère la liste de tous les scénarios avec leur statut
   */
  static async getScenarios(): Promise<ScenarioStatus[]> {
    const result = await makeRequest<ScenarioList>('/api/scenarios/');
    return result.scenarios;
  }

  /**
   * Récupère le contenu détaillé d'un scénario
   */
  static async getScenarioDetails(scenarioFile: string): Promise<string> {
    return await makeRequest<string>(`/api/scenarios/${encodeURIComponent(scenarioFile)}`);
  }

  /**
   * Démarre un nouveau scénario avec un personnage
   */
  static async startScenario(request: StartScenarioRequest): Promise<StartScenarioResponse> {
    return await makeRequest<StartScenarioResponse>('/api/scenarios/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Envoie un message pour jouer le scénario
   */
  static async playScenario(sessionId: string, request: PlayScenarioRequest): Promise<PlayScenarioResponse> {
    const params = new URLSearchParams({ session_id: sessionId });
    return await makeRequest<PlayScenarioResponse>(`/api/scenarios/play?${params}`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Récupère l'historique complet d'une session de jeu
   */
  static async getScenarioHistory(sessionId: string): Promise<any[]> {
    const result = await makeRequest<{ history: any[] }>(`/api/scenarios/history/${sessionId}`);
    return result.history || [];
  }

  // ========================================
  // Gestion des sessions en cours
  // ========================================

  /**
   * Récupère la liste des sessions de jeu en cours
   */
  static async getActiveSessions(): Promise<GameSession[]> {
    const scenarios = await this.getScenarios();
    const activeSessions: GameSession[] = [];

    for (const scenario of scenarios) {
      if (scenario.status === 'active' && scenario.session_id) {
        activeSessions.push({
          session_id: scenario.session_id,
          scenario_name: scenario.scenario_name || scenario.name,
          character_name: scenario.character_name || 'Personnage inconnu',
          status: 'active',
          last_activity: new Date().toISOString(), // On pourrait récupérer cela du backend
        });
      }
    }

    return activeSessions;
  }

  /**
   * Récupère une session spécifique par son ID
   */
  static async getSession(sessionId: string): Promise<GameSession | null> {
    const sessions = await this.getActiveSessions();
    return sessions.find(session => session.session_id === sessionId) || null;
  }

  // ========================================
  // Gestion du combat
  // ========================================

  /**
   * Effectue une attaque dans le système de combat
   */
  static async performAttack(request: CombatAttackRequest): Promise<Record<string, any>> {
    const params = new URLSearchParams({
      attacker_id: request.attacker_id,
      target_id: request.target_id,
      attack_value: request.attack_value.toString(),
    });

    return await makeRequest<Record<string, any>>(`/api/combat/attack?${params}`, {
      method: 'POST',
      body: JSON.stringify(request.combat_state),
    });
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
      .replace(/\.md$/, '') // Retire l'extension .md
      .replace(/_/g, ' ') // Remplace les underscores par des espaces
      .replace(/\b\w/g, l => l.toUpperCase()); // Met en forme title case
  }

  /**
   * Convertit un Character en CharacterContext pour les interfaces existantes
   */
  static characterToContext(character: Character): CharacterContext {
    return {
      id: character.id,
      name: character.name,
      race: character.race,
      culture: character.culture,
      profession: character.profession,
      caracteristiques: character.caracteristiques,
      competences: character.competences,
      hp: character.hp,
      inventory: character.inventory?.map(item => item.name) || [],
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
}

// Export par défaut du service
export default JdrApiService;

// Export des types pour utilisation dans les composants
export type {
  Character,
  CharacterList,
  ScenarioStatus,
  ScenarioList,
  StartScenarioRequest,
  StartScenarioResponse,
  PlayScenarioRequest,
  PlayScenarioResponse,
  GameSession,
  CombatAttackRequest,
};
