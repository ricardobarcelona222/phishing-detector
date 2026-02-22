const form = document.getElementById("registerForm");

const email = document.getElementById("email");
const password = document.getElementById("password");

function validateEmail(){
const regex=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if(regex.test(email.value)){
email.classList.add("input-valid");
}else{
email.classList.add("input-invalid");
}
}

function validatePass(){
if(password.value.length>=4){
password.classList.add("input-valid");
}else{
password.classList.add("input-invalid");
}
}

email.addEventListener("input",validateEmail);
password.addEventListener("input",validatePass);

form.addEventListener("submit", async (e)=>{
e.preventDefault();

try{

const res = await fetch("/register",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({
email:email.value,
password:password.value
})
});

if(!res.ok) throw new Error();

form.classList.add("fade-out");

setTimeout(()=>{
window.location.href="/";
},700);

}catch{
document.getElementById("msg").innerText="Error al registrar";
}

});
