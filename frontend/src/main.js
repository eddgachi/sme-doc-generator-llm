import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Import the router

// Import Bootstrap CSS (assuming it's installed or linked in index.html)
import 'bootstrap/dist/css/bootstrap.min.css'
// Import Bootstrap JS Bundle (includes Popper)
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import Font Awesome CSS
import '@fortawesome/fontawesome-free/css/all.min.css'

// Import potential global styles
// import './assets/main.css'

const app = createApp(App)

app.use(router) // Use the router

app.mount('#app')
