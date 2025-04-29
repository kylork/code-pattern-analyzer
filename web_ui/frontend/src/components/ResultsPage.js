import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'react-chartjs-2';
import ApiService from '../services/api';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const ResultsPage = () => {
  const { analysisId } = useParams();
  const [results, setResults] = useState(null);
  const [htmlReport, setHtmlReport] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [view, setView] = useState('summary'); // 'summary', 'details', or 'html'

  // Load analysis results
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch analysis data and HTML report in parallel
        const [resultsResponse, htmlResponse] = await Promise.all([
          ApiService.getAnalysis(analysisId),
          ApiService.getAnalysisHtml(analysisId)
        ]);
        
        setResults(resultsResponse.data);
        setHtmlReport(htmlResponse.data);
      } catch (err) {
        setError(`Failed to load analysis results: ${err.message}`);
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [analysisId]);

  // Prepare chart data for pattern counts
  const getPatternChartData = () => {
    if (!results || !results.summary || !results.summary.pattern_counts) {
      return null;
    }

    const { pattern_counts } = results.summary;
    
    return {
      labels: Object.keys(pattern_counts),
      datasets: [
        {
          data: Object.values(pattern_counts),
          backgroundColor: [
            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
            '#9b59b6', '#1abc9c', '#d35400', '#34495e'
          ],
          borderWidth: 1,
        },
      ],
    };
  };

  // Prepare chart data for pattern types
  const getTypeChartData = () => {
    if (!results || !results.summary || !results.summary.type_counts) {
      return null;
    }

    const { type_counts } = results.summary;
    
    return {
      labels: Object.keys(type_counts),
      datasets: [
        {
          data: Object.values(type_counts),
          backgroundColor: [
            '#3498db', '#2ecc71', '#e74c3c', '#f39c12', 
            '#9b59b6', '#1abc9c', '#d35400', '#34495e'
          ],
          borderWidth: 1,
        },
      ],
    };
  };

  if (isLoading) {
    return <div>Loading analysis results...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div>
      {results && (
        <>
          {/* Results Header */}
          <div className="card">
            <div className="card-header">
              Analysis Results
            </div>
            <div className="card-body">
              <div>
                <p><strong>File:</strong> {results.file}</p>
                <p><strong>Language:</strong> {results.language}</p>
                {results.summary && (
                  <p><strong>Total Patterns Found:</strong> {results.summary.total_patterns}</p>
                )}
              </div>
              
              {/* View Selection */}
              <div style={{ marginTop: '20px' }}>
                <button 
                  className={`btn ${view === 'summary' ? 'btn-secondary' : ''}`}
                  onClick={() => setView('summary')}
                  style={{ marginRight: '10px' }}
                >
                  Summary
                </button>
                <button 
                  className={`btn ${view === 'details' ? 'btn-secondary' : ''}`}
                  onClick={() => setView('details')}
                  style={{ marginRight: '10px' }}
                >
                  Details
                </button>
                <button 
                  className={`btn ${view === 'html' ? 'btn-secondary' : ''}`}
                  onClick={() => setView('html')}
                >
                  HTML Report
                </button>
              </div>
            </div>
          </div>

          {/* Summary View */}
          {view === 'summary' && results.summary && (
            <div className="card">
              <div className="card-header">
                Summary
              </div>
              <div className="card-body">
                <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap' }}>
                  {/* Pattern Chart */}
                  {getPatternChartData() && (
                    <div style={{ width: '300px', margin: '20px' }}>
                      <h3>Patterns Distribution</h3>
                      <Pie data={getPatternChartData()} />
                    </div>
                  )}
                  
                  {/* Type Chart */}
                  {getTypeChartData() && (
                    <div style={{ width: '300px', margin: '20px' }}>
                      <h3>Pattern Types</h3>
                      <Pie data={getTypeChartData()} />
                    </div>
                  )}
                </div>

                {/* Pattern Counts */}
                <div>
                  <h3>Pattern Counts</h3>
                  <ul className="pattern-list">
                    {Object.entries(results.summary.pattern_counts || {}).map(([pattern, count]) => (
                      <li key={pattern} className="pattern-item">
                        {pattern}: {count}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Details View */}
          {view === 'details' && (
            <div className="card">
              <div className="card-header">
                Pattern Details
              </div>
              <div className="card-body">
                {Object.entries(results.patterns || {}).map(([patternName, matches]) => (
                  <div key={patternName} style={{ marginBottom: '20px' }}>
                    <h3>{patternName}</h3>
                    <p>Found {matches.length} matches</p>
                    
                    <ul className="pattern-list">
                      {matches.map((match, index) => (
                        <li key={index} className="pattern-item">
                          <p>
                            <strong>{match.name || 'Unnamed pattern'}</strong>
                            {match.type && ` (${match.type})`}
                            {match.line && ` at line ${match.line}`}
                          </p>
                          {match.snippet && (
                            <pre className="code-preview">{match.snippet}</pre>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* HTML Report View */}
          {view === 'html' && (
            <div className="card">
              <div className="card-header">
                HTML Report
              </div>
              <div className="card-body">
                <div dangerouslySetInnerHTML={{ __html: htmlReport }} />
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default ResultsPage;
