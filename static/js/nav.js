function clickOnPopUp(){
    const history = document.getElementById("history");
    history.addEventListener("click", () => {
        const popup = document.getElementById("popup")
        if(popup.classList.contains("hidden")){
            popup.classList.remove("slide-right")
            popup.classList.remove("hidden")
            popup.classList.add("slide-left")
        }
        else{
            popup.classList.remove("slide-left")
            popup.classList.add("slide-right")
            setTimeout(() => {
                popup.classList.add("hidden")
            }, 500);
        }
        
    })
}

clickOnPopUp()