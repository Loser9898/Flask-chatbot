

document.addEventListener("DOMContentLoaded", () => {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");

    function appendMessage(sender, message) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add(sender + "-message");
        msgDiv.innerText = message;
        chatBox.appendChild(msgDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage("user", message);
        userInput.value = "";

        appendMessage("bot", "✍️ टाइप गर्दैछ...");

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        chatBox.lastChild.innerText = data.reply;
    }

    async function startVoice() {
        const response = await fetch("/voice");
        const data = await response.json();
        appendMessage("user", "🎤 " + data.voice_text);
        sendMessageFromVoice(data.voice_text);
    }

    async function sendMessageFromVoice(text) {
        appendMessage("bot", "✍️ टाइप गर्दैछ...");

        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text })
        });

        const data = await response.json();
        chatBox.lastChild.innerText = data.reply;

        fetch("/speak", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: data.reply })
        });
    }

    function toggleDarkMode() {
        document.body.classList.toggle("dark-mode");
    }

    window.sendMessage = sendMessage;
    window.startVoice = startVoice;
    window.toggleDarkMode = toggleDarkMode;
});