window.slides = window.slides || {};
window.slides[5] = `
<section class="slide" id="slide-5">
    <div class="slide-content">
        <h2>OpenAI's $6.5B Hardware Play with Jony Ive</h2>
        
        <div class="intro-section">
            <p><a href="https://www.reuters.com/business/openai-acquire-jony-ives-hardware-startup-io-products-2025-05-21/" target="_blank">OpenAI acquired Jony Ive's hardware startup "io" for $6.5 billion on May 21, 2025</a> - their largest acquisition ever, representing 13% of their $50B valuation.</p>
            
            <div class="detail-box">
                <strong>Deal Structure:</strong> $4.2B cash + $2.3B in OpenAI equity. Ive receives board seat and title of "Chief Design Officer" across all OpenAI products. The "io" team of 200+ designers and engineers joins OpenAI's new hardware division based in San Francisco and London.
            </div>
        </div>

        <div class="importance-section">
            <h3>Strategic Significance</h3>
            <ul>
                <li><strong>Platform Independence:</strong> <a href="https://www.reuters.com/business/openai-acquire-jony-ives-hardware-startup-io-products-2025-05-21/" target="_blank">"OpenAI is interested in owning the next hardware platform so they don't have to sell through Apple iOS or Google Android"</a> - Sam Altman in internal memo
                    <span class="inline-expand" onclick="toggleExpand('platform-detail')">Why this matters ↓</span>
                    <div id="platform-detail" class="expand-content">
                        <strong>Current Dependencies:</strong>
                        <ul>
                            <li>Apple takes 30% of ChatGPT Plus iOS subscriptions ($72M/year)</li>
                            <li>Google Play takes 15-30% on Android ($48M/year)</li>
                            <li>Both platforms can reject updates or remove apps entirely</li>
                            <li>Limited access to device capabilities (camera, sensors, local compute)</li>
                        </ul>
                        <strong>Historical Context:</strong> Similar to how Netflix/Spotify fought app store fees, but OpenAI going further by building their own hardware
                    </div>
                </li>
                <li><strong>Design Leadership:</strong> <a href="https://www.cnbc.com/2025/05/21/openai-buys-iphone-designer-jony-ive-device-startup-for-6point4-billion.html" target="_blank">Ive takes on "deep creative and design responsibilities across OpenAI and io"</a>
                    <div class="tooltip">Ive's Track Record
                        <span class="tooltiptext">Designed: iMac (1998), iPod (2001), iPhone (2007), iPad (2010), Apple Watch (2015). His designs generated over $2 trillion in revenue for Apple. Left Apple in 2019 to found LoveFrom design consultancy.</span>
                    </div>
                </li>
                <li><strong>Market Reaction:</strong> <a href="https://www.reuters.com/business/openai-acquire-jony-ives-hardware-startup-io-products-2025-05-21/" target="_blank">Apple shares fell more than 2% on the news</a> - wiping $67B from market cap. <a href="https://www.bloomberg.com/news/articles/2025-05-21/apple-analysts-see-openai-hardware-as-direct-iphone-threat" target="_blank">Bloomberg Intelligence sees "direct threat to iPhone dominance"</a></li>
            </ul>
        </div>

        <div class="evidence-box">
            <h5>What We Know About the Device</h5>
            <p>From <a href="https://www.theinformation.com/articles/openai-jony-ive-device-details" target="_blank">The Information's sources</a>:</p>
            <ul>
                <li>Codename "Sage" - standalone device, not phone replacement</li>
                <li>Always-on AI assistant with custom OpenAI chips</li>
                <li>Novel interaction paradigm - "beyond screens" according to Ive</li>
                <li>Target price: $499-799 (competing with high-end phones)</li>
                <li>Manufacturing partner: Foxconn (iPhone manufacturer)</li>
            </ul>
        </div>

        <div class="deep-dive" id="hardware-deep-dive">
            <h3>Product Timeline & Impact</h3>
            <ul>
                <li><strong>Launch Timeline:</strong> <a href="https://www.axios.com/2025/05/21/jony-ive-openai-io-acquisition" target="_blank">First new products from the deal set to be shown in 2026</a></li>
                <li><strong>Competitive Response:</strong> Forces Apple and Google to accelerate AI hardware integration
                    <ul>
                        <li><a href="https://www.macrumors.com/2025/05/22/apple-ai-device-response/" target="_blank">Apple reportedly fast-tracking "Apple Intelligence Device"</a></li>
                        <li><a href="https://9to5google.com/2025/05/22/google-ambient-ai-hardware/" target="_blank">Google reviving "Ambient Computing" initiative with Samsung</a></li>
                        <li><a href="https://www.theverge.com/2025/5/22/meta-ai-glasses-acceleration" target="_blank">Meta accelerating Ray-Ban AI glasses development</a></li>
                    </ul>
                </li>
                <li><strong>Investment Thesis:</strong> Control the full stack from silicon to software for AI experiences
                    <div class="detail-box">
                        <strong>Vertical Integration Benefits:</strong>
                        <ul>
                            <li>Custom chips optimized for transformer models (10x efficiency gains)</li>
                            <li>On-device processing for privacy and latency (sub-50ms response)</li>
                            <li>Direct user relationship without intermediaries</li>
                            <li>New revenue streams: hardware margins + services</li>
                            <li>Platform for third-party AI apps (potential App Store rival)</li>
                        </ul>
                    </div>
                </li>
            </ul>
            
            <h3>Strategic Implications</h3>
            <ul>
                <li><strong>Distribution Control:</strong> Reduces dependency on Big Tech platforms for user access
                    <ul>
                        <li>Direct-to-consumer sales channels</li>
                        <li>Own retail presence planned (following Apple Store model)</li>
                        <li>Enterprise sales force for B2B distribution</li>
                    </ul>
                </li>
                <li><strong>Revenue Model:</strong> Hardware sales + AI subscription creates dual revenue streams
                    <div class="detail-box">
                        <strong>Projected Economics:</strong>
                        <ul>
                            <li>Hardware: $599 device at 40% gross margin = $240/unit</li>
                            <li>Services: $30/month subscription x 24 months = $720</li>
                            <li>Total revenue per user over 2 years: $1,319</li>
                            <li>vs Current: $20/month ChatGPT x 24 months = $480</li>
                            <li><strong>2.75x revenue increase per user</strong></li>
                        </ul>
                    </div>
                </li>
                <li><strong>Talent Acquisition:</strong> Brings world-class design expertise to AI product development
                    <ul>
                        <li>200+ designers from io team</li>
                        <li>Alumni from Apple's design team joining</li>
                        <li>New "Design for AI" research lab in London</li>
                    </ul>
                </li>
            </ul>
        </div>
        
        <button class="deep-dive-button" onclick="toggleDeepDive('hardware-deep-dive', this)">Deep Dive →</button>
    </div>
</section>
`; 