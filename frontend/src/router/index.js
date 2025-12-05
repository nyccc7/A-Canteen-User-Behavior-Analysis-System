import { createRouter, createWebHistory } from 'vue-router'
import PortalView from '../views/PortalView.vue'
import StudentMenu from '../views/StudentMenu.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'portal',
            component: PortalView
        },
        {
            path: '/student',
            name: 'student',
            component: StudentMenu
        },
        {
            path: '/admin',
            name: 'admin',
            component: AdminDashboard
        }
    ]
})

export default router
