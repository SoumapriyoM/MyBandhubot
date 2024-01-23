const chatbox = document.getElementById("chatbox");
    const chatInput = document.getElementById("userMessage");

    const createChatLi = (message, className) => {
        const chatLi = document.createElement("li");
        chatLi.classList.add("chat", `${className}`);
        let chatContent = className === "outgoing" ? `<div class="mb-2 text-right"><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>` : `<div class="mb-2 flex items-start"><span class="material-symbols-outlined line-height[32px] mb-2 mr-2 h-8 w-8 self-end rounded-md bg-white text-center text-gray-800">smart_toy</span><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>`;
        chatLi.innerHTML = chatContent;
        return chatLi;
    }

    const generateResponse = (responseMessage) => {
        const incomingChatLi = createChatLi(responseMessage, "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
    }

    const handleChat = async () => {
        const userMessage = chatInput.value.trim();
        if (!userMessage) return;

        chatInput.value = ""; // Clear the input textarea

        const outgoingChatLi = createChatLi(userMessage, "outgoing");
        chatbox.appendChild(outgoingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);

        try {
            // Send user's message to the FastAPI app for prediction
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ pattern: userMessage }),
            });

            if (response.ok) {
                const responseData = await response.json();
                generateResponse(responseData.answer);
            } else {
                throw new Error(`Failed to get response. Status: ${response.status}`);
            }
        } catch (error) {
            console.error(error);
            const errorMessage = "Oops! Something went wrong. Please try again.";
            const errorChatLi = createChatLi(errorMessage, "incoming");
            chatbox.appendChild(errorChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }
    }

    // Additional JavaScript code (if needed)...
    chatInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            handleChat();
        }
    });