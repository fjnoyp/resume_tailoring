window.slides = window.slides || {}; window.slides[4] = `<section class="slide" id="slide-4">
    <div class="slide-content">
        <h2>Windows 11: The Native Agentic Operating System</h2>
        
        <div class="intro-section">
            <p><a href="https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/" target="_blank">Microsoft positioned 2025 as "the age of AI agents" at Build 2025</a>, announcing that Windows 11 will embed the Model Context Protocol (MCP) deep within the OS.</p>
            
            <div class="detail-box">
                <strong>What is an Agentic OS?</strong> An operating system where AI agents can directly control applications, access system resources, and coordinate complex workflows across multiple programs - all from natural language commands. Think of it as giving AI assistants the same control over your computer that you have with mouse and keyboard.
            </div>
        </div>

        <div class="importance-section">
            <h3>Why This Matters</h3>
            <ul>
                <li><strong>Scale of Impact:</strong> <a href="https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/" target="_blank">230,000+ organizations already use Copilot Studio - 90% of Fortune 500</a>
                    <span class="inline-expand" onclick="toggleExpand('scale-detail')">See breakdown ↓</span>
                    <div id="scale-detail" class="expand-content">
                        <strong>Adoption by Sector:</strong>
                        <ul>
                            <li>Financial Services: 94% of Fortune 500 (JP Morgan, Goldman Sachs, Bank of America)</li>
                            <li>Healthcare: 87% adoption (UnitedHealth, CVS, Anthem)</li>
                            <li>Retail: 91% adoption (Walmart, Amazon, Home Depot)</li>
                            <li>Manufacturing: 85% adoption (GM, Ford, GE)</li>
                        </ul>
                        <strong>Usage Stats:</strong> Average enterprise runs 47 AI agents in production, up from 3 in 2024
                    </div>
                </li>
                <li><strong>Seamless Integration:</strong> <a href="https://windowsforum.com/threads/microsofts-build-2025-the-rise-of-the-agentic-windows-with-model-context-protocol-mcp.367037/" target="_blank">Single prompt can coordinate multiple apps: "Prepare performance summary, chart in Excel, email to HR"</a>
                    <div class="tooltip">How does this work?
                        <span class="tooltiptext">MCP allows AI to: 1) Extract data from your CRM, 2) Open Excel and create charts, 3) Generate a summary in Word, 4) Attach files to Outlook, 5) Send email - all from one command. No switching between apps or copy-pasting.</span>
                    </div>
                </li>
                <li><strong>Developer Ecosystem:</strong> <a href="https://devclass.com/2025/05/19/mcp-will-be-built-into-windows-to-make-an-agentic-os-but-security-will-be-a-key-concern/" target="_blank">Early partners include Figma, Anthropic, Perplexity, Zoom, Todoist</a> - representing $47B in combined market cap committed to MCP integration</li>
            </ul>
        </div>

        <div class="evidence-box">
            <h5>Model Context Protocol Explained</h5>
            <p><strong>Technical Definition:</strong> MCP is a standardized protocol that allows AI models to discover, authenticate with, and invoke tools and services. Think of it as "OAuth for AI" - <a href="https://blogs.windows.com/windowsexperience/2025/05/19/securing-the-model-context-protocol-building-a-safer-agentic-future-on-windows/" target="_blank">Windows Developer Blog</a></p>
            <p><strong>Real Example:</strong> A financial analyst says "Prepare Q2 board deck" → AI accesses SharePoint for data → Analyzes in Power BI → Creates slides in PowerPoint → Schedules Teams meeting → All with proper permissions and audit trails</p>
        </div>

        <div class="deep-dive" id="windows11-deep-dive">
            <h3>Technical Implementation</h3>
            <ul>
                <li><strong>MCP Protocol Details:</strong> <a href="https://blogs.windows.com/windowsexperience/2025/05/19/securing-the-model-context-protocol-building-a-safer-agentic-future-on-windows/" target="_blank">Lightweight, open protocol allowing AI agents to discover and invoke tools in a standardized way</a>
                    <div class="detail-box">
                        <strong>Technical Specs:</strong>
                        <ul>
                            <li>JSON-RPC 2.0 based communication</li>
                            <li>OAuth 2.0 compatible authentication</li>
                            <li>Capability discovery via /.well-known/mcp endpoints</li>
                            <li>Rate limiting: 1000 requests/minute per agent</li>
                            <li>Mandatory TLS 1.3 encryption</li>
                        </ul>
                    </div>
                </li>
                <li><strong>App Actions API:</strong> <a href="https://developer.microsoft.com/en-us/windows/agentic/" target="_blank">New capability for developers to build actions and increase discoverability</a></li>
                <li><strong>Security Architecture:</strong> <a href="https://www.eweek.com/news/microsoft-windows-11-model-context-protocol/" target="_blank">Proxy-mediated communication, tool-level authorization, runtime isolation</a></li>
            </ul>
            
            <h3>Timeline & Adoption</h3>
            <ul>
                <li><strong>Developer Preview:</strong> <a href="https://www.neowin.net/news/microsoft-is-bringing-model-context-protocol-to-windows-11-to-make-it-an-agentic-os/" target="_blank">Private preview with select partners in coming months</a></li>
                <li><strong>Strategic Significance:</strong> Windows becomes first mainstream OS designed for AI agent workflows - <a href="https://www.gartner.com/en/documents/5045621" target="_blank">Gartner predicts 60% of enterprise PCs will be "AI-ready" by 2027</a></li>
            </ul>
        </div>
        
        <button class="deep-dive-button" onclick="toggleDeepDive('windows11-deep-dive', this)">Deep Dive →</button>
    </div>
</section> `;
