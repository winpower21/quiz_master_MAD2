import Home from '../pages/home.js'
import Login from '../pages/login.js'
import Register from '../pages/register.js';
import Dashboard from '../pages/dashboard.js';



const routes = [
    {path: '/', component: Home},
    {path: "/login", component: Login},
    {path: "/register", component: Register},
    {path: "/dashboard", component: Dashboard}
]

const router = new VueRouter({
    routes
})

export default router