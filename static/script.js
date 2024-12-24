document.getElementById("submitBtn").addEventListener("click", function () {
    let inputText = document.getElementById("inputText").value.trim();

    if (inputText === "") {
        alert("Please enter some text!");
        return;
    }

    // Send the input text to the Flask server for prediction
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: inputText }),
    })
        .then((response) => response.json())
        .then((data) => {
            // Log the prediction to debug
            console.log("Prediction received from server:", data.prediction);

            // Display the prediction result
            document.getElementById("predictionResult").textContent = `Prediction: ${data.prediction}`;

            // Normalize the prediction text
            const prediction = data.prediction.trim().toLowerCase();
            const body = document.body;
            const container = document.querySelector(".container");

            // Handle background color changes
            if (prediction.includes("no hate") ) {
                body.style.backgroundColor = "#00ffff"; // Blue for No Hate and Offensive Speech
                container.style.backgroundColor = "#d0fcfc"; // Light blue for container
            } else if (prediction.includes("offensive speech")) {
                body.style.backgroundColor = "#ff0000"; // Red for Offensive Speech
                container.style.backgroundColor = "#fcd0d0"; // Light red for container
            } else {
                // Default background for unrecognized predictions
                body.style.backgroundColor = "#f4f4f4";
                container.style.backgroundColor = "white";
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
});

document.getElementById("clearBtn").addEventListener("click", function () {
    // Clear the textarea and prediction result
    document.getElementById("inputText").value = "";
    document.getElementById("predictionResult").textContent = "Prediction result will appear here...";

    // Reset the background color
    document.body.style.backgroundColor = "#f4f4f4"; // Default light gray background
    document.querySelector(".container").style.backgroundColor = "white"; // Default white container background
});
