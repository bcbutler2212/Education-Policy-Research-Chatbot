class ChatBot {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatMessages = document.getElementById('chatMessages');
        this.loadingOverlay = document.getElementById('loadingOverlay');

        this.initializeEventListeners();
        this.adjustTextareaHeight();
    }

    initializeEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());

        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.messageInput.addEventListener('input', () => {
            this.adjustTextareaHeight();
            this.updateSendButton();
        });

        this.messageInput.addEventListener('focus', () => {
            this.hideSuggestions();
        });
    }

    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendButton.disabled = !hasText;
        this.sendButton.classList.toggle('active', hasText);
    }

    hideSuggestions() {
        const suggestions = document.querySelector('.suggestions');
        if (suggestions) {
            suggestions.style.display = 'none';
        }
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.addUserMessage(message);
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        this.updateSendButton();
        this.showLoading();

        try {
            const response = await this.queryBot(message);
            this.addBotMessage(response);
        } catch (error) {
            console.error('Error querying bot:', error);
            this.addBotMessage('Sorry, I encountered an error while processing your question. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async queryBot(message) {
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.response;
    }

    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${this.escapeHtml(message)}</p>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addBotMessage(response) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const parts = response.split('--- Sources Used ---');
        const answer = parts[0].replace('Answer:', '').trim();

        let sourcesHtml = '';
        if (parts.length > 1) {
            const sourcesSection = parts[1];
            const sources = sourcesSection
                .split('--------------------')[0]
                .split('\n')
                .filter(line => line.trim() && !line.includes('---'))
                .map(source => source.trim());

            if (sources.length > 0) {
                sourcesHtml = `
                    <div class="sources">
                        <h4>Sources:</h4>
                        <ul>
                            ${sources.map(source => `<li>${this.escapeHtml(source)}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="answer">${this.formatText(answer)}</div>
                ${sourcesHtml}
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    formatText(text) {
        return text
            .split('\n')
            .map(line => line.trim())
            .filter(line => line.length > 0)
            .map(line => `<p>${this.escapeHtml(line)}</p>`)
            .join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showLoading() {
        this.loadingOverlay.classList.remove('hidden');
        this.sendButton.disabled = true;
        this.messageInput.disabled = true;
    }

    hideLoading() {
        this.loadingOverlay.classList.add('hidden');
        this.sendButton.disabled = false;
        this.messageInput.disabled = false;
        this.messageInput.focus();
    }

    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
}

function sendSuggestion(suggestion) {
    const chatBot = new ChatBot();
    chatBot.messageInput.value = suggestion;
    chatBot.sendMessage();
}

document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});

window.sendSuggestion = sendSuggestion;