import SubjectCard from "../components/SubjectCard.js"

const Dashboard = {
    template: `
    <div class="container mt-4">
        <h1>Dashboard</h1>
        <h3>Subjects</h3>
        <div class="row justify-content-start">
            <div class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3 p-2 " v-for="(subject, index) in subjects" :key="subject.id">
                <SubjectCard :name="subject.name" :description="subject.description" :image="subject.image_url" :chapters="subject.chapters" />
            </div>
        </div>
    </div>
    `,
    data(){
        return {
            subjects: []
        }
    },
    methods:{},
    async mounted(){
        const res = await fetch(location.origin + "/api/subjects", {
            headers: {
                "Authentication-Token": this.$store.state.auth_token
            }
        })
        this.subjects = await res.json()
        console.log(this.subjects)
    },
    components: {
        SubjectCard
    }
}


export default Dashboard