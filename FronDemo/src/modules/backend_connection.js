import { HttpError, ResponseFormatError } from "./errors.js"

const LOCAL_HOST = "http://127.0.0.1:8000";
const GLOBAL_HOST = "missing"//"http://18.224.67.125";
const API_URI = "http://127.0.0.1:8000";
// const API_URI = GLOBAL_HOST;

//Api on start validation
fetch(`${API_URI}/`, {
    method : "GET"
}).then(response => {
    if (!response.ok){
        console.error("conexion con backend fallida");
        console.error({"error code":response.status});
    }
    return response.json();
})
.then(_ => {})
.catch(error => {
    console.error(error);
});

//Throws an expcetion if the format of the response does not match the expected one
//Otherwiise does nothing and returns undefined
function validateResponseFormat(response, expectedFormat) {
    if (!response || !expectedFormat || typeof response !== typeof expectedFormat)
        throw new ResponseFormatError("Null or undefined parameters");

    const expected = Object.keys(expectedFormat);
    if (Object.keys(response).length !== expected.length)
        throw new ResponseFormatError("Invalid response format structure");

    for (let key of expected) {
        if (!response.hasOwnProperty(key))
            throw new ResponseFormatError("Invalid response format structure");

        const responseVal = response[key];
        const expectedVal = expectedFormat[key];
        if (expectedVal === undefined)
            continue;
        if (typeof expectedVal !== typeof responseVal)
            throw new ResponseFormatError(`Invalid attribute "${key}" type`);
        if (typeof expectedVal === "object" && !Array.isArray(expectedVal))
            validateResponseFormat(responseVal, expectedVal);
    }
}

//Api Calls
//Send the text
export async function analyseTweet(text) {
    const fetchURI = `${API_URI}/user/process`;
    const response = await fetch(fetchURI, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text }) // Enviar el texto en el cuerpo de la solicitud
    });

    const parsedResponse = await response.json();

    if (!response.ok) 
        throw new HttpError(response.status, parsedResponse);
    
    validateResponseFormat(parsedResponse, { "valid_text": true });


    return parsedResponse.valid_text;
}


