import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '@/views/Dashboard/index.vue';
import Report from '@/views/Report/index.vue';
import NotFound from '@/views/NotFound.vue';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: Dashboard,
    },
    {
      path: '/report/:traceId',
      name: 'Report',
      component: Report,
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: NotFound,
    },
  ],
});

export default router;
