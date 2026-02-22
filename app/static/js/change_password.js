const form = document.getElementById("changeForm");

const current = document.getElementById("current_password");
const newPass = document.getElementById("new_password");

function validate(input){
if(input.value.length >= 4){
input.classList.add("input-valid");
input.classList.remove("input-invalid");
}else{
input.classList.add("input-invalid");
input.classList.remove("input-valid");
}
}

current.addEventListener("input",()=>validate(current));
newPass.addEventListener("input",()=>validate(newPass));

form.addEventListener("submit", async (e)=>{
e.preventDefault();

try{

const token = localStorage.getItem("token");

const res = await fetch("/change-password",{
method:"POST",
headers:{
"Content-Type":"application/json",
"Authorization":`Bearer ${token}`
},
body:JSON.stringify({
current_password:current.value,
new_password:newPass.value
})
});

const data = await res.json();

if(!res.ok) throw new Error();

form.classList.add("fade-out");

setTimeout(()=>{
document.getElementById("msg").innerText="✅ Contraseña actualizada";
},500);

}catch{
document.getElementById("msg").innerText="❌ Error al cambiar contraseña";
}

});
