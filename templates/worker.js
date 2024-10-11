self.onmessage = function(event) {
  const { url, title } = event.data; // Destructure the data received
  console.log('Received URL:', url);
  console.log('Received Title:', title);

  logToMainThread(`Worker finished processing. url: ${url}`);

  const result = processData(url, title);
  self.postMessage(result);
  
};

async function processData(url, title) {
  const response = await fetch('/start_contact', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url_data: url, title_search: title})
  });

  const data = await response.json();
  return data.results;
}

function logToMainThread(message) {
  self.postMessage({ log: message }); // Send log message back to the main thread
}