// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract GovernanceToken is ERC20, Ownable {
    mapping(address => uint256) public votingPower;
    mapping(address => uint256) public lastVoteTimestamp;
    
    uint256 public constant VOTE_COOLDOWN = 1 days;
    uint256 public constant INITIAL_SUPPLY = 1000000 * 10**18;
    
    event VotingPowerUpdated(address indexed voter, uint256 newPower);
    event TokensStaked(address indexed staker, uint256 amount);
    event TokensUnstaked(address indexed staker, uint256 amount);
    
    constructor() ERC20("StockSpiderGov", "SSG") {
        _mint(msg.sender, INITIAL_SUPPLY);
        votingPower[msg.sender] = INITIAL_SUPPLY;
    }
    
    function stakeForVoting(uint256 amount) external {
        require(balanceOf(msg.sender) >= amount, "Insufficient balance");
        require(amount > 0, "Amount must be positive");
        
        _transfer(msg.sender, address(this), amount);
        votingPower[msg.sender] += amount;
        
        emit TokensStaked(msg.sender, amount);
        emit VotingPowerUpdated(msg.sender, votingPower[msg.sender]);
    }
    
    function unstakeFromVoting(uint256 amount) external {
        require(votingPower[msg.sender] >= amount, "Insufficient voting power");
        require(canVote(msg.sender), "In cooldown period");
        
        votingPower[msg.sender] -= amount;
        _transfer(address(this), msg.sender, amount);
        
        emit TokensUnstaked(msg.sender, amount);
        emit VotingPowerUpdated(msg.sender, votingPower[msg.sender]);
    }
    
    function getVotingPower(address voter) external view returns (uint256) {
        return votingPower[voter];
    }
    
    function canVote(address voter) public view returns (bool) {
        return block.timestamp >= lastVoteTimestamp[voter] + VOTE_COOLDOWN;
    }
    
    function updateVoteTimestamp(address voter) external onlyOwner {
        lastVoteTimestamp[voter] = block.timestamp;
    }
    
    function mintTokens(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
        votingPower[to] += amount;
    }
    
    // Backlog siguiente: "Sistema de votación con poder ponderado y quórum"
}