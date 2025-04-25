const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
  const messageInput = document.getElementById('messageInput') as HTMLInputElement;
  const sendButton = document.getElementById('sendButton') as HTMLButtonElement;
  const responseDiv = document.getElementById('response') as HTMLDivElement;
  const responseText = document.getElementById('responseText') as HTMLSpanElement;

  sendButton.addEventListener('click', async () => {
    const message = messageInput.value.trim();
    if (!message) return;

    try {
      const result = await ipcRenderer.invoke('api-request', {
        endpoint: '/api/message',
        method: 'POST',
        data: { message },
      });

      responseText.textContent = result.response;
      responseDiv.style.display = 'block';
    } catch (error) {
      console.error('Error:', error);
      responseText.textContent = 'Error communicating with the backend';
      responseDiv.style.display = 'block';
    }
  });

  // Also handle Enter key in the input field
  messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      sendButton.click();
    }
  });
}); 