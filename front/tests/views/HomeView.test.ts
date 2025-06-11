/**
 * Tests pour la vue HomeView
 * Vérifie l'affichage de la page d'accueil
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import JdrDemo from '@/components/JdrDemo.vue'

// Mock FontAwesome
const mockFontAwesome = {
  template: '<i></i>',
  props: ['icon']
}

// Configuration du router pour les tests
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/sessions', component: { template: '<div>Sessions</div>' } },
    { path: '/nouveau-scenario', component: { template: '<div>Nouveau Scenario</div>' } },
    { path: '/personnages', component: { template: '<div>Personnages</div>' } },
    { path: '/scenarios', component: { template: '<div>Scenarios</div>' } }
  ]
})

describe('HomeView', () => {  it('devrait se monter correctement', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper).toBeTruthy()
  })
  it('devrait afficher le titre principal', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper.text()).toContain('Terres du Milieu')
  })
  it('devrait afficher la description', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper.text()).toContain('Vivez des aventures épiques dans l\'univers du Jeu de Rôle des Terres du Milieu')
  })
  it('devrait afficher les fonctionnalités principales', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper.text()).toContain('Personnages')
    expect(wrapper.text()).toContain('Combat')
    expect(wrapper.text()).toContain('Scénarios')
    expect(wrapper.text()).toContain('Sessions')
  })
  it('devrait afficher les statistiques du projet', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper.text()).toContain('Vue.js')
    expect(wrapper.text()).toContain('TypeScript')
    expect(wrapper.text()).toContain('FastAPI')
  })
  it('devrait avoir des boutons d\'action principaux', () => {
    const wrapper = mount(HomeView, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome,
          'JdrDemo': JdrDemo
        }
      }
    })
    
    expect(wrapper.text()).toContain('Commencer une Aventure')
    expect(wrapper.text()).toContain('Sessions en Cours')
  })
})
