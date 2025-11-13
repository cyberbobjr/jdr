<script setup lang="ts">
/**
 * Composant de démonstration des fonctionnalités JDR
 * Affiche un exemple d'utilisation de TailwindCSS et FontAwesome
 */

import { ref } from 'vue'

// Données d'exemple pour les dés
const diceResult = ref<number | null>(null)
const isRolling = ref(false)

/**
 * Lance un dé D20 avec animation
 */
const rollDice = async () => {
  isRolling.value = true
  diceResult.value = null
  
  // Simulation de l'animation de lancer
  setTimeout(() => {
    diceResult.value = Math.floor(Math.random() * 20) + 1
    isRolling.value = false
  }, 1000)
}

// Données d'exemple pour un personnage
const character = ref({
  name: 'Elara la Magicienne',
  level: 5,
  class: 'Magicien',
  hp: 45,
  maxHp: 60,
  mp: 30,
  maxMp: 40,
  stats: {
    strength: 12,
    dexterity: 16,
    constitution: 14,
    intelligence: 18,
    wisdom: 15,
    charisma: 13
  }
})
</script>

<template>
  <div class="w-full mx-auto p-6">
    <!-- Titre de la démonstration -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-white mb-4 flex items-center justify-center space-x-3">
        <font-awesome-icon :icon="['fas', 'wand-magic-sparkles']" class="text-purple-400" />
        <span>Démonstration des fonctionnalités</span>
      </h2>
      <p class="text-slate-300">
        Exemple d'interface utilisant Vue.js, TailwindCSS et FontAwesome
      </p>
    </div>

    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Section Lanceur de dés -->
      <div class="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <h3 class="text-xl font-bold text-white mb-4 flex items-center space-x-2">
          <font-awesome-icon :icon="['fas', 'dice-d20']" class="text-red-400" />
          <span>Lanceur de dés</span>
        </h3>
        
        <div class="text-center">
          <div class="mb-6">
            <font-awesome-icon 
              :icon="['fas', 'dice-d20']" 
              :class="['text-6xl transition-all duration-300', 
                      isRolling ? 'text-yellow-400 animate-spin' : 'text-red-400']"
            />
          </div>
          
          <div v-if="diceResult !== null && !isRolling" class="mb-4">
            <div class="text-4xl font-bold text-white mb-2">{{ diceResult }}</div>
            <div class="text-slate-300">Résultat du D20</div>
          </div>
          
          <button 
            @click="rollDice"
            :disabled="isRolling"
            class="bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2 mx-auto"
          >
            <font-awesome-icon 
              :icon="['fas', isRolling ? 'spinner' : 'dice']" 
              :class="{ 'animate-spin': isRolling }"
            />
            <span>{{ isRolling ? 'Lancement...' : 'Lancer le dé' }}</span>
          </button>
        </div>
      </div>

      <!-- Section Fiche de personnage -->
      <div class="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-slate-700/50">
        <h3 class="text-xl font-bold text-white mb-4 flex items-center space-x-2">
          <font-awesome-icon :icon="['fas', 'user-ninja']" class="text-blue-400" />
          <span>Fiche de personnage</span>
        </h3>
        
        <!-- Informations générales -->
        <div class="mb-4">
          <h4 class="text-lg font-semibold text-white mb-2">{{ character.name }}</h4>
          <div class="flex items-center space-x-4 text-sm text-slate-300">
            <span>{{ character.class }}</span>
            <span>Niveau {{ character.level }}</span>
          </div>
        </div>

        <!-- Barres de vie et magie -->
        <div class="space-y-3 mb-4">
          <!-- Points de vie -->
          <div>
            <div class="flex justify-between text-sm text-slate-300 mb-1">
              <span class="flex items-center space-x-1">
                <font-awesome-icon :icon="['fas', 'heart']" class="text-red-400" />
                <span>Points de vie</span>
              </span>
              <span>{{ character.hp }}/{{ character.maxHp }}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-2">
              <div 
                class="bg-red-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${(character.hp / character.maxHp) * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Points de magie -->
          <div>
            <div class="flex justify-between text-sm text-slate-300 mb-1">
              <span class="flex items-center space-x-1">
                <font-awesome-icon :icon="['fas', 'magic']" class="text-blue-400" />
                <span>Points de magie</span>
              </span>
              <span>{{ character.mp }}/{{ character.maxMp }}</span>
            </div>
            <div class="w-full bg-slate-700 rounded-full h-2">
              <div 
                class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${(character.mp / character.maxMp) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Caractéristiques -->
        <div>
          <h5 class="text-sm font-semibold text-white mb-2">Caractéristiques</h5>
          <div class="grid grid-cols-3 gap-2 text-xs">
            <div v-for="(value, stat) in character.stats" :key="stat" 
                 class="bg-slate-700/50 rounded p-2 text-center">
              <div class="text-slate-300 capitalize">{{ stat.slice(0, 3) }}</div>
              <div class="text-white font-bold">{{ value }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section boutons d'action -->
    <div class="mt-8 text-center">
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <button class="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2">
          <font-awesome-icon :icon="['fas', 'fist-raised']" />
          <span>Combat</span>
        </button>
        <button class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2">
          <font-awesome-icon :icon="['fas', 'suitcase']" />
          <span>Inventaire</span>
        </button>
        <button class="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2">
          <font-awesome-icon :icon="['fas', 'book-open']" />
          <span>Sorts</span>
        </button>
        <button class="bg-orange-600 hover:bg-orange-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2">
          <font-awesome-icon :icon="['fas', 'cog']" />
          <span>Paramètres</span>
        </button>
      </div>
    </div>
  </div>
</template>
