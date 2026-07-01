document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const messageText = inputField.value.trim();
    
    if (!messageText) return;

    // 1. Append User Message visually
    appendMessage(messageText, 'user-message');
    inputField.value = '';

    try {
        // 2. Query our FastAPI Python Server
        const response = await fetch('https://well-being-companionai.onrender.com/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: messageText })
        });

        const data = await response.json();

        // Check if the server returned an error detail message instead
        if (!response.ok) {
            appendMessage(`Error: ${data.detail || "Something went wrong on the server."}`, 'assistant-message');
            return;
        }

        // 3. Handle a proper response or fall back gracefully
        if (data.crisis_triggered) {
            appendMessage(data.response, 'message crisis-message');
        } else {
            // Safe fallback if data.response isn't an exact match
            const finalReply = data.response || "I heard you, but my response text format was blank.";
            appendMessage(finalReply, 'assistant-message');
        }

    } catch (error) {
        console.error('Error communicating with server:', error);
        appendMessage("I'm having trouble connecting to my brain right now. Please make sure the backend server is running.", 'assistant-message');
    }
}

function appendMessage(text, className) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerText = text;
    
    chatMessages.appendChild(messageDiv);
    // Auto-scroll panel to the bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}