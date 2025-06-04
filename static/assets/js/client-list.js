
        function showNoFactureMessage(event) {
            event.preventDefault();
            alert("Pas de facture, cette personne n'est pas encore devenue un membre.");
        }
   
        
        function openModal() {
            document.getElementById("modal-client").style.display = "flex";
        }
    
        function closeModal() {
            document.getElementById("modal-client").style.display = "none";
            document.querySelector("#modal-client form").reset();
    
            // Supprimer les messages d'alerte
            var alerts = document.querySelectorAll("#modal-client .alert");
            alerts.forEach(alert => alert.remove());
        }
    
        window.onclick = function(event) {
            var modal = document.getElementById("modal-client");
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }
    
        // Fonction de validation du formulaire
        function validateForm(event) {
            var checkbox = document.getElementById("confirm-checkbox");
            var errorMessage = document.getElementById("error-message");
            var btnText = document.getElementById("btn-text");
            var loader = document.getElementById("loader");
    
            // Si la case n'est pas cochée, on bloque l'envoi et affiche un message d'erreur
            if (!checkbox.checked) {
                errorMessage.style.display = "block";
                event.preventDefault(); // Empêche l'envoi du formulaire
                return false;
            } else {
                // Si la case est cochée, on cache le message d'erreur et on montre le loader
                errorMessage.style.display = "none";
    
                // Effet loader
                btnText.style.display = "none";
                loader.style.display = "inline-block";
    
                return true; // Permet l'envoi du formulaire
            }
        }
       
       //suppression :
       function openDeleteModal(counter) {
        document.getElementById(`deleteModal${counter}`).style.display = "flex";
    }
    
    function closeDeleteModal(counter) {
        document.getElementById(`deleteModal${counter}`).style.display = "none";
    }
    window.addEventListener("click", function(event) {
        const modals = document.querySelectorAll(".custom-modal");
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        });
    });
        

    window.addEventListener('DOMContentLoaded', function () {
       const modalShouldOpen = {{ modal_open|yesno:"true,false" }};
       if (modalShouldOpen) {
           document.getElementById("modal-client").style.display = "flex";
       }
   });

