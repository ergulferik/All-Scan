const updateButton = document.querySelector(".update-database-button");
const spinnerUpdate = document.querySelector(".spinner-update");
const spinnerDrop = document.querySelector(".spinner-drop");
const dropButton = document.querySelector(".drop-database-button");

document.addEventListener("DOMContentLoaded", function() {


    updateButton.addEventListener("click", async function() {
        updateButton.disabled = true; // Butonu pasif hale getir
        spinnerUpdate.style.display = "inline-block"; // Spinner'ı göster

        try {
            await updateDatabase();
        } catch (error) {
            console.error('Hata:', error);
        } finally {
            spinnerUpdate.style.display = "none"; // Spinner'ı gizle
            updateButton.disabled = false; // Butonu etkin hale getir
        }
    });


    // Silme düğmesi
    dropButton.addEventListener("click", async function () {
        dropButton.disabled = true; // Butonu pasif hale getir
        spinnerDrop.style.display = "inline-block"; // Spinner'ı göster

        try {
            await dropDatabase();
        } catch (error) {
            console.error('Hata:', error);
        } finally {
            spinnerDrop.style.display = "none"; // Spinner'ı gizle
            dropButton.disabled = false; // Butonu etkin hale getir
        }
    });



});

async function updateDatabase() {
    console.log("123");
    try {
        const response = await fetch('http://127.0.0.1:8000/update-database', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data);
        } else {
            throw new Error('Linkler ayrıştırılamadı.');
        }
    } catch (error) {
        throw new Error(error.message);
    }
}

async function dropDatabase() {
    try {
        const response = await fetch('http://127.0.0.1:8000/drop-database', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log(data);
        } else {
            throw new Error('Linkler ayrıştırılamadı.');
        }
    } catch (error) {
        throw new Error(error.message);
    }
}