# Design System Document: The Clinical Precision Framework

## 1. Overview & Creative North Star: "The Empathetic Authority"

This design system moves beyond the cold, sterile nature of traditional healthcare platforms to embrace **"The Empathetic Authority."** Our Creative North Star focuses on a "High-End Editorial" approach to medical information—combining the unshakeable reliability of a peer-reviewed journal with the approachable clarity of a luxury wellness boutique.

To break the "template" look, this system rejects rigid, boxed-in grids. Instead, it utilizes **intentional asymmetry** and **tonal layering**. By overlapping "glass" surfaces and using aggressive white space, we create a layout that feels breathable and calm—essential for users who may be navigating stressful health decisions. We lead with typography that commands attention and surfaces that feel physical and high-touch.

---

## 2. Colors: Tonal Depth & The "No-Line" Rule

The palette is anchored in `primary` (#002869), a deep medical blue that evokes institutional trust, balanced by `secondary` (#006b5e), a calming teal that represents healing and vitality.

### The "No-Line" Rule
To achieve a premium aesthetic, **1px solid borders are prohibited for sectioning.** Conventional lines create visual "noise" and feel dated. Boundaries must be defined through:
- **Background Shifts:** Place a `surface-container-low` (#f4f3fa) section directly against a `surface` (#faf8ff) background.
- **Tonal Transitions:** Use subtle shifts between `surface-container` tiers to define content blocks.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, physical layers.
- **Base:** `surface` (#faf8ff)
- **Primary Content Blocks:** `surface-container-low` (#f4f3fa)
- **Feature Cards:** `surface-container-lowest` (#ffffff) to create a "pop" against darker sections.
- **Interactive Modals:** `surface-bright` (#faf8ff) with backdrop blurs.

### The "Glass & Gradient" Rule
For hero sections and primary CTAs, avoid flat color. Use a **Signature Texture**:
- **Gradients:** A subtle linear transition from `primary` (#002869) to `primary_container` (#103e8f) adds "soul" and prevents the medical blue from feeling heavy.
- **Glassmorphism:** For floating navigation or patient alerts, use `surface` at 80% opacity with a `backdrop-blur` of 20px. This ensures the UI feels integrated and modern.

---

## 3. Typography: Editorial Clarity

We utilize two distinct typefaces to balance authority with accessibility.

*   **Display & Headlines (Public Sans):** Chosen for its geometric stability and neutral, trustworthy tone.
    *   **Display-LG (3.5rem):** Use for high-impact hero statements.
    *   **Headline-MD (1.75rem):** Used for section headers to establish immediate hierarchy.
*   **Body & Labels (Inter):** A highly legible sans-serif optimized for screen readability at small sizes.
    *   **Body-LG (1rem):** The standard for patient education text and articles.
    *   **Label-MD (0.75rem):** Used for metadata and micro-copy.

**Hierarchy Strategy:** Use `primary` (#002869) for all headlines to maintain an authoritative voice, while `on_surface_variant` (#434651) should be used for body text to reduce eye strain and improve the "softness" of the reading experience.

---

## 4. Elevation & Depth: Tonal Layering

Traditional shadows are often too harsh for a clinical environment. This system relies on **Tonal Layering** and **Ambient Light**.

*   **The Layering Principle:** Depth is achieved by stacking. Place a `surface-container-lowest` (#ffffff) card atop a `surface-container-high` (#e8e7ef) background. This creates a natural "lift" without artificial effects.
*   **Ambient Shadows:** If a floating element (like a FAB or Popover) requires a shadow, use a large blur (32px+) at 6% opacity. Use the `on_surface` color tinted into the shadow to simulate natural light.
*   **The "Ghost Border" Fallback:** If a container requires a border for accessibility (e.g., in high-contrast modes), use `outline_variant` (#c4c6d3) at **15% opacity**. Never use 100% opaque borders.
*   **Glassmorphism:** Use semi-transparent `surface_container_lowest` for headers. This allows the medical blue of hero sections to bleed through, softening the transition as the user scrolls.

---

## 5. Components: Refined Interaction

### Buttons
- **Primary:** High-contrast `primary` (#002869) with `on_primary` (#ffffff) text. Use `xl` (0.75rem) roundedness for a modern, approachable feel.
- **Secondary:** Use `secondary_container` (#94f0df) with `on_secondary_container` (#006f62). This is for "Positive" actions like "Book Appointment."
- **Tertiary:** Ghost style using `primary` text. No container until hover.

### Cards & Lists
- **The "No-Divider" Rule:** Forbid the use of hairline dividers. Separate list items using `body-md` spacing (vertical whitespace) or by alternating background tones between `surface-container-low` and `surface-container-lowest`.
- **Nesting:** Ensure cards have a `md` (0.375rem) corner radius to feel precise but not sharp.

### Input Fields
- **State:** Use `surface_container_highest` (#e2e2e9) for the input background to provide a clear "target." 
- **Focus:** Transition to a 2px `surface_tint` (#365bad) "Ghost Border" on focus. 
- **Error:** Use `error` (#ba1a1a) for text and `error_container` (#ffdad6) for the background fill.

### Specialized Component: The "Trust Badge"
- A small `secondary_fixed` (#97f3e2) chip used to highlight verified credentials or "Doctor Recommended" status. It uses `on_secondary_fixed_variant` (#005047) for the label.

---

## 6. Do's and Don'ts

### Do
- **Do** use asymmetrical margins (e.g., 80px left, 120px right) in editorial sections to create a premium, non-standard feel.
- **Do** utilize `primary_fixed` (#dae2ff) for large background areas that need to feel "medical" but light.
- **Do** prioritize `display-md` typography for key statistics (e.g., "99% Success Rate").

### Don't
- **Don't** use pure black (#000000) for text. Always use `on_surface` (#1a1b21).
- **Don't** use standard "drop shadows" on cards; stick to tonal shifts.
- **Don't** use harsh 1px dividers to separate patient data. Use vertical space and subtle background containers.
- **Don't** use the `secondary` teal for error or warning states; keep it strictly for "healing" and "positive" progression.

### Accessibility Note
Ensure that all `primary` on `surface` combinations maintain a 4.5:1 contrast ratio. Use the `on_primary_container` (#8eadff) sparingly for decorative elements, as it may not pass contrast requirements for small body text against white.