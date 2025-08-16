# Makefile for Mac AI Content Factory Setup
.PHONY: setup install-deps install-sadtalker run clean help

help: ## Show this help message
	@echo "🍎 Mac AI Content Factory Setup Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: install-deps ## Complete setup with dependencies only (recommended for testing)
	@echo "✅ Basic setup complete! You can now run the app with: make run"
	@echo "💡 For lip-sync avatars, run: make install-sadtalker"

install-deps: ## Install Mac-optimized dependencies (Apple Silicon + Intel)
	@echo "🍎 Installing Mac-optimized dependencies..."
	python3 install_dependencies.py

install-sadtalker: ## Install SadTalker for lip-sync (optional, takes ~10-15 minutes)
	@echo "🎬 Installing SadTalker (this will take several minutes)..."
	python3 setup_sadtalker.py

run: ## Run the Streamlit app
	@echo "🚀 Starting AI Content Factory..."
	streamlit run app.py

test: ## Test the installation
	@echo "🧪 Running comprehensive system check..."
	python3 check_system.py

quick-test: ## Quick test of core functionality
	@echo "🧪 Quick testing..."
	python3 -c "from core.character_manager import CharacterManager; from core.avatar_manager import AvatarManager; print('✅ Core modules work')"
	python3 -c "import torch; print(f'✅ PyTorch {torch.__version__} works')"
	@echo "✅ Basic tests passed!"

clean: ## Clean up temporary files
	@echo "🧹 Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf generated_videos/temp*
	rm -f temp_audio_*.mp3
	rm -f output_video_*.mp4

requirements: ## Install from requirements.txt only
	pip3 install -r requirements.txt

# Quick start for different use cases
quick-start: install-deps ## Quick start without SadTalker (fastest)
	@echo "🚀 Quick start setup complete!"
	@echo "✅ You can now create educational videos with static avatars"
	@echo "🎥 Run: make run"

full-setup: install-deps install-sadtalker ## Full setup with SadTalker (takes longer)
	@echo "🎉 Full setup with SadTalker complete!"
	@echo "🎬 You can now create videos with realistic lip-sync"
	@echo "🎥 Run: make run"

info: ## Show system information
	@echo "🍎 System Information:"
	@echo "Platform: $$(python3 -c 'import platform; print(platform.platform())')"
	@echo "Architecture: $$(python3 -c 'import platform; print(platform.machine())')"
	@echo "Python: $$(python3 --version)"
	@echo "Git: $$(git --version 2>/dev/null || echo 'Not installed')"