import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import Vue3TouchEvents from "vue3-touch-events";
import '@coddicat/vue-pinch-scroll-zoom/style.css';

const app = createApp(App);
app.use(Vue3TouchEvents);
app.mount('#app')
