// Register a candidate (Admin Page)

window.onload = function() {
    getCandidates();
};


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

// Fetch and display all candidates with delete button
function getCandidates() {
    // Check if the user is an admin and get the voting status
    let isAdmin = false;
    let votingStarted = false;
    let votingEnded = false;

    // Get voting status
    fetch('/voting_status')
    .then(response => response.json())
    .then(status => {
        votingStarted = status.voting_started;
        votingEnded = status.voting_ended;

        // Fetch candidate count and determine if the user is an admin
        return fetch('/candidate_count');
    })
    .then(response => response.json())
    .then(data => {
        isAdmin = data.is_admin;
        console.log(isAdmin);
        let candidateCount = data.candidateCount;
        let candidatesList = document.getElementById("candidatesList");
        candidatesList.innerHTML = '';  // Clear previous list
        let activeCadidateCount = 0;
        for (let i = 1; i <= candidateCount; i++) {
            fetch(`/candidate/${i}`)
            .then(response => response.json())
            .then(candidate => {
                if (candidate.name && candidate.name !== ""){
                    activeCadidateCount ++;
                }
            });
        }

        if (isAdmin) {
            let controlPanel = document.getElementById("controlPanel");
            controlPanel.innerHTML = '';  // Clear previous controls

            if (votingStarted && !votingEnded) {
                controlPanel.innerHTML += `<button  onclick="stopVoting()" class="stop-button col-md-2">Stop Voting</button>`;
            } else if (!votingStarted) {
                controlPanel.innerHTML += `<button onclick="startVoting()" class="start-button col-md-2"${activeCadidateCount >2 ? `>Start Voting</button>` :`disabled>Start Voting</button><p>Please register minimum 2 candidates to start voting</p>`}`;
            }
        }else{
            let controlPanel = document.getElementById("message");
            controlPanel.innerHTML = '';  // Clear previous controls

            if (votingStarted && !votingEnded) {
                controlPanel.innerHTML += `<h3 class="text-success text-center">Votting is Started. You can vote now</h3>`;
            } else if (!votingStarted) {
                controlPanel.innerHTML += `<h3 class="text-danger text-center">Voting is stopped.</h3>`;
            }
        }

        for (let i = 1; i <= candidateCount; i++) {
            fetch(`/candidate/${i}`)
            .then(response => response.json())
            .then(candidate => {
                if (candidate.name && candidate.name !== "") {
                    let listItem = document.createElement("tr");
                    
                    // Show vote button only if voting has started and hasn't ended
                    let voteButton = (!isAdmin && votingStarted && !votingEnded) ? 
                        `<button class="vote-button col-md-2" onclick="vote(${i})">Vote</button>` : `Votes: ${candidate.voteCount}`;
                    
                    // Show delete button for admin only if voting hasn't started
                    let deleteButton = (isAdmin && !votingStarted) ? 
                        `<button class="delete-button col-md-2" onclick="deleteCandidate(${i})">Delete</button>` : '';

                    listItem.innerHTML = `<td>${candidate.name}</td>
                        <td>${isAdmin ? `Votes: ${candidate.voteCount} ${deleteButton}` : ` ${voteButton}`} </td>
                    `;
                    
                    candidatesList.appendChild(listItem);
                }
            });
        }
    });
}


// Function to start voting
function startVoting() {
    fetch('/start_voting', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        getCandidates();  
        btn = document.getElementById('registerbtn');
        btn.disabled=true;
        btn.innerText="Registeration closed"
    });
}

// Function to stop voting
function stopVoting() {
    fetch('/stop_voting', { method: 'POST' })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        getCandidates(); 
        btn = document.getElementById('registerbtn');
        btn.disabled=false;
        btn.innerText="Register Candidate"
    });
}


function vote(candidateId) {
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
        alert(data.message || data.error);
        getCandidates(); // Refresh the candidate list with updated votes
    });
}
// Function to delete a candidate by ID
function deleteCandidate(candidateId) {
    fetch('/delete_candidate', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ candidateId })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message || data.error);
        getCandidates(); // Refresh the candidate list
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
// async function vote() {
//     const candidateId = parseInt(document.getElementById("candidateId").value);

//     if (!window.userAccount) {
//         alert("Please connect to MetaMask first.");
//         return;
//     }

//     fetch('/vote', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify({ candidateId, voterAddress: window.userAccount })
//     })
//     .then(response => response.json())
//     .then(data => {
//         document.getElementById("voteResult").innerText = data.message || data.error;
//         getCandidates(); // Refresh the candidate list with updated votes
//     });
// }

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
