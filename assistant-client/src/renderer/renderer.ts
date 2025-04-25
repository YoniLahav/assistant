const { ipcRenderer } = require('electron');

function initHandler() {
  // Remove this listener first to prevent any race conditions
  document.removeEventListener('DOMContentLoaded', initHandler);

  const messageInput = document.getElementById('messageInput') as HTMLInputElement;
  const sendButton = document.getElementById('sendButton') as HTMLButtonElement;
  const responseDiv = document.getElementById('response') as HTMLDivElement;
  const responseText = document.getElementById('responseText') as HTMLSpanElement;

  let isProcessing = false;

  async function sendMessage() {
    if (isProcessing) return;
    
    const message = messageInput.value.trim();
    messageInput.value = '';
    if (!message) return;

    try {
      isProcessing = true;
      sendButton.disabled = true;

      // Clear previous response
      responseText.textContent = '';
      responseDiv.style.display = 'block';

      // Create the request body
      const requestBody = JSON.stringify({ message });

      // Make the fetch request
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

      // Handle streaming response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      if (!reader) {
        throw new Error('No reader available');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode the chunk and add it to our buffer
        buffer += decoder.decode(value, { stream: true });

        // Process complete lines from the buffer
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep the last incomplete line in the buffer

        for (const line of lines) {
          if (line.trim()) {
            try {
              const { token } = JSON.parse(line);
              responseText.textContent += token;
            } catch (e) {
              console.error('Error parsing JSON:', e);
            }
          }
        }
      }

      // Process any remaining content in the buffer
      if (buffer.trim()) {
        try {
          const { token } = JSON.parse(buffer);
          responseText.textContent += token;
        } catch (e) {
          console.error('Error parsing JSON:', e);
        }
      }

    } catch (error) {
      console.error('Error:', error);
      responseText.textContent = 'Error communicating with the backend';
      responseDiv.style.display = 'block';
    } finally {
      isProcessing = false;
      sendButton.disabled = false;
    }
  }

  sendButton.addEventListener('click', sendMessage);
  messageInput.addEventListener('keypress', (e) => {
    if ((e as KeyboardEvent).key === 'Enter') {
      sendMessage();
    }
  });
}

// Only add the listener if we haven't already
if (!document.readyState || document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initHandler);
} else {
  // If DOM is already loaded, run immediately
  initHandler();
} 