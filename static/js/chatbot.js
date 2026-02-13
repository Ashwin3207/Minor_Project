/**
 * Chatbot JavaScript
 * Handles chat UI interactions and API communication
 */

document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    const suggestionsList = document.getElementById('suggestionsList');
    const loadingSpinner = document.getElementById('loadingSpinner');

    let isWaitingForResponse = false;

    // Load suggestions on page load
    loadSuggestions();

    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message || isWaitingForResponse) return;

        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';

        // Hide suggestions when user starts chatting
        suggestionsContainer.style.display = 'none';

        // Show loading indicator
        showTypingIndicator();
        setWaitingState(true);

        // Send message to API
        sendMessage(message);
    });

    // Allow Enter key to send message
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && !isWaitingForResponse) {
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Suggestion buttons click handler
    suggestionsList.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-btn')) {
            const suggestionText = e.target.textContent.trim();
            messageInput.value = suggestionText;
            messageInput.focus();
            // Optional: auto-submit the suggestion
            // chatForm.dispatchEvent(new Event('submit'));
        }
    });

    /**
     * Add a message to the chat display
     */
    function addMessage(text, sender) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `message-container ${sender}-container`;

        const messageBubble = document.createElement('div');
        messageBubble.className = `chat-message ${sender}-message`;
        messageBubble.innerHTML = formatMessage(text);

        messageContainer.appendChild(messageBubble);
        chatMessages.appendChild(messageContainer);

        // Scroll to bottom
        scrollToBottom();
    }

    /**
     * Format message text (convert markdown-like syntax)
     */
    function formatMessage(text) {
        // Convert **text** to <strong>text</strong>
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert new lines to <br>
        text = text.replace(/\n/g, '<br>');
        
        // Convert URLs to links
        text = text.replace(
            /(?:https?:\/\/|www\.)[^\s]+/g,
            '<a href="$&" target="_blank">$&</a>'
        );
        
        return text;
    }

    /**
     * Show typing indicator
     */
    function showTypingIndicator() {
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container bot-container';
        messageContainer.id = 'typingIndicator';

        const indicator = document.createElement('div');
        indicator.className = 'chat-message bot-message';
        indicator.innerHTML = '<div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';

        messageContainer.appendChild(indicator);
        chatMessages.appendChild(messageContainer);

        scrollToBottom();
    }

    /**
     * Remove typing indicator
     */
    function removeTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    /**
     * Scroll chat to bottom
     */
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    /**
     * Send message to chatbot API
     */
    function sendMessage(message) {
        fetch('/chatbot/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            removeTypingIndicator();

            if (data.success && data.answer) {
                addMessage(data.answer, 'bot');
            } else {
                addMessage('Sorry, I couldn\'t process your request. Please try again.', 'bot');
            }

            setWaitingState(false);
        })
        .catch(error => {
            removeTypingIndicator();
            console.error('Error:', error);
            addMessage('Sorry, there was an error communicating with the chatbot. Please try again.', 'bot');
            setWaitingState(false);
        });
    }

    /**
     * Load suggestions from API
     */
    function loadSuggestions() {
        fetch('/chatbot/api/suggestions', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                displaySuggestions(data.suggestions);
            }
        })
        .catch(error => {
            console.error('Error loading suggestions:', error);
        });
    }

    /**
     * Display suggestion buttons
     */
    function displaySuggestions(suggestions) {
        suggestionsList.innerHTML = '';
        suggestions.forEach(suggestion => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'suggestion-btn';
            btn.textContent = suggestion;
            suggestionsList.appendChild(btn);
        });
        suggestionsContainer.style.display = 'block';
    }

    /**
     * Set waiting state for response
     */
    function setWaitingState(waiting) {
        isWaitingForResponse = waiting;
        sendBtn.disabled = waiting;
        messageInput.disabled = waiting;
        
        if (waiting) {
            sendBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Thinking...';
            loadingSpinner.classList.remove('d-none');
        } else {
            sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send';
            loadingSpinner.classList.add('d-none');
        }
    }
});
