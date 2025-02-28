document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.querySelector(".chatbot-toggle");
    const window = document.querySelector(".chatbot-window");
    const close = document.querySelector(".chat-close");
    const sendBtn = document.querySelector("#chat-send");
    const input = document.querySelector("#chat-input");
    const chatBody = document.querySelector("#chat-body");

    // Toggle chatbot window
    toggle.addEventListener("click", () => {
        window.style.display = window.style.display === "flex" ? "none" : "flex";
        if (window.style.display === "flex" && !chatBody.innerHTML) {
            const welcomeMsg = document.createElement("div");
            welcomeMsg.className = "chat-message bot";
            welcomeMsg.textContent = "Hi! I’m your Garden Assistant—ask me about your rooftop plantation!";
            chatBody.appendChild(welcomeMsg);
        }
    });

    // Close chatbot window
    close.addEventListener("click", () => {
        window.style.display = "none";
    });

    // Send message
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        const userMsg = document.createElement("div");
        userMsg.className = "chat-message user";
        userMsg.textContent = message;
        chatBody.appendChild(userMsg);

        input.value = "";
        const loadingMsg = document.createElement("div");
        loadingMsg.className = "chat-message bot";
        loadingMsg.textContent = "Thinking...";
        chatBody.appendChild(loadingMsg);
        chatBody.scrollTop = chatBody.scrollHeight;

        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            chatBody.removeChild(loadingMsg);
            const botMsg = document.createElement("div");
            botMsg.className = "chat-message bot";
            botMsg.textContent = data.response;
            chatBody.appendChild(botMsg);
            chatBody.scrollTop = chatBody.scrollHeight;
        })
        .catch(() => {
            chatBody.removeChild(loadingMsg);
            const botMsg = document.createElement("div");
            botMsg.className = "chat-message bot";
            botMsg.textContent = "Oops, something went wrong—try again!";
            chatBody.appendChild(botMsg);
        });
    }
});