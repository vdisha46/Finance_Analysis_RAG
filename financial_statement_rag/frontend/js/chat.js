const chatWindow = document.getElementById('chatWindow');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendChatBtn');

function appendMessage(sender, text) {
    const div = document.createElement('div');
    div.className = `p-3 mb-2 rounded chat-bubble-${sender}`;
    div.textContent = text;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

async function sendChatMessage(question) {
    appendMessage('user', question);
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    });
    const data = await response.json();
    appendMessage('ai', data.answer || 'No answer found.');
}

sendBtn?.addEventListener('click', () => {
    const question = chatInput.value.trim();
    if (!question) return;
    sendChatMessage(question);
    chatInput.value = '';
});

document.querySelectorAll('.question-btn').forEach(button => {
    button.addEventListener('click', () => sendChatMessage(button.textContent));
});
