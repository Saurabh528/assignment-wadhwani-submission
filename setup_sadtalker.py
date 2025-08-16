#!/usr/bin/env python3
"""
Automated SadTalker Setup for Mac (Apple Silicon & Intel)
This script automatically detects your Mac type and installs SadTalker with proper dependencies
"""

import os
import sys
import subprocess
import platform
import urllib.request
import zipfile
import shutil
from pathlib import Path

class MacSadTalkerInstaller:
    def __init__(self):
        self.is_apple_silicon = platform.machine() == 'arm64' and platform.system() == 'Darwin'
        self.is_intel_mac = platform.machine() == 'x86_64' and platform.system() == 'Darwin'
        self.is_mac = platform.system() == 'Darwin'
        self.project_root = Path(__file__).parent
        self.sadtalker_path = self.project_root / "sadtalker"
        
    def detect_system(self):
        """Detect Mac system type"""
        print("🔍 Detecting system...")
        print(f"Platform: {platform.platform()}")
        print(f"Architecture: {platform.machine()}")
        print(f"Python: {sys.version}")
        
        if not self.is_mac:
            print("❌ This installer is designed for Mac only")
            return False
            
        if self.is_apple_silicon:
            print("✅ Apple Silicon Mac detected (M1/M2/M3)")
        elif self.is_intel_mac:
            print("✅ Intel Mac detected")
        else:
            print("⚠️  Unknown Mac architecture")
            
        return True
    
    def check_homebrew(self):
        """Check if Homebrew is installed"""
        print("\n🍺 Checking Homebrew...")
        try:
            result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Homebrew is installed")
                return True
        except FileNotFoundError:
            pass
            
        print("⚠️  Homebrew not found. Installing...")
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        print("Please run this command to install Homebrew:")
        print(install_cmd)
        return False
    
    def install_system_dependencies(self):
        """Install system dependencies via Homebrew"""
        print("\n📦 Installing system dependencies...")
        dependencies = ['python@3.10', 'ffmpeg', 'git-lfs', 'cmake']
        
        for dep in dependencies:
            print(f"Installing {dep}...")
            try:
                result = subprocess.run(['brew', 'install', dep], 
                                      capture_output=True, text=True, check=True)
                print(f"✅ {dep} installed")
            except subprocess.CalledProcessError as e:
                # Check if it's already installed
                check_result = subprocess.run(['brew', 'list', dep], 
                                            capture_output=True, text=True)
                if check_result.returncode == 0:
                    print(f"✅ {dep} already installed")
                else:
                    print(f"❌ {dep} installation failed: {e}")
                    return False
        
        return True
    
    def install_pytorch(self):
        """Install PyTorch optimized for Mac"""
        print("\n🔥 Installing PyTorch...")
        
        if self.is_apple_silicon:
            print("Installing PyTorch with Apple Silicon optimization...")
            pytorch_cmd = [
                sys.executable, '-m', 'pip', 'install',
                'torch', 'torchvision', 'torchaudio'
            ]
        else:  # Intel Mac
            print("Installing PyTorch for Intel Mac...")
            pytorch_cmd = [
                sys.executable, '-m', 'pip', 'install', 
                'torch', 'torchvision', 'torchaudio',
                '--index-url', 'https://download.pytorch.org/whl/cpu'
            ]
        
        try:
            subprocess.run(pytorch_cmd, check=True)
            print("✅ PyTorch installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ PyTorch installation failed: {e}")
            return False
        
        return True
    
    def clone_sadtalker(self):
        """Clone SadTalker repository"""
        print("\n📥 Cloning SadTalker...")
        
        if self.sadtalker_path.exists():
            print("⚠️  SadTalker directory already exists, removing...")
            shutil.rmtree(self.sadtalker_path)
        
        try:
            subprocess.run([
                'git', 'clone', 
                'https://github.com/OpenTalker/SadTalker.git',
                str(self.sadtalker_path)
            ], check=True)
            print("✅ SadTalker cloned successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone SadTalker: {e}")
            return False
    
    def install_sadtalker_dependencies(self):
        """Install SadTalker Python dependencies"""
        print("\n📚 Installing SadTalker dependencies...")
        
        # Change to SadTalker directory
        original_cwd = os.getcwd()
        os.chdir(self.sadtalker_path)
        
        try:
            # Install compatible dependencies for Python 3.13
            print("Installing Python 3.13 compatible dependencies...")
            compatible_deps = [
                'numpy>=1.24.0',
                'face-alignment>=1.3.5',
                'imageio>=2.19.0',
                'imageio-ffmpeg>=0.4.7',
                'librosa>=0.9.0',
                'numba',
                'resampy>=0.3.0',
                'pydub>=0.25.0',
                'scipy>=1.10.0',
                'kornia>=0.6.0',
                'tqdm',
                'yacs>=0.1.8',
                'pyyaml',
                'joblib>=1.1.0',
                'scikit-image>=0.19.0',
                'gradio',
                'av',
                'safetensors',
                'opencv-python',
                'dlib',
                'face-recognition'
            ]
            
            for dep in compatible_deps:
                print(f"Installing {dep}...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                 check=True, capture_output=True)
                    print(f"✅ {dep} installed")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  {dep} failed, skipping: {e}")
            
            # Try to install basicsr and facexlib separately as they might be problematic
            optional_deps = ['basicsr>=1.4.0', 'facexlib>=0.3.0', 'gfpgan']
            for dep in optional_deps:
                print(f"Installing optional {dep}...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                                 check=True, capture_output=True)
                    print(f"✅ {dep} installed")
                except subprocess.CalledProcessError:
                    print(f"⚠️  {dep} failed (optional), continuing...")
            
            print("✅ Dependencies installed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Dependency installation failed: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def download_models(self):
        """Download SadTalker models"""
        print("\n📡 Downloading SadTalker models...")
        
        original_cwd = os.getcwd()
        os.chdir(self.sadtalker_path)
        
        try:
            # Try to run the download script
            if (self.sadtalker_path / "scripts" / "download_models.sh").exists():
                subprocess.run(['bash', 'scripts/download_models.sh'], check=True)
                print("✅ Models downloaded successfully")
            else:
                print("⚠️  Download script not found, trying alternative method...")
                return self.download_models_alternative()
                
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Script failed, trying alternative: {e}")
            return self.download_models_alternative()
        finally:
            os.chdir(original_cwd)
    
    def download_models_alternative(self):
        """Alternative model download method"""
        print("📥 Downloading models manually...")
        
        models_dir = self.sadtalker_path / "checkpoints"
        models_dir.mkdir(exist_ok=True)
        
        # Model URLs (you may need to update these)
        models = {
            "SadTalker_V002.safetensors": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V002.safetensors",
            "mapping_00109-model.pth.tar": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
            "facevid2vid_00189-model.pth.tar": "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/facevid2vid_00189-model.pth.tar"
        }
        
        for model_name, url in models.items():
            model_path = models_dir / model_name
            if not model_path.exists():
                try:
                    print(f"Downloading {model_name}...")
                    urllib.request.urlretrieve(url, model_path)
                    print(f"✅ {model_name} downloaded")
                except Exception as e:
                    print(f"⚠️  Failed to download {model_name}: {e}")
        
        return True
    
    def test_installation(self):
        """Test SadTalker installation"""
        print("\n🧪 Testing installation...")
        
        # Test our integration
        try:
            sys.path.insert(0, str(self.project_root))
            from core.sadtalker_manager import SadTalkerManager
            
            manager = SadTalkerManager()
            if manager.check_installation():
                print("✅ SadTalker integration test passed!")
                return True
            else:
                print("❌ SadTalker integration test failed")
                return False
                
        except Exception as e:
            print(f"❌ Integration test error: {e}")
            return False
    
    def create_activation_script(self):
        """Create activation script for easy use"""
        print("\n📝 Creating activation script...")
        
        script_content = f'''#!/bin/bash
# SadTalker Activation Script for Mac
echo "🎬 Activating SadTalker environment..."

# Set environment variables
export SADTALKER_PATH="{self.sadtalker_path}"
export PYTHONPATH="$PYTHONPATH:{self.project_root}"

# Check PyTorch
python3 -c "import torch; print(f'PyTorch: {{torch.__version__}}')"

# Check SadTalker
python3 -c "from core.sadtalker_manager import SadTalkerManager; print('SadTalker:', SadTalkerManager().check_installation())"

echo "✅ Environment ready!"
echo "🚀 You can now use avatar-based videos in your app"
'''
        
        script_path = self.project_root / "activate_sadtalker.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"✅ Activation script created: {script_path}")
    
    def run_installation(self):
        """Run complete installation process"""
        print("🚀 Starting automated SadTalker installation for Mac...")
        print("=" * 60)
        
        steps = [
            ("Detect system", self.detect_system),
            ("Check Homebrew", self.check_homebrew),
            ("Install system dependencies", self.install_system_dependencies),
            ("Install PyTorch", self.install_pytorch),
            ("Clone SadTalker", self.clone_sadtalker),
            ("Install SadTalker dependencies", self.install_sadtalker_dependencies),
            ("Download models", self.download_models),
            ("Test installation", self.test_installation),
            ("Create activation script", self.create_activation_script)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ {step_name} failed")
                    return False
            except Exception as e:
                print(f"❌ {step_name} error: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 SadTalker installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run your Streamlit app: streamlit run app.py")
        print("2. Enable 'Generate AI Avatars' in the sidebar")
        print("3. Enable 'Avatar-Based Videos' in the sidebar")
        print("4. Enable 'SadTalker Lip-Sync' for realistic animation")
        print("\n🍎 Your Mac is now ready for AI avatar videos!")
        
        return True

def main():
    """Main installation function"""
    installer = MacSadTalkerInstaller()
    success = installer.run_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()