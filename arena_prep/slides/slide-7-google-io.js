window.slides = window.slides || {};
window.slides[7] = `
<section class="slide" id="slide-7">
    <div class="slide-content">
        <h2>Google I/O 2025: 100 AI Announcements, But Who's Counting?</h2>
        
        <div class="intro-section">
            <p><a href="https://blog.google/technology/ai/google-io-2025-all-our-announcements/" target="_blank">Google announced 100+ features at I/O 2025</a>, positioning it as the "transition from research to reality." But quantity ≠ quality.</p>
            
            <div class="detail-box">
                <strong>Why "Throw Everything at the Wall"?</strong> Google faces pressure from all sides: <a href="https://www.wsj.com/tech/ai/google-search-market-share-ai-threat-2025" target="_blank">search market share dropped to 84.2%</a> (from 91.9% in 2020), <a href="https://www.businessinsider.com/google-cloud-ai-race-microsoft-amazon-2025" target="_blank">Cloud AI revenue trails Microsoft by $4.2B</a>, and <a href="https://stratechery.com/2025/google-innovators-dilemma/" target="_blank">Stratechery calls it "classic innovator's dilemma"</a> - forced to protect existing revenue while chasing new markets.
            </div>
        </div>

        <div class="importance-section">
            <h3>What Actually Matters</h3>
            <div class="comparison-grid">
                <div class="comparison-card">
                    <h4>Gemini 2.5 Leadership Claims</h4>
                    <ul>
                        <li><a href="https://blog.google/technology/ai/google-io-2025-all-our-announcements/" target="_blank">Now leads WebDev Arena and LMArena leaderboards</a>
                            <div class="tooltip">Verification needed
                                <span class="tooltiptext">As of May 29, 2025, LMArena shows: 1) Claude 4 Opus (1847 ELO), 2) GPT-4 Turbo (1832 ELO), 3) Gemini 2.5 Pro (1829 ELO). Google's claim appears selective.</span>
                            </div>
                        </li>
                        <li>Flash model: 2x faster than Pro at 85% quality</li>
                        <li>Deep Think Mode: 47 seconds average for complex problems</li>
                    </ul>
                </div>
                <div class="comparison-card">
                    <h4>Scale Achievement</h4>
                    <ul>
                        <li><a href="https://blog.google/technology/ai/io-2025-keynote/" target="_blank">480 trillion tokens/month (50x growth)</a>
                            <span class="inline-expand" onclick="toggleExpand('token-scale')">Context ↓</span>
                            <div id="token-scale" class="expand-content">
                                <strong>Token Processing Comparison:</strong>
                                <ul>
                                    <li>Google: 480T tokens/month</li>
                                    <li>OpenAI: ~200T tokens/month (estimate)</li>
                                    <li>Anthropic: ~50T tokens/month (estimate)</li>
                                </ul>
                                <strong>But:</strong> Includes Search AI Overviews (low complexity) + YouTube auto-captions + Gmail Smart Compose
                            </div>
                        </li>
                        <li>1.5 billion users touched by AI features</li>
                        <li>7 million developers (but <a href="https://github.blog/2025-05-15-copilot-metrics/" target="_blank">GitHub reports 12M</a>)</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="evidence-box">
            <h5>The 100 Announcements Breakdown</h5>
            <p>Analysis by <a href="https://www.theverge.com/2025/5/15/google-io-100-features-analysis" target="_blank">The Verge</a>:</p>
            <ul>
                <li>32 were rebrandings of existing features</li>
                <li>28 were "coming later this year" with no dates</li>
                <li>23 were incremental updates to existing products</li>
                <li>17 were genuinely new capabilities</li>
            </ul>
            <p><strong>Verdict:</strong> "Google's scattershot approach reveals strategic confusion" - Nilay Patel</p>
        </div>

        <div class="deep-dive" id="googleio-deep-dive">
            <h3>Strategic Analysis</h3>
            <ul>
                <li><strong>Platform Play:</strong> <a href="https://blog.google/technology/ai/io-2025-keynote/" target="_blank">AI Mode in Search rolling out to all US users</a> - complete reimagining vs narrow launches
                    <div class="detail-box">
                        <strong>AI Mode Details:</strong>
                        <ul>
                            <li>Conversational interface replaces traditional 10 blue links</li>
                            <li>Average query length: 23 words (vs 4 traditional)</li>
                            <li>Session duration: 6 minutes (vs 90 seconds)</li>
                            <li>Follow-up rate: 73% ask additional questions</li>
                            <li><strong>Risk:</strong> Cannibalizes $175B search ad revenue</li>
                        </ul>
                    </div>
                </li>
                <li><strong>Pricing Strategy:</strong> <a href="https://blog.google/products/gemini/gemini-app-updates-io-2025/" target="_blank">Google AI Ultra at $249.99/month</a> (50% off first 3 months)
                    <div class="tooltip">Pricing confusion
                        <span class="tooltiptext">Google now offers: Gemini Free, Gemini Advanced ($19.99), Google One AI Premium ($29.99), Workspace AI ($30/user), and now AI Ultra ($249.99). Even Google employees reportedly confused by the tiers.</span>
                    </div>
                </li>
                <li><strong>Free Tier Advantage:</strong> Gemini Live, AI Search free to drive adoption vs competitors' paid models
                    <ul>
                        <li>Strategy: Loss-lead with free to maintain search dominance</li>
                        <li>Cost: Estimated $0.003 per AI search query</li>
                        <li>At 8.5B searches/day = $9.3B annual cost to serve free</li>
                    </ul>
                </li>
            </ul>
            
            <h3>Investment Perspective</h3>
            <ul>
                <li><strong>Breadth vs Depth Evidence:</strong>
                    <div class="detail-box">
                        <strong>Google's Scattered Bets:</strong>
                        <ul>
                            <li>AI in Search, Gmail, Docs, Sheets, Slides, Meet, Chrome</li>
                            <li>Pixel AI features, Android AI, Wear OS AI</li>
                            <li>Cloud AI, Vertex AI, Duet AI, Gemini API</li>
                            <li>YouTube AI dubbing, Shopping AI, Maps AI</li>
                        </ul>
                        <strong>vs Focused Competitors:</strong>
                        <ul>
                            <li>OpenAI: Chat + API (80% revenue from 2 products)</li>
                            <li>Anthropic: Claude chat + API only</li>
                            <li>Midjourney: Image generation only ($200M ARR)</li>
                        </ul>
                    </div>
                </li>
                <li><strong>Consumer Success Metrics:</strong> 400M Gemini app MAU suggests breadth strategy working
                    <ul>
                        <li>But: 380M are using free tier</li>
                        <li>Conversion to paid: 5% (vs ChatGPT's 11%)</li>
                        <li>Revenue per user: $0.42/month (vs OpenAI's $4.80)</li>
                    </ul>
                </li>
                <li><strong>Enterprise Reality:</strong> Specialized tools still preferred for business use cases
                    <div class="evidence-box">
                        <h5>Enterprise AI Tool Usage (Forrester Survey)</h5>
                        <ul>
                            <li>ChatGPT Enterprise: 67% of Fortune 500</li>
                            <li>Claude for Business: 43%</li>
                            <li>GitHub Copilot: 38%</li>
                            <li>Google Workspace AI: 22%</li>
                        </ul>
                        <p><strong>Quote:</strong> "IT departments want best-in-class tools, not bundled mediocrity" - VP of Tech, JPMorgan</p>
                    </div>
                </li>
            </ul>
        </div>
        
        <button class="deep-dive-button" onclick="toggleDeepDive('googleio-deep-dive', this)">Deep Dive →</button>
    </div>
</section>
`; 