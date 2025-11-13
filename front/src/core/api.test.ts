// Tests unitaires pour le service API
// Validation des interfaces et de la logique métier

import { describe, it, expect, vi, beforeEach } from 'vitest';
import JdrApiService, { ApiError, type GameSession, type CombatAttackRequest } from './api';
import type { 
  Character, 
  RaceData,
  CultureData,
  Item,
  CharacteristicsData
} from './interfaces';

// Mock de fetch pour les tests
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('JdrApiService', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  describe('Validation des UUIDs', () => {
    it('doit valider un UUID correct', () => {
      const validUUID = '550e8400-e29b-41d4-a716-446655440000';
      expect(JdrApiService.isValidUUID(validUUID)).toBe(true);
    });

    it('doit rejeter un UUID incorrect', () => {
      const invalidUUID = 'invalid-uuid';
      expect(JdrApiService.isValidUUID(invalidUUID)).toBe(false);
    });

    it('doit lever une erreur pour un sessionId invalide', () => {
      expect(() => {
        JdrApiService.validateSessionParams('invalid-uuid');
      }).toThrow(ApiError);
    });
  });

  describe('Gestion des erreurs', () => {
    it('doit créer une ApiError avec les bons paramètres', () => {
      const error = new ApiError(404, 'Not Found', { detail: 'Resource not found' });
      expect(error.status).toBe(404);
      expect(error.message).toBe('Not Found');
      expect(error.details).toEqual({ detail: 'Resource not found' });
    });

    it('doit gérer les erreurs inconnues', () => {
      expect(() => {
        JdrApiService.handleApiError(new Error('Test error'));
      }).toThrow(ApiError);
    });
  });

  describe('Utilitaires', () => {
    it('doit générer un ID de session valide', () => {
      const sessionId = JdrApiService.generateSessionId();
      expect(sessionId).toMatch(/^session_\d+_[a-z0-9]+$/);
    });

    it('doit formater correctement un nom de scénario', () => {
      const formatted = JdrApiService.formatScenarioName('Les_Pierres_du_Passe.md');
      expect(formatted).toBe('Les Pierres Du Passe');
    });    it('doit convertir un Character en CharacterContext', () => {
      const character: Character = {
        id: '550e8400-e29b-41d4-a716-446655440000',
        status: 'active',
        name: 'Test Character',
        race: {
          name: 'Hobbit',
          characteristic_bonuses: { Constitution: 2, Agilité: 1 },
          destiny_points: 8,
          special_abilities: ['Chance extraordinaire'],
          base_languages: ['Hobbitais'],
          optional_languages: ['Westron']
        } as RaceData,
        culture: {
          name: 'Comté',
          description: 'Culture paisible du Comté',
          skill_bonuses: { 'Artisanat': 2 },
          characteristic_bonuses: { Constitution: 1 }
        } as CultureData,
        caracteristiques: { Force: 10, Agilité: 15 },        competences: { Discretion: 20, Crochetage: 15 },
        hp: 100,
        gold: 50,        inventory: [
          { id: '1', name: 'Épée', weight: 2.5, base_value: 100 } as Item
        ],
        spells: ['Lumière'],
        culture_bonuses: { Constitution: 1 }
      };

      const context = JdrApiService.characterToContext(character);
      
      expect(context.id).toBe(character.id);
      expect(context.name).toBe(character.name);
      expect(context.inventory).toEqual(['Épée']);
      expect(context.gold).toBe(50);
    });
  });

  describe('Interfaces TypeScript', () => {
    it('doit respecter l\'interface GameSession', () => {
      const session: GameSession = {
        session_id: '550e8400-e29b-41d4-a716-446655440000',
        scenario_name: 'Les Pierres du Passé',
        character_name: 'Bilbon Baggins',
        status: 'active',
        last_activity: new Date().toISOString()
      };

      expect(session.session_id).toBeDefined();
      expect(['active', 'paused', 'completed']).toContain(session.status);
    });

    it('doit respecter l\'interface CombatAttackRequest', () => {
      const request: CombatAttackRequest = {
        attacker_id: 'attacker-uuid',
        target_id: 'target-uuid',
        attack_value: 15,
        combat_state: {
          round: 1,
          participants: ['attacker-uuid', 'target-uuid']
        }
      };

      expect(request.attacker_id).toBeDefined();
      expect(request.target_id).toBeDefined();
      expect(typeof request.attack_value).toBe('number');
      expect(typeof request.combat_state).toBe('object');
    });
  });
  describe('Routes de création', () => {
    it('doit appeler la route characteristics correctement', async () => {      const mockCharacteristics: CharacteristicsData = {
        characteristics: {
          "Force": {
            "short_name": "FOR",
            "category": "physical",
            "description": "Force physique, carrure. Détermine les dégâts au corps à corps et la capacité de port.",
            "examples": ["Soulever des objets lourds", "Briser une porte", "Dégâts d'arme de mêlée"]
          }
        },
        bonus_table: {
          "46-50": 0,
          "51-55": 1,
          "56-60": 2
        },
        cost_table: {
          "1-90": 1,
          "91-95": 2
        },
        starting_points: 550,
        maximum_starting_value: 90
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCharacteristics),
        headers: { get: () => 'application/json' }
      });

      const result = await JdrApiService.getCharacteristics();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/creation/characteristics',
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          })
        })
      );
      expect(result).toEqual(mockCharacteristics);
      expect(result.characteristics.Force.short_name).toBe('FOR');
      expect(result.starting_points).toBe(550);
    });
  });
});
