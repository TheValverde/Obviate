#!/usr/bin/env python3
"""
Clean test script to verify smart card creation positioning works correctly.
Tests both auto-positioning and explicit positioning with reordering.
"""

import asyncio
import aiohttp
import json

async def test_smart_card_creation_clean():
    """Test that card creation handles both auto and explicit positioning correctly."""
    base_url = "http://localhost:12003"

    async with aiohttp.ClientSession() as session:
        print("🧪 Testing Smart Card Creation Positioning (Clean Test)")
        print("=" * 65)

        # Create test workspace
        print("1. Creating test workspace...")
        workspace_data = {"name": "Smart Card Creation Clean Test", "meta_data": {"test": True}}
        async with session.post(f"{base_url}/v1/workspaces/", json=workspace_data) as response:
            workspace_result = await response.json()
            workspace_id = workspace_result["data"]["id"]
            print(f"   ✅ Created workspace: {workspace_id}")

        # Create test board
        print("2. Creating test board...")
        board_data = {"name": "Smart Card Creation Clean Test Board", "workspace_id": workspace_id, "meta_data": {"test": True}}
        async with session.post(f"{base_url}/v1/boards/", json=board_data) as response:
            board_result = await response.json()
            board_id = board_result["data"]["id"]
            print(f"   ✅ Created board: {board_id}")

        # Get the first column
        print("3. Getting board columns...")
        async with session.get(f"{base_url}/v1/boards/{board_id}/columns") as response:
            columns_result = await response.json()
            columns = columns_result["data"]
            if not columns:
                print("   ❌ No columns found!")
                return
            column_id = columns[0]["id"]
            print(f"   ✅ Using column: {column_id}")

        # Test 1: Create first card with auto-positioning (should be position 0)
        print("\n4. Test 1: Creating first card with auto-positioning...")
        card1_data = {
            "title": "Auto Card 1",
            "description": "This should be at position 0 (auto)",
            "board_id": board_id,
            "column_id": column_id,
            "priority": 1
            # No position specified - should auto-assign
        }
        async with session.post(f"{base_url}/v1/cards/", json=card1_data) as response:
            card1_result = await response.json()
            card1_id = card1_result["id"]
            card1_position = card1_result["position"]
            print(f"   ✅ Created card: {card1_id} at position {card1_position}")
            if card1_position != 0:
                print(f"   ❌ Expected position 0, got {card1_position}")

        # Test 2: Create second card with auto-positioning (should be position 1)
        print("\n5. Test 2: Creating second card with auto-positioning...")
        card2_data = {
            "title": "Auto Card 2",
            "description": "This should be at position 1 (auto)",
            "board_id": board_id,
            "column_id": column_id,
            "priority": 2
            # No position specified - should auto-assign
        }
        async with session.post(f"{base_url}/v1/cards/", json=card2_data) as response:
            card2_result = await response.json()
            card2_id = card2_result["id"]
            card2_position = card2_result["position"]
            print(f"   ✅ Created card: {card2_id} at position {card2_position}")
            if card2_position != 1:
                print(f"   ❌ Expected position 1, got {card2_position}")

        # Test 3: Create third card with explicit position 0 (should insert at beginning)
        print("\n6. Test 3: Creating third card with explicit position 0...")
        card3_data = {
            "title": "Insert at Beginning",
            "description": "This should be at position 0 (explicit)",
            "board_id": board_id,
            "column_id": column_id,
            "position": 0,
            "priority": 3
        }
        async with session.post(f"{base_url}/v1/cards/", json=card3_data) as response:
            card3_result = await response.json()
            card3_id = card3_result["id"]
            card3_position = card3_result["position"]
            print(f"   ✅ Created card: {card3_id} at position {card3_position}")
            if card3_position != 0:
                print(f"   ❌ Expected position 0, got {card3_position}")

        # Test 4: Create fourth card with explicit position 1 (should insert in middle)
        print("\n7. Test 4: Creating fourth card with explicit position 1...")
        card4_data = {
            "title": "Insert in Middle",
            "description": "This should be at position 1 (explicit)",
            "board_id": board_id,
            "column_id": column_id,
            "position": 1,
            "priority": 4
        }
        async with session.post(f"{base_url}/v1/cards/", json=card4_data) as response:
            card4_result = await response.json()
            card4_id = card4_result["id"]
            card4_position = card4_result["position"]
            print(f"   ✅ Created card: {card4_id} at position {card4_position}")
            if card4_position != 1:
                print(f"   ❌ Expected position 1, got {card4_position}")

        # Test 5: Create fifth card with auto-positioning (should be at end)
        print("\n8. Test 5: Creating fifth card with auto-positioning...")
        card5_data = {
            "title": "Auto Card 5",
            "description": "This should be at the end (auto)",
            "board_id": board_id,
            "column_id": column_id,
            "priority": 5
            # No position specified - should auto-assign to end
        }
        async with session.post(f"{base_url}/v1/cards/", json=card5_data) as response:
            card5_result = await response.json()
            card5_id = card5_result["id"]
            card5_position = card5_result["position"]
            print(f"   ✅ Created card: {card5_id} at position {card5_position}")
            if card5_position != 4:
                print(f"   ❌ Expected position 4, got {card5_position}")

        # Check final card order (filter by our test cards only)
        print("\n9. Checking final card order...")
        async with session.get(f"{base_url}/v1/cards/?column_id={column_id}") as response:
            cards_result = await response.json()
            cards = cards_result["data"]
            
            # Filter to only our test cards
            test_cards = [card for card in cards if card['title'].startswith(('Auto Card', 'Insert'))]
            test_cards.sort(key=lambda x: x['position'])
            
            print("   Final card order (test cards only):")
            for card in test_cards:
                print(f"     Position {card['position']}: {card['title']} ({card['id']})")

        # Verify the expected order
        expected_order = [
            "Insert at Beginning",      # position 0
            "Insert in Middle",         # position 1  
            "Auto Card 1",              # position 2 (shifted from 0)
            "Auto Card 2",              # position 3 (shifted from 1)
            "Auto Card 5"               # position 4 (auto at end)
        ]
        
        print("\n10. Verifying expected order...")
        actual_titles = [card['title'] for card in test_cards]
        if actual_titles == expected_order:
            print("   ✅ Card order matches expected sequence!")
        else:
            print("   ❌ Card order doesn't match expected sequence!")
            print(f"   Expected: {expected_order}")
            print(f"   Actual:   {actual_titles}")

        # Cleanup
        print("\n11. Cleaning up test data...")
        for card_id in [card1_id, card2_id, card3_id, card4_id, card5_id]:
            async with session.delete(f"{base_url}/v1/cards/{card_id}") as response:
                print(f"   ✅ Deleted card: {card_id}")

        async with session.delete(f"{base_url}/v1/boards/{board_id}") as response:
            print(f"   ✅ Deleted board: {board_id}")

        async with session.delete(f"{base_url}/v1/workspaces/{workspace_id}") as response:
            print(f"   ✅ Deleted workspace: {workspace_id}")

        print("\n🎉 Smart card creation positioning test completed!")

if __name__ == "__main__":
    asyncio.run(test_smart_card_creation_clean())





