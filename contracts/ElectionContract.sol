// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract ElectionContract {
    struct Candidate {
        uint id;
        string name;
        uint voteCount;
    }

    mapping(uint => Candidate) public candidates;
    mapping(address => bool) public voters;

    uint public candidateCount;

    event CandidateRegistered(uint id, string name);
    event Voted(uint candidateId);

    function registerCandidate(string memory name) public {
        candidateCount++;
        candidates[candidateCount] = Candidate(candidateCount, name, 0);
        emit CandidateRegistered(candidateCount, name);
    }

    function vote(uint candidateId) public {
        require(!voters[msg.sender], "You have already voted.");
        require(candidateId > 0 && candidateId <= candidateCount, "Invalid candidate ID.");

        voters[msg.sender] = true;
        candidates[candidateId].voteCount++;
        emit Voted(candidateId);
    }

    function getCandidate(uint candidateId) public view returns (string memory name, uint voteCount) {
        require(candidateId > 0 && candidateId <= candidateCount, "Invalid candidate ID.");
        Candidate storage candidate = candidates[candidateId];
        return (candidate.name, candidate.voteCount);
    }
}
