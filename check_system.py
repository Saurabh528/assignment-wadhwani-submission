#!/usr/bin/env python3
"""
System Status Checker
Quick verification that all components are ready for UI testing
"""

import os
import sys
import importlib
from pathlib import Path

def check_component(name, check_function):
    """Check a system component"""
    try:
        result = check_function()
        status = "✅" if result else "❌"
        print(f"{status} {name}")
        return result
    except Exception as e:
        print(f"❌ {name} - Error: {e}")
        return False

def check_python_modules():
    """Check required Python modules"""
    required_modules = [
        'streamlit', 'openai', 'moviepy', 'PIL', 'numpy', 
        'requests', 'dotenv', 'psutil'
    ]
    
    missing = []
    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"Missing modules: {', '.join(missing)}")
        return False
    return True

def check_pytorch():
    """Check PyTorch installation and Mac optimization"""
    try:
        import torch
        print(f"   PyTorch version: {torch.__version__}")
        
        if torch.backends.mps.is_available():
            print("   🚀 Metal Performance Shaders (MPS) available - Apple Silicon optimized!")
        elif torch.cuda.is_available():
            print("   🚀 CUDA available")  
        else:
            print("   💻 CPU mode - suitable for Intel Macs")
            
        return True
    except ImportError:
        return False

def check_openai_key():
    """Check if OpenAI API key is configured"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key.startswith('sk-'):
        print("   API key found and properly formatted")
        return True
    elif api_key:
        print("   ⚠️  API key found but may be invalid format")
        return False
    else:
        print("   ❌ No API key found - create .env file with OPENAI_API_KEY=your_key")
        return False

def check_core_modules():
    """Check our custom modules"""
    try:
        from core.character_manager import CharacterManager
        from core.avatar_manager import AvatarManager
        from core.avatar_video_generator import AvatarVideoGenerator
        from core.sadtalker_manager import SadTalkerManager
        print("   All core modules importable")
        return True
    except ImportError as e:
        print(f"   Import error: {e}")
        return False

def check_database():
    """Check database setup"""
    try:
        from core.character_manager import CharacterManager
        manager = CharacterManager()
        characters = manager.get_all_characters()
        print(f"   Database working, {len(characters)} characters found")
        return True
    except Exception as e:
        print(f"   Database error: {e}")
        return False

def check_sadtalker():
    """Check SadTalker installation"""
    try:
        from core.sadtalker_manager import SadTalkerManager
        manager = SadTalkerManager()
        installed = manager.check_installation()
        if installed:
            print("   SadTalker ready for lip-sync")
        else:
            print("   SadTalker not installed (static avatars only)")
        return True  # Return True even if not installed, as it's optional
    except Exception as e:
        print(f"   SadTalker check error: {e}")
        return False

def check_directories():
    """Check required directories exist"""
    dirs = ['generated_videos', 'generated_videos/avatars']
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("   Required directories created/verified")
    return True

def main():
    """Run all system checks"""
    print("🔍 AI Content Factory - System Status Check")
    print("=" * 50)
    
    checks = [
        ("Python Modules", check_python_modules),
        ("PyTorch Installation", check_pytorch),
        ("OpenAI API Key", check_openai_key),
        ("Core Modules", check_core_modules),
        ("Database Setup", check_database),
        ("SadTalker (Optional)", check_sadtalker),
        ("Directories", check_directories)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_component(name, check_func)
        results.append(result)
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All systems ready! You can start UI testing.")
        print("\n📋 Next steps:")
        print("1. Run: streamlit run app.py")
        print("2. Follow UI_TEST_GUIDE.md")
        print("3. Start with Phase 1: Basic Setup Test")
        return True
    else:
        print(f"⚠️  {passed}/{total} checks passed. Fix issues above before UI testing.")
        
        if not any(results[:3]):  # Critical components failed
            print("\n🚨 Critical issues found. Try:")
            print("1. Run: make install-deps")
            print("2. Check .env file has OPENAI_API_KEY")
            print("3. Restart terminal and try again")
        else:
            print("\n💡 Minor issues found. Most features should work.")
            print("You can still do basic UI testing.")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)