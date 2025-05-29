# Claude 4 Autonomous Coding Demo
*Duration: 5-7 minutes*

## Pre-Meeting Setup (30 minutes before)

### Required Tools
- Cursor IDE with Claude Opus 4 enabled
- Sample React codebase (20+ components using class-based architecture)
- Terminal window for time tracking
- Memory file viewer (VS Code or similar)

### Preparation Steps
1. Clone demo repository: `git clone https://github.com/demo/react-legacy-app`
2. Open in Cursor IDE
3. Create empty `memory.md` file in project root
4. Start screen recording software as backup

## Live Demo Flow

### 1. Introduction (30 seconds)
"I'm going to show you Claude 4 working autonomously on a real codebase refactoring task - something that would typically take a developer 1-2 days."

### 2. Show Initial State (1 minute)
- Display file tree showing 20+ React components
- Open 2-3 class components to show legacy code
- Point out: "These are using outdated patterns from 2018"

### 3. Give Claude the Task (1 minute)
**Prompt to use:**
```
Please refactor all React class components in the /src/components directory to use functional components with hooks. 

As you work:
1. Create and maintain a memory.md file to track your progress
2. Test each component after refactoring
3. Update any parent components that import these
4. Fix any TypeScript errors that arise

Work autonomously and let me know when complete.
```

### 4. Show Claude Working (3 minutes)
- Show Claude creating memory.md file
- Display it updating the memory file with progress:
  ```markdown
  ## Refactoring Progress
  - [x] Header.jsx - Converted to functional component
  - [x] Navigation.jsx - Added useState for menu state
  - [ ] UserProfile.jsx - In progress...
  ```
- Show multiple files being edited simultaneously
- Point out the terminal showing elapsed time
- Highlight: "Notice it's handling state management, lifecycle methods, and maintaining all functionality"

### 5. Results & Impact (1 minute)
- Show final statistics: "23 components refactored in X minutes"
- Open a before/after comparison
- Run the app to show everything still works
- Emphasize: "This ran continuously without human intervention"

## Key Talking Points

- **Marathon capability**: "Previous models would lose context after 5-10 files"
- **Memory persistence**: "It's building knowledge about your codebase as it works"
- **Error handling**: "Watch how it catches and fixes its own mistakes"
- **Cost efficiency**: "$200/month vs $200k/year for developers doing this work"

## Backup Plan

If live demo fails:
1. Show pre-recorded video (keep on desktop)
2. Walk through before/after code samples
3. Show memory.md file progression
4. Display time-lapse statistics

## Common Questions & Answers

**Q: How accurate is the refactoring?**
A: In testing, Claude 4 maintains 95%+ functionality with proper testing

**Q: Can it handle complex business logic?**
A: Yes - show example of complex state management being converted

**Q: What about code review?**
A: Still recommended, but the quality is senior-developer level

## Post-Demo
- Offer to share the refactored codebase
- Mention other use cases: bug fixing, documentation, test writing
- Reference the safety classification (Level 3) if asked 