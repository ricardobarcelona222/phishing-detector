document.getElementById("resetForm").addEventListener("submit", async (e) => {

    e.preventDefault();

    const token = document.getElementById("token").value;
    const password = document.getElementById("password").value;

    try {

        const response = await fetch("/reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                token: token,
                new_password: password
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail);
        }

        document.getElementById("msg").innerHTML =
            "<span class='text-success'>Contraseña actualizada</span>";

        setTimeout(() => {
            window.location.href = "/";
        }, 1500);

    } catch (err) {

        document.getElementById("msg").innerHTML =
            "<span class='text-danger'>" + err.message + "</span>";

    }

});
