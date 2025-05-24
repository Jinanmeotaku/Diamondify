// frontend/src/index.ts
async function fetchData() {
    const response = await fetch('http://localhost:5000/api/data');
    const data = await response.json();
    document.getElementById('message')!.textContent = data.message;
}

fetchData();
