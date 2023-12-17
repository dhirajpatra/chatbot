document.addEventListener("DOMContentLoaded", function() {
    // Add initial message to chat container
    appendMessage("Chat Bot", "Hello! Type a message and press send.");

    // Set up event listener for input field
    document.getElementById("message-input").addEventListener("keyup", function(event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
});

function sendMessage() {
    // Get user input
    var userInput = document.getElementById("message-input").value;

    // Add user's message to chat container
    appendMessage("You", userInput, true);

    // Call Azure Function API
    callAzureFunctionAPI(userInput);

    // Clear the input field
    document.getElementById("message-input").value = "";
}

function appendMessage(sender, message, isUser = false) {
    var chatContainer = document.getElementById("chat-container");
    var messageDiv = document.createElement("div");
    messageDiv.className = isUser ? "user-message" : "bot-message";

    // Check if the message is an array (indicating a tabular response)
    if (Array.isArray(message)) {
        var table = document.createElement("table");
        table.className = "response-table";

        // // Split the first element to get headers
        // var headers = message[0].split("\t");

        // // Add headers
        // var headerRow = table.insertRow(0);
        // for (var i = 0; i < headers.length; i++) {
        //     var headerCell = headerRow.insertCell(i);
        //     headerCell.innerHTML = `<strong>${headers[i]}</strong>`;
        // }

        // Add data rows
        for (var i = 0; i < message.length; i++) {
            var dataRow = table.insertRow(i);
            var rowData = message[i].split("\t");
            for (var j = 0; j < rowData.length; j++) {
                var dataCell = dataRow.insertCell(j);
                dataCell.innerHTML = rowData[j];
            }
        }

        messageDiv.appendChild(table);
    } else {
        // Display as a regular message
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    }

    chatContainer.appendChild(messageDiv);

    // Scroll to the bottom to show the latest message
    chatContainer.scrollTop = chatContainer.scrollHeight;
}


function callAzureFunctionAPI(userInput) {
    // Replace with your Azure Function API endpoint
    var apiUrl = "https://chatbotfuncappdhiraj.azurewebsites.net/api/chat?code=wIkCDqa6opZhczjy2-vcMKQY70Ry1e7bD8Gt9ky9SGicAzFu4ADkPw==";

    // Make a POST request to the Azure Function API
    fetch(apiUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-function-key": "wIkCDqa6opZhczjy2-vcMKQY70Ry1e7bD8Gt9ky9SGicAzFu4ADkPw==",
        },
        body: JSON.stringify({ "message": userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Log the entire response in the console
        console.log("Azure Function API Response:", data);

        // Add bot's response to chat container
        appendMessage("Chat Bot", data.response);
    })
    .catch(error => console.error("Error:", error));
}
