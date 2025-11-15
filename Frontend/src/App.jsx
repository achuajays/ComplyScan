import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [scanning, setScanning] = useState(false)
  const [results, setResults] = useState(null)
  const [complianceResults, setComplianceResults] = useState(null)
  const [error, setError] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)

  const handleScan = async () => {
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    // Clear all previous results when starting a new scan
    setScanning(true)
    setError(null)
    setResults(null)
    setComplianceResults(null)
    setAnalyzing(false)

    try {
      // Validate URL format
      let targetUrl = url.trim()
      if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
        targetUrl = 'https://' + targetUrl
      }

      // Try multiple CORS proxies as fallback
      const proxies = [
        {
          url: `https://api.allorigins.win/get?url=${encodeURIComponent(targetUrl)}`,
          type: 'json' // Returns JSON with contents field
        },
        {
          url: `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(targetUrl)}`,
          type: 'html' // Returns HTML directly
        },
        {
          url: `https://thingproxy.freeboard.io/fetch/${targetUrl}`,
          type: 'html' // Returns HTML directly
        }
      ]

      let htmlContent = null
      let lastError = null

      // Try each proxy until one works
      for (const proxy of proxies) {
        try {
          // Add timeout to fetch request
          const controller = new AbortController()
          const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 second timeout

          const response = await fetch(proxy.url, {
            method: 'GET',
            headers: {
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            },
            signal: controller.signal
          })

          clearTimeout(timeoutId)

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`)
          }

          if (proxy.type === 'json') {
            // Proxy returns JSON with contents field
            const data = await response.json()
            htmlContent = data.contents || data.content || data.data
          } else {
            // Proxy returns HTML directly
            htmlContent = await response.text()
          }

          if (htmlContent && htmlContent.trim().length > 0) {
            break // Success, exit the loop
          }
        } catch (err) {
          if (err.name === 'AbortError') {
            lastError = new Error('Request timeout - the proxy server took too long to respond')
          } else {
            lastError = err
          }
          console.warn(`Proxy failed: ${proxy.url}`, err)
          continue // Try next proxy
        }
      }

      if (!htmlContent || htmlContent.trim().length === 0) {
        throw new Error(
          lastError?.message || 'Failed to fetch page content. All proxy servers failed. ' +
          'This might be due to network issues or the website blocking proxy requests.'
        )
      }

      // Create a blob URL with the HTML content to load in same-origin iframe
      const blob = new Blob([htmlContent], { type: 'text/html' })
      const blobUrl = URL.createObjectURL(blob)

      // Create iframe to load the blob URL (same-origin, so no CORS issues)
      const iframe = document.createElement('iframe')
      iframe.style.position = 'absolute'
      iframe.style.left = '-9999px'
      iframe.style.width = '1px'
      iframe.style.height = '1px'
      iframe.style.border = 'none'
      iframe.style.visibility = 'hidden'
      iframe.src = blobUrl
      document.body.appendChild(iframe)

      // Wait for iframe to load
      await new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new Error('Timeout: Page took too long to load'))
        }, 30000)

        iframe.onload = () => {
          clearTimeout(timeout)
          resolve()
        }

        iframe.onerror = () => {
          clearTimeout(timeout)
          reject(new Error('Failed to load the page content'))
        }
      })

      // Now we can access the iframe document (same-origin)
      const iframeWindow = iframe.contentWindow
      const iframeDocument = iframe.contentDocument || iframeWindow.document

      // Update base URL and fix relative links to work with the original URL
      const baseTag = iframeDocument.createElement('base')
      baseTag.href = targetUrl
      iframeDocument.head.insertBefore(baseTag, iframeDocument.head.firstChild)

      // Load axe-core script
      const script = iframeDocument.createElement('script')
      script.src = 'https://unpkg.com/axe-core@4.9.0/axe.min.js'
      
      await new Promise((resolve, reject) => {
        script.onload = resolve
        script.onerror = () => reject(new Error('Failed to load axe-core'))
        iframeDocument.head.appendChild(script)
      })

      // Wait a bit for any dynamic content to load
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Run the accessibility scan
      const scanResults = await iframeWindow.axe.run(iframeDocument, {
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice']
        }
      })

      // Clean up
      URL.revokeObjectURL(blobUrl)
      document.body.removeChild(iframe)

      setResults(scanResults)

      // Send to backend for compliance analysis
      await analyzeCompliance(scanResults, targetUrl)
    } catch (err) {
      setError(err.message || 'An error occurred during the scan')
      console.error('Scan error:', err)
    } finally {
      setScanning(false)
    }
  }

  const analyzeCompliance = async (axeResults, targetUrl) => {
    setAnalyzing(true)
    try {
      // Use environment variable for API URL, default to localhost for development
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          violations: axeResults.violations || [],
          incomplete: axeResults.incomplete || [],
          passes: axeResults.passes || [],
          url: targetUrl
        })
      })

      if (!response.ok) {
        throw new Error(`Backend analysis failed: ${response.statusText}`)
      }

      const complianceData = await response.json()
      setComplianceResults(complianceData)
    } catch (err) {
      console.error('Compliance analysis error:', err)
      // Don't show error to user, just log it - frontend scan still works
    } finally {
      setAnalyzing(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !scanning) {
      handleScan()
    }
  }

  return (
    <div className="app-container">
      <div className="scanner-card">
        <h1>Accessibility Scanner</h1>
        <p className="subtitle">Scan any website for accessibility issues using axe-core</p>
        
        <div className="input-group">
          <input
            type="text"
            value={url}
            onChange={(e) => {
              const newUrl = e.target.value
              // Clear results immediately when user types (if there are any results)
              if (results || complianceResults) {
                setResults(null)
                setComplianceResults(null)
                setError(null)
                setAnalyzing(false)
              }
              setUrl(newUrl)
            }}
            onKeyPress={handleKeyPress}
            placeholder="Enter URL (e.g., https://example.com)"
            className="url-input"
            disabled={scanning}
          />
          <button
            onClick={handleScan}
            disabled={scanning || !url.trim()}
            className="scan-button"
          >
            {scanning ? 'Scanning...' : 'Scan'}
          </button>
        </div>

        {analyzing && (
          <div className="analyzing-message">
            <p>Analyzing compliance and generating AI recommendations...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
            <p className="error-hint">
              <strong>Troubleshooting tips:</strong>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', textAlign: 'left' }}>
                <li>Check if the URL is correct and accessible</li>
                <li>Some websites block proxy requests for security reasons</li>
                <li>Try a different URL or check your internet connection</li>
                <li>The website might require authentication or have CORS restrictions</li>
              </ul>
            </p>
          </div>
        )}

        {results && (
          <div className="results-container">
            <h2>Scan Results</h2>
            <div className="results-summary">
              <div className="summary-item violations">
                <span className="summary-label">Violations</span>
                <span className="summary-value">{results.violations?.length || 0}</span>
              </div>
              <div className="summary-item incomplete">
                <span className="summary-label">Incomplete</span>
                <span className="summary-value">{results.incomplete?.length || 0}</span>
              </div>
              <div className="summary-item passes">
                <span className="summary-label">Passes</span>
                <span className="summary-value">{results.passes?.length || 0}</span>
              </div>
            </div>

            {results.violations && results.violations.length > 0 ? (
              <div className="violations-section">
                <h3>Violations ({results.violations.length})</h3>
                {results.violations.map((violation, index) => (
                  <div key={index} className="violation-item">
                    <div className="violation-header">
                      <span className="violation-id">{violation.id}</span>
                      <span className={`violation-impact impact-${violation.impact || 'unknown'}`}>
                        {violation.impact || 'unknown'}
                      </span>
                    </div>
                    <p className="violation-description">{violation.description}</p>
                    <p className="violation-help">{violation.help}</p>
                    {violation.nodes && violation.nodes.length > 0 && (
                      <div className="violation-nodes">
                        <strong>Affected elements:</strong> {violation.nodes.length}
                        {violation.nodes.slice(0, 3).map((node, nodeIndex) => (
                          <div key={nodeIndex} className="node-item">
                            <code>{node.html}</code>
                          </div>
                        ))}
                        {violation.nodes.length > 3 && (
                          <p className="more-nodes">+ {violation.nodes.length - 3} more</p>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-violations">
                <p>✓ No accessibility violations found!</p>
              </div>
            )}

            {results.incomplete && results.incomplete.length > 0 && (
              <div className="incomplete-section">
                <h3>Incomplete Checks ({results.incomplete.length})</h3>
                <p className="section-note">
                  These items need manual review as they could not be automatically verified.
                </p>
                {results.incomplete.map((item, index) => (
                  <div key={index} className="incomplete-item">
                    <div className="incomplete-header">
                      <span className="incomplete-id">{item.id}</span>
                    </div>
                    <p className="incomplete-description">{item.description}</p>
                    <p className="incomplete-help">{item.help}</p>
                  </div>
                ))}
              </div>
            )}

            {results.passes && results.passes.length > 0 && (
              <div className="passes-section">
                <h3>Passed Checks ({results.passes.length})</h3>
                <p className="section-note">
                  These accessibility checks passed successfully.
                </p>
                <div className="passes-list">
                  {results.passes.map((pass, index) => (
                    <div key={index} className="pass-item">
                      <span className="pass-id">{pass.id}</span>
                      <span className="pass-description">{pass.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {(!results.violations || results.violations.length === 0) &&
             (!results.incomplete || results.incomplete.length === 0) &&
             (!results.passes || results.passes.length === 0) && (
              <div className="no-results">
                <p>No scan results available. The page may be empty or could not be analyzed.</p>
              </div>
            )}
          </div>
        )}

        {complianceResults && (
          <div className="compliance-container">
            <h2>Compliance Analysis</h2>
            <div className="compliance-score">
              <div className="score-circle">
                <span className="score-value">{complianceResults.score}%</span>
                <span className="score-label">Compliance Score</span>
              </div>
              <div className="score-details">
                <div className="score-item">
                  <span className="score-item-label">Passed:</span>
                  <span className="score-item-value passed">{complianceResults.passed_checks}/{complianceResults.total_checks}</span>
                </div>
                <div className="score-item">
                  <span className="score-item-label">Failed:</span>
                  <span className="score-item-value failed">{complianceResults.failed_checks}/{complianceResults.total_checks}</span>
                </div>
              </div>
            </div>

            <div className="compliance-checks">
              <h3>Compliance Checks</h3>
              {complianceResults.checks.map((check, index) => (
                <div key={index} className={`compliance-check-item ${check.passed ? 'passed' : 'failed'}`}>
                  <div className="check-header">
                    <span className="check-status">{check.passed ? '✓' : '✗'}</span>
                    <span className="check-name">{check.check_name}</span>
                  </div>
                  {check.issues && check.issues.length > 0 && (
                    <div className="check-issues">
                      <strong>Issues:</strong>
                      <ul>
                        {check.issues.map((issue, i) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {check.recommendation && (
                    <div className="check-recommendation">
                      <strong>Recommendation:</strong>
                      <p>{check.recommendation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {complianceResults.ai_recommendations && (
              <div className="ai-recommendations">
                <h3>AI Recommendations (Powered by LongCat)</h3>
                <div className="ai-content">
                  <ReactMarkdown>{complianceResults.ai_recommendations}</ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
