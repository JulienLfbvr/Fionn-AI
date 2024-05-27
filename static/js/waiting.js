const carousels = document.querySelectorAll(".carousel");

let carouselIntervals = [];
let duration = [8000, 6000];
let carousel_interspace = 10;

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


// Do a loop of the carousel
function loopCarousel(carousel, duration) {
    moveCarouselUp(carousel, duration);

    setTimeout(() => {
        resetCarousel(carousel, duration);
    }, duration);
}

function start_carousels() {
    carousels.forEach((carousel, index) => {

        let interval = setInterval(() => {
            loopCarousel(carousel, duration[index]);
        }, (duration[index] + carousel_interspace));

        carouselIntervals.push(interval);
    });
}


let steps = ["tiles", "masks", "crops", "score", "redirect", false, false];

socket.on('message', (data) => {
    let ul = document.getElementById("log");
    let li = document.createElement("li");
    li.appendChild(document.createTextNode(data.text));

    // Appliquer une translation initiale sur l'axe X
    li.classList.add("transform", "-translate-y-full", "text-[#0b1d3e]", "text-4xl", "font-bold", "transition", "duration-500", "ease-in-out");
    ul.insertBefore(li, ul.firstChild);

    // Animer la translation X pour la ramener à sa position initiale
    setTimeout(() => {
        li.classList.remove("-translate-y-full");
        li.classList.add("translate-y-0");
    }, 10);

    // Décaler les autres éléments pour laisser la place au nouveau
    let otherLis = ul.getElementsByTagName("li");
    for (let i = 1; i < otherLis.length; i++) {
        otherLis[i].classList.remove("text-4xl", "font-bold");
        otherLis[i].classList.add("text-xl");

        let opacity = Math.max(1 - i * 0.2, 0.1);
        otherLis[i].style.opacity = opacity.toString();
        otherLis[i].style.transform = "translateY(" + 20 + "px)";
    }

    if (steps[data.step] == "tiles"){
        carousels.forEach(carousel => {
            carousel.classList.remove("hidden");
        });
            
        setTimeout(() => {
            carousels.forEach((carousel, index) => {
                loopCarousel(carousel, duration[index]);
            });

            start_carousels();
        }, 100);
    }

    if (steps[data.step] && steps[data.step] != "score" && steps[data.step] != "redirect" ) {
        fetch("/" + steps[data.step])
            .then(response => response.json())
            .then(data => {
                for (let i = 0; i < data.result.length; i++) {
                    let img = document.getElementById("img" + i);
                    img.src = data.result[i];
                    img = document.getElementById("img_" + i);
                    img.src = data.result[i];
                }
            });
    } 
    else if (steps[data.step] == "redirect") {
        window.location.replace(data.text);
    }
    else if (data.step == -2) {
        li.classList.add("text-teal-500");
    }
});