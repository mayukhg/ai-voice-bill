# Skill Icons and Images

This directory contains the skill icons and images required for the Alexa Skills Store listing.

## Required Images

### 1. Small Icon
- **File**: `small-icon.png`
- **Size**: 108x108 pixels
- **Format**: PNG
- **Background**: Transparent
- **Usage**: Displayed in skill search results and skill cards

### 2. Large Icon
- **File**: `large-icon.png`
- **Size**: 512x512 pixels
- **Format**: PNG
- **Background**: Transparent
- **Usage**: Displayed on skill detail page

### 3. Skill Preview Image
- **File**: `skill-preview.png`
- **Size**: 1200x800 pixels
- **Format**: PNG
- **Usage**: Displayed on skill store listing page

## Design Guidelines

1. **Icons should:**
   - Represent bill payment/money theme
   - Be clear and recognizable at small sizes
   - Use high contrast colors
   - Follow Amazon's content guidelines

2. **Preview image should:**
   - Show the skill's main features
   - Include text describing key capabilities
   - Be visually appealing and professional
   - Not include any sensitive information

## Creating Icons

You can create these icons using:
- Design tools (Figma, Adobe Illustrator, Canva)
- Online icon generators
- Professional graphic designer

## Example Design Ideas

- **Icon**: Dollar sign or bill/document icon with voice waves
- **Preview**: Showcase "Voice Bill Payment", "Secure OTP Verification", "Proactive Reminders"

## Upload Instructions

1. Create the icons according to specifications
2. Upload to your web server or CDN
3. Update URLs in `skill.json`:
   - `smallIconUri`
   - `largeIconUri`
   - Preview image URL in Developer Console

## Notes

- Icons must be publicly accessible via HTTPS
- Amazon may reject icons that don't meet guidelines
- Test icons on different devices/screens
- Ensure icons are not copyrighted or trademarked

