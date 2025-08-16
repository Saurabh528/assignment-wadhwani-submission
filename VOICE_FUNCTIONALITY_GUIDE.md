# 🎤 Voice Functionality Guide

## Overview

The educational video generation system now includes comprehensive voice style management with real-time preview and testing capabilities. This guide explains all the voice-related features available in the dashboard.

## 🎯 Voice Styles Available

### 8 Professional Voice Styles

1. **Professional** - Clear, authoritative voice suitable for educational content
2. **Friendly** - Warm, approachable voice that builds rapport
3. **Energetic** - Dynamic, enthusiastic voice that engages learners
4. **Calm** - Soothing, patient voice for complex topics
5. **Confident** - Self-assured, commanding presence
6. **Playful** - Fun, engaging voice for younger audiences
7. **Narrative** - Storytelling voice with natural flow
8. **Technical** - Precise, detailed voice for complex subjects

### 3 Gender Options

- **Male** - Masculine voice characteristics
- **Female** - Feminine voice characteristics  
- **Neutral** - Balanced, gender-neutral voice

## 🎵 OpenAI Voice Mapping

The system maps your character's gender and voice style to specific OpenAI TTS voices:

| OpenAI Voice | Characteristic | Best For |
|--------------|----------------|----------|
| **onyx** | Deep, authoritative male voice | Professional, Confident, Technical |
| **nova** | Clear, professional female voice | Professional, Confident, Technical |
| **echo** | Warm, friendly male voice | Friendly, Narrative, Playful |
| **shimmer** | Bright, engaging female voice | Friendly, Energetic, Playful |
| **fable** | Dynamic, expressive voice | Energetic, Playful, Narrative |
| **alloy** | Balanced, versatile voice | All styles, Neutral gender |

## 🚀 Dashboard Features

### 1. Character Creation with Voice Preview

**Location:** Step 2 → Character Management → Create New Character

**Features:**
- Select from 8 voice styles with descriptions
- Choose gender (Male/Female/Neutral)
- Real-time voice preview before creating character
- Voice mapping information display
- Characteristic descriptions for each OpenAI voice

**How to use:**
1. Enter character name and description
2. Select voice style (see descriptions)
3. Choose gender
4. Enter preview text
5. Click "🎵 Preview Voice" to hear how it sounds
6. Review voice mapping information
7. Click "Add Character" to save

### 2. Voice Settings for Existing Characters

**Location:** Step 2 → Character Management → Character Library

**Features:**
- Expandable voice settings for each character
- Current voice configuration display
- Individual character voice preview
- Voice mapping information

**How to use:**
1. Find your character in the library
2. Click the expander "🎤 Voice Settings for [Character Name]"
3. View current voice configuration
4. Enter custom preview text
5. Click "🎵 Preview" to hear the character's voice

### 3. Voice Style Testing Lab

**Location:** Step 2 → Character Management → Voice Style Testing Lab

**Features:**
- Test any gender + voice style combination
- Custom test text input
- Real-time audio generation
- Download test audio files
- Voice characteristic information

**How to use:**
1. Select gender and voice style
2. Enter test text
3. Click "🎵 Test Voice Combination"
4. Listen to the generated audio
5. Download the test file if needed

### 4. Voice Style Comparison

**Location:** Step 2 → Character Management → Voice Style Comparison

**Features:**
- Side-by-side comparison of two voice styles
- Same gender, different styles
- Same text for fair comparison
- Download both audio files
- Detailed voice information

**How to use:**
1. Select gender for comparison
2. Choose two different voice styles
3. Enter comparison text
4. Click "🔄 Compare Voices"
5. Listen to both versions side by side

### 5. Advanced Speech Synthesis

**Location:** Step 3 → OpenAI Speech Synthesis

**Features:**
- Custom voice instructions
- Multiple OpenAI voices
- Quality settings (Standard/HD)
- Speed control (0.25x to 4.0x)
- Predefined instruction templates

**How to use:**
1. Enter text to synthesize
2. Add custom voice instructions
3. Select OpenAI voice and quality
4. Adjust speech speed
5. Generate and download audio

## 🎬 Video Generation Integration

When generating videos, the system automatically:

1. **Uses character voice styles** - Each character's dialogue is synthesized using their assigned voice style
2. **Maintains consistency** - Same character always uses the same voice across all scenes
3. **Maps to OpenAI voices** - Automatically converts character settings to appropriate OpenAI TTS voices
4. **Generates synchronized audio** - Creates audio files that match the video timing

## 🔧 Technical Implementation

### Voice Mapping Logic

```python
# Example: Male Professional character
voice_key = "Male_Professional"
mapped_voice = "onyx"  # Deep, authoritative male voice

# Example: Female Friendly character  
voice_key = "Female_Friendly"
mapped_voice = "shimmer"  # Bright, engaging female voice
```

### TTS Manager Methods

- `generate_voiceover(text, character, output_path)` - Generate speech for a character
- `get_voice_style_descriptions()` - Get all available voice styles
- `get_voice_characteristics()` - Get OpenAI voice descriptions
- `get_voice_mapping_info(gender, style)` - Get detailed mapping information

## 💡 Best Practices

### Choosing Voice Styles

1. **Educational Content**: Use Professional, Confident, or Technical
2. **Engaging Learners**: Use Friendly, Energetic, or Playful
3. **Complex Topics**: Use Calm or Professional
4. **Storytelling**: Use Narrative or Friendly
5. **Younger Audiences**: Use Playful or Energetic

### Character Voice Design

1. **Consistency**: Keep the same voice style for each character
2. **Personality Match**: Choose voice style that matches character personality
3. **Audience Consideration**: Consider your target audience when selecting voices
4. **Content Type**: Match voice style to content type (technical vs. casual)

### Testing Recommendations

1. **Preview Before Creating**: Always test voice before finalizing character
2. **Compare Options**: Use comparison feature to choose between similar styles
3. **Test with Real Content**: Use actual script text for testing
4. **Check Consistency**: Ensure voice works well across different text lengths

## 🎯 Example Use Cases

### Case 1: Professional Course
- **Professor**: Male Professional (onyx voice)
- **Teaching Assistant**: Female Technical (nova voice)
- **Student Examples**: Female Friendly (shimmer voice)

### Case 2: Children's Educational Content
- **Main Teacher**: Female Playful (shimmer voice)
- **Story Narrator**: Male Narrative (echo voice)
- **Fun Character**: Neutral Energetic (fable voice)

### Case 3: Technical Training
- **Expert Instructor**: Male Confident (onyx voice)
- **Step-by-step Guide**: Female Professional (nova voice)
- **Troubleshooting**: Male Calm (onyx voice)

## 🚨 Troubleshooting

### Common Issues

1. **Voice not generating**: Check OpenAI API key and internet connection
2. **Wrong voice style**: Verify character's gender and voice style settings
3. **Audio quality issues**: Try different OpenAI voices or quality settings
4. **Preview not working**: Ensure text is not empty and API key is valid

### Performance Tips

1. **Use test mode** for faster preview generation
2. **Keep preview text short** for quicker testing
3. **Cache generated audio** to avoid regenerating same content
4. **Use appropriate quality settings** (standard for testing, HD for production)

## 📊 Cost Considerations

- **TTS Cost**: $0.015 per 1,000 characters
- **Preview Generation**: Each preview uses API credits
- **Video Generation**: All character dialogue is synthesized
- **Testing**: Multiple tests will increase costs

**Recommendation**: Use test mode and short previews during development to minimize costs.

---

## 🎉 Getting Started

1. **Run the dashboard**: `streamlit run app.py`
2. **Create a character**: Go to Step 2 → Character Management
3. **Test voice styles**: Use the preview and testing features
4. **Generate content**: Create curriculum and scripts
5. **Produce videos**: Generate final videos with character voices

The voice functionality is now fully integrated and ready for production use!
