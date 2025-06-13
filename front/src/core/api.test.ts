// Tests unitaires pour le service API
// Validation des interfaces et de la logique métier

import { describe, it, expect, vi } from 'vitest';
import JdrApiService, { ApiError, type GameSession, type CombatAttackRequest } from './api';
import type { 
  Character, 
  StartScenarioRequest, 
  PlayScenarioRequest 
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
    });

    it('doit convertir un Character en CharacterContext', () => {
      const character: Character = {
        id: '550e8400-e29b-41d4-a716-446655440000',
        name: 'Test Character',
        race: 'Hobbit',
        culture: 'Comté',
        profession: 'Cambrioleur',
        caracteristiques: { force: 10, dexterite: 15 },
        competences: { discretion: 20, crochetage: 15 },
        hp: 100,
        inventory: [
          { id: '1', name: 'Épée', weight: 2.5, base_value: 100 }
        ],
        equipment: ['Armure de cuir'],
        spells: ['Lumière'],
        equipment_summary: { total_cost: 150, total_weight: 10, remaining_money: 50, starting_money: 200 },
        culture_bonuses: { dexterite: 2 }
      };

      const context = JdrApiService.characterToContext(character);
      
      expect(context.id).toBe(character.id);
      expect(context.name).toBe(character.name);
      expect(context.inventory).toEqual(['Épée']);
      expect(context.equipment_summary.total_cost).toBe(150);
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
});
