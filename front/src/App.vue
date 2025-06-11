<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { ref } from 'vue'

const isMobileMenuOpen = ref(false)

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}
</script>

<template>
  <div class="app-container">
    <!-- Navigation Header -->
    <header class="jdr-navbar">
      <div class="jdr-container">
        <div class="navbar-content jdr-flex jdr-justify-between jdr-items-center">
          <!-- Logo et titre -->
          <RouterLink to="/" class="jdr-navbar-brand">
            <font-awesome-icon :icon="['fas', 'dice-d20']" />
            Terres du Milieu
          </RouterLink>

          <!-- Navigation Desktop -->
          <nav class="desktop-nav jdr-navbar-nav">
            <RouterLink 
              to="/" 
              class="jdr-navbar-link"
              exact-active-class="active"
            >
              <font-awesome-icon :icon="['fas', 'home']" />
              Accueil
            </RouterLink>
            <RouterLink 
              to="/sessions" 
              class="jdr-navbar-link"
              active-class="active"
            >
              <font-awesome-icon :icon="['fas', 'gamepad']" />
              Sessions
            </RouterLink>
            <RouterLink 
              to="/nouveau-scenario" 
              class="jdr-navbar-link"
              active-class="active"
            >
              <font-awesome-icon :icon="['fas', 'rocket']" />
              Nouvelle Aventure
            </RouterLink>
            <RouterLink 
              to="/personnages" 
              class="jdr-navbar-link"
              active-class="active"
            >
              <font-awesome-icon :icon="['fas', 'user-shield']" />
              Personnages
            </RouterLink>
            <RouterLink 
              to="/scenarios" 
              class="jdr-navbar-link"
              active-class="active"
            >
              <font-awesome-icon :icon="['fas', 'scroll']" />
              Scénarios
            </RouterLink>
          </nav>

          <!-- Bouton menu mobile -->
          <button 
            @click="toggleMobileMenu"
            class="mobile-menu-btn jdr-btn jdr-btn-outline jdr-btn-sm"
          >
            <font-awesome-icon :icon="['fas', isMobileMenuOpen ? 'times' : 'bars']" />
          </button>
        </div>

        <!-- Navigation Mobile -->
        <nav v-show="isMobileMenuOpen" class="mobile-nav">
          <RouterLink 
            to="/" 
            class="mobile-nav-link"
            @click="isMobileMenuOpen = false"
          >
            <font-awesome-icon :icon="['fas', 'home']" />
            Accueil
          </RouterLink>
          <RouterLink 
            to="/sessions" 
            class="mobile-nav-link"
            @click="isMobileMenuOpen = false"
          >
            <font-awesome-icon :icon="['fas', 'gamepad']" />
            Sessions en Cours
          </RouterLink>
          <RouterLink 
            to="/nouveau-scenario" 
            class="mobile-nav-link"
            @click="isMobileMenuOpen = false"
          >
            <font-awesome-icon :icon="['fas', 'rocket']" />
            Nouvelle Aventure
          </RouterLink>
          <RouterLink 
            to="/personnages" 
            class="mobile-nav-link"
            @click="isMobileMenuOpen = false"
          >
            <font-awesome-icon :icon="['fas', 'user-shield']" />
            Personnages
          </RouterLink>
          <RouterLink 
            to="/scenarios" 
            class="mobile-nav-link"
            @click="isMobileMenuOpen = false"
          >
            <font-awesome-icon :icon="['fas', 'scroll']" />
            Scénarios
          </RouterLink>
        </nav>
      </div>
    </header>

    <!-- Contenu principal -->
    <main class="main-content">
      <RouterView />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="jdr-container">
        <div class="footer-content jdr-text-center">
          <div class="footer-info">
            <font-awesome-icon :icon="['fas', 'dice-d20']" />
            <span>JDR "Terres du Milieu" - Système basé sur le Jeu de Rôle des Terres du Milieu</span>
          </div>
          <div class="footer-tech">
            <font-awesome-icon :icon="['fas', 'code']" />
            <span>Créé avec Vue.js 3, TypeScript, TailwindCSS et FastAPI</span>
            <font-awesome-icon :icon="['fas', 'heart']" />
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--jdr-bg-primary) 0%, var(--jdr-bg-secondary) 100%);
}

.navbar-content {
  padding: 1rem 0;
}

.desktop-nav {
  display: none;
}

.mobile-menu-btn {
  display: flex;
}

.mobile-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem 0;
  border-top: 1px solid var(--jdr-border-color);
  margin-top: 1rem;
}

.mobile-nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: var(--jdr-text-secondary);
  text-decoration: none;
  border-radius: var(--jdr-border-radius);
  transition: all 0.3s ease;
}

.mobile-nav-link:hover {
  background: var(--jdr-bg-tertiary);
  color: var(--jdr-secondary);
}

.mobile-nav-link.router-link-active {
  background: var(--jdr-bg-tertiary);
  color: var(--jdr-secondary);
  border-left: 4px solid var(--jdr-secondary);
}

.main-content {
  flex: 1;
  min-height: 0;
}

.app-footer {
  background: linear-gradient(145deg, var(--jdr-bg-primary), var(--jdr-bg-secondary));
  border-top: 1px solid var(--jdr-border-color);
  padding: 2rem 0;
  margin-top: auto;
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
}

.footer-info,
.footer-tech {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--jdr-text-muted);
  font-size: 0.9rem;
}

.footer-info {
  font-weight: 500;
}

.footer-tech {
  font-size: 0.8rem;
}

/* Navigation desktop */
@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }
  
  .mobile-menu-btn {
    display: none;
  }
  
  .mobile-nav {
    display: none;
  }
  
  .footer-content {
    flex-direction: row;
    justify-content: space-between;
  }
}

@media (min-width: 1024px) {
  .navbar-content {
    padding: 1.5rem 0;
  }
  
  .jdr-navbar-brand {
    font-size: 1.75rem;
  }
  
  .desktop-nav {
    gap: 2.5rem;
  }
}

/* Animations pour le menu mobile */
.mobile-nav {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Styles pour les liens actifs */
.jdr-navbar-link.active {
  color: var(--jdr-secondary);
}

.jdr-navbar-link.active:after {
  width: 100%;
}
</style>
