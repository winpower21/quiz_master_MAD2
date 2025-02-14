const store = new Vuex.Store({
    state: {
        auth_token: null,
        login_status: false,
        role: null,
        user_id: null,
    },
    mutations: {
        setUser(state){
            try {
                if (JSON.parse(sessionStorage.getItem("user"))) {
                    const user = JSON.parse(sessionStorage.getItem("user"))
                    state.auth_token = user.token
                    state.login_status = true
                    state.role = user.role
                    state.user_id = user.id
                }
            } catch {
                console.warn("Not logged in")
            }
        },
        logout(state){
            state.auth_token = null
            state.login_status = false
            state.role = null
            state.user_id = null
            sessionStorage.removeItem("user")
        }
    },
    actions: {
        
    }
})

store.commit("setUser")
export default store