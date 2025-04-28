const { ipcRenderer } = require('electron');

interface Message {
  text: string;
  role: 'user' | 'assistant';
}

function initHandler() {
  document.removeEventListener('DOMContentLoaded', initHandler);

  const messageInput = document.getElementById('messageInput') as HTMLInputElement;
  const sendButton = document.getElementById('sendButton') as HTMLButtonElement;
  const clearButton = document.getElementById('clearButton') as HTMLButtonElement; // New clear button
  const chatContainer = document.getElementById('chatContainer') as HTMLDivElement;

  let isProcessing = false;
  let currentAssistantMessage: HTMLDivElement | null = null;

  function addMessage(message: string, isUser: boolean) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    messageDiv.textContent = message;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return messageDiv;
  }

  async function sendMessage() {
    if (isProcessing) return;

    const message = messageInput.value.trim();
    messageInput.value = '';
    if (!message) return;

    try {
      isProcessing = true;
      sendButton.disabled = true;

      addMessage(message, true);

      const requestBody = JSON.stringify({
        message: {
          text: message,
          role: 'user'
        }
      });

      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      currentAssistantMessage = addMessage('', false);
      let assistantResponse = '';

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('No reader available');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const { token } = JSON.parse(line);
              if (currentAssistantMessage) {
                currentAssistantMessage.textContent += token;
                assistantResponse += token;
              }
            } catch (e) {
              console.error('Error parsing JSON:', e);
            }
          }
        }
      }

      if (buffer.trim()) {
        try {
          const { token } = JSON.parse(buffer);
          if (currentAssistantMessage) {
            currentAssistantMessage.textContent += token;
            assistantResponse += token;
          }
        } catch (e) {
          console.error('Error parsing JSON:', e);
        }
      }
    } catch (error) {
      console.error('Error:', error);
      if (currentAssistantMessage) {
        currentAssistantMessage.textContent = 'Error communicating with the backend';
      }
    } finally {
      isProcessing = false;
      sendButton.disabled = false;
      currentAssistantMessage = null;
    }
  }

  async function clearChat() {
    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ clear: true }),
      });
  
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
  
      // Clear UI messages
      chatContainer.innerHTML = '';
  
      // Also clear any local assistant message state
      currentAssistantMessage = null;
  
      console.log('Chat cleared successfully');
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  }

  sendButton.addEventListener('click', sendMessage);
  clearButton.addEventListener('click', clearChat); // TODO: registers twice, fix this
  messageInput.addEventListener('keypress', (e) => {
    if ((e as KeyboardEvent).key === 'Enter') {
      sendMessage();
    }
  });
}

if (!document.readyState || document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initHandler);
} else {
  initHandler();
}
