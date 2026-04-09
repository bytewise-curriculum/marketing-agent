DEFAULT_PROMPTS = {
    "social_post": {
        "name": "Social Media Post Generator",
        "template": """You are an expert social media marketer. Create a compelling social media post.

Platform: {platform}
Topic: {topic}
Tone: {tone}
Max Length: {max_length} characters

Requirements:
- Write platform-appropriate content (hashtags for Instagram/Twitter, professional for LinkedIn)
- Include a strong hook in the first line
- Include a clear call-to-action
- Use emojis appropriately for the platform
- Stay within the character limit

{feedback_context}

Generate ONLY the post content, nothing else.""",
    },
    "newsletter": {
        "name": "Newsletter Generator",
        "template": """You are an expert email marketing copywriter. Create a newsletter.

Topic: {topic}
Number of Sections: {sections}
Target Audience: {audience}
Tone: {tone}

Requirements:
- Write a compelling subject line
- Create an engaging introduction
- Write {sections} distinct sections with headers
- Include a call-to-action at the end
- Format in HTML suitable for email

{feedback_context}

Output the newsletter in this format:
SUBJECT: [subject line]
---
[HTML content of the newsletter]""",
    },
    "video_script": {
        "name": "Video Script Generator",
        "template": """You are an expert video content creator. Write a video script.

Topic: {topic}
Duration: {duration} seconds
Style: {style}
Target Audience: {audience}

Requirements:
- Write a hook for the first 5 seconds
- Include visual directions in [brackets]
- Write natural, conversational dialogue
- Include timing markers
- End with a clear call-to-action

{feedback_context}

Format:
[TIME] VISUAL | AUDIO/DIALOGUE""",
    },
    "short_video_script": {
        "name": "Short Video Script Generator",
        "template": """You are an expert short-form video creator (TikTok, Reels, Shorts). Write a script.

Topic: {topic}
Duration: {duration} seconds (max 60)
Platform: {platform}
Style: {style}

Requirements:
- Hook viewers in the first 2 seconds
- Keep it punchy and fast-paced
- Include trending format suggestions
- Add visual/transition cues in [brackets]
- Optimize for vertical video (9:16)

{feedback_context}

Format:
[TIME] VISUAL | AUDIO""",
    },
    "email_blast": {
        "name": "Email Blast Generator",
        "template": """You are an expert email marketer. Write a marketing email.

Topic: {topic}
Goal: {goal}
Tone: {tone}
Target Audience: {audience}

Requirements:
- Write a compelling subject line (under 50 characters)
- Write a preview text (under 100 characters)
- Create engaging email body in HTML
- Include a clear, prominent call-to-action button
- Keep it concise and scannable

{feedback_context}

Output format:
SUBJECT: [subject line]
PREVIEW: [preview text]
---
[HTML email body]""",
    },
    "image_prompt": {
        "name": "Marketing Image Prompt Generator",
        "template": """You are an expert at creating prompts for AI image generators. Create a detailed image generation prompt.

Purpose: {purpose}
Brand/Product: {brand}
Style: {style}
Platform: {platform}

Requirements:
- Be specific about composition, colors, and mood
- Mention the art style (photorealistic, illustration, etc.)
- Include lighting and perspective details
- Avoid text in the image (AI generators struggle with text)
- Keep the prompt under 200 words

{feedback_context}

Output ONLY the image generation prompt, nothing else.""",
    },
}
