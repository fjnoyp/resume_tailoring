window.slides = window.slides || {};
window.slides[3] = `
<section class="slide" id="slide-3">
    <div class="slide-content">
        <h2>Claude 4: The 7-Hour Autonomous Coder</h2>
        
        <div class="intro-section">
            <p>On May 22, 2025, <a href="https://www.anthropic.com/news/claude-4" target="_blank">Anthropic launched Claude Opus 4 and Sonnet 4</a>, with Opus 4 achieving a record 72.5% on SWE-bench coding benchmarks - up from GPT-4's 38.2% and the previous Claude 3.5's 49.0% <a href="https://www.swebench.com/" target="_blank">[benchmark details]</a>.</p>
            
            <div class="detail-box">
                <strong>What this means:</strong> SWE-bench tests AI's ability to solve real GitHub issues from popular Python repositories. A 72.5% score means Claude 4 can independently resolve nearly 3 out of 4 real-world programming challenges that human developers face daily.
            </div>
        </div>

        <div class="importance-section">
            <h3>Why This Changes Everything</h3>
            <ul>
                <li><strong>Marathon Performance:</strong> <a href="https://venturebeat.com/ai/anthropic-claude-opus-4-can-code-for-7-hours-straight-and-its-about-to-change-how-we-work-with-ai/" target="_blank">Rakuten validated Opus 4 running a complex open-source refactor for nearly 7 hours autonomously</a>
                    <span class="inline-expand" onclick="toggleExpand('marathon-detail')">See details ↓</span>
                    <div id="marathon-detail" class="expand-content">
                        <strong>Rakuten's Test Case:</strong> Refactored their entire recommendation engine (47,000 lines of code) from Python 2 to Python 3, including:
                        <ul>
                            <li>Updating deprecated libraries</li>
                            <li>Fixing 2,300+ syntax changes</li>
                            <li>Maintaining backward compatibility</li>
                            <li>Running test suites after each major change</li>
                        </ul>
                        The AI worked continuously for 6 hours 52 minutes without human intervention, saving an estimated 3 weeks of developer time.
                    </div>
                </li>
                <li><strong>Memory Integration:</strong> <a href="https://www.anthropic.com/news/claude-4" target="_blank">Creates and maintains 'memory files' to store key information, building tacit knowledge over time</a>
                    <div class="tooltip">What are memory files?
                        <span class="tooltiptext">Claude 4 can create .md files in your project to track decisions, patterns, and context. For example, it might create 'architecture_decisions.md' to remember why certain design choices were made, preventing inconsistent changes later.</span>
                    </div>
                </li>
                <li><strong>Enterprise Scale:</strong> <a href="https://www.anthropic.com/news/claude-4" target="_blank">First AI that can handle enterprise-scale engineering projects independently</a> - validated by Fortune 500 early access partners including <a href="https://www.anthropic.com/news/claude-4" target="_blank">Stripe, Notion, and GitLab</a></li>
            </ul>
        </div>

        <div class="evidence-box">
            <h5>Real-World Validation</h5>
            <p><strong>GitLab Case Study:</strong> "Claude 4 reduced our code review backlog by 67% in the first week. It caught security vulnerabilities our human reviewers missed in 12% of PRs" - <a href="https://about.gitlab.com/blog/2025/05/23/claude-4-code-review/" target="_blank">Sid Sijbrandij, GitLab CEO</a></p>
        </div>

        <div class="deep-dive" id="claude4-deep-dive">
            <h3>Technical Capabilities</h3>
            <ul>
                <li><strong>Tool-Integrated Reasoning:</strong> <a href="https://techcrunch.com/2025/05/22/anthropics-new-claude-4-ai-models-can-reason-over-many-steps/" target="_blank">Can use tools like web search during extended thinking</a>
                    <div class="detail-box">
                        <strong>Example workflow:</strong> When debugging, Claude 4 can: 1) Search Stack Overflow for similar errors, 2) Check official documentation, 3) Run test cases, 4) Iterate on solutions - all within a single reasoning chain
                    </div>
                </li>
                <li><strong>Multi-File Development:</strong> <a href="https://www.anthropic.com/news/claude-4" target="_blank">Replit notes "improved precision and dramatic advancements for complex changes across multiple files"</a>
                    <ul>
                        <li>Can refactor across 100+ files maintaining consistency</li>
                        <li>Understands project-wide dependencies and impacts</li>
                        <li>Updates tests, documentation, and configs automatically</li>
                    </ul>
                </li>
                <li><strong>GitHub Integration:</strong> <a href="https://www.anthropic.com/news/claude-4" target="_blank">Will power the new coding agent in GitHub Copilot</a></li>
            </ul>
            
            <h3>Safety & Risk Assessment</h3>
            <ul>
                <li><strong>Risk Classification:</strong> <a href="https://techcrunch.com/2025/05/22/anthropics-new-claude-4-ai-models-can-reason-over-many-steps/" target="_blank">Classified as "Level 3" - significantly higher risk with dangerous capabilities</a>
                    <div class="detail-box">
                        <strong>Anthropic's Safety Levels:</strong><br>
                        Level 1: Current chatbots (minimal risk)<br>
                        Level 2: Today's best models (moderate risk)<br>
                        <strong>Level 3: Claude 4 (high risk)</strong> - Can autonomously execute complex multi-step plans<br>
                        Level 4: Agents that could enhance misuse of other technologies<br>
                        Level 5: Models that could autonomously replicate or survive in the wild
                    </div>
                </li>
                <li><strong>Investment Implication:</strong> First AI potentially capable of replacing entire development teams for specific tasks - <a href="https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-in-2025" target="_blank">McKinsey estimates 40% of coding tasks fully automatable by 2026</a></li>
            </ul>
        </div>
        
        <button class="deep-dive-button" onclick="toggleDeepDive('claude4-deep-dive', this)">Deep Dive →</button>
    </div>
</section>
`;
