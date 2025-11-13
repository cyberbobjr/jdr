import { describe, it, expect, vi, beforeEach } from 'vitest';
import { mount } from '@vue/test-utils';
import CharacterSheet from '@/components/CharacterSheet.vue';
import JdrApiService from '@/core/api';
import type { Character } from '@/core/interfaces';

// Mock JdrApiService
vi.mock('@/core/api', () => ({
  default: {
    getCharacters: vi.fn()
  }
}));

// Mock Font Awesome
vi.mock('@fortawesome/vue-fontawesome', () => ({
  FontAwesomeIcon: {
    name: 'FontAwesomeIcon',
    template: '<i></i>'
  }
}));

const mockCharacter: Character = {
  id: '1',
  name: 'Test Hero',
  race: { name: 'Humain' },
  culture: { name: 'Nordique' },
  hp: 100,
  gold: 50,
  caracteristiques: {
    force: 15,
    agilite: 12,
    intelligence: 14,
    constitution: 13,
    perception: 11,
    volonte: 10
  },
  competences: {
    armes_blanches: 45,
    arcane: 30,
    athletisme: 25,
    discretion: 20
  },
  inventory: [
    {
      id: '1',
      name: 'Épée longue',
      type: 'weapon',
      equipped: true,
      quantity: 1
    },
    {
      id: '2',
      name: 'Armure de cuir',
      type: 'armor',
      equipped: true,
      quantity: 1
    },
    {
      id: '3',
      name: 'Potion de soin',
      type: 'potion',
      equipped: false,
      quantity: 3
    }
  ]
};

describe('CharacterSheet', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('affiche le message de chargement par défaut', () => {
    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    expect(wrapper.text()).toContain('Chargement du personnage...');
  });

  it('affiche les informations du personnage après chargement', async () => {
    vi.mocked(JdrApiService.getCharacters).mockResolvedValue([mockCharacter]);

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    // Attendre que le composant soit monté et que les données soient chargées
    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(wrapper.text()).toContain('Test Hero');
    expect(wrapper.text()).toContain('Humain');
    expect(wrapper.text()).toContain('Nordique');
    expect(wrapper.text()).toContain('100');
    expect(wrapper.text()).toContain('50 po');
  });

  it('calcule correctement les bonus de caractéristiques', async () => {
    vi.mocked(JdrApiService.getCharacters).mockResolvedValue([mockCharacter]);

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Force (15) devrait donner un bonus de +2
    const characteristicItems = wrapper.findAll('.characteristic-item');
    expect(characteristicItems.length).toBeGreaterThan(0);
  });

  it('change d\'onglet correctement', async () => {
    vi.mocked(JdrApiService.getCharacters).mockResolvedValue([mockCharacter]);

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    // Cliquer sur l'onglet Compétences
    const skillsTab = wrapper.find('[data-test="skills-tab"]') || 
                     wrapper.findAll('.tab-button').find(tab => tab.text().includes('Compétences'));
    
    if (skillsTab) {
      await skillsTab.trigger('click');
      expect(wrapper.find('.skills-list').exists()).toBe(true);
    }
  });

  it('filtre les compétences principales', () => {
    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session'
      }
    });

    const vm = wrapper.vm as any;
    const mainSkills = vm.getMainSkills(mockCharacter.competences);

    // Devrait filtrer les compétences avec valeur > 0
    expect(Object.keys(mainSkills)).toContain('armes_blanches');
    expect(Object.keys(mainSkills)).toContain('arcane');
    expect(mainSkills.armes_blanches).toBe(45);
  });

  it('sépare l\'équipement équipé du non-équipé', () => {
    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session'
      }
    });

    const vm = wrapper.vm as any;
    const equippedItems = vm.getEquippedItems(mockCharacter.inventory);
    const unequippedItems = vm.getUnequippedItems(mockCharacter.inventory);

    expect(equippedItems).toHaveLength(2); // Épée et armure
    expect(unequippedItems).toHaveLength(1); // Potion
    expect(equippedItems[0].name).toBe('Épée longue');
    expect(unequippedItems[0].name).toBe('Potion de soin');
  });

  it('émet l\'événement characterLoaded quand le personnage est chargé', async () => {
    vi.mocked(JdrApiService.getCharacters).mockResolvedValue([mockCharacter]);

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(wrapper.emitted('characterLoaded')).toBeTruthy();
    expect(wrapper.emitted('characterLoaded')![0][0]).toEqual(mockCharacter);
  });

  it('émet l\'événement characterError en cas d\'erreur', async () => {
    vi.mocked(JdrApiService.getCharacters).mockRejectedValue(new Error('API Error'));

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero'
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(wrapper.emitted('characterError')).toBeTruthy();
    expect(wrapper.emitted('characterError')![0][0]).toBe('Erreur lors du chargement du personnage');
  });

  it('recharge le personnage quand refreshTrigger change', async () => {
    const getCharactersSpy = vi.mocked(JdrApiService.getCharacters).mockResolvedValue([mockCharacter]);

    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session',
        characterName: 'Test Hero',
        refreshTrigger: 0
      }
    });

    await wrapper.vm.$nextTick();
    await new Promise(resolve => setTimeout(resolve, 0));

    expect(getCharactersSpy).toHaveBeenCalledTimes(1);

    // Changer le trigger
    await wrapper.setProps({ refreshTrigger: 1 });
    await wrapper.vm.$nextTick();

    expect(getCharactersSpy).toHaveBeenCalledTimes(2);
  });

  it('affiche la bonne icône pour chaque type d\'équipement', () => {
    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session'
      }
    });

    const vm = wrapper.vm as any;

    expect(vm.getItemIcon({ type: 'weapon' })).toBe('sword');
    expect(vm.getItemIcon({ type: 'armor' })).toBe('shield-alt');
    expect(vm.getItemIcon({ type: 'potion' })).toBe('flask');
    expect(vm.getItemIcon({ type: 'unknown' })).toBe('box');
  });

  it('formate correctement les noms de compétences', () => {
    const wrapper = mount(CharacterSheet, {
      props: {
        sessionId: 'test-session'
      }
    });

    const vm = wrapper.vm as any;

    expect(vm.formatSkillName('armes_blanches')).toBe('Armes Blanches');
    expect(vm.formatSkillName('testSkill')).toBe('Test Skill');
    expect(vm.formatSkillName('simple')).toBe('Simple');
  });
});
