def build_character_prompt(request):
    return f"""
Create a game-ready character concept based on the following creative brief.

Character description:
{request.character_prompt}

Companion mood guiding the design:
{request.companion_mood}

Art direction:
{request.art_style}

World/environment influence:
{request.environment}

Creative direction:
{request.enhancement}

Reference image guidance:
{request.reference_instruction}

Design requirements:
- Use the art direction and environment to influence outfit, colors, lighting, materials, pose, and mood.
- Make the character visually unique and suitable for a game concept art pipeline.
- Include clear silhouette, readable costume details, and strong personality.
- If a reference image is provided, use it as inspiration according to the user's reference guidance without copying it directly.
- Avoid blurry details, extra limbs, broken anatomy, distorted hands, and unreadable face details.
- The final image should feel polished, intentional, and production-ready.
"""