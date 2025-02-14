export default {
    props: ['name', 'description', 'image', 'chapters'],
    template: `
    <div class="card" style="width: auto; margin: 5px;">
        <img src="{{image}}" class="card-img-top" alt="...">
        <div class="card-header text-center">
            {{name}}
        </div>
        <div class="card-body">
            <h6 class="card-text">{{description}}</h6>
        </div>
        <div class="card-footer text-body-secondary">
            Chapters: {{chapterCount}}
        </div>
    </div>
    `,
    computed: {
        chapterCount(){
            const chapters = this.chapters
            return chapters.length
        }
    }
}