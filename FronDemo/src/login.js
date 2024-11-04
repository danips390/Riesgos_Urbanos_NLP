import * as backend from "./modules/backend_connection.js"
import { requestFeedback } from "./modules/ui_feedback.js"
import { redirectTo } from "./modules/user_fetch.js"

//DOM Ids
const IDs = {
    writeText: "text-write",
    sendButton: "text-send",

};

document.addEventListener("DOMContentLoaded", _ => {
    const elems = Object.keys(IDs).reduce((output, id) => {
        output[IDs[id]] = document.getElementById(IDs[id]);
        return output;
    }, {});

    //send text
    elems[IDs.sendButton].addEventListener("click", _ => {
        const texto = elems[IDs.writeText].value;
        if (texto === "") {
            alert("Por favor, escribe un texto.");
            return;
        }
        const request = backend.analyseTweet(texto); // Cambiar a función que elimine en backend
        requestFeedback(request, elems[IDs.sendButton], "", "Error");
        request.then(success => {
            if (!success) {
                alert("Texto sin entidades");
                return;
            }
            redirectTo("map");
        });
    });

});
