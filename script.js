document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

let chatHistory = [];

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const messageText = inputField.value.trim();
    
    if (!messageText) return;

    appendMessage(messageText, 'user-message');
    inputField.value = '';

    try {

        const response = await fetch('https://well-being-companionai.onrender.com/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify({ 
                message: messageText,
                history: chatHistory 
            })
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 429) {
                appendMessage("I'm pausing to gather my thoughts. Please wait a short moment before sending your next message! 🤍", 'assistant-message');
            } else {
                appendMessage(`Error: ${data.detail || "Something went wrong on the server."}`, 'assistant-message');
            }
            return;
        }

        if (data.crisis_triggered) {
            appendMessage(data.response, 'message crisis-message');
        } else {
            const finalReply = data.response || "I heard you, but my response text format was blank.";
            appendMessage(finalReply, 'assistant-message');

            chatHistory.push({ sender: 'user', text: messageText });
            chatHistory.push({ sender: 'assistant', text: finalReply });
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
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
