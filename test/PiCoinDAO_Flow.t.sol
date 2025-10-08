// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/PiCoinDAO_Web4_Secure_Fixed.sol";

contract PiCoinDAO_FlowTest is Test {
    PiCoinDAO_Web4_Secure_Fixed public picoin;
    address public constant OWNER = address(0x1000);
    address public constant USER1 = address(0x2000);
    address public constant USER2 = address(0x3000);
    address public constant TREASURY = address(0x4000);
    
    uint256 public constant BASE_FLOW_RATE = 0.001 ether;
    uint256 public constant CONTRIBUTION_DELTA = 0.0001 ether;
    uint256 public constant RING_SIZE = 100;
    uint256 public constant MIN_CONTRIBUTION = 0.01 ether;

    function setUp() public {
        vm.deal(OWNER, 100 ether);
        vm.deal(USER1, 10 ether);
        vm.deal(USER2, 10 ether);
        
        vm.prank(OWNER);
        picoin = new PiCoinDAO_Web4_Secure_Fixed(
            "PiCoinDAO Flow",
            "PIDAO",
            BASE_FLOW_RATE,
            CONTRIBUTION_DELTA,
            RING_SIZE,
            TREASURY,
            MIN_CONTRIBUTION
        );
    }

    function test_Deployment() public {
        assertEq(picoin.name(), "PiCoinDAO Flow");
        assertEq(picoin.symbol(), "PIDAO");
        assertEq(picoin.baseFlowRateWei(), BASE_FLOW_RATE);
        assertEq(picoin.contributionDeltaWei(), CONTRIBUTION_DELTA);
        assertEq(picoin.flowTreasury(), TREASURY);
        assertEq(picoin.minContributionWeiForActive(), MIN_CONTRIBUTION);
    }

    function test_ContributionFlow() public {
        vm.prank(USER1);
        uint256 contribution = 0.1 ether;
        picoin.contribute{value: contribution}(1);
        
        uint256 expectedTokens = (contribution * 9975 / 10000) / BASE_FLOW_RATE;
        assertEq(picoin.balanceOf(USER1), expectedTokens * 1e18);
        
        (,, uint256 cumulativeWei, uint256 scoreTokens, bool isActive) = picoin.contributorContexts(USER1);
        assertTrue(isActive);
        assertGt(cumulativeWei, 0);
        assertEq(scoreTokens, expectedTokens * 1e18);
    }

    function test_FlowValueTransfer() public {
        vm.prank(USER1);
        picoin.contribute{value: 0.1 ether}(1);
        
        uint256 initialBalance = picoin.balanceOf(USER1);
        uint256 transferAmount = initialBalance / 2;
        
        vm.prank(USER1);
        picoin.flowValue(USER2, transferAmount / 1e18);
        
        assertEq(picoin.balanceOf(USER1), initialBalance - transferAmount);
        assertEq(picoin.balanceOf(USER2), transferAmount);
    }

    function test_InactivityDeactivation() public {
        vm.prank(USER1);
        picoin.contribute{value: MIN_CONTRIBUTION}(1);
        assertTrue(picoin.contributorContexts(USER1).isActive);
        
        vm.warp(block.timestamp + 91 days);
        
        vm.prank(USER1);
        picoin.flowValue(USER2, 0);
        
        assertFalse(picoin.contributorContexts(USER1).isActive);
        assertEq(picoin.activeContributors(), 0);
    }

    function test_EmergencyPause() public {
        vm.prank(OWNER);
        picoin.emergencyPause();
        
        vm.prank(USER1);
        vm.expectRevert("Pausable: paused");
        picoin.contribute{value: 0.1 ether}(1);
        
        vm.prank(OWNER);
        picoin.emergencyUnpause();
        
        vm.prank(USER1);
        picoin.contribute{value: 0.1 ether}(1);
    }

    function testFuzz_Contribution(uint96 amount) public {
        vm.assume(amount > 0.001 ether && amount < 10 ether);
        
        vm.deal(USER1, amount);
        vm.prank(USER1);
        
        picoin.contribute{value: amount}(1);
        
        assertGt(picoin.balanceOf(USER1), 0);
        assertTrue(picoin.contributorContexts(USER1).cumulativeContributionWei > 0);
    }

    function test_MinimumContributionEdge() public {
        vm.prank(USER1);
        picoin.contribute{value: MIN_CONTRIBUTION}(1);
        
        assertTrue(picoin.contributorContexts(USER1).isActive);
    }

    function test_ReentrancyProtection() public {
        bytes memory contributeBytecode = type(PiCoinDAO_Web4_Secure_Fixed).runtimeCode;
        assertTrue(_containsString(contributeBytecode, "nonReentrant"));
    }
    
    function _containsString(bytes memory data, string memory search) internal pure returns (bool) {
        bytes memory searchBytes = bytes(search);
        if (searchBytes.length > data.length) return false;
        
        for (uint i = 0; i <= data.length - searchBytes.length; i++) {
            bool found = true;
            for (uint j = 0; j < searchBytes.length; j++) {
                if (data[i + j] != searchBytes[j]) {
                    found = false;
                    break;
                }
            }
            if (found) return true;
        }
        return false;
    }

    function test_DampingMechanism() public {
        uint256 initialPrice = picoin.currentFlowValueWei();
        
        for (uint256 i = 0; i < 10050; i++) {
            address user = address(uint160(0x5000 + i));
            vm.deal(user, 1 ether);
            vm.prank(user);
            picoin.contribute{value: MIN_CONTRIBUTION}(1);
        }
        
        uint256 finalPrice = picoin.currentFlowValueWei();
        assertTrue(finalPrice > initialPrice);
        assertLt(finalPrice, initialPrice + (10050 * CONTRIBUTION_DELTA));
    }

    function test_RegenerationPool() public {
        uint256 initialPool = picoin.regenPoolWei();
        
        vm.prank(USER1);
        picoin.contribute{value: 1 ether}(1);
        
        uint256 expectedFee = 1 ether * 25 / 10000;
        assertEq(picoin.regenPoolWei(), initialPool + expectedFee);
    }
}