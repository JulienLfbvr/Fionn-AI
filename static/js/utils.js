 // Fonction pour charger et traiter le fichier CSV
 function chargerFichierCSV() {
    return fetch('../static/js/C2321120-1-A-PAS1.csv') // Utilisation de '../' pour remonter au niveau du dossier "static"
        .then(response => response.text())
        .then(data => {
            // Traitement du fichier CSV
            let lignes = data.split('\n');
            // Exclure la première ligne
            for (let i = 1; i < lignes.length; i++) {
                let colonnes = lignes[i].split(';');
                let cheminComplet = colonnes[0]; // Supposons que la première colonne contient le chemin de l'image

                let cheminRelatif = cheminComplet.split('server')[1]; // Récupération du chemin relatif

                // Créer une nouvelle div pour afficher l'image
                let nouvelleDiv = document.createElement('div');
                nouvelleDiv.classList.add('flex', 'flex-col', 'items-center', 'image-container');
                
                let nouvelleImage = document.createElement('img');
                nouvelleImage.src = cheminRelatif;
                nouvelleImage.width = "170";

                let nouveauParagraphe = document.createElement('p');
                nouveauParagraphe.classList.add('text-center');
                nouveauParagraphe.textContent = "Texte sous l'image " + (i + 1); // Comme l'index commence à 0, on ajoute 1

                nouvelleDiv.appendChild(nouvelleImage);
                nouvelleDiv.appendChild(nouveauParagraphe);

                // Ajouter la nouvelle div au div avec l'id "images"
                document.getElementById('images').appendChild(nouvelleDiv);
            }
        })
        .catch(error => {
            console.error('Une erreur s\'est produite lors du chargement du fichier CSV :', error);
        });
}



function chargerFichierCSVetNombreLesion() {
    return fetch('../static/js/C2321120-1-A-PAS1.csv')
        .then(response => response.text())
        .then(data => {
            // Diviser les données CSV en lignes
            let lignes = data.split('\n');

            let count_yesM = 0;
            let count_yesE = 0;
            let count_yesS = 0;
            let count_yesC = 0;

            // Parcourir chaque ligne de données
            lignes.forEach(function(ligne) {
                // Diviser la ligne en colonnes
                let colonnes = ligne.split(';');

                // Vérifier si M est oui
                if (colonnes[5] == 1) {
                    count_yesM++;
                }
                // Vérifier si E est oui
                if (colonnes[6] == 1) {
                    count_yesE++;
                }
                // Vérifier si S est oui
                if (colonnes[7] == 1) {
                    count_yesS++;
                }
                // Vérifier si C est oui
                if (colonnes[8] == 1) {
                    count_yesC++;
                }
            });
            
            
            // Retourner les résultats
            return {
                count_yesM: count_yesM,
                count_yesE: count_yesE,
                count_yesS: count_yesS,
                count_yesC: count_yesC
            };
            
        });
        
}

chargerFichierCSVetNombreLesion().then(results => {
    const GraphLesionData = {
        labels: ['M', 'E', 'S', 'C'],
        datasets: [{
            label: 'Nombre de glomérules pour la WSI',
            data: [results.count_yesM, results.count_yesE, results.count_yesS, results.count_yesC],
            backgroundColor: [
                'rgba(59, 130, 246, 0.9)',
                'rgba(59, 130, 246, 0.9)',
                'rgba(59, 130, 246, 0.9)',
                'rgba(59, 130, 246, 0.9)',
            ],
            borderColor: [
                'rgb(59, 130, 246)',
                'rgb(59, 130, 246)',
                'rgb(59, 130, 246)',
                'rgb(59, 130, 246)',
            ],
            borderWidth: 2
        }]
    };

    const GraphLesionAccuracyData = {
        labels: ['M', 'E', 'S', 'C'],
        datasets: [{
            label: 'Accuracy du modèle pour la lésion',
            data: [results.count_yesM, results.count_yesE, results.count_yesS, results.count_yesC],
            backgroundColor: [
                'rgba(59, 130, 246, 0.9)',
                'rgba(59, 150, 246, 0.9)',
                'rgba(59, 170, 246, 0.9)',
                'rgba(59, 190, 246, 0.9)',
            ],
            borderColor: [
                'rgb(59, 130, 246)',
                'rgb(59, 150, 246)',
                'rgb(59, 170, 246)',
                'rgb(59, 190, 246)',
            ],
            borderWidth: 2
        }]
    };

    const config = {
        type: 'bar',
        data: GraphLesionData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            responsive: false,
            maintainAspectRatio: true,
            plugins: {
                title: {
                    display: true,
                    text: 'Nombre de glomérules par lésion',
                    color: 'rgb(59, 130, 246)',
                    font: {
                        weight: 'bold',
                        size: 20
                    }
                },
                legend: {
                    display: false
                },
            }
        }
    };

    const config2 = {
        type: 'polarArea',
        data: GraphLesionAccuracyData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            },
            responsive: false,
            maintainAspectRatio: true,
            legend: {
                display: true,
                labels: {
                    generateLabels: function (chart) {
                        const labels = chart.data.datasets.map(function (dataset, index) {
                            return {
                                text: dataset.label,
                                fillStyle: dataset.borderColor,
                                strokeStyle: dataset.borderColor,
                                lineWidth: 1,
                                hidden: false,
                                index: index
                            };
                        });
                        return labels;
                    }
                }
            }
        }
    };

    const canvasElement = document.getElementById('GraphLesion');
    const GraphLesion = new Chart(canvasElement, config);

    const canvasElement2 = document.getElementById('GraphAccuracy');
    const GraphAccuracy = new Chart(canvasElement2, config2);

});

chargerFichierCSV()

