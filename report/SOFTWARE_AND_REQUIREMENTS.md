# Software & Environment Requirements

This document outlines the complete set of software, tools, and dependencies required to simulate the mathematical battery model and build/deploy the EcoDrain mobile application.

---

## 1. Mathematical Simulation (Backend)
The simulation core is built in Python to handle the high-fidelity 2RC-Thevenin differential equations.

### Required Software
- **Python 3.10+**: [Download here](https://www.python.org/downloads/)
- **Jupyter Notebook**: (Optional, for running `.ipynb` files)

### Python Packages
Install these via the terminal:
```bash
pip install numpy scipy matplotlib ipykernel
```
*Note: These are also listed in `code/requirements.txt`.*

---

## 2. Combined Mobile App (React + Capacitor)
The dashboard and mobile app are built using a modern web-to-native stack.

### Required Software
- **Node.js (LTS)**: Required for the React framework and package management. [Download here](https://nodejs.org/)
- **Android Studio**: Required to compile the app for Android and run the emulator. [Download here](https://developer.android.com/studio)
    - **SDK Components**: Android SDK, Android SDK Platform-Tools, and a Virtual Device (Emulator).
- **Java Development Kit (JDK) 17**: Required by Android Studio/Gradle. [Download here](https://adoptium.net/)

### Global CLI Tools
```bash
npm install -g npm
```

### Project Dependencies (React Stack)
Inside the `mobile_app` directory, the following are utilized:
- **React 18** & **Vite** (Build tool)
- **Framer Motion** (Physical animations)
- **Lucide React** (Vector icons)
- **Capacitor CLI** (Native bridge)

To install project-specific packages:
```bash
cd mobile_app
npm install
```

---

## 3. Build & Deployment Tools (Cross-Platform)

### Android Deployment
- **Capacitor Android**:
```bash
npm install @capacitor/android
```

### iOS Deployment (Optional - Requires macOS)
- **Xcode**: Required to build for iPhone.
- **CocoaPods**: Dependency manager for iOS.

---

## 4. Summary Checklist for New Setup
If setting up on a new machine, follow this order:

1.  **Install Base Runtimes**: Install Python (add to PATH) and Node.js.
2.  **Install IDEs**: Install Android Studio and run the "Setup Wizard" to download the SDK.
3.  **Simulation Check**:
    - `cd code`
    - `pip install -r requirements.txt`
    - `python simulation.py` (Verify plot generation)
4.  **Mobile App Check**:
    - `cd mobile_app`
    - `npm install`
    - `npm run build`
    - `npx cap sync`
    - `npx cap open android` (Launches Android Studio)

---

## 5. Directory Structure Reference
- `/code`: Mathematical engine (Python).
- `/mobile_app`: Main cross-platform application (React).
- `/android_applet`: Legacy static dashboard (HTML/JS).
- `/report`: LaTeX source and documentation.
