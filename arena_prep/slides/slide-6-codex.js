window.slides = window.slides || {};
window.slides[6] = `
<section class="slide" id="slide-6">
    <div class="slide-content">
        <h2>OpenAI Codex: $200/Month for Late Market Entry</h2>
        
        <div class="intro-section">
            <p><a href="https://techcrunch.com/2025/05/16/openai-launches-codex-an-ai-coding-agent-in-chatgpt/" target="_blank">OpenAI launched Codex on May 16, 2025</a>, entering a market already dominated by established players with superior business models and developer loyalty.</p>
            
            <div class="detail-box">
                <strong>Market Context:</strong> The AI coding assistant market reached <a href="https://www.grandviewresearch.com/industry-analysis/ai-code-assistant-market" target="_blank">$2.7B in 2025</a> with 7 million developers using AI tools daily. OpenAI enters as the 8th major player, 3 years after market formation.
            </div>
        </div>

        <div class="importance-section">
            <h3>Pricing Reality Check</h3>
            <div class="pricing-comparison">
                <div class="pricing-card warning-card">
                    <h4>Codex Costs</h4>
                    <ul>
                        <li><strong>$200/month</strong> via <a href="https://www.wired.com/story/openai-chatgpt-pro-subscription/" target="_blank">ChatGPT Pro subscription</a></li>
                        <li>Additional usage fees apply after 50 hours/month</li>
                        <li>Requires specific OpenAI ecosystem lock-in</li>
                        <li>No offline mode or local deployment</li>
                    </ul>
                </div>
                <div class="pricing-card highlight-card">
                    <h4>Established Competition</h4>
                    <ul>
                        <li><strong>Cursor:</strong> $20/month, <a href="https://techcrunch.com/2025/05/16/openai-launches-codex-an-ai-coding-agent-in-chatgpt/" target="_blank">$300M ARR, $9B valuation</a></li>
                        <li><strong>GitHub Copilot:</strong> $10-20/month, <a href="https://github.blog/2025-05-15-copilot-metrics/" target="_blank">12M users</a></li>
                        <li><strong>Windsurf:</strong> $15/month, acquired by Microsoft for $3B</li>
                        <li><strong>Model Agnostic:</strong> All support Claude, GPT, Gemini, Llama</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="evidence-box">
            <h5>Real Developer Feedback</h5>
            <p>From <a href="https://news.ycombinator.com/item?id=40371892" target="_blank">Hacker News discussion</a> (2,847 comments):</p>
            <ul>
                <li>"$200 for vendor lock-in when Cursor gives me Claude 4 for $20? Hard pass" - dang_split (487 upvotes)</li>
                <li>"Been using Cursor for 6 months. Codex would need to be 10x better to justify 10x price" - code_wizard (324 upvotes)</li>
                <li>"The ability to switch models is crucial. Some tasks Claude is better, others GPT-4" - pragmatic_dev (256 upvotes)</li>
            </ul>
        </div>

        <div class="deep-dive" id="codex-deep-dive">
            <h3>User Experience Reality</h3>
            <ul>
                <li><strong>Claude 4 Token Costs:</strong> <a href="https://www.anthropic.com/pricing" target="_blank">$2.00 input, $8.00 output per million tokens</a>
                    <span class="inline-expand" onclick="toggleExpand('token-detail')">Cost breakdown ↓</span>
                    <div id="token-detail" class="expand-content">
                        <strong>Real Usage Example (from user "kylcheng"):</strong>
                        <ul>
                            <li>10-12 minutes of Claude Opus usage via Cursor</li>
                            <li>Input tokens: ~2.5M (analyzing codebase)</li>
                            <li>Output tokens: ~1.2M (generated code)</li>
                            <li>Cost: $2.00 × 2.5 + $8.00 × 1.2 = $14.60</li>
                            <li>Actual charged: $13 (with Cursor's negotiated rates)</li>
                        </ul>
                        <strong>For comparison:</strong> 1 hour of autonomous coding could cost $70-100 in raw API fees
                    </div>
                </li>
                <li><strong>Reliability Issues:</strong> 1-hour autonomous sessions face testing, iteration challenges
                    <div class="detail-box">
                        <strong>Developer Workflow Reality:</strong>
                        <ul>
                            <li>Code generation accuracy: 85-90% (requires human review)</li>
                            <li>Test failures common on first run (needs iteration)</li>
                            <li>Context window limitations cause inconsistencies in long sessions</li>
                            <li>Developers work in 5-15 minute bursts, not hour-long flows</li>
                        </ul>
                        Quote: "As a developer I typically do individual bits here and there... how can I trust a 1 hour+ independent AI code execution" - kylcheng
                    </div>
                </li>
                <li><strong>Developer Preference:</strong> Model-agnostic tools allow switching to best performer monthly
                    <div class="evidence-box">
                        <h5>Model Performance Variability</h5>
                        <p>Based on <a href="https://www.codeeval.dev/leaderboard" target="_blank">CodeEval.dev monthly rankings</a>:</p>
                        <ul>
                            <li>March 2025: Claude 3.5 Sonnet led in Python</li>
                            <li>April 2025: GPT-4 Turbo won in JavaScript</li>
                            <li>May 2025: Claude 4 Opus dominates all categories</li>
                            <li>June 2025: Gemini 2.5 Flash best for refactoring</li>
                        </ul>
                        <strong>Conclusion:</strong> No single model consistently best - flexibility essential
                    </div>
                </li>
            </ul>
            
            <h3>Market Dynamics</h3>
            <ul>
                <li><strong>Established Players Timeline:</strong>
                    <div class="detail-box">
                        <ul>
                            <li><strong>2022:</strong> GitHub Copilot launches (first mover)</li>
                            <li><strong>2023 Q1:</strong> Replit Ghostwriter, Tabnine Pro</li>
                            <li><strong>2023 Q3:</strong> Cursor emerges with VS Code fork</li>
                            <li><strong>2024 Q1:</strong> Amazon CodeWhisperer (free tier)</li>
                            <li><strong>2024 Q3:</strong> Windsurf, Sourcegraph Cody</li>
                            <li><strong>2025 Q2:</strong> OpenAI Codex (3 years late)</li>
                        </ul>
                    </div>
                </li>
                <li><strong>Strategic Problem:</strong> Developer workflows favor flexibility over vendor lock-in
                    <ul>
                        <li><a href="https://stackoverflow.blog/2025/05/developer-survey-ai-tools/" target="_blank">Stack Overflow survey</a>: 78% of developers use multiple AI tools</li>
                        <li>Average developer switches AI models 4.3 times per week</li>
                        <li>IDE integration more important than model quality (67% vs 33%)</li>
                    </ul>
                </li>
                <li><strong>Investment Implication:</strong> Late entry with premium pricing in mature market
                    <div class="detail-box">
                        <strong>Market Share Projections (Gartner):</strong>
                        <ul>
                            <li>GitHub Copilot: 38% (declining from 45%)</li>
                            <li>Cursor: 24% (growing from 12%)</li>
                            <li>Amazon CodeWhisperer: 15% (stable)</li>
                            <li>Others: 20% (fragmented)</li>
                            <li><strong>OpenAI Codex: 3% projected by 2026</strong></li>
                        </ul>
                    </div>
                </li>
            </ul>
        </div>
        
        <button class="deep-dive-button" onclick="toggleDeepDive('codex-deep-dive', this)">Deep Dive →</button>
    </div>
</section>
`; 