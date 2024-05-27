const carousels = document.querySelectorAll(".carousel");
//const folders = ['original', 'crop256', 'mask'];

let duration = [8000, 6000];
let carousel_interspace = 10;

// Sélectionner un dossier aléatoirement
function getRandomFolder() {
    const randomIndex = Math.floor(Math.random() * folders.length);
    return folders[randomIndex];
}

function moveCarouselUp(carousel, duration) {
    carousel.classList.remove("translate-y-0");
    carousel.classList.add("translate-y-[-125%]");
    carousel.classList.add("transition", `duration-[${duration}ms]`);
}

function resetCarousel(carousel, duration) {
    carousel.classList.remove("transition", `duration-[${duration}ms]`);
    carousel.classList.remove("translate-y-[-125%]");
    carousel.classList.add("translate-y-0");
}

// Boucle de carrousel
function loopCarousel(carousel, duration) {
    console.log(carousel, duration);
    
    moveCarouselUp(carousel, duration);

    setTimeout(() => {
        resetCarousel(carousel, duration);
    }, duration);
}

function startCarousels() {
    carousels.forEach((carousel, index) => {
        // Choix du dossier et attribution des images
        const selectedFolder = "original"; //getRandomFolder();
        for (let i = 0; i < 10; i++) {
            const imgElement = carousel.querySelector(`#img${i}`);
            const imgElement2 = carousel.querySelector(`#img_${i}`);
            if (imgElement) {
                if (selectedFolder === 'mask') {
                    imgElement.src = `static/img/${selectedFolder}/image${i + 1}.png`; // Assurez-vous que les noms d'images correspondent
                    imgElement2.src = `static/img/${selectedFolder}/image${i + 1}.png`; // Assurez-vous que les noms d'images correspondent
                } else {
                // Construire le chemin de l'image
                imgElement.src = `static/img/${selectedFolder}/image${i + 1}.jpeg`; // Assurez-vous que les noms d'images correspondent
                imgElement2.src = `static/img/${selectedFolder}/image${i + 1}.jpeg`; // Assurez-vous que les noms d'images correspondent
                }
            }
        }

        loopCarousel(carousel, duration[index]);

        setInterval(() => {
            loopCarousel(carousel, duration[index]);
        }, (duration[index] + carousel_interspace));

        // Recommencer après la fin de la dernière animation
        setTimeout(() => {
            startCarousels();
        }, 10000000);
    });
}

startCarousels();
