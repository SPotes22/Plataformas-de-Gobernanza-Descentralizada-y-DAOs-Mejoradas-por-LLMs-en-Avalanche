// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/*
 PiCoinDAO_Web4_Secure_Fixed.sol
 Web4 Flow Economy - Secure & Gas Optimized
 CRITICAL FIXES APPLIED:
 - Removed redundant SafeMath (using native ^0.8 overflow checks)
 - Fixed uint128 truncation issues (using uint256 for monetary accumulators)
 - Removed redundant ETH balance check
 - Simplified ring buffer without unnecessary require
 - Enhanced inactivity logic with proper timestamp handling
 - Added emergency pause functionality
*/

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract PiCoinDAO_Web4_Secure_Fixed is ERC20, ReentrancyGuard, Ownable, Pausable {
    // Flow economics - with safe defaults
    uint256 public baseFlowRateWei;
    uint256 public contributionDeltaWei;
    uint256 public maxFlowValueWei;
    uint256 public activeContributors;
    
    // Security parameters
    uint256 public minContributionWeiForActive;
    uint256 public constant INACTIVITY_PERIOD = 90 days;
    uint256 public constant MAX_SUSTAINABILITY_BPS = 100; // 1% max
    
    // Contributor context with uint256 for monetary values
    struct ContributorContext {
        uint64 firstContribution;
        uint64 lastContribution;
        uint256 cumulativeContributionWei; // CRITICAL FIX: uint256 for wei accumulators
        uint256 contributionScoreTokens;   // CRITICAL FIX: uint256 for token accumulators
        bool isActive;
    }
    
    mapping(address => ContributorContext) public contributorContexts;
    
    // Fixed-size ring buffer for recent contributors
    address[] public contributorRing;
    uint256 public ringIndex;
    uint256 public immutable ringSize;
    
    // Flow accounting
    uint256 public totalValueFlowedWei;
    uint256 public sustainabilityBps = 25;
    uint256 public regenPoolWei;
    address public flowTreasury;
    
    // Damping mechanism
    uint256 public dampingThresholdContributors = 10000;
    uint256 public dampingFactorBps = 5000;
    
    // Security events
    event ContributionMade(
        address indexed contributor, 
        uint256 meaningTokens, 
        uint256 weiIn, 
        uint256 netWei, 
        uint256 flowValueWei
    );
    event ValueFlowed(address indexed from, address indexed to, uint256 tokenUnits, uint256 timestamp);
    event ContextUpdated(address indexed identity, uint256 cumulativeWei, uint256 scoreTokens, bool isActive);
    event RegenPoolCollected(uint256 amountWei);
    event RegenPoolWithdrawn(address indexed to, uint256 amountWei);
    event FlowTreasuryUpdated(address indexed newTreasury);
    event SecurityCheckFailed(string reason, address user);
    event EmergencyPauseToggled(bool paused);

    constructor(
        string memory name_,
        string memory symbol_,
        uint256 baseFlowRateWei_,
        uint256 contributionDeltaWei_,
        uint256 ringSize_,
        address flowTreasury_,
        uint256 minContributionWeiForActive_
    ) ERC20(name_, symbol_) {
        require(baseFlowRateWei_ > 0, "Base flow rate must be positive");
        require(contributionDeltaWei_ > 0, "Contribution delta must be positive");
        require(ringSize_ > 0 && ringSize_ <= 1000, "Ring size invalid");
        
        baseFlowRateWei = baseFlowRateWei_;
        contributionDeltaWei = contributionDeltaWei_;
        maxFlowValueWei = type(uint256).max;
        ringSize = ringSize_;
        contributorRing = new address[](ringSize);
        flowTreasury = flowTreasury_;
        minContributionWeiForActive = minContributionWeiForActive_;
    }

    // Secure flow value calculation with overflow protection (native ^0.8)
    function currentFlowValueWei() public view returns (uint256) {
        uint256 effectiveDelta = contributionDeltaWei;
        
        // Apply damping if threshold exceeded
        if (activeContributors >= dampingThresholdContributors && dampingFactorBps < 10000) {
            effectiveDelta = (effectiveDelta * dampingFactorBps) / 10000;
        }
        
        // Safe calculation with native overflow protection
        uint256 deltaComponent = activeContributors * effectiveDelta;
        uint256 rawValue = baseFlowRateWei + deltaComponent;
        
        return rawValue > maxFlowValueWei ? maxFlowValueWei : rawValue;
    }

    // Main contribution function with comprehensive security checks
    function contribute(uint256 minMeaningTokens) external payable nonReentrant whenNotPaused {
        // Input validation
        require(msg.value > 0, "Flow requires energy");
        require(minMeaningTokens > 0, "Min tokens must be positive");
        
        uint256 flowValueWei = currentFlowValueWei();
        require(flowValueWei > 0, "No flow value");
        
        // Calculate regeneration fee safely
        uint256 regen = (msg.value * sustainabilityBps) / 10000;
        uint256 net = msg.value - regen;
        
        // Handle regeneration fee securely
        _handleRegenerationFee(regen);
        
        // Calculate tokens with overflow protection (native ^0.8)
        uint256 meaningTokens = net / flowValueWei;
        require(meaningTokens >= minMeaningTokens, "Insufficient meaning tokens");
        
        uint256 tokenUnits = meaningTokens * (10 ** decimals());
        require(tokenUnits > 0, "Token units calculation error");
        
        // CRITICAL FIX: Removed redundant ETH balance check
        
        // Mint tokens and update context
        _mint(msg.sender, tokenUnits);
        _updateContributorContextOnContribute(msg.sender, net, tokenUnits);
        
        // Update total flow
        totalValueFlowedWei += net;
        
        // Handle refund securely
        _handleRefund(net, meaningTokens, flowValueWei);
        
        emit ContributionMade(msg.sender, meaningTokens, msg.value, net, flowValueWei);
    }

    // Secure value transfer with comprehensive checks
    function flowValue(address to, uint256 meaningTokens) external nonReentrant whenNotPaused {
        require(to != address(0), "Invalid recipient");
        require(to != msg.sender, "Cannot flow to self");
        require(meaningTokens > 0, "Zero flow");
        
        uint256 tokenUnits = meaningTokens * (10 ** decimals());
        require(balanceOf(msg.sender) >= tokenUnits, "Insufficient balance");
        
        _transfer(msg.sender, to, tokenUnits);
        _updateContributorContextOnUpdate(msg.sender);
        _updateContributorContextOnUpdate(to);
        
        emit ValueFlowed(msg.sender, to, tokenUnits, block.timestamp);
    }

    // Internal: Secure contributor context update with proper inactivity handling
    function _updateContributorContextOnContribute(
        address contributor, 
        uint256 netWei, 
        uint256 tokenUnits
    ) internal {
        ContributorContext storage ctx = contributorContexts[contributor];
        uint256 prevLast = ctx.lastContribution;
        bool wasActive = ctx.isActive;
        
        // Initialize new contributor
        if (ctx.firstContribution == 0) {
            ctx.firstContribution = uint64(block.timestamp);
            _addToContributorRing(contributor);
        }
        
        // CRITICAL FIX: Check inactivity BEFORE updating lastContribution
        if (wasActive && prevLast != 0 && block.timestamp - prevLast > INACTIVITY_PERIOD) {
            ctx.isActive = false;
            if (activeContributors > 0) {
                activeContributors--;
            }
        }
        
        // Update contribution data
        ctx.lastContribution = uint64(block.timestamp);
        ctx.cumulativeContributionWei += netWei; // CRITICAL FIX: uint256 safe
        ctx.contributionScoreTokens += tokenUnits; // CRITICAL FIX: uint256 safe
        
        // Activate contributor if threshold met
        if (!ctx.isActive && ctx.cumulativeContributionWei >= minContributionWeiForActive) {
            ctx.isActive = true;
            activeContributors++;
        }
        
        emit ContextUpdated(
            contributor, 
            ctx.cumulativeContributionWei, 
            ctx.contributionScoreTokens, 
            ctx.isActive
        );
    }

    // Internal: Lightweight context update
    function _updateContributorContextOnUpdate(address contributor) internal {
        ContributorContext storage ctx = contributorContexts[contributor];
        
        if (ctx.firstContribution == 0) {
            ctx.firstContribution = uint64(block.timestamp);
            _addToContributorRing(contributor);
            return;
        }
        
        // CRITICAL FIX: Check inactivity BEFORE updating lastContribution
        uint256 prevLast = ctx.lastContribution;
        if (ctx.isActive && prevLast != 0 && block.timestamp - prevLast > INACTIVITY_PERIOD) {
            ctx.isActive = false;
            if (activeContributors > 0) {
                activeContributors--;
            }
        }
        
        ctx.lastContribution = uint64(block.timestamp);
    }

    // CRITICAL FIX: Simplified ring buffer without unnecessary require
    function _addToContributorRing(address contributor) internal {
        if (ringSize == 0) return;
        contributorRing[ringIndex] = contributor;
        ringIndex = (ringIndex + 1) % ringSize;
    }

    // Secure regeneration fee handling
    function _handleRegenerationFee(uint256 regen) internal {
        if (regen == 0) return;
        
        if (flowTreasury != address(0)) {
            (bool success, ) = flowTreasury.call{value: regen}("");
            if (success) {
                emit RegenPoolCollected(regen);
                return;
            }
        }
        
        // If treasury transfer fails or no treasury set, accumulate locally
        regenPoolWei += regen;
        emit RegenPoolCollected(regen);
    }

    // Secure refund handling with fallback to regen pool
    function _handleRefund(uint256 net, uint256 meaningTokens, uint256 flowValueWei) internal {
        uint256 usedWei = meaningTokens * flowValueWei;
        if (net > usedWei) {
            uint256 refund = net - usedWei;
            (bool success, ) = msg.sender.call{value: refund}("");
            if (!success) {
                // If refund fails, add to regeneration pool instead of reverting
                regenPoolWei += refund;
                emit SecurityCheckFailed("Refund failed, added to regen pool", msg.sender);
            }
        }
    }

    // Override transfer with security checks
    function _transfer(address from, address to, uint256 amount) internal override whenNotPaused {
        require(from != address(0), "Transfer from zero address");
        require(to != address(0), "Transfer to zero address");
        require(amount > 0, "Transfer amount zero");
        
        super._transfer(from, to, amount);
        _updateContributorContextOnUpdate(from);
        _updateContributorContextOnUpdate(to);
    }

    // Emergency pause functionality
    function emergencyPause() external onlyOwner {
        _pause();
        emit EmergencyPauseToggled(true);
    }
    
    function emergencyUnpause() external onlyOwner {
        _unpause();
        emit EmergencyPauseToggled(false);
    }

    // Secure owner functions with validation
    function setBaseFlowRateWei(uint256 newBase) external onlyOwner {
        require(newBase > 0, "Base rate must be positive");
        baseFlowRateWei = newBase;
    }
    
    function setContributionDeltaWei(uint256 newDelta) external onlyOwner {
        require(newDelta > 0, "Delta must be positive");
        contributionDeltaWei = newDelta;
    }
    
    function setSustainabilityBps(uint256 bps) external onlyOwner {
        require(bps <= MAX_SUSTAINABILITY_BPS, "Sustainability too high");
        sustainabilityBps = bps;
    }

    // Secure withdrawal functions
    function withdrawRegenPool(address payable to, uint256 amountWei) external onlyOwner nonReentrant {
        require(to != address(0), "Invalid recipient");
        require(amountWei <= regenPoolWei, "Amount exceeds pool");
        require(amountWei <= address(this).balance, "Insufficient contract balance");
        
        regenPoolWei -= amountWei;
        (bool success, ) = to.call{value: amountWei}("");
        require(success, "Withdrawal failed");
        
        emit RegenPoolWithdrawn(to, amountWei);
    }

    // Secure view functions
    function getContributorRing() external view returns (address[] memory) {
        return contributorRing;
    }

    function getFlowMetrics() external view returns (
        uint256 currentValueWei,
        uint256 totalActiveContributors,
        uint256 totalFlowWei,
        uint256 regenPoolWeiLocal
    ) {
        return (currentFlowValueWei(), activeContributors, totalValueFlowedWei, regenPoolWei);
    }

    // Emergency drain only for stuck funds (not regenPool)
    function emergencyDrain(address payable to, uint256 amountWei) external onlyOwner {
        require(to != address(0), "Invalid recipient");
        require(amountWei <= address(this).balance - regenPoolWei, "Cannot drain regen pool");
        (bool success, ) = to.call{value: amountWei}("");
        require(success, "Drain failed");
    }

    receive() external payable {
        // Accept ETH for contract funding
    }
}