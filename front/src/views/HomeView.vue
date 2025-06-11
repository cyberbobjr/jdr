<script setup lang="ts">
// Page d'accueil du gestionnaire de JDR "Terres du Milieu"
import JdrDemo from '../components/JdrDemo.vue'
import { ref, onMounted } from 'vue'
import JdrApiService from '@/core/api'

// État pour vérifier la connexion API
const apiStatus = ref<'checking' | 'connected' | 'error'>('checking')
const statsData = ref({
  characters: 0,
  scenarios: 0,
  activeSessions: 0
})

onMounted(async () => {
  try {
    // Vérifier la connexion API et charger les statistiques
    const [charactersData, scenariosData, sessionsData] = await Promise.all([
      JdrApiService.getCharacters().catch(() => []),
      JdrApiService.getScenarios().catch(() => []),
      JdrApiService.getActiveSessions().catch(() => [])
    ])
    
    statsData.value = {
      characters: charactersData.length,
      scenarios: scenariosData.length,
      activeSessions: sessionsData.length
    }
    
    apiStatus.value = 'connected'
  } catch (err) {
    console.warn('Erreur lors du chargement des statistiques:', err)
    apiStatus.value = 'error'
  }
})
</script>

<template>
  <div class="home-container">
    <!-- Section Hero -->
    <section class="hero-section">
      <div class="jdr-container">
        <div class="hero-content jdr-text-center">
          <h1 class="jdr-title jdr-title-xl hero-title">
            <font-awesome-icon :icon="['fas', 'dice-d20']" class="hero-icon" />
            Terres du Milieu
          </h1>
          <p class="jdr-subtitle hero-subtitle">
            Vivez des aventures épiques dans l'univers du Jeu de Rôle des Terres du Milieu.<br>
            Un système complet pour gérer vos personnages, scénarios et parties.
          </p>
          
          <!-- Statut de connexion API -->
          <div class="api-status jdr-mb-4">
            <div v-if="apiStatus === 'checking'" class="status-indicator checking">
              <i class="fas fa-spinner fa-spin"></i>
              <span>Connexion au serveur...</span>
            </div>
            <div v-else-if="apiStatus === 'connected'" class="status-indicator connected">
              <i class="fas fa-check-circle"></i>
              <span>Serveur connecté</span>
            </div>
            <div v-else class="status-indicator error">
              <i class="fas fa-exclamation-triangle"></i>
              <span>Serveur déconnecté (mode démo)</span>
            </div>
          </div>
          
          <!-- Actions principales -->
          <div class="hero-actions">
            <router-link to="/nouveau-scenario" class="jdr-btn jdr-btn-primary jdr-btn-xl">
              <font-awesome-icon :icon="['fas', 'rocket']" />
              <span>Commencer une Aventure</span>
            </router-link>
            <router-link to="/sessions" class="jdr-btn jdr-btn-secondary jdr-btn-xl">
              <font-awesome-icon :icon="['fas', 'gamepad']" />
              <span>Sessions en Cours</span>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Statistiques -->
    <section class="stats-section" v-if="apiStatus === 'connected'">
      <div class="jdr-container">
        <div class="stats-grid">
          <div class="stat-card jdr-card jdr-text-center">
            <div class="stat-icon">
              <font-awesome-icon :icon="['fas', 'user-shield']" />
            </div>
            <div class="stat-number">{{ statsData.characters }}</div>
            <div class="stat-label">Personnage{{ statsData.characters > 1 ? 's' : '' }}</div>
          </div>
          
          <div class="stat-card jdr-card jdr-text-center">
            <div class="stat-icon">
              <font-awesome-icon :icon="['fas', 'scroll']" />
            </div>
            <div class="stat-number">{{ statsData.scenarios }}</div>
            <div class="stat-label">Scénario{{ statsData.scenarios > 1 ? 's' : '' }}</div>
          </div>
          
          <div class="stat-card jdr-card jdr-text-center">
            <div class="stat-icon">
              <font-awesome-icon :icon="['fas', 'play']" />
            </div>
            <div class="stat-number">{{ statsData.activeSessions }}</div>
            <div class="stat-label">Session{{ statsData.activeSessions > 1 ? 's' : '' }} active{{ statsData.activeSessions > 1 ? 's' : '' }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Fonctionnalités principales -->
    <section class="features-section">
      <div class="jdr-container">
        <div class="features-header jdr-text-center jdr-mb-4">
          <h2 class="jdr-title jdr-title-lg">Fonctionnalités</h2>
          <p class="jdr-subtitle">Tout ce dont vous avez besoin pour vos aventures</p>
        </div>
        
        <div class="features-grid">
          <!-- Gestion des personnages -->
          <div class="feature-card jdr-card jdr-card-character">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'user-shield']" />
              </div>
              <h3 class="jdr-card-title">Personnages</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Gérez vos héros avec un système complet de caractéristiques, compétences, équipements et sorts.
                Chaque personnage dispose d'une fiche détaillée et d'un historique d'aventures.
              </p>
            </div>
            <div class="jdr-card-footer">
              <router-link to="/personnages" class="jdr-btn jdr-btn-primary">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                Voir les personnages
              </router-link>
            </div>
          </div>

          <!-- Scénarios -->
          <div class="feature-card jdr-card jdr-card-scenario">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'scroll']" />
              </div>
              <h3 class="jdr-card-title">Scénarios</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Découvrez une bibliothèque riche de scénarios prêts à jouer. Chaque aventure est guidée par
                un Maître du Jeu IA qui s'adapte à vos choix et actions.
              </p>
            </div>
            <div class="jdr-card-footer">
              <router-link to="/scenarios" class="jdr-btn jdr-btn-primary">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                Parcourir les scénarios
              </router-link>
            </div>
          </div>

          <!-- Sessions de jeu -->
          <div class="feature-card jdr-card">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'gamepad']" />
              </div>
              <h3 class="jdr-card-title">Sessions de Jeu</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Jouez en temps réel avec un système de dialogue interactif. Sauvegardez vos parties,
                consultez l'historique et reprenez vos aventures à tout moment.
              </p>
            </div>
            <div class="jdr-card-footer">
              <router-link to="/sessions" class="jdr-btn jdr-btn-primary">
                <font-awesome-icon :icon="['fas', 'arrow-right']" />
                Voir les sessions
              </router-link>
            </div>
          </div>

          <!-- Système de combat -->
          <div class="feature-card jdr-card">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'sword']" />
              </div>
              <h3 class="jdr-card-title">Combat Tactique</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Un système de combat intégré avec gestion automatique des attaques, défenses et sorts.
                Les dés sont lancés automatiquement selon les règles du JRTM.
              </p>
            </div>
            <div class="jdr-card-footer">
              <button class="jdr-btn jdr-btn-outline" disabled>
                <font-awesome-icon :icon="['fas', 'cog']" />
                En développement
              </button>
            </div>
          </div>

          <!-- Intelligence Artificielle -->
          <div class="feature-card jdr-card jdr-card-highlight">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'hat-wizard']" />
              </div>
              <h3 class="jdr-card-title">Maître du Jeu IA</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Powered by PydanticAI, notre MJ artificiel comprend les règles, s'adapte à vos actions
                et crée des histoires immersives et cohérentes.
              </p>
            </div>
            <div class="jdr-card-footer">
              <div class="jdr-badge jdr-badge-primary">
                <font-awesome-icon :icon="['fas', 'magic']" />
                Intelligence Artificielle
              </div>
            </div>
          </div>

          <!-- Technologies -->
          <div class="feature-card jdr-card">
            <div class="jdr-card-header">
              <div class="feature-icon">
                <font-awesome-icon :icon="['fas', 'code']" />
              </div>
              <h3 class="jdr-card-title">Technologies Modernes</h3>
            </div>
            <div class="jdr-card-body">
              <p>
                Interface Vue.js 3 avec TypeScript, backend FastAPI, et base de données JSON.
                Une architecture moderne pour une expérience fluide.
              </p>
            </div>
            <div class="jdr-card-footer">
              <div class="tech-badges">
                <span class="jdr-badge jdr-badge-info">Vue.js</span>
                <span class="jdr-badge jdr-badge-info">FastAPI</span>
                <span class="jdr-badge jdr-badge-info">TypeScript</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Section de démonstration -->
    <section class="demo-section">
      <div class="jdr-container">
        <div class="demo-header jdr-text-center jdr-mb-4">
          <h2 class="jdr-title jdr-title-lg">Démonstration Interactive</h2>
          <p class="jdr-subtitle">Testez les fonctionnalités en live</p>
        </div>
        
        <div class="demo-container jdr-card">
          <JdrDemo />
        </div>
      </div>
    </section>

    <!-- Call to Action -->
    <section class="cta-section">
      <div class="jdr-container">
        <div class="cta-content jdr-card jdr-card-highlight jdr-text-center">
          <div class="cta-icon">
            <font-awesome-icon :icon="['fas', 'dice-d20']" />
          </div>
          <h2 class="jdr-title jdr-title-md">Prêt pour l'Aventure ?</h2>
          <p class="cta-description">
            Commencez dès maintenant votre première quête dans les Terres du Milieu.
            Choisissez votre personnage, sélectionnez un scénario et laissez-vous guider !
          </p>
          <div class="cta-actions">
            <router-link to="/nouveau-scenario" class="jdr-btn jdr-btn-primary jdr-btn-lg">
              <font-awesome-icon :icon="['fas', 'play']" />
              Commencer Maintenant
            </router-link>
            <router-link to="/about" class="jdr-btn jdr-btn-outline jdr-btn-lg">
              <font-awesome-icon :icon="['fas', 'info-circle']" />
              En savoir plus
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
}

/* Section Hero */
.hero-section {
  padding: 4rem 0 6rem 0;
  background: linear-gradient(135deg, 
    rgba(44, 24, 16, 0.9) 0%, 
    rgba(60, 36, 20, 0.8) 50%, 
    rgba(74, 44, 24, 0.9) 100%),
    url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23DAA520" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  margin-bottom: 2rem;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
}

.hero-icon {
  color: var(--jdr-secondary);
  margin-right: 1rem;
  animation: jdr-glow 3s ease-in-out infinite;
}

.hero-subtitle {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.api-status {
  margin-bottom: 2rem;
}

.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--jdr-border-radius);
  font-size: 0.9rem;
}

.status-indicator.checking {
  background: var(--jdr-bg-tertiary);
  color: var(--jdr-text-muted);
}

.status-indicator.connected {
  background: rgba(34, 139, 34, 0.2);
  color: var(--jdr-success);
  border: 1px solid var(--jdr-success);
}

.status-indicator.error {
  background: rgba(178, 34, 34, 0.2);
  color: var(--jdr-danger);
  border: 1px solid var(--jdr-danger);
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Section Statistiques */
.stats-section {
  padding: 3rem 0;
  background: linear-gradient(145deg, var(--jdr-bg-secondary), var(--jdr-bg-tertiary));
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.stat-card {
  padding: 2rem 1rem;
  background: linear-gradient(145deg, var(--jdr-bg-primary), var(--jdr-bg-secondary));
  border: 2px solid var(--jdr-border-color);
  transition: all 0.3s ease;
}

.stat-card:hover {
  border-color: var(--jdr-secondary);
  transform: translateY(-4px);
  box-shadow: var(--jdr-shadow-large);
}

.stat-icon {
  font-size: 2.5rem;
  color: var(--jdr-accent);
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 3rem;
  font-weight: bold;
  color: var(--jdr-secondary);
  font-family: var(--jdr-font-fantasy);
  line-height: 1;
  margin-bottom: 0.5rem;
}

.stat-label {
  color: var(--jdr-text-muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.9rem;
}

/* Section Fonctionnalités */
.features-section {
  padding: 4rem 0;
}

.features-header {
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
}

.feature-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--jdr-shadow-large);
}

.feature-icon {
  font-size: 2rem;
  color: var(--jdr-accent);
  margin-right: 1rem;
}

.jdr-card-body {
  flex: 1;
}

.tech-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Section Démonstration */
.demo-section {
  padding: 4rem 0;
  background: linear-gradient(145deg, var(--jdr-bg-tertiary), var(--jdr-bg-secondary));
}

.demo-header {
  margin-bottom: 2rem;
}

.demo-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
}

/* Section Call to Action */
.cta-section {
  padding: 4rem 0;
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
  padding: 3rem 2rem;
  background: linear-gradient(145deg, 
    rgba(218, 165, 32, 0.1), 
    rgba(139, 69, 19, 0.1));
  border: 2px solid var(--jdr-secondary);
}

.cta-icon {
  font-size: 4rem;
  color: var(--jdr-secondary);
  margin-bottom: 1.5rem;
  animation: jdr-pulse 2s ease-in-out infinite;
}

.cta-description {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  color: var(--jdr-text-secondary);
}

.cta-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-section {
    padding: 2rem 0 3rem 0;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-subtitle {
    font-size: 1rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .hero-actions .jdr-btn {
    width: 100%;
    max-width: 300px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .cta-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .cta-actions .jdr-btn {
    width: 100%;
    max-width: 280px;
  }
  
  .demo-container {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .hero-icon {
    margin-right: 0;
    display: block;
    margin-bottom: 1rem;
  }
  
  .stat-number {
    font-size: 2.5rem;
  }
  
  .feature-icon {
    margin-right: 0;
    margin-bottom: 1rem;
  }
  
  .cta-content {
    padding: 2rem 1rem;
  }
}

/* Animations spéciales */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-card {
  animation: fadeInUp 0.6s ease-out;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }
.feature-card:nth-child(4) { animation-delay: 0.4s; }
.feature-card:nth-child(5) { animation-delay: 0.5s; }
.feature-card:nth-child(6) { animation-delay: 0.6s; }
</style>
