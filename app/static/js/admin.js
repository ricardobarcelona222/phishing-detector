document.addEventListener("DOMContentLoaded", loadAdminStats);

async function loadAdminStats() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/analysis/admin/global-stats", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            alert("No eres administrador");
            window.location.href = "/dashboard";
            return;
        }

        const data = await response.json();

        document.getElementById("adminStats").innerText = `
Usuarios registrados: ${data.total_users}
Total análisis: ${data.total_analysis}
Phishing detectados: ${data.phishing_detected}
        `;

    } catch {
        alert("Error cargando panel admin");
    }
}

document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "/";
        return;
    }

    loadUsers();
    loadAnalysis();
    loadStats();

});


function logout(){
    localStorage.removeItem("token");
    window.location.href="/";
}


// ================= USERS =================

async function loadUsers(){

    const token = localStorage.getItem("token");

    const res = await fetch("/analysis/admin/users",{
        headers:{ "Authorization":"Bearer "+token }
    });

    const data = await res.json();

    const table = document.getElementById("usersTable");

    table.innerHTML="";

    data.forEach(user=>{

        table.innerHTML+=`
        <tr>
            <td>${user.id}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>
                <button class="btn btn-danger btn-sm" onclick="deleteUser(${user.id})">
                    Eliminar
                </button>
            </td>
        </tr>
        `;

    });

}


async function deleteUser(id){

    const token = localStorage.getItem("token");

    await fetch(`/analysis/admin/delete-user/${id}`,{
        method:"DELETE",
        headers:{ "Authorization":"Bearer "+token }
    });

    loadUsers();

}


// ================= ANALYSIS =================

async function loadAnalysis(){

    const token = localStorage.getItem("token");

    const res = await fetch("/analysis/admin/all-analysis",{
        headers:{ "Authorization":"Bearer "+token }
    });

    const data = await res.json();

    const table = document.getElementById("analysisTable");

    table.innerHTML="";

    data.forEach(item=>{

        table.innerHTML+=`
        <tr>
            <td>${item.id}</td>
            <td>${item.message}</td>
            <td>${item.phishing ? "Sí":"No"}</td>
            <td>${new Date(item.created_at).toLocaleString()}</td>
        </tr>
        `;

    });

}


// ================= STATS =================

async function loadStats(){

    const token = localStorage.getItem("token");

    const res = await fetch("/analysis/admin/global-stats",{
        headers:{ "Authorization":"Bearer "+token }
    });

    const data = await res.json();

    const ctx = document.getElementById("adminStatsChart").getContext("2d");

    new Chart(ctx,{
        type:"pie",
        data:{
            labels:["Phishing","Legítimos"],
            datasets:[{
                data:[data.phishing,data.legit]
            }]
        }
    });

}
