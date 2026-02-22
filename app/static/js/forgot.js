document.getElementById("forgotForm").addEventListener("submit", async (e)=>{

    e.preventDefault();

    const email = document.getElementById("email").value;

    await fetch("/forgot-password",{
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body:JSON.stringify({email})
    });

    alert("Revisa tu correo");
});
