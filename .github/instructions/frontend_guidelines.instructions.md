---
applyTo: "**/*.{ts,tsx,js,jsx}"
description: "Frontend guidelines"
---
# Frontend Guidelines

## Loading States (NON-NEGOTIABLE)

- Every waiting state > **200 ms** must be materialised without layout shift (CLS = 0).
- Hierarchy: **skeleton → progress bar → spinner**. Never a full-screen spinner on a page with known structure.
- Use `React.lazy()` + `<Suspense fallback={<Skeleton />}>` for all routes, charts, modals, editors.
- Skeletons: `<Skeleton />` from shadcn/ui, shaped like the content. Add `aria-busy="true"`, respect `prefers-reduced-motion`.
- Show skeleton on `isPending`. **Never hide existing content** during background refetch (`isFetching`).
- Progress bar: determinate (`<Progress value={n} />`) when a real % exists. Top-of-page indeterminate for route transitions only.
- Images: always `loading="lazy" decoding="async"` + explicit `width`/`height` or `aspect-ratio` to prevent CLS.
- i18n: all user-facing strings via `react-i18next` (`useTranslation`). No hardcoded UI text in components.
