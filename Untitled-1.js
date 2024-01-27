
const chatbox = document.getElementById("chatbox");
const chatInput = document.getElementById("userMessage");
const dataCardsQueue = document.querySelector(".data-cards-queue");

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = className === "outgoing" ? `<div class="mb-2 text-right"><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>` : `<div class="mb-2 flex items-start"><span class="material-symbols-outlined line-height[32px] mb-2 mr-2 h-8 w-8 self-end rounded-md bg-white text-center text-gray-800">smart_toy</span><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>`;
    chatLi.innerHTML = chatContent;
    return chatLi;
}

const generateFearMessage = (recommendation) => {
    const messages = [
        `Also, you seem fearful. How about listening to this calming religious song: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`,
        `Feeling fear? Find solace in this comforting religious song: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`,
        `Don't let fear overwhelm you. Listen to this soothing religious song: ${recommendation.track_name} by ${recommendation.artist_name}. Click [here](${recommendation.track_url}).`
    ];
    return messages[Math.floor(Math.random() * messages.length)];
}
const generateSadnessMessage = (recommendation) => {
    const messages = [
        `Feeling sad? Let this comforting song lift your spirits: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`,
        `In moments of sadness, find solace in this beautiful song: ${recommendation.track_name} by ${recommendation.artist_name}. Click [here](${recommendation.track_url}).`,
        `Also, you seem sad. How about listening to this soothing song: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`
    ];
    return messages[Math.floor(Math.random() * messages.length)];
}
const generateAngerMessage = (recommendation) => {
    const messages = [
        `Channel your anger through this calming song: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`,
        `Feeling angry? Let this relaxing song ease your emotions: ${recommendation.track_name} by ${recommendation.artist_name}. Click [here](${recommendation.track_url}).`,
        `In the face of anger, find tranquility with this soothing song: ${recommendation.track_name} by ${recommendation.artist_name}. Listen [here](${recommendation.track_url}).`
    ];
    return messages[Math.floor(Math.random() * messages.length)];
}

const generateResponse = async (responseData) => {
    const { answer, emotion } = responseData;
    const incomingChatLi = createChatLi(answer, "incoming");
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Fetch and display music recommendations based on emotion
    if (emotion) {
        try {
            const recommendationsResponse = await fetch(`/recommendations?emotion=${emotion}`);
            if (recommendationsResponse.ok) {
                const recommendationsData = await recommendationsResponse.json();

                // Display a special message for sadness
                if (emotion === 'sadness') {
                    const sadnessRecommendation = recommendationsData.recommendations[0];
                    const sadnessMessage = generateSadnessMessage(sadnessRecommendation);
                    const sadnessChatLi = createChatLi(sadnessMessage, "incoming");
                    chatbox.appendChild(sadnessChatLi);
                    chatbox.scrollTo(0, chatbox.scrollHeight);
                }

                // Display a special message for fear
                if (emotion === 'fear') {
                    const fearRecommendation = recommendationsData.recommendations[0];
                    const fearMessage = generateFearMessage(fearRecommendation);
                    const fearChatLi = createChatLi(fearMessage, "incoming");
                    chatbox.appendChild(fearChatLi);
                    chatbox.scrollTo(0, chatbox.scrollHeight);
                }

                // Display a special message for anger
                if (emotion === 'anger') {
                    const angerRecommendation = recommendationsData.recommendations[0];
                    const angerMessage = generateAngerMessage(angerRecommendation);
                    const angerChatLi = createChatLi(angerMessage, "incoming");
                    chatbox.appendChild(angerChatLi);
                    chatbox.scrollTo(0, chatbox.scrollHeight);
                }

                // The rest of the code for displaying general recommendations remains unchanged
                recommendationsData.recommendations.forEach((rec) => {
                    const recommendationMessage = createChatLi(`Check out this song: ${rec.track_name} by ${rec.artist_name}. Listen [here](${rec.track_url}).`, "incoming");
                    chatbox.appendChild(recommendationMessage);
                    chatbox.scrollTo(0, chatbox.scrollHeight);
                });
            } else {
                throw new Error(`Failed to get recommendations. Status: ${recommendationsResponse.status}`);
            }
        } catch (error) {
            console.error(error);
            const errorMessage = "Oops! Something went wrong while fetching recommendations.";
            const errorChatLi = createChatLi(errorMessage, "incoming");
            chatbox.appendChild(errorChatLi);
            chatbox.scrollTo(0, chatbox.scrollHeight);
        }
    }
}

// Additional JavaScript code (if needed)...
chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        handleChat();
    }
});
