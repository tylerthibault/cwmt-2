# CWMT Frontend Styling Guide

## Hero Section Redesign

### Design Philosophy
The hero section follows a **modern, mobile-first design approach** with unique visual elements that set CWMT apart. The design emphasizes:
- Clean, contemporary aesthetics with depth and motion
- Glassmorphism and modern UI patterns
- Smooth animations and micro-interactions
- Brand consistency through CSS variables

---

## Visual Elements

### 1. Animated Background Shapes
Three floating gradient orbs create ambient motion and depth behind the content.

**Implementation:**
- Three circular shapes with heavy blur (`filter: blur(80px)`)
- Each shape uses brand gradient variables
- Continuous floating animation (20s loop) with scale and translation
- Positioned strategically for balanced composition
- Low opacity (0.4) for subtle effect

**Colors:**
- Shape 1: `--brand-gradient-primary` (red gradient)
- Shape 2: `--brand-gradient-blue` (blue gradient)
- Shape 3: `--brand-gradient-dark` (dark gradient)

### 2. Typography Hierarchy
Multi-level title system with gradient text effects.

**Structure:**
```
hero-title-top: "Master the Road" (small, uppercase, muted)
hero-title-main: "Central Washington" (large, gradient text)
hero-title-accent: "Motorcycle Training" (large, red gradient)
```

**Techniques:**
- `background-clip: text` with gradient backgrounds for color depth
- `clamp()` for responsive font sizing
- Stacked vertical layout for dramatic presentation
- Different font weights (600, 900, 800) for visual hierarchy

### 3. Glassmorphism Effects
Modern translucent cards with backdrop blur.

**Applied to:**
- Hero badge (certification badge)
- Quick stats card (mobile)
- Feature pills (desktop)
- Floating stats card
- Secondary button

**CSS Properties:**
- `backdrop-filter: blur(10px)` for glass effect
- Semi-transparent white backgrounds (`--overlay-white-80`, `--overlay-white-90`, etc.)
- Subtle borders with low opacity
- Soft shadows for depth

### 4. Interactive Video Card
Portrait-oriented video with 3D hover effect and play badge overlay.

**Features:**
- Portrait aspect ratio (4:5) for modern aesthetic
- 3D rotation on hover (`perspective(1000px) rotateY(-5deg)` on desktop)
- Play badge appears on hover with scale animation
- Dark gradient overlay for text readability
- Rounded corners (24px) with shadow

**Video Aspect Ratios:**
- Mobile: 4:5 (portrait)
- Tablet landscape: 16:10 (wide)
- Desktop: 4:5 (portrait)

### 5. Floating Stats Card
Animated card that hovers over video with success metrics.

**Design:**
- Positioned absolutely at bottom-right of video
- Continuous bounce animation (3s loop)
- Green gradient icon with checkmark
- Glass effect background
- Shows 98% pass rate prominently

### 6. Button Designs

**Primary Button (Get Started):**
- Red brand gradient background
- White text with arrow icon
- Arrow slides right on hover
- Lift effect on hover (`translateY(-2px)`)
- Enhanced shadow on hover
- Gradient overlay on hover for shine effect

**Secondary Button (Explore Courses):**
- Glass effect with transparent background
- Dark text
- Subtle border
- Lift and shadow on hover

### 7. Quick Stats Bar (Mobile Only)
Horizontal stats display for mobile devices.

**Layout:**
- Three stats with vertical dividers
- Glass card background
- Compact sizing for mobile
- Hidden on desktop (replaced by feature pills)

### 8. Feature Pills (Desktop Only)
Icon-based feature highlights that appear only on larger screens.

**Features Displayed:**
- Expert Instructors (users icon)
- Modern Equipment (badge icon)
- Flexible Schedule (clock icon)

**Style:**
- Pill-shaped with rounded corners
- Glass effect background
- Icons in brand primary color
- Lift and shadow on hover

---

## Responsive Breakpoints

### Mobile (320px - 639px)
- Vertical stacking of content
- Full-width buttons stacked vertically
- Portrait video aspect ratio
- Quick stats bar visible
- Compact spacing and padding
- Centered text alignment

### Tablet (640px - 767px)
- Horizontal button layout
- Larger text sizes
- Increased padding
- Floating stats card repositioned

### Tablet Landscape (768px - 1023px)
- Enhanced spacing
- Larger titles
- Video aspect ratio changes to 16:10

### Desktop (1024px+)
- Side-by-side grid layout (1.1fr 1fr)
- Content on left, video on right
- Left-aligned text
- Quick stats hidden, feature pills visible
- 3D video hover effect active
- Maximum visual impact

### Large Desktop (1280px+)
- Increased spacing between grid columns
- Larger typography
- Enhanced padding

### Extra Large Desktop (1536px+)
- Maximum font sizes applied
- Optimal spacing for large displays

---

## CSS Architecture

### Variables System
All colors, gradients, and overlays use CSS variables for maintainability.

**Brand Colors:**
```css
--brand-primary: #a93226
--brand-primary-light: #e74c3c
--brand-dark: #2c3e50
--brand-dark-light: #34495e
--brand-accent-blue: #3498db
```

**Brand Gradients:**
```css
--brand-gradient-primary: linear-gradient(135deg, #a93226 0%, #e74c3c 100%)
--brand-gradient-dark: linear-gradient(135deg, #2c3e50 0%, #34495e 100%)
--brand-gradient-blue: linear-gradient(135deg, #3498db 0%, #2980b9 100%)
--brand-gradient-bg: linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f1f3f5 100%)
```

**Overlay Colors:**
```css
--overlay-white-90: rgba(255, 255, 255, 0.9)
--overlay-white-80: rgba(255, 255, 255, 0.8)
--overlay-white-95: rgba(255, 255, 255, 0.95)
--overlay-black-10: rgba(0, 0, 0, 0.1)
--overlay-black-40: rgba(0, 0, 0, 0.4)
--overlay-gradient-white: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%)
--overlay-gradient-dark: linear-gradient(to top, rgba(0,0,0,0.4) 0%, transparent 50%)
```

### Animation System

**fadeInDown:**
- Fades in from above
- Used for badge
- Duration: 0.8s

**fadeInUp:**
- Fades in from below
- Staggered delays for sequential reveal
- Used for title (0.2s), description (0.4s), buttons (0.6s), stats (0.8s)

**float:**
- Continuous floating motion for background shapes
- 20s duration with ease-in-out
- Combines translation and scale
- Different delay for each shape

**floatCard:**
- Gentle vertical bounce for floating stats card
- 3s duration infinite loop
- Subtle motion (10px)

### Color Usage Strategy

**With `color-mix()` for dynamic transparency:**
```css
border: 1px solid color-mix(in srgb, var(--brand-primary) 20%, transparent);
box-shadow: 0 4px 12px color-mix(in srgb, var(--brand-primary) 10%, transparent);
```

This modern CSS function allows mixing brand colors with transparency dynamically.

---

## Design Patterns Used

1. **Mobile-First Approach**: All base styles target mobile, with progressive enhancement for larger screens
2. **Glassmorphism**: Translucent elements with backdrop blur for modern aesthetic
3. **Gradient Text**: Brand colors enhanced with gradients using background-clip
4. **Micro-interactions**: Subtle hover effects on all interactive elements
5. **Asymmetric Composition**: Floating card breaks the grid for visual interest
6. **Progressive Disclosure**: Different elements visible at different breakpoints
7. **Motion Design**: Ambient background animation with purposeful hover states
8. **Depth Layering**: Multiple z-index layers create depth perception

---

## Performance Considerations

- **Will-change**: Not used to avoid over-optimization
- **Transform & Opacity**: Used for animations (GPU-accelerated)
- **Backdrop-filter**: Used sparingly on static elements only
- **Video optimization**: HTML5 video with autoplay, muted, loop, and playsinline attributes
- **Aspect-ratio**: Modern CSS property for consistent video sizing
- **Clamp()**: Fluid typography scales naturally without JavaScript

---

## Accessibility Features

- Semantic HTML structure
- High contrast text colors
- Adequate touch targets (min 44px on mobile)
- Reduced motion not yet implemented (future enhancement needed)
- SVG icons with proper viewBox attributes
- Video with proper source declarations

---

## Future Enhancements

1. Add `@media (prefers-reduced-motion: reduce)` to disable animations for accessibility
2. Implement lazy loading for video on mobile
3. Add skeleton loading states
4. Consider adding scroll-triggered animations
5. Implement dark mode support using CSS variables
6. Add focus-visible styles for keyboard navigation
