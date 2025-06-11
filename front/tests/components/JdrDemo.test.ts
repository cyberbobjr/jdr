/**
 * Tests pour le composant JdrDemo
 * Vérifie l'affichage et les fonctionnalités de base
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import JdrDemo from '@/components/JdrDemo.vue'

// Mock FontAwesome
const mockFontAwesome = {
  template: '<i></i>',
  props: ['icon']
}

describe('JdrDemo', () => {
  let wrapper: any

  beforeEach(() => {
    // Mock du composant FontAwesome
    wrapper = mount(JdrDemo, {
      global: {
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
  })

  it('devrait se monter correctement', () => {
    expect(wrapper).toBeTruthy()
  })

  it('devrait afficher le titre principal', () => {
    expect(wrapper.text()).toContain('Démonstration des fonctionnalités')
  })

  it('devrait afficher la section lanceur de dés', () => {
    expect(wrapper.text()).toContain('Lanceur de dés')
    expect(wrapper.text()).toContain('Lancer le dé')
  })

  it('devrait afficher la fiche de personnage', () => {
    expect(wrapper.text()).toContain('Fiche de personnage')
    expect(wrapper.text()).toContain('Elara la Magicienne')
    expect(wrapper.text()).toContain('Points de vie')
    expect(wrapper.text()).toContain('Points de magie')
  })

  it('devrait avoir des boutons d\'action', () => {
    expect(wrapper.text()).toContain('Combat')
    expect(wrapper.text()).toContain('Inventaire')
    expect(wrapper.text()).toContain('Sorts')
    expect(wrapper.text()).toContain('Paramètres')
  })

  it('devrait gérer le clic sur le bouton de lancer de dé', async () => {
    const rollButton = wrapper.find('button')
    expect(rollButton.exists()).toBe(true)
    
    // Simuler un clic
    await rollButton.trigger('click')
    
    // Vérifier que le bouton change d'état
    expect(rollButton.text()).toContain('Lancement...')
  })

  it('devrait afficher les statistiques du personnage', () => {
    // Vérifier que les caractéristiques sont affichées
    const statsSection = wrapper.find('.grid.grid-cols-3')
    expect(statsSection.exists()).toBe(true)
      // Vérifier quelques stats
    expect(wrapper.text()).toContain('str') // Strength abrégé en minuscules
    expect(wrapper.text()).toContain('int') // Intelligence abrégé en minuscules
  })

  it('devrait afficher les barres de progression', () => {
    // Vérifier que les barres de vie et magie sont présentes
    const progressBars = wrapper.findAll('.bg-red-500, .bg-blue-500')
    expect(progressBars.length).toBeGreaterThanOrEqual(2)
  })
})
