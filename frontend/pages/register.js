const Register = {
    template: `
    <div style="margin: 0; padding: 0; background-image: url('/frontend/static/media/home.jpeg'); background-size: cover; background-position: center; 
    background-repeat: no-repeat;">
        <div class="d-flex justify-content-left align-items-center vh-100" style="margin-left: 50px; margin-right: 50px;">
            <div style="color: white; text-align: center; padding: 50px; background-color: rgba(0, 0, 0, 0.5); border-radius: 10px; width: 800px;">
                <h3 class="pb-3">Register</h3>
                <div>
                    <div class="mb-3">
                        <label for="Name" class="form-label">Full Name </label>
                        <input v-model="name" type="text" class="form-control" id="Name" aria-describedby="emailHelp">
                    </div>
                    <div class="mb-3">
                        <label for="Email" class="form-label">Email </label>
                        <input v-model="email" type="email" class="form-control" id="Email" aria-describedby="emailHelp">
                    </div>
                    <div class="mb-3">
                        <label for="Password" class="form-label">Password</label>
                        <input v-model="password" type="password" class="form-control" id="Password">
                    </div>
                    <div class="row">
                        <div class="col" style="text-align: right;">
                            <a href="#">Forgot Password?</a>
                        </div>
                    </div>
                    <div class="pb-2">
                        <button class="btn btn-dark w-100 font-weight-bold mt-2" @click="register">Register</button>
                    </div>
                </div>
                <div class="sideline">OR</div>
                    <div style="text-align:center;">
                        <h6>Already have an account?</h6>
                        <router-link class="btn btn-primary w-100 font-weight-bold mt-2" to="/login">Login</router-link>
                    </div>  
                </div>                
            </div>
        </div>
    </div>
    `,
    data(){
        return{
            name: null,
            email: null,
            password: null
        }
    },
    methods:{
        async register(){
            const res = await fetch(location.origin + "/register", 
                {
                    method :"POST", 
                    headers:{'Content-Type': 'application/json'}, 
                    body: JSON.stringify({"name": this.name, "email": this.email, "password": this.password})
                }
            )
            if (res.ok) {
                console.log("register successful")
                const data = await res.json()
                console.log(data)
            }
        }
    }
}

export default Register