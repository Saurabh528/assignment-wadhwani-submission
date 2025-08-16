/**
 * PROMPTS DOCUMENTATION
 * 
 * This file contains all the prompts used throughout the educational video generation project.
 * This is for reference only and is not linked to any code.
 * 
 * Last Updated: 2025-08-15
 */

export const PROMPTS = {
  // ============================================================================
  // CURRICULUM AGENT PROMPTS
  // ============================================================================
  
  curriculum: {
    system: "You are an expert educational content creator.",
    
    user: (topic: string, numLessons: number) => `
Create a structured curriculum for the topic: "${topic}"
Generate exactly ${numLessons} lessons.

Each lesson must have:
1. Title (engaging and descriptive)
2. Introduction (hook the viewer, 2-3 sentences)
3. Main Body (core content, 3-4 key points)
4. Summary/CTA (recap and call-to-action)

Format as JSON with this structure:
{
    "topic": "${topic}",
    "lessons": [
        {
            "title": "...",
            "introduction": "...",
            "main_body": "...",
            "summary": "..."
        }
    ]
}
    `.trim()
  },

  // ============================================================================
  // SCRIPT AGENT PROMPTS
  // ============================================================================
  
  script: {
    system: "You are a video script writer. Always ensure the visual prompt illustrates the dialogue vividly and clearly.",
    
    user: (lesson: any, characters: any[]) => `
Create a video script for this lesson:
Title: ${lesson.title}
Introduction: ${lesson.introduction}
Main Body: ${lesson.main_body}
Summary: ${lesson.summary}

Use these characters:
${JSON.stringify(characters.slice(0, 2))}

Requirements:
- 4 to 8 scenes total
- For each scene, craft the "visual" as a concise yet detailed image-generation prompt derived directly from the scene's dialogue so the image best depicts what is being said. Avoid including on-image text instructions. Use concrete nouns, setting, lighting, camera angle, mood, and style suitable for educational content.
- Keep "duration" realistic for the spoken dialogue.

Return as JSON with structure:
{
    "scenes": [
        {
            "scene_number": 1,
            "duration": 5,
            "visual": "A detailed image prompt derived from the dialogue",
            "character": "Character name",
            "dialogue": "What the character says",
            "captions": "Text overlay if any"
        }
    ]
}
    `.trim()
  },

  // ============================================================================
  // AVATAR MANAGER PROMPTS
  // ============================================================================
  
  avatar: {
    generatePrompt: (characterDetails: any) => {
      const gender = characterDetails.gender || 'person';
      const description = characterDetails.description || '';
      const voiceStyle = characterDetails.voiceStyle || 'Professional';
      
      // Build dynamic prompt based on available information
      let basePrompt = `Professional portrait photograph of a ${gender}`;
      
      // Add role based on voice style
      if (voiceStyle.toLowerCase() === 'professional') {
        basePrompt += " educator or professor";
      } else if (voiceStyle.toLowerCase() === 'friendly') {
        basePrompt += " teacher or mentor";
      } else if (voiceStyle.toLowerCase() === 'energetic') {
        basePrompt += " motivational speaker or coach";
      } else if (voiceStyle.toLowerCase() === 'calm') {
        basePrompt += " counselor or guide";
      } else {
        basePrompt += " instructor";
      }
      
      // If description is provided, use it; otherwise generate based on attributes
      let appearance;
      if (description && description.length > 10) {
        appearance = description;
      } else {
        // Generate generic but appropriate appearance
        if (gender.toLowerCase() === 'male') {
          appearance = "Well-groomed man with professional attire";
        } else if (gender.toLowerCase() === 'female') {
          appearance = "Well-presented woman with professional attire";
        } else {
          appearance = "Well-dressed person with professional appearance";
        }
      }
      
      return `${basePrompt}

Appearance: ${appearance}
Expression: ${voiceStyle.toLowerCase()} and approachable demeanor, warm smile, direct eye contact

Technical specifications:
- Front-facing portrait, shoulders and head visible
- Centered in frame
- Professional studio lighting
- Clean, neutral background (light gray or soft gradient)
- Photorealistic style
- High detail facial features for animation
- Natural skin tones
- No text or watermarks
- No accessories blocking face`.trim();
    }
  },

  // ============================================================================
  // AVATAR VIDEO GENERATOR PROMPTS
  // ============================================================================
  
  avatarVideoGenerator: {
    // Image generation prompt for educational content
    educationalImage: (description: string) => 
      `Educational illustration: ${description}. Professional, clean, suitable for learning content.`,
    
    // Dialogue to visual conversion prompt
    dialogueToVisual: (dialogue: string) => 
      `Convert this dialogue into a concise image prompt: ${dialogue}`
  },

  // ============================================================================
  // VIDEO GENERATOR PROMPTS
  // ============================================================================
  
  videoGenerator: {
    // System prompt for visual prompt engineering
    visualPromptEngineer: 
      "You are a visual prompt engineer. Convert the spoken dialogue into a highly specific, photorealistic image prompt. " +
      "Include setting, subject, key objects, composition, lens and depth of field, lighting (cinematic/soft/natural), mood, color palette, and style. " +
      "The image must directly reflect the semantics of the dialogue. Avoid any on-image text or watermarks. One vivid sentence only.",
    
    // User prompt for dialogue to image conversion
    dialogueToImage: (dialogue: string, characterName?: string) => {
      const speaker = characterName ? ` by ${characterName}` : "";
      return `Dialogue${speaker}:

${dialogue}

Write ONE ultra-photorealistic prompt sentence that best depicts this dialogue.`;
    },
    
    // DALL-E image generation prompts
    dalleUltraPhotorealistic: (description: string) =>
      `Ultra-photorealistic photograph. ${description}. Cinematic lighting, shallow depth of field, realistic textures, high detail skin, no text, no watermark.`,
    
    dalleVariant: (description: string, variationNumber: number) =>
      `Ultra-photorealistic photograph. ${description}. Variation ${variationNumber}, alternate angle or moment. Cinematic lighting, shallow depth of field, realistic textures, no text, no watermark.`
  },

  // ============================================================================
  // PROMPT TEMPLATES AND PATTERNS
  // ============================================================================
  
  templates: {
    // Generic educational content prompt
    educationalContent: (topic: string, style: string = 'professional') =>
      `Educational ${style} illustration about ${topic}. Clean, modern design suitable for learning materials.`,
    
    // Character-based dialogue prompt
    characterDialogue: (characterName: string, dialogue: string) =>
      `${characterName} says: "${dialogue}". Create a visual that represents this moment.`,
    
    // Scene description prompt
    sceneDescription: (sceneNumber: number, content: string) =>
      `Scene ${sceneNumber}: ${content}. Create a visual representation of this educational moment.`
  },

  // ============================================================================
  // PROMPT CONFIGURATIONS
  // ============================================================================
  
  configurations: {
    // Temperature settings for different types of generation
    temperature: {
      curriculum: 0.7,
      script: 0.7,
      avatar: 0.4,
      visualPrompt: 0.4,
      dialogueToVisual: 0.4
    },
    
    // Model configurations
    models: {
      llm: "gpt-4o-mini", // or "gpt-4o" for production
      image: "dall-e-3",
      tts: "tts-1"
    },
    
    // Image generation settings
    imageSettings: {
      size: "1024x1024",
      quality: "standard", // or "hd" for production
      style: "natural" // or "vivid"
    }
  },

  // ============================================================================
  // PROMPT BEST PRACTICES
  // ============================================================================
  
  bestPractices: {
    // Guidelines for creating effective prompts
    guidelines: [
      "Always be specific about the desired output format",
      "Include technical specifications when generating images",
      "Use clear, descriptive language for visual prompts",
      "Maintain consistency in character descriptions",
      "Avoid ambiguous or subjective terms",
      "Include context for educational content",
      "Specify style and mood requirements",
      "Use concrete nouns and specific details"
    ],
    
    // Common pitfalls to avoid
    pitfalls: [
      "Vague or generic descriptions",
      "Inconsistent character attributes",
      "Missing technical specifications",
      "Overly complex or verbose prompts",
      "Inappropriate content for educational context",
      "Missing style or quality specifications"
    ]
  }
};

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

export const USAGE_EXAMPLES = {
  // Example of generating a curriculum
  curriculumExample: {
    topic: "Introduction to Machine Learning",
    numLessons: 3,
    expectedOutput: {
      topic: "Introduction to Machine Learning",
      lessons: [
        {
          title: "What is Machine Learning?",
          introduction: "Discover how computers can learn from data without being explicitly programmed.",
          main_body: "Definition, types of ML, real-world applications, basic concepts",
          summary: "Machine learning enables computers to improve through experience."
        }
      ]
    }
  },
  
  // Example of generating a script
  scriptExample: {
    lesson: {
      title: "Understanding Neural Networks",
      introduction: "Neural networks are the foundation of modern AI.",
      main_body: "Neurons, layers, activation functions, training process",
      summary: "Neural networks mimic human brain function for pattern recognition."
    },
    characters: [
      { name: "Professor Alex", description: "Expert educator" },
      { name: "Student Sam", description: "Curious learner" }
    ]
  },
  
  // Example of avatar generation
  avatarExample: {
    characterDetails: {
      name: "Professor Alex",
      gender: "Male",
      description: "Professional educator with glasses",
      voiceStyle: "Professional"
    }
  }
};

// ============================================================================
// PROMPT VALIDATION RULES
// ============================================================================

export const VALIDATION_RULES = {
  // Rules for validating prompt quality
  curriculum: {
    requiredFields: ["topic", "lessons"],
    lessonFields: ["title", "introduction", "main_body", "summary"],
    maxLessons: 10,
    minLessons: 1
  },
  
  script: {
    requiredFields: ["scenes"],
    sceneFields: ["scene_number", "duration", "visual", "character", "dialogue"],
    maxScenes: 12,
    minScenes: 3
  },
  
  avatar: {
    requiredFields: ["gender", "description", "voiceStyle"],
    maxDescriptionLength: 500,
    minDescriptionLength: 10
  }
};

export default PROMPTS;
