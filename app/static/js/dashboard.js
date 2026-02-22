// ===========================
// VERIFICAR TOKEN AL CARGAR
// ===========================

document.addEventListener("DOMContentLoaded", () => {

    const token = localStorage.getItem("token");

    if (!token) {
        window.location.href = "/";
        return;
    }

    loadStats();
    loadStatsByDate();
});


// ===========================
// LOGOUT
// ===========================

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}


// ===========================
// ANALIZAR MENSAJE
// ===========================
async function analyzeMessage() {

    const message = document.getElementById("message").value.trim();

    if (!message) {
        alert("Escribe un mensaje primero.");
        return;
    }

    try {

        const response = await fetch("/analysis/message", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + localStorage.getItem("token")
            },
            body: JSON.stringify({
                text: message
            })
        });

        const data = await response.json();

        const probabilityRaw = data.phishing_probability;
        const probability = (probabilityRaw * 100).toFixed(2);
        const isPhishing = data.is_phishing;

        // 🔎 Calcular nivel riesgo
        let riskLevel = "LOW";
        if (probabilityRaw > 0.75) riskLevel = "HIGH";
        else if (probabilityRaw > 0.40) riskLevel = "MEDIUM";

        // 🎯 Obtener elementos
        const card = document.getElementById("resultCard");
        const title = document.getElementById("analysisTitle");
        const badge = document.getElementById("analysisBadge");
        const progressBar = document.getElementById("progressBar");
        const description = document.getElementById("analysisDescription");

        // 🔄 Reset visual antes de animar
        card.classList.remove("show");
        progressBar.style.width = "0%";

        // Mostrar tarjeta
        card.classList.remove("hidden");
        setTimeout(() => {
            card.classList.add("show");
        }, 10);

        setTimeout(() => {
            card.classList.add("show");
        }, 50);

        // 🎨 Configurar colores dinámicos
        let color = "#22c55e";
        let textMessage = "Este mensaje parece legítimo.";

        if (riskLevel === "MEDIUM") {
            color = "#facc15";
            textMessage = "Este mensaje tiene características sospechosas. Se recomienda precaución.";
        }

        if (riskLevel === "HIGH") {
            color = "#ef4444";
            textMessage = "Este mensaje es altamente sospechoso y podría ser phishing. No hagas clic en enlaces.";
        }

        // 📝 Actualizar contenido
        title.innerText = `Probabilidad de phishing: ${probability}%`;
        badge.innerText = isPhishing ? "⚠️ PHISHING" : "✅ LEGÍTIMO";
        badge.style.backgroundColor = color;
        badge.style.color = "#fff";

        progressBar.style.backgroundColor = color;

        description.innerText = textMessage;

        // 🎬 Animar barra suavemente
        setTimeout(() => {
            progressBar.style.width = probability + "%";
        }, 200);

        // Limpiar textarea
        document.getElementById("message").value = "";

        // 🔄 Actualizar métricas sin recargar
        await loadStats();
        await loadStatsByDate();
        await loadHistory();

    } catch (error) {

        console.error(error);

        const description = document.getElementById("analysisDescription");
        const card = document.getElementById("resultCard");

        card.classList.remove("hidden");
        card.classList.add("show");

        description.innerText = "Error al analizar el mensaje.";
    }
}



let historyData = [];


// ===========================
// CARGAR HISTORIAL
// ===========================
async function loadHistory() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/analysis/history", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!response.ok) {
            throw new Error("No se pudo cargar historial");
        }

        const data = await response.json();

        historyData = data; // guardar copia global

        renderHistoryTable(historyData);

    } catch (error) {
        console.error(error);
        alert("Error cargando historial");
    }
}

function renderHistoryTable(data) {

    const tableBody = document.getElementById("historyTable");

    tableBody.innerHTML = "";

    data.forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.message}</td>
            <td>
                ${item.phishing 
                    ? '<span class="badge bg-danger">Sí</span>' 
                    : '<span class="badge bg-success">No</span>'}
            </td>
            <td>${item.risk_score}</td>
            <td>${item.risk_level}</td>
            <td>${new Date(item.created_at).toLocaleString()}</td>
        `;

        tableBody.appendChild(row);
    });
}


function applyFilters() {

    const textFilter = document.getElementById("filterText").value.toLowerCase();
    const typeFilter = document.getElementById("filterType").value;
    const riskFilter = document.getElementById("filterRisk").value;

    let filtered = historyData;

    // FILTRO TEXTO
    if (textFilter) {
        filtered = filtered.filter(item =>
            item.message.toLowerCase().includes(textFilter)
        );
    }

    // FILTRO TIPO
    if (typeFilter === "phishing") {
        filtered = filtered.filter(item => item.phishing === true);
    }

    if (typeFilter === "legit") {
        filtered = filtered.filter(item => item.phishing === false);
    }

    // FILTRO RIESGO
    if (riskFilter) {
        filtered = filtered.filter(item => item.risk_level === riskFilter);
    }

    renderHistoryTable(filtered);
}


// ===========================
// VARIABLES GLOBALES DE GRAFICAS
// ===========================

let statsChart = null;
let statsByDateChart = null;


// ===========================
// GRAFICA ESTADISTICAS GENERAL
// ===========================

async function loadStats() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/analysis/stats", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        // ===== ACTUALIZAR TARJETAS =====
        document.getElementById("metricTotal").textContent =
            data.total_analysis || 0;

        document.getElementById("metricPhishing").textContent =
            data.phishing_detected || 0;

        document.getElementById("metricLegit").textContent =
            data.legitimate_detected || 0;

        document.getElementById("metricRate").textContent =
            (data.phishing_rate || 0) + "%";


        // ===== GRAFICA PIE =====
        const ctx = document.getElementById("statsChart").getContext("2d");

        if (statsChart) {
            statsChart.destroy();
        }

        statsChart = new Chart(ctx, {
            type: "pie",
            data: {
                labels: ["Phishing", "Legítimos"],
                datasets: [{
                    data: [
                        data.phishing_detected || 0,
                        data.legitimate_detected || 0
                    ]
                }]
            }
        });

    } catch (error) {
        console.error(error);
        alert("Error cargando estadísticas");
    }
}


// ===========================
// GRAFICA ANALISIS POR FECHA
// ===========================

async function loadStatsByDate() {

    const token = localStorage.getItem("token");

    try {

        const response = await fetch("/analysis/stats-by-date", {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        const data = await response.json();

        if (!Array.isArray(data) || data.length === 0) {
            console.log("No hay datos por fecha");
            return;
        }

        const labels = data.map(item => item.date);
        const totals = data.map(item => item.total);

        const ctx = document.getElementById("statsByDateChart").getContext("2d");

        if (statsByDateChart) {
            statsByDateChart.destroy();
        }

        statsByDateChart = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Análisis por fecha",
                    data: totals
                }]
            }
        });

    } catch (error) {
        console.error(error);
        alert("Error cargando gráfica por fecha");
    }
}

// ===========================
// EXPORTAR HISTORIAL A PDF
// ===========================

function exportHistoryPDF() {

    if (!historyData || historyData.length === 0) {
        alert("No hay historial para exportar");
        return;
    }

    const { jsPDF } = window.jspdf;

    const doc = new jsPDF();

    // Título
    doc.setFontSize(16);
    doc.text("Historial - Phishing Detector", 14, 15);

    // Fecha
    doc.setFontSize(10);
    doc.text(
        "Generado: " + new Date().toLocaleString(),
        14,
        22
    );

    // Preparar datos
    const tableData = historyData.map(item => [
        item.id,
        item.message,
        item.phishing ? "Sí" : "No",
        item.risk_score,
        item.risk_level,
        new Date(item.created_at).toLocaleString()
    ]);

    // Crear tabla
    doc.autoTable({
        startY: 30,
        head: [["ID", "Mensaje", "Phishing", "Riesgo", "Nivel", "Fecha"]],
        body: tableData,
        styles: {
            fontSize: 8
        },
        columnStyles: {
            1: { cellWidth: 60 } // Mensaje más ancho
        }
    });

    // Guardar archivo
    doc.save("historial_phishing.pdf");
}

// ===========================
// EXPORTAR HISTORIAL A EXCEL
// ===========================

function exportHistoryExcel() {

    if (!historyData || historyData.length === 0) {
        alert("No hay historial para exportar");
        return;
    }

    // Convertir datos a formato Excel
    const excelData = historyData.map(item => ({
        ID: item.id,
        Mensaje: item.message,
        Phishing: item.phishing ? "Sí" : "No",
        Riesgo: item.risk_score,
        Nivel: item.risk_level,
        Fecha: new Date(item.created_at).toLocaleString()
    }));

    // Crear hoja Excel
    const worksheet = XLSX.utils.json_to_sheet(excelData);

    // Crear libro
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Historial");

    // Descargar archivo
    XLSX.writeFile(workbook, "historial_phishing.xlsx");
}


async function analyzeFile() {

    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Selecciona un archivo primero.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("/analysis/file", {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + localStorage.getItem("token")
            },
            body: formData
        });

        const data = await response.json();

        const probability = (data.phishing_probability * 100).toFixed(2);
        const riskLevel = data.risk_level;

        const card = document.getElementById("resultCard");
        const title = document.getElementById("analysisTitle");
        const badge = document.getElementById("analysisBadge");
        const progressBar = document.getElementById("progressBar");
        const description = document.getElementById("analysisDescription");

        card.classList.remove("hidden");
        setTimeout(() => {
            card.classList.add("show");
        }, 10);

        let color = "#22c55e";
        let textMessage = "El archivo parece legítimo.";

        if (riskLevel === "MEDIUM") {
            color = "#facc15";
            textMessage = "El archivo contiene elementos sospechosos.";
        }

        if (riskLevel === "HIGH") {
            color = "#ef4444";
            textMessage = "El archivo contiene contenido altamente sospechoso.";
        }

        title.innerText = `Resultado del archivo: ${probability}%`;
        badge.innerText = riskLevel;
        badge.style.backgroundColor = color;

        progressBar.style.width = probability + "%";
        progressBar.style.backgroundColor = color;

        description.innerText = textMessage;

        fileInput.value = "";
        document.getElementById("fileName").textContent =
            "Haz clic para seleccionar archivo (PDF, DOCX, TXT)";

        await loadStats();
        await loadStatsByDate();
        await loadHistory();

    } catch (error) {
        console.error(error);
        alert("Error al analizar el archivo.");
    }
}


document.getElementById("fileInput").addEventListener("change", function () {
    const fileNameSpan = document.getElementById("fileName");
    if (this.files.length > 0) {
        fileNameSpan.textContent = this.files[0].name;
    } else {
        fileNameSpan.textContent = "Haz clic para subir un archivo";
    }
});
