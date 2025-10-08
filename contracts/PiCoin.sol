// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

/**
 * @title PiCoin
 * @author PiTech Engineering
 * @notice ERC20 with staking and governance for Web4
 * @dev Safe deployment for Fuji Testnet
 */
contract PiCoin {
    string public name = "PiCoin";
    string public symbol = "PICO";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public staked;
    
    address public owner;
    uint256 private constant MIN_SUPPLY = 6000 * 10**18;
    uint256 private constant MAX_SUPPLY = 1000000 * 10**18;
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event TokensStaked(address indexed user, uint256 amount);
    event TokensUnstaked(address indexed user, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
        _mint(msg.sender, MIN_SUPPLY);
    }

    function _mint(address to, uint256 value) internal {
        require(to != address(0), "Zero address");
        totalSupply += value;
        unchecked {
            balanceOf[to] += value;
        }
        emit Transfer(address(0), to, value);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        require(totalSupply + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }

    function transfer(address to, uint256 value) external returns (bool) {
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        unchecked {
            balanceOf[to] += value;
        }
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) external returns (bool) {
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function transferFrom(address from, address to, uint256 value) external returns (bool) {
        require(allowance[from][msg.sender] >= value, "Allowance exceeded");
        require(balanceOf[from] >= value, "Insufficient balance");
        
        allowance[from][msg.sender] -= value;
        balanceOf[from] -= value;
        unchecked {
            balanceOf[to] += value;
        }
        emit Transfer(from, to, value);
        return true;
    }

    function stake(uint256 amount) external {
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        balanceOf[msg.sender] -= amount;
        staked[msg.sender] += amount;
        emit TokensStaked(msg.sender, amount);
    }

    function unstake(uint256 amount) external {
        require(staked[msg.sender] >= amount, "Insufficient staked");
        staked[msg.sender] -= amount;
        balanceOf[msg.sender] += amount;
        emit TokensUnstaked(msg.sender, amount);
    }

    function votingPower(address user) external view returns (uint256) {
        return staked[user];
    }
}
