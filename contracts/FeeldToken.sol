// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title FEELD Token with 1% fee split to Safety/Growth vaults
/// @notice Prototype token. Use audited OpenZeppelin ERC20 in production.
contract FeeldToken {
    string public name = "FEELD";
    string public symbol = "FEELD";
    uint8 public immutable decimals = 18;

    uint256 public totalSupply;
    address public owner;
    address public safetyVault;
    address public growthVault;

    uint256 public constant FEE_BPS = 100; // 1%
    uint256 public constant BPS_DENOMINATOR = 10_000;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event VaultsUpdated(address indexed safetyVault, address indexed growthVault);
    event FeeTaken(address indexed from, uint256 fee, uint256 safety, uint256 growth);

    modifier onlyOwner() {
        require(msg.sender == owner, "not owner");
        _;
    }

    constructor(
        uint256 initialSupply,
        address safetyVault_,
        address growthVault_
    ) {
        require(safetyVault_ != address(0), "safety vault required");
        require(growthVault_ != address(0), "growth vault required");
        owner = msg.sender;
        safetyVault = safetyVault_;
        growthVault = growthVault_;
        _mint(msg.sender, initialSupply);
    }

    function updateVaults(address safetyVault_, address growthVault_) external onlyOwner {
        require(safetyVault_ != address(0), "safety vault required");
        require(growthVault_ != address(0), "growth vault required");
        safetyVault = safetyVault_;
        growthVault = growthVault_;
        emit VaultsUpdated(safetyVault_, growthVault_);
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        require(allowed >= amount, "allowance exceeded");
        allowance[from][msg.sender] = allowed - amount;
        _transfer(from, to, amount);
        return true;
    }

    function _transfer(address from, address to, uint256 amount) internal {
        require(to != address(0), "invalid to");
        require(balanceOf[from] >= amount, "balance too low");
        uint256 fee = (amount * FEE_BPS) / BPS_DENOMINATOR;
        uint256 netAmount = amount - fee;
        uint256 safety = fee / 2;
        uint256 growth = fee - safety;

        balanceOf[from] -= amount;
        balanceOf[to] += netAmount;
        balanceOf[safetyVault] += safety;
        balanceOf[growthVault] += growth;

        emit Transfer(from, to, netAmount);
        emit Transfer(from, safetyVault, safety);
        emit Transfer(from, growthVault, growth);
        emit FeeTaken(from, fee, safety, growth);
    }

    function _mint(address to, uint256 amount) internal {
        require(to != address(0), "invalid to");
        totalSupply += amount;
        balanceOf[to] += amount;
        emit Transfer(address(0), to, amount);
    }
}
