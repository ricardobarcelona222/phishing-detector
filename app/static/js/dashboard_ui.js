function scrollToSection(id){
    document.getElementById(id).scrollIntoView({
        behavior:"smooth"
    });
}

function toggleTheme(){
    document.body.classList.toggle("dark-mode");
}
