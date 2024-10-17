// Set up Web3 with Ganache connection
if (typeof window.ethereum !== 'undefined') {
  console.log('MetaMask is installed!');
  window.web3 = new Web3(window.ethereum);
  window.ethereum.enable();
} else {
  alert("Please install MetaMask to use this dApp!");
}

// Register a candidate
function registerCandidate() {
  const candidateName = document.getElementById("candidateName").value;
  fetch('http://127.0.0.1:5000/register_candidate', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: candidateName })
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById("registerResult").innerText = data.message || data.error;
  });
}

// Cast a vote
function vote() {
  const candidateId = parseInt(document.getElementById("candidateId").value);
  const voterAddress = document.getElementById("voterAddress").value;
  fetch('http://127.0.0.1:5000/vote', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ candidateId, voterAddress })
  })
  .then(response => response.json())
  .then(data => {
      document.getElementById("voteResult").innerText = data.message || data.error;
  });
}

// Get candidate count
function getCandidateCount() {
  fetch('http://127.0.0.1:5000/candidate_count')
  .then(response => response.json())
  .then(data => {
      document.getElementById("candidateCountResult").innerText = `Candidate Count: ${data.candidateCount}`;
  });
}

// Get candidate details
function getCandidate() {
  const candidateId = parseInt(document.getElementById("getCandidateId").value);
  fetch(`http://127.0.0.1:5000/candidate/${candidateId}`)
  .then(response => response.json())
  .then(data => {
      document.getElementById("candidateDetailsResult").innerText = 
          `Name: ${data.name}, Vote Count: ${data.voteCount}`;
  });
}
