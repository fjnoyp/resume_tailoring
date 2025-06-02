# Resume Tailoring Application - Technical Specification

## Product Vision

### Core Goals
1. **Ease of use** - Intuitive workflow for resume tailoring
2. **Clarity** - Transparent AI reasoning and recommendations  
3. **Trust** - Reliable, consistent results users can depend on

### Core Hypothesis
Users want an easy-to-use system they can trust to tailor their resume effectively for specific job applications.

## Architecture Overview

### Core Features
1. **User Profile Management** - Global view of all candidate information
2. **Job Tailoring** - Per-job view of tailored resumes and analysis

### Data Architecture

#### PostgreSQL Schema
```sql
-- Users table
CREATE TABLE users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE,
  full_resume text,
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

-- Jobs table (contains ALL job-related content)
CREATE TABLE jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id),
  
  -- Input content
  job_description text,
  
  -- AI-generated content (streaming outputs)
  company_strategy text,
  recruiter_feedback text,
  tailored_resume text,
  tailored_cv text,
  
  -- Metadata
  confidence_score decimal,
  status text DEFAULT 'processing',
  job_title text,
  company_name text,
  
  created_at timestamp DEFAULT now(),
  updated_at timestamp DEFAULT now()
);

-- NOTE - you will likely need to create a ai chat messages table (can copy from Seren project) for the information collection step - make sure they have a parent job id 
```

#### Supabase Storage Structure
```
userId/
  profile_photo.jpg
  jobId/
    final_resume.pdf
    final_cover_letter.pdf
```

## API Specification

### Core Endpoints

#### 1. ResumeRewrite API
- **Inputs**: `userId`, `jobId`
- **Reads**: Full Resume, Job Description
- **Outputs (Streamed)**:
  - Thought Tokens
  - Company Strategy
  - Recruiter Feedback  
  - Tailored Resume (or MissingInformation request)
  - Tailored Cover Letter

#### 2. InfoCollection API  
- **Inputs**: `userId`, `MissingInformation`
- **Outputs (Streamed)**:
  - AI Messages
  - Updated Full Resume
  - Final Collected Info

#### 3. UpdateUserProfile API
- **Inputs**: Full Resume, New Info
- **Outputs (Streamed)**: Updated Full Resume

### Technical Infrastructure
- **Streaming**: LangGraph API with real-time text streaming
- **State Management**: Riverpod providers
- **Real-time Updates**: Supabase PostgreSQL subscriptions

## User Interface Specification

### Design Philosophy
Follow LinkedIn-style navigation with:
- Top navigation bar with page icons
- Left sidebar for lists (20% width)
- Main content area for details (80% width)

### Page Specifications

#### 1. Home Page
**States:**
- **No Resume**: "Please upload your LinkedIn or Resume to get started" → Button to Profile Page
- **Has Resume**: Welcome message + future statistics overview

#### 2. User Profile Page
**Purpose**: Display and update the user's master resume

**Layout:**
```
┌─ User Profile ──────────────────────────┐
│                                         │
│ ┌─ Input Data Section ─────────────────┐ │
│ │ LinkedIn URL: [input] [Read]         │ │
│ │ [Upload File Button]                 │ │
│ │ Add Information: [expandable text]   │ │
│ │                 [Process]            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ ┌─ Full Resume Display ────────────────┐ │
│ │ [Master resume content]              │ │
│ │ [Future: editing capabilities]       │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Behavior:**
- Loading states with overlay during AI processing
- Stream updates to resume display area
- Lock input section during processing

#### 3. Jobs List Page
**Layout:**
```
┌─ Jobs ──────────────────────────────────┐
│ ┌─ Job List ─┐ ┌─ Job Details ─────────┐ │
│ │ □ Job 1    │ │ [Selected job content] │ │
│ │ ■ Job 2    │ │                       │ │
│ │ □ Job 3    │ │                       │ │
│ │            │ │                       │ │
│ └───────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────┘
```

**States:**
- **No User Profile**: Warning with link to Profile Page
- **Job Selected**: Show Job Details Page in right panel

#### 4. Job Details Page
**Purpose**: Display tailored resume and analysis steps

**Content Sections** (as scrollable markdown - https://pub.dev/packages/markdown_widget):
1. **Company Strategy**
2. **Recruiter Feedback** 
3. **Tailored Resume**
4. **Tailored Cover Letter**
5. **Information Collection** (conditional)

**States:**
- **No Job Description**: Input prompt → Processing state
- **Processing**: Streaming markdown sections with real-time updates
- **Complete**: Static display with edit/download options

**Information Collection Widget:**
- Inline chat interface (borrowed from SerenAI)
- Always-visible "Finish" button to skip/end conversation
- Triggered when additional user information needed

## Implementation Notes

### State Management Architecture

#### High-Level Goals
1. **Word-by-word streaming** from LangGraph → immediate UI updates
2. **Smart DB persistence** - save complete sections, not every word
3. **State recovery** - reload from DB if stream fails
4. **Real-time sync** across devices/tabs

#### Core Challenge: Stream vs Persistence
- **LangGraph**: Streams individual words/tokens
- **UI**: Needs immediate word-by-word display  
- **PostgreSQL**: Should store complete sections, not individual words

#### Solution: Buffer + Batch Strategy

```dart
@riverpod
class JobStreamingState extends _$JobStreamingState {
  final Map<String, StringBuffer> _buffers = {};
  Timer? _saveTimer;

  @override
  JobData build(String jobId) {
    // Load initial state from DB
    return ref.watch(jobFromDbProvider(jobId)).value ?? JobData.empty();
  }

  void handleStreamToken(String section, String token) {
    // 1. Update UI immediately (word-by-word)
    _buffers[section] ??= StringBuffer(state.getSection(section));
    _buffers[section]!.write(token);
    
    state = state.updateSection(section, _buffers[section]!.toString());
    
    // 2. Debounced save to DB (every 2 seconds or section complete)
    _scheduleDbSave();
  }

  void _scheduleDbSave() {
    _saveTimer?.cancel();
    _saveTimer = Timer(Duration(seconds: 2), () => _saveToDb());
  }

  void _saveToDb() {
    ref.read(jobDbProvider).updateJob(state.id, _buffers);
  }
}
```

#### Data Flow
```
LangGraph → word → Buffer → UI (instant)
              ↓
         Timer → PostgreSQL (batched)
```

#### Benefits
- ✅ **Instant UI updates** (every word)
- ✅ **Efficient DB usage** (batched saves)  
- ✅ **Recovery support** (reload from DB)
- ✅ **Real-time sync** (PostgreSQL subscriptions)

### State Management
- **Riverpod**: Primary state management
- **PostgreSQL Subscriptions**: Real-time data synchronization
- **Streaming Integration**: LangGraph API streaming to Riverpod providers

### Development Priorities
1. Copy/adapt existing Supabase setup from SerenAI project for Postgres Tables 
2. Update Langgraph Cloud to store into Postgres instead of Storage 
3. Build/check streaming API integration with Langgraph Cloud
4. Create proper Riverpod providers in Flutter for interacting with Supabase Postgres Tables 

### Future Considerations
- Section navigation within job details
- Resume editing capabilities
- Advanced analytics and insights
- Vector search for job/resume matching

---

## AI Implementation Guide

### 🤖 **How to Use AI to Build This Specification**

#### **1. Start with Architecture Design Prompts**
```
"Based on this technical specification [attach this document], help me design the Flutter project structure for a resume tailoring app with:
- Riverpod state management
- Supabase PostgreSQL backend  
- LangGraph streaming API integration
- The specific screens and providers mentioned

Show me the folder structure and key files I need to create."
```

#### **2. Implement Database Schema First**
```
"I need to implement this PostgreSQL schema [paste schema from document]. Help me:
1. Create the Supabase migration files
2. Add proper indexes for performance
3. Set up Row Level Security policies
4. Create the chat_messages table mentioned in the notes

Show me the exact SQL commands."
```

#### **3. Build Core Providers with Context**
```
"I need to implement the JobStreamingState provider described in this spec [paste state management section]. The key requirements are:
- Word-by-word streaming from LangGraph
- Buffer strategy with debounced PostgreSQL saves  
- Recovery from database if stream fails

Help me implement this with proper error handling and memory cleanup."
```

#### **4. Create UI Components Step-by-Step**
```
"Based on this UI specification [paste Jobs List section], help me create:
1. The Jobs List page with 20/80 split layout
2. Job card widgets for the left sidebar
3. Job details page for the right panel
4. Proper navigation state management

Use the markdown_widget package mentioned for displaying AI responses."
```

#### **5. Integrate LangGraph Streaming**
```
"I need to connect to LangGraph Cloud API for streaming resume generation. The API should:
- Stream company_strategy, recruiter_feedback, tailored_resume sections
- Handle missing_information requests for additional user data
- Return word-by-word tokens for real-time UI updates

Help me implement the service class and error handling."
```

#### **6. Test Each Component**
```
"I just implemented [specific component]. Help me write tests that verify:
- The exact behavior described in the specification
- Error cases and edge conditions
- Integration with other components
- Performance with streaming data

Show me unit tests and widget tests."
```

### 💡 **Effective Prompting Strategies**

#### **Be Specification-Driven**
Always reference this document: *"According to the specification in next_steps_3.md..."*

#### **Request Implementation Validation**
*"Does this implementation match the requirements in the specification? What's missing?"*

#### **Ask for Architecture Reviews**
*"Review my provider structure against the state management architecture described in the spec."*

#### **Demand Concrete Examples**
*"Show me the exact code for the handleStreamToken method described in the buffer strategy."*

#### **Focus on Integration Points**
*"How do I connect the JobStreamingState provider to the Job Details Page UI as specified?"*

### 🎯 **Implementation Order**

1. **PostgreSQL Schema** → Test with Supabase
2. **Basic Riverpod Providers** → Test CRUD operations  
3. **UI Screens (Static)** → Test navigation flow
4. **LangGraph Integration** → Test streaming
5. **State Management** → Test buffer strategy
6. **Polish & Error Handling** → Test edge cases

**Key Principle**: Implement each specification section completely before moving to the next. Use AI to validate against the original requirements at each step.

