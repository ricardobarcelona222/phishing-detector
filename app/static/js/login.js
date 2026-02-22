const form = document.getElementById("loginForm");
const loader = document.getElementById("loader");

const emailInput = document.getElementById("email");
const passInput = document.getElementById("password");

/* VALIDACION TIEMPO REAL */

emailInput.addEventListener("input", ()=>{
validateEmail();
});

passInput.addEventListener("input", ()=>{
validatePassword();
});

function validateEmail(){
const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if(regex.test(emailInput.value)){
emailInput.classList.add("input-valid");
emailInput.classList.remove("input-invalid");
}else{
emailInput.classList.add("input-invalid");
emailInput.classList.remove("input-valid");
}
}

function validatePassword(){
if(passInput.value.length >= 4){
passInput.classList.add("input-valid");
passInput.classList.remove("input-invalid");
}else{
passInput.classList.add("input-invalid");
passInput.classList.remove("input-valid");
}
}

/* LOGIN */

form.addEventListener("submit", async (e)=>{

e.preventDefault();

loader.classList.remove("hidden");

try{

const response = await fetch("http://127.0.0.1:8000/login",{
method:"POST",
headers:{
"Content-Type":"application/x-www-form-urlencoded"
},
body:`username=${encodeURIComponent(emailInput.value)}&password=${encodeURIComponent(passInput.value)}`
});

const data = await response.json();

/* 🔥 AQUI ESTA EL CAMBIO IMPORTANTE */
if(!response.ok){
    throw new Error(data.detail || "Error al iniciar sesión");
}

/* SUCCESS ANIMATION */

form.classList.add("fade-out");

setTimeout(()=>{

localStorage.setItem("token", data.access_token);

const payload = JSON.parse(atob(data.access_token.split(".")[1]));

if(payload.role === "admin"){
window.location.href="/admin";
}else{
window.location.href="/dashboard";
}

},600);

}catch(err){

loader.classList.add("hidden");

/* 🔥 AHORA MUESTRA EL MENSAJE REAL DEL BACKEND */
document.getElementById("error").innerText = err.message;

}

});
