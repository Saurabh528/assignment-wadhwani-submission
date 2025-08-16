# 🍎 Mac Setup Guide - AI Content Factory

## 🚀 One-Command Setup

Choose your setup speed:

### ⚡ **Quick Setup (Recommended for Testing)**
```bash
make quick-start
```
- Installs Mac-optimized dependencies
- Static avatars (fast generation)
- Ready in ~2-3 minutes

### 🎬 **Full Setup (With Lip-Sync)**
```bash
make full-setup
```
- Everything from quick setup
- + SadTalker for realistic lip-sync
- Takes ~10-15 minutes

## 🔧 **Manual Setup (Step by Step)**

If you prefer manual control:

### 1. Install Dependencies
```bash
# This auto-detects Apple Silicon vs Intel Mac
python3 install_dependencies.py
```

### 2. (Optional) Install SadTalker
```bash
# Only if you want realistic lip-sync
python3 setup_sadtalker.py
```

### 3. Run the App
```bash
streamlit run app.py
```

## 🍎 **What Gets Auto-Detected**

The installer automatically handles:

| Mac Type | PyTorch | Optimization | Avatar Speed |
|----------|---------|-------------|--------------|
| **Apple Silicon (M1/M2/M3)** | MPS enabled | Metal shaders | ~20-40s |
| **Intel Mac** | CPU version | CPU optimized | ~60-120s |

## ✅ **Verify Installation**

```bash
make test
```

This checks:
- ✅ Core modules working
- ✅ PyTorch installation
- ✅ Mac optimization active

## 🎯 **Usage Modes**

### 1. **Static Avatar Mode (Fast)**
- Enable: "Generate AI Avatars" ✅
- Enable: "Avatar-Based Videos" ✅  
- Leave: "SadTalker Lip-Sync" ❌
- Result: Static talking avatar

### 2. **Lip-Sync Mode (Realistic)**
- Enable: "Generate AI Avatars" ✅
- Enable: "Avatar-Based Videos" ✅
- Enable: "SadTalker Lip-Sync" ✅
- Result: Realistic lip-synchronized avatar

## 🆘 **Troubleshooting**

### Issue: "PyTorch not working"
```bash
python3 -c "import torch; print(torch.__version__)"
```
If fails: `make install-deps` again

### Issue: "SadTalker not found"
```bash
make install-sadtalker
```

### Issue: "Permission denied"
```bash
chmod +x install_dependencies.py
chmod +x setup_sadtalker.py
```

### Issue: "Homebrew required"
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

## 📊 **Expected Performance**

| Mac Model | Memory Usage | Video Generation | Quality |
|-----------|-------------|------------------|---------|
| M3 MacBook Pro | 6-8GB | ~30-45s | Excellent |
| M2 MacBook Air | 4-6GB | ~45-60s | Very Good |
| M1 MacBook | 4-6GB | ~60-90s | Good |
| Intel MacBook | 2-4GB | ~90-120s | Good |

## 🎬 **Video Layout**

```
┌─────────────┬─────────────────────────────────┐
│             │                                 │
│   Avatar    │      Educational Content        │
│   (1/4)     │         (3/4 screen)           │
│             │                                 │
│  Speaking   │    • Images                     │
│  Teacher    │    • Diagrams                   │
│             │    • Illustrations              │
│             │                                 │
└─────────────┴─────────────────────────────────┘
```

## 🧹 **Cleanup**

Remove temporary files:
```bash
make clean
```

## 🔍 **System Info**

Check your Mac specs:
```bash
make info
```

---

## 🎉 **Quick Start Summary**

1. `make quick-start` (or `make full-setup`)
2. `make run`
3. Create characters with avatars
4. Generate curriculum
5. Create avatar-based videos!

**That's it! Your Mac is now a video generation powerhouse! 🚀**