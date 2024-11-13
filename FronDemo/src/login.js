import * as backend from "./modules/backend_connection.js";
import { requestFeedback } from "./modules/ui_feedback.js";
// DOM Ids
const IDs = {
    writeText: "text-write",
    sendButton: "text-send",
    openModal: "new-tweet-button",
    closeModal: "close-modal",
    modal: "tweet-modal"
};

// Esperar a que el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    const elems = Object.keys(IDs).reduce((output, id) => {
        output[IDs[id]] = document.getElementById(IDs[id]);
        return output;
    }, {});

    // Abrir el modal
    elems[IDs.openModal].addEventListener("click", () => {
        elems[IDs.modal].style.display = "flex";
    });

    // Cerrar el modal
    elems[IDs.closeModal].addEventListener("click", () => {
        elems[IDs.modal].style.display = "none";
    });

    // Enviar el texto
    elems[IDs.sendButton].addEventListener("click", () => {
        const texto = elems[IDs.writeText].value;
        if (texto === "") {
            alert("Por favor, escribe un texto.");
            return;
        }

        const request = backend.analyseTweet(texto);
        requestFeedback(request, elems[IDs.sendButton], "", "Error");
        request.then(mapHTML => {
            if (!mapHTML) {
                alert("Texto sin entidades");
                return;
            }
            alert("Tweet enviado correctamente.");
            elems[IDs.writeText].value = "";  // Limpiar el campo de texto
            elems[IDs.modal].style.display = "none";  // Cerrar el modal después de enviar

            // Actualizar el contenido del iframe con el nuevo HTML del mapa
            const mapIframe = document.getElementById("qgis-map");
            mapIframe.contentDocument.open();
            mapIframe.contentDocument.write(mapHTML);
            mapIframe.contentDocument.close();
        });
    });
});
