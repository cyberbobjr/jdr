/**
 * Tests pour le composant App
 * Vérifie la structure principale de l'application
 */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import App from '@/App.vue'

// Mock FontAwesome
const mockFontAwesome = {
  template: '<i></i>',
  props: ['icon']
}

// Configuration du router pour les tests avec les nouvelles routes
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: { template: '<div>Home</div>' } },
    { path: '/sessions', component: { template: '<div>Sessions</div>' } },
    { path: '/nouveau-scenario', component: { template: '<div>Nouveau Scenario</div>' } },
    { path: '/personnages', component: { template: '<div>Personnages</div>' } },
    { path: '/scenarios', component: { template: '<div>Scenarios</div>' } },
    { path: '/jeu/:sessionId', component: { template: '<div>Jeu</div>' } }
  ]
})

describe('App', () => {
  it('devrait se monter correctement', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
    
    expect(wrapper).toBeTruthy()
  })
  it('devrait afficher le header avec navigation', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
    
    expect(wrapper.text()).toContain('Terres du Milieu')
    expect(wrapper.text()).toContain('Accueil')
    expect(wrapper.text()).toContain('Sessions')
  })
  it('devrait afficher le footer', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
    
    expect(wrapper.text()).toContain('Créé avec Vue.js 3, TypeScript, TailwindCSS et FastAPI')
  })
  it('devrait avoir les liens de navigation', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
    
    const homeLink = wrapper.find('a[href="/"]')
    const sessionsLink = wrapper.find('a[href="/sessions"]')
    
    expect(homeLink.exists()).toBe(true)
    expect(sessionsLink.exists()).toBe(true)
  })
  it('devrait appliquer les styles personnalisés correctement', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [router],
        components: {
          'font-awesome-icon': mockFontAwesome
        }
      }
    })
    
    // Vérifier la présence de classes de notre thème personnalisé
    expect(wrapper.find('.app-container').exists() || wrapper.find('[class*="jdr"]').exists()).toBe(true)
  })
})
