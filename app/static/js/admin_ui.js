// DARK MODE
function toggleDarkMode(){
    document.body.classList.toggle("dark-mode");
}


// SCROLL ANIMATION
const observer = new IntersectionObserver(entries=>{
    entries.forEach(entry=>{
        if(entry.isIntersecting){
            entry.target.classList.add("visible");
        }
    });
});

document.querySelectorAll(".fade-scroll").forEach(el=>{
    observer.observe(el);
});


// KPI COUNTER
function animateValue(id, end){

    let el = document.getElementById(id);
    let start = 0;

    let duration = 800;
    let step = end / (duration/16);

    let counter = setInterval(()=>{

        start += step;

        if(start >= end){
            el.innerText = end;
            clearInterval(counter);
        }
        else{
            el.innerText = Math.floor(start);
        }

    },16);
}
