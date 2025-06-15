import './assets/style.css'
import './assets/responsive.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// FontAwesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'

// Ajouter les icônes à la bibliothèque
library.add(fas, far, fab)

const app = createApp(App)

// Enregistrer le composant FontAwesome globalement
app.component('font-awesome-icon', FontAwesomeIcon)

app.use(router)

app.mount('#app')
