const chatbox = document.getElementById("chatbox");
const chatInput = document.getElementById("userMessage");

const createChatLi = (message, className, includeSmartToy = true) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);

    let chatContent;
    if (className === "outgoing") {
        chatContent = `<div class="mb-2 text-right"><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-red">${message}</p></div>`;
    } else {
        if (includeSmartToy) {
            chatContent = `<div class="mb-2 flex items-start"><span class="material-symbols-outlined line-height[32px] mb-2 mr-2 h-8 w-8 self-end rounded-md bg-white text-center text-gray-800"> smart_toy</span><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>`;
        } else {
            chatContent = `<div class="mb-2 flex items-start"><p class="white-space-pre-wrap max-w-[75%] rounded-bl-lg rounded-tl-lg bg-white px-4 py-3 text-lg text-black">${message}</p></div>`;
        }
    }

    chatLi.innerHTML = chatContent;
    return chatLi;
};

const generateRecommendationMessage = (emotion, recommendations) => {
    const randomIndex = Math.floor(Math.random() * recommendations.length);
    const recommendation = recommendations[randomIndex];

    if (recommendation) {
        const messages = {
            sadness: [
                `Feeling sad? Let this comforting song lift your spirits: ${recommendation.track_name} by ${recommendation.artist_name}.`,
                `In moments of sadness, find solace in this beautiful song: ${recommendation.track_name} by ${recommendation.artist_name}.`,
                `Also, you seem sad. How about listening to this soothing song: ${recommendation.track_name} by ${recommendation.artist_name}.`
            ],
            fear: [
                `Also, you seem fearful. How about listening to this calming religious song: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Listen here</a>.`,
                `Feeling fear? Find solace in this comforting religious song: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Listen here</a>.`,
                `Don't let fear overwhelm you. Listen to this soothing religious song: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Click here</a>.`
            ],
            anger: [
                `Channel your anger through this calming song: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Listen here</a>.`,
                `Feeling angry? Let this relaxing song ease your emotions: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Click here</a>.`,
                `In the face of anger, find tranquility with this soothing song: ${recommendation.track_name} by ${recommendation.artist_name}. <a href="${recommendation.track_url}" target="_blank">Listen here</a>.`
            ]
        };

        const recommendationMessages = messages[emotion];
        if (recommendationMessages) {
            const randomMessage = recommendationMessages[Math.floor(Math.random() * recommendationMessages.length)];

            // Return both the HTML content and the index
            return { recommendationChatLi: createChatLi(randomMessage, "incoming", false), index: randomIndex };
        }
    }

    // Return null if no recommendation is available
    return null;
};

const generateResponse = async (responseData) => {
    const { answer, emotion } = responseData;

    if (emotion && ['sadness', 'fear', 'anger'].includes(emotion)) {
        try {
            const recommendationsResponse = await fetch(`/recommendations?emotion=${emotion}`);
            if (recommendationsResponse.ok) {
                const recommendationsData = await recommendationsResponse.json();
                const recommendationData = generateRecommendationMessage(emotion, recommendationsData.recommendations);

                // Concatenate the raw text content of both messages
                const combinedContent = answer + ' ' + recommendationData.recommendationChatLi.textContent;
                
                // Create a single div element to hold both messages
                const combinedChatLi = createChatLi(combinedContent, "incoming");

                // Append the combined content to the chatbox
                chatbox.appendChild(combinedChatLi);

                // Add the link to the chatbox
                const link = `<a href="${recommendationsData.recommendations[recommendationData.index].track_url}" target="_blank">Listen here</a>.`;
                chatbox.insertAdjacentHTML('beforeend', link);

                chatbox.scrollTo(0, chatbox.scrollHeight);
            } else {
                console.error(`Failed to get recommendations. Status: ${recommendationsResponse.status}`);
            }
        } catch (error) {
            console.error(`Error fetching recommendations: ${error}`);
        }
    } else {
        const incomingChatLi = createChatLi(answer, "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
    }
};




const handleChat = async () => {
    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    chatInput.value = "";

    const outgoingChatLi = createChatLi(userMessage, "outgoing");
    chatbox.appendChild(outgoingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pattern: userMessage }),
        });

        if (response.ok) {
            const responseData = await response.json();
            generateResponse(responseData);
        } else {
            console.error(`Failed to get response. Status: ${response.status}`);
        }
    } catch (error) {
        console.error(`Error handling chat: ${error}`);
    }
};

chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        handleChat();
    }
});
