const form = document.getElementById("forgotForm");
const emailInput = document.getElementById("email");
const msg = document.getElementById("msg");

function validateEmail(){
const regex=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;

if(regex.test(emailInput.value)){
emailInput.classList.add("input-valid");
emailInput.classList.remove("input-invalid");
}else{
emailInput.classList.add("input-invalid");
emailInput.classList.remove("input-valid");
}
}

emailInput.addEventListener("input",validateEmail);

form.addEventListener("submit", async(e)=>{
e.preventDefault();

try{

const res = await fetch("/forgot-password",{
method:"POST",
headers:{ "Content-Type":"application/json" },
body:JSON.stringify({ email: emailInput.value })
});

const data = await res.json();

if(!res.ok) throw new Error();

form.classList.add("fade-out");

setTimeout(()=>{
msg.innerHTML = `
 Token generado <br>
<a href="/reset-password?token=${data.token}">
Ir a cambiar contraseña
</a>`;
},500);

}catch{
msg.innerHTML = " Error enviando token";
}

});
