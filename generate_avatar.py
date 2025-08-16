#!/usr/bin/env python3
"""
Script to generate real avatars for all characters or specific ones using DALL-E 3
"""

from core.character_manager import CharacterManager
from core.avatar_manager import AvatarManager
import sys

def generate_avatar_for_character(character_name, character_manager, avatar_manager):
    """Generate a real avatar for a specific character"""
    
    # Get character details
    character = character_manager.get_character(character_name)
    
    if not character:
        print(f"Character '{character_name}' not found in database")
        return False
    
    print(f"\nGenerating avatar for {character_name}...")
    print(f"Description: {character.get('description', 'No description')}")
    print(f"Style: {character.get('voice_style', 'Professional')} {character.get('gender', 'person')}")
    
    # Generate the avatar
    try:
        avatar_path = avatar_manager.generate_avatar(
            character_name,
            character,
            force_regenerate=True  # Force new generation
        )
        
        if avatar_path and avatar_path != "dummy_avatar.png":
            print(f"✅ Avatar successfully generated: {avatar_path}")
            
            # Update the database with the new avatar path
            success = character_manager.update_avatar_path(character_name, avatar_path)
            
            if success:
                print(f"✅ Database updated with avatar path")
            else:
                print(f"⚠️ Failed to update database")
            
            return True
        else:
            print(f"❌ Failed to generate avatar")
            return False
            
    except Exception as e:
        print(f"❌ Error generating avatar: {str(e)}")
        return False

def generate_all_missing_avatars():
    """Generate avatars for all characters that don't have valid ones"""
    
    character_manager = CharacterManager()
    avatar_manager = AvatarManager(test_mode=False)  # Use production quality
    
    # Get all characters
    all_characters = character_manager.get_all_characters()
    
    if not all_characters:
        print("No characters found in database")
        return
    
    print(f"Found {len(all_characters)} characters in database")
    
    generated_count = 0
    failed_count = 0
    
    for character in all_characters:
        name = character['name']
        current_avatar = character.get('avatar_path')
        
        # Check if avatar exists and is valid
        import os
        needs_avatar = (
            not current_avatar or 
            not os.path.exists(current_avatar) or 
            'placeholder' in current_avatar.lower() or
            current_avatar == "dummy_avatar.png"
        )
        
        if needs_avatar:
            print(f"\n{'='*50}")
            success = generate_avatar_for_character(name, character_manager, avatar_manager)
            if success:
                generated_count += 1
            else:
                failed_count += 1
        else:
            print(f"\n✓ {name} already has a valid avatar: {current_avatar}")
    
    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"✅ Successfully generated: {generated_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"Total characters: {len(all_characters)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            # Generate for all characters missing avatars
            generate_all_missing_avatars()
        else:
            # Generate for specific character
            character_manager = CharacterManager()
            avatar_manager = AvatarManager(test_mode=False)
            character_name = sys.argv[1]
            
            success = generate_avatar_for_character(character_name, character_manager, avatar_manager)
            
            if success:
                print(f"\n🎉 Avatar generation complete for {character_name}!")
            else:
                print(f"\n❌ Avatar generation failed for {character_name}")
    else:
        print("Usage:")
        print("  python generate_avatar.py <character_name>  # Generate for specific character")
        print("  python generate_avatar.py --all            # Generate for all characters missing avatars")
        print("\nExample:")
        print("  python generate_avatar.py alex")
        print("  python generate_avatar.py --all")