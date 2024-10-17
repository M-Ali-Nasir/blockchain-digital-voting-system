// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ElectionContract {
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
        bool isDeleted;
    }

    address public admin;
    mapping(uint => Candidate) public candidates;
    mapping(address => bool) public voters;

    uint public candidateCount;

    event CandidateRegistered(uint id, string name);
    event Voted(uint candidateId);
    event CandidateDeleted(uint id);

    // Constructor to set the contract deployer as admin
    constructor() {
        admin = msg.sender;
    }

    // Modifier to restrict certain functions to the admin only
    modifier onlyAdmin() {
        require(msg.sender == admin, "Admin access required.");
        _;
    }

    // Register a new candidate (admin only)
    function registerCandidate(string memory name) public onlyAdmin {
        candidateCount++;
        candidates[candidateCount] = Candidate(candidateCount, name, 0, false);
        emit CandidateRegistered(candidateCount, name);
    }

    // Vote for a candidate
    function vote(uint candidateId) public {
        require(!voters[msg.sender], "You have already voted.");
        require(
            candidateId > 0 && candidateId <= candidateCount,
            "Invalid candidate ID."
        );

        voters[msg.sender] = true;
        candidates[candidateId].voteCount++;
        emit Voted(candidateId);
    }

    // Delete a candidate (admin only)
    function deleteCandidate(uint candidateId) public onlyAdmin {
        require(
            candidateId > 0 && candidateId <= candidateCount,
            "Invalid candidate ID."
        );

        // Remove candidate by deleting from the mapping
        delete candidates[candidateId];
        candidates[candidateId].isDeleted = true;
        emit CandidateDeleted(candidateId);
    }

    // Get candidate details
    function getCandidate(
        uint candidateId
    ) public view returns (string memory name, uint voteCount) {
        require(
            candidateId > 0 && candidateId <= candidateCount,
            "Invalid candidate ID."
        );
        Candidate storage candidate = candidates[candidateId];
        return (candidate.name, candidate.voteCount);
    }
}
