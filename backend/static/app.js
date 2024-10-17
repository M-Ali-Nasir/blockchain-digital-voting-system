// Register a candidate (Admin Page)
function registerCandidate() {
  const candidateName = document.getElementById("candidateName").value;
  fetch('/register_candidate', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: candidateName })
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById("registerResult").innerText = data.message || data.error;
      getCandidates(); // Refresh the candidate list
  });
}

// Get all candidates and their vote counts (both pages)
function getCandidates() {
  fetch('/candidate_count')
  .then(response => response.json())
  .then(data => {
      let candidateCount = data.candidateCount;
      let candidatesList = document.getElementById("candidatesList");
      candidatesList.innerHTML = '';  // Clear previous list

      for (let i = 1; i <= candidateCount; i++) {
          fetch(`/candidate/${i}`)
          .then(response => response.json())
          .then(candidate => {
              let listItem = document.createElement("li");
              listItem.innerText = `ID: ${i}, Name: ${candidate.name}, Votes: ${candidate.voteCount}`;
              candidatesList.appendChild(listItem);
          });
      }
  });
}


// Prompt user to connect their MetaMask wallet
async function connectMetaMask() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            // Request account access
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            window.userAccount = accounts[0];
            console.log("Connected MetaMask account:", window.userAccount);
            alert("Connected with MetaMask address: " + window.userAccount);
        } catch (error) {
            console.error("MetaMask connection failed", error);
            alert("Failed to connect MetaMask. Please try again.");
        }
    } else {
        alert("MetaMask is not installed. Please install MetaMask to use this feature.");
    }
}

// Function to vote using the connected MetaMask account
async function vote() {
    const candidateId = parseInt(document.getElementById("candidateId").value);

    if (!window.userAccount) {
        alert("Please connect to MetaMask first.");
        return;
    }

    fetch('/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ candidateId, voterAddress: window.userAccount })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("voteResult").innerText = data.message || data.error;
        getCandidates(); // Refresh the candidate list with updated votes
    });
}

// Automatically connect MetaMask on page load or prompt to connect
window.addEventListener('load', async () => {
    if (typeof window.ethereum !== 'undefined') {
        console.log("MetaMask is installed!");
        await connectMetaMask();
    } else {
        console.log("MetaMask is not installed.");
        alert("MetaMask is required to use this application.");
    }
});
