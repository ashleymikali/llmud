"""Tool for detecting traps in the current room."""

import json
import random
from pathlib import Path
from typing import Dict, Any

# Define traps for specific rooms
ROOM_TRAPS = {
    "darkwood_forest_entrance": {
        "has_trap": True,
        "trap_type": "tripwire",
        "description": "A nearly invisible tripwire stretched across the path, connected to a net trap overhead.",
        "difficulty": "easy",
        "damage": "1d6"
    },
    "ancient_crypt": {
        "has_trap": True,
        "trap_type": "pressure_plate",
        "description": "A stone pressure plate on the floor, likely triggering poison darts from the walls.",
        "difficulty": "medium",
        "damage": "2d6"
    },
    "dragon_lair": {
        "has_trap": True,
        "trap_type": "magical_ward",
        "description": "Glowing runes around the entrance - a magical alarm that will alert the dragon.",
        "difficulty": "hard",
        "damage": "3d8"
    }
}


def detect_traps(session_id: str, perception_bonus: int = 0) -> Dict[str, Any]:
    """
    Attempt to detect traps in the current room.
    
    Args:
        session_id: The game session identifier
        perception_bonus: Character's perception bonus (default: 0)
    
    Returns:
        Dictionary with detection results including:
        - success: Whether any traps were detected
        - roll: The perception roll result
        - trap_info: Details about detected trap (if any)
        - message: Description of what was found
    """
    # Read the session to get current room
    session_dir = Path("game_data") / "sessions" / session_id
    state_file = session_dir / "state.json"
    
    if not state_file.exists():
        return {
            "error": True,
            "message": f"Session '{session_id}' not found. Create a session first with create_session()."
        }
    
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
    except Exception as e:
        return {
            "error": True,
            "message": f"Failed to read session state: {str(e)}"
        }
    
    current_room = state.get("current_room", "")
    
    # Roll perception check (d20 + bonus)
    perception_roll = random.randint(1, 20) + perception_bonus
    
    # Check if current room has a trap
    if current_room in ROOM_TRAPS:
        trap_data = ROOM_TRAPS[current_room]
        
        # Determine DC based on difficulty
        difficulty_dc = {
            "easy": 10,
            "medium": 15,
            "hard": 20
        }
        dc = difficulty_dc.get(trap_data["difficulty"], 15)
        
        # Check if perception roll beats DC
        if perception_roll >= dc:
            return {
                "success": True,
                "roll": perception_roll,
                "dc": dc,
                "trap_found": True,
                "trap_type": trap_data["trap_type"],
                "description": trap_data["description"],
                "difficulty": trap_data["difficulty"],
                "potential_damage": trap_data["damage"],
                "message": f"🎯 Success! (Rolled {perception_roll} vs DC {dc})\n\nYou carefully scan the area and spot a {trap_data['trap_type']}:\n{trap_data['description']}\n\nThis trap appears to be {trap_data['difficulty']} to disarm and could deal {trap_data['damage']} damage if triggered."
            }
        else:
            return {
                "success": False,
                "roll": perception_roll,
                "dc": dc,
                "trap_found": False,
                "message": f"❌ Failed! (Rolled {perception_roll} vs DC {dc})\n\nYou search the area carefully but don't notice anything suspicious. The room appears safe... or does it?"
            }
    else:
        # No trap in this room
        return {
            "success": True,
            "roll": perception_roll,
            "trap_found": False,
            "message": f"✓ Clear! (Rolled {perception_roll})\n\nYou thoroughly search the area. There are no traps in this location - you can proceed safely."
        }