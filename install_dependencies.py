#!/usr/bin/env python3
"""
Automatic Mac Dependencies Installer
Detects Apple Silicon vs Intel and installs appropriate PyTorch version
"""

import subprocess
import sys
import platform
import os

def detect_mac_type():
    """Detect Mac architecture"""
    machine = platform.machine()
    system = platform.system()
    
    if system != 'Darwin':
        print("❌ This script is for Mac only")
        return None
    
    if machine == 'arm64':
        return 'apple_silicon'
    elif machine == 'x86_64':
        return 'intel'
    else:
        return 'unknown'

def install_pytorch_for_mac(mac_type):
    """Install PyTorch optimized for Mac type"""
    print(f"\n🔥 Installing PyTorch for {mac_type} Mac...")
    
    if mac_type == 'apple_silicon':
        # Apple Silicon - use default PyTorch with Metal support
        cmd = [sys.executable, '-m', 'pip', 'install', 'torch', 'torchvision', 'torchaudio']
        print("📱 Installing with Apple Silicon optimization (Metal support)")
    else:
        # Intel Mac - use CPU version
        cmd = [sys.executable, '-m', 'pip', 'install', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu']
        print("💻 Installing CPU version for Intel Mac")
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ PyTorch installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyTorch installation failed: {e}")
        return False

def install_base_requirements():
    """Install base requirements"""
    print("\n📦 Installing base requirements...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Base requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Base requirements failed: {e}")
        return False

def test_pytorch():
    """Test PyTorch installation"""
    print("\n🧪 Testing PyTorch...")
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} installed")
        
        if torch.backends.mps.is_available():
            print("🚀 Metal Performance Shaders (MPS) available - Apple Silicon optimized!")
        elif torch.cuda.is_available():
            print("🚀 CUDA available")
        else:
            print("💻 Using CPU - suitable for Intel Macs")
        
        return True
    except ImportError:
        print("❌ PyTorch import failed")
        return False

def main():
    print("🍎 Mac Dependencies Auto-Installer")
    print("=" * 40)
    
    # Detect system
    mac_type = detect_mac_type()
    if not mac_type:
        return False
    
    print(f"✅ Detected: {mac_type.replace('_', ' ').title()} Mac")
    
    # Install PyTorch first
    if not install_pytorch_for_mac(mac_type):
        return False
    
    # Install other requirements
    if not install_base_requirements():
        return False
    
    # Test installation
    if not test_pytorch():
        return False
    
    print("\n" + "=" * 40)
    print("🎉 Dependencies installed successfully!")
    print("\n📋 Next steps:")
    print("1. Run: python3 setup_sadtalker.py (for full SadTalker setup)")
    print("2. Or just use static avatars for now")
    print("3. Start app: streamlit run app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)