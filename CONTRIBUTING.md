# 🤝 Contributing to Knowledge-Task OS (KT-OS)

We welcome contributions! However, since this is a **Premium Standard** and **Local-First** AI project, we have strict guidelines to maintain the integrity of the architecture.

## 🧠 Core Philosophy
1. **Local AI First:** We prioritize MLX and local models over Cloud APIs. If your PR introduces an external API dependency, it must be optional.
2. **Simplicity First:** No over-engineering. Surgical changes only.
3. **Shift-Left Security:** All code must pass the offline Aegis Gatekeeper checks.

## 🏗 Development Setup

This project uses **Turborepo** for managing multiple applications and packages.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/helgklaizar/KT-OS.git
   cd KT-OS
   ```
2. **Install dependencies:**
   ```bash
   npm install
   ```
3. **Start the development server:**
   ```bash
   npm run dev
   ```

## 📜 Pull Request Process
1. Create a new branch: `git checkout -b feature/your-feature-name`.
2. Ensure your code follows the Glassmorphism UI guidelines (for frontend) and PEP8 (for Python).
3. Run `npm test` locally.
4. Submit a PR with a detailed description of the changes.

> 🍏 **Part of the Mac AI Ecosystem Initiative**
> *This project is part of a large-scale initiative to build missing hardcore tools and extensions for AI development on Apple Silicon.*
