import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/sessions',
      name: 'sessions',
      component: () => import('../views/SessionsView.vue'),
      meta: {
        title: 'Sessions en Cours',
        description: 'Liste des sessions de jeu actives'
      }
    },
    {
      path: '/nouveau-scenario',
      name: 'nouveau-scenario',
      component: () => import('../views/NouveauScenarioView.vue'),
      meta: {
        title: 'Nouvelle Aventure',
        description: 'Démarrer un nouveau scénario'
      }
    },
    {
      path: '/jeu/:sessionId',
      name: 'jeu',
      component: () => import('../views/JeuView.vue'),
      props: true,
      meta: {
        title: 'Jeu en Cours',
        description: 'Session de jeu active'
      }
    },
    {
      path: '/personnages',
      name: 'personnages',
      component: () => import('../views/PersonnagesView.vue'),
      meta: {
        title: 'Personnages',
        description: 'Gestion des personnages'
      }
    },
    {
      path: '/scenarios',
      name: 'scenarios',
      component: () => import('../views/ScenariosView.vue'),
      meta: {
        title: 'Scénarios',
        description: 'Bibliothèque de scénarios'
      }
    }
  ],
})

export default router
