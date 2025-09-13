const endDate = "15 March 2026 10:00:00 AM";
document.getElementById("end-date").innerText = endDate;
const inputs = document.querySelectorAll("input");

function clock() {
    const end = new Date(endDate);
    const now = new Date();
    const diff = (end - now) / 1000;

    if (diff < 0) {
        clearInterval(timer);
        alert("Nuvanta has launched! 🎉");
        return;
    }

    inputs[0].value = Math.floor(diff / 3600 / 24);                       // Days
    inputs[1].value = String(Math.floor(diff / 3600) % 24).padStart(2, '0'); // Hours
    inputs[2].value = String(Math.floor(diff / 60) % 60).padStart(2, '0');   // Minutes
    inputs[3].value = String(Math.floor(diff) % 60).padStart(2, '0');        // Seconds
}

// initial call
clock();
const timer = setInterval(clock, 1000);
