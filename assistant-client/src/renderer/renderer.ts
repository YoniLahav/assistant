const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
  const messageInput = document.getElementById('messageInput') as HTMLInputElement;
  const sendButton = document.getElementById('sendButton') as HTMLButtonElement;
  const responseDiv = document.getElementById('response') as HTMLDivElement;
  const responseText = document.getElementById('responseText') as HTMLSpanElement;

  async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    try {
      // Clear previous response
      responseText.textContent = '';
      responseDiv.style.display = 'block';

      // Create the request body
      const requestBody = JSON.stringify({ message });

      // Make the fetch request
      const response = await fetch('http://localhost:5000/chat', {
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
    }
  }

  sendButton.addEventListener('click', sendMessage);

  // Also handle Enter key in the input field
  messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  });
}); 