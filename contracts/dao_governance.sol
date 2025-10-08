// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract DAOGovernance {
    address public owner;
    uint256 public proposalCount;
    
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        uint256 voteCount;
        uint256 endTime;
        bool executed;
        mapping(address => bool) voters;
    }
    
    mapping(uint256 => Proposal) public proposals;
    
    event ProposalCreated(uint256 indexed id, address indexed proposer, string description);
    event Voted(uint256 indexed proposalId, address indexed voter);
    event ProposalExecuted(uint256 indexed proposalId);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    function createProposal(string memory _description, uint256 _votingDuration) external returns (uint256) {
        proposalCount++;
        Proposal storage newProposal = proposals[proposalCount];
        newProposal.id = proposalCount;
        newProposal.proposer = msg.sender;
        newProposal.description = _description;
        newProposal.endTime = block.timestamp + _votingDuration;
        
        emit ProposalCreated(proposalCount, msg.sender, _description);
        return proposalCount;
    }
    
    function vote(uint256 _proposalId) external {
        Proposal storage proposal = proposals[_proposalId];
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!proposal.voters[msg.sender], "Already voted");
        
        proposal.voters[msg.sender] = true;
        proposal.voteCount++;
        
        emit Voted(_proposalId, msg.sender);
    }
    
    function executeProposal(uint256 _proposalId) external {
        Proposal storage proposal = proposals[_proposalId];
        require(block.timestamp > proposal.endTime, "Voting not ended");
        require(!proposal.executed, "Already executed");
        require(proposal.voteCount > 0, "No votes");
        
        proposal.executed = true;
        emit ProposalExecuted(_proposalId);
    }
    
    // Backlog siguiente: "Implementar token ERC20 para votación ponderada"
}