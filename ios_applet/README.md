# EcoDrain Combined Framework (React)

This directory contains the cross-platform React implementation of the EcoDrain Intelligence Dashboard. It uses the same mathematical 2RC-Thevenin model derived in the project report, optimized for mobile performance on both Android and iOS.

## Cross-Platform Strategy
- **Framework**: React 18 with Vite
- **Styling**: Tailwind-inspired CSS for responsive, mobile-first design.
- **Animations**: Framer Motion for premium, high-frequency UI updates.
- **Icons**: Lucide React (Vector-based cross-platform support).
- **Mobile Integration**: Ready for **Capacitor** or **React Native Web** to wrap into native `.apk` (Android) or `.ipa` (iOS) files.

## Local Development
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm run dev
   ```

## Key Markers Implemented
1. **CPU Activity**: Models dynamic frequency scaling drain.
2. **OLED APR**: Active Pixel Ratio tracking for Dark Mode optimization.
3. **Network Signal**: dBm-based power scaling for 5G modems.
4. **Thermal Throttling**: Monitors temperature to predict efficiency drops ($\eta$).

## Deployment to Mobile
To generate native iOS/Android projects:
```bash
npx cap init
npx cap add android
npx cap add ios
npm run build
npx cap copy
```
