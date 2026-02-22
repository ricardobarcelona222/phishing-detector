document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "/";
        return;
    }

    loadUsers();
    loadPendingUsers();
    loadStats();
    loadHistory();
});

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}


// ================= USERS =================

async function loadUsers() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/admin/users", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const users = await response.json();
        const tableBody = document.getElementById("usersTable");
        tableBody.innerHTML = "";

        users.forEach(user => {

            const statusBadge = user.is_approved
                ? `<span class="badge badge-approved">Aprobado</span>`
                : `<span class="badge badge-pending">Pendiente</span>`;

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.email}</td>
                <td>${user.is_admin ? "ADMIN" : "USER"}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-danger btn-sm"
                        onclick="deleteUser(${user.id})">
                        Eliminar
                    </button>
                </td>
            `;

            tableBody.appendChild(row);
        });

    } catch (error) {
        alert("Error cargando usuarios");
    }
}


// ================= PENDING USERS =================

async function loadPendingUsers() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/admin/pending-users", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const users = await response.json();
        const table = document.getElementById("pendingUsersTable");
        table.innerHTML = "";

        users.forEach(user => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.email}</td>
                <td>${user.auth_provider}</td>
                <td>
                    <button class="btn btn-approve btn-sm"
                        onclick="approveUser(${user.id})">
                        Aprobar
                    </button>
                </td>
            `;

            table.appendChild(row);
        });

    } catch (error) {
        console.log("Error cargando pendientes");
    }
}

async function approveUser(userId) {

    const token = localStorage.getItem("token");

    try {

        await fetch(`/admin/approve-user/${userId}`, {
            method: "PUT",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        loadPendingUsers();
        loadUsers();

    } catch (error) {
        alert("Error aprobando usuario");
    }
}


// ================= DELETE =================

async function deleteUser(userId) {

    const token = localStorage.getItem("token");

    if (!confirm("¿Seguro que deseas eliminar este usuario?")) return;

    try {

        await fetch(`/admin/delete-user/${userId}`, {
            method: "DELETE",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        loadUsers();
        loadPendingUsers();

    } catch (error) {
        alert("Error eliminando usuario");
    }
}


// ================= STATS =================
async function loadStats() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/admin/stats", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const stats = await response.json();
        const ctx = document.getElementById("adminStatsChart");

        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Phishing", "Legítimo"],
                datasets: [{
                    data: [stats.phishing, stats.safe]
                }]
            }
        });

        const total = stats.phishing + stats.safe;

        animateValue("kpiPhishing", stats.phishing);
        animateValue("kpiSafe", stats.safe);
        animateValue("kpiTotal", total);

    } catch (error) {
        console.log("Error cargando stats", error);
    }
}


// ================= GLOBAL HISTORY =================

async function loadHistory() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/admin/history", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const history = await response.json();
        const table = document.getElementById("analysisTable");
        table.innerHTML = "";

        history.forEach(item => {

            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.message}</td>
                <td>${item.phishing ? "Sí" : "No"}</td>
                <td>${new Date(item.created_at).toLocaleString()}</td>
            `;

            table.appendChild(row);
        });

    } catch (error) {
        console.log("Error cargando historial");
    }
}
