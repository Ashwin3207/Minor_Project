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

    // Initialize AI provider badge
    initializeAIProviderBadge();

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
        console.log('[AskAssistant] Sending message:', message);
        fetch('/chatbot/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(errorBody => {
                    console.error('[AskAssistant] API HTTP error:', {
                        status: response.status,
                        body: errorBody
                    });
                    throw new Error(`HTTP error! status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('[AskAssistant] API response:', data);
            removeTypingIndicator();

            if (data.answer) {
                console.log('[AskAssistant] Assistant answer:', {
                    extraction_method: data.extraction_method || 'unknown',
                    intent: data.intent || null,
                    answer: data.answer
                });
                addMessage(data.answer, 'bot');
                
                // Show AI provider information
                updateAIProviderBadge(data.extraction_method, data.confidence, data.intent);
                if (!data.success) {
                    console.warn('[AskAssistant] Backend returned success=false but provided an answer:', data);
                    if (data.context === 'ai_unavailable') {
                        console.error('[AskAssistant] AI provider failure details:', data.ai_error || 'No error details returned');
                    }
                }
            } else {
                console.error('[AskAssistant] Invalid/unsuccessful response payload:', data);
                addMessage('Sorry, I couldn\'t process your request. Please try again.', 'bot');
                updateAIProviderBadge('error', 'low');
            }

            setWaitingState(false);
        })
        .catch(error => {
            removeTypingIndicator();
            console.error('[AskAssistant] Request failed:', error);
            addMessage('Sorry, there was an error communicating with the chatbot. Please try again.', 'bot');
            updateAIProviderBadge('error', 'low');
            setWaitingState(false);
        });
    }

    /**
     * Update AI provider badge to show which AI was used
     */
    function updateAIProviderBadge(method, confidence, intent) {
        const badge = document.getElementById('aiProviderBadge');
        if (!badge) return;

        let badgeText = '✓ ';
        let badgeColor = '#28a745';
        
        if (method === 'gemini') {
            badgeText += 'Gemini AI';
            badgeColor = '#1a73e8';
        } else if (method === 'mistral') {
            badgeText += 'Mistral AI';
            badgeColor = '#0d47a1';
        } else if (method === 'keyword_fallback') {
            badgeText += '📚 Pattern Match';
            badgeColor = '#ff9800';
        } else if (method === 'error') {
            badgeText = '⚠️ Error';
            badgeColor = '#dc3545';
        } else {
            badgeText += 'Processing';
            badgeColor = '#017cba';
        }

        // Add confidence indicator
        if (confidence === 'high') {
            badgeText += ' ✓✓';
        } else if (confidence === 'medium') {
            badgeText += ' ✓';
        } else if (confidence === 'low') {
            badgeText += ' •';
        }

        badge.textContent = badgeText;
        badge.style.backgroundColor = 'rgba(0,0,0,0.2)';
        badge.title = `Intent: ${intent || 'unknown'} | Confidence: ${confidence || 'unknown'} | Method: ${method || 'unknown'}`;
    }

    /**
     * Initialize AI provider badge on page load
     */
    function initializeAIProviderBadge() {
        const badge = document.getElementById('aiProviderBadge');
        if (!badge) return;
        
        // Check which AI provider is available
        fetch('/chatbot/api/health', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            // Try to detect which provider is configured
            // This is determined by the first query, but we can show a ready state
            badge.textContent = '🤖 Ready to Chat';
            badge.title = 'Click below to start chatting with the Intelligent Placement Assistant';
            badge.style.backgroundColor = 'rgba(255,255,255,0.15)';
        })
        .catch(error => {
            console.error('Error checking AI provider:', error);
            // Still show ready state even if health check fails
            badge.textContent = '👋 Ready';
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

