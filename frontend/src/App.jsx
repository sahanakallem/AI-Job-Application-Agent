import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    job_title: "",
    company_name: "",
    job_description: "",
    resume_text: "",
  });

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const analyzeJob = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAnalysis(null);

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/analyze-job",
        formData
      );

      setAnalysis(response.data);
    } catch (err) {
      setError("Something went wrong while analyzing the job.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreLabel = (score) => {
    if (score >= 75) return "Strong Match";
    if (score >= 50) return "Moderate Match";
    return "Needs Tailoring";
  };

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">AI Job Application Agent</p>
        <h1>Tailor your resume to a job description</h1>
        <p className="subtitle">
          Paste a job description and your resume text. The agent extracts job
          requirements, compares your resume, and generates tailored suggestions.
        </p>
      </header>

      <main className="layout">
        <section className="card">
          <h2>New Job Analysis</h2>

          <form onSubmit={analyzeJob} className="form">
            <label>
              Job Title
              <input
                name="job_title"
                value={formData.job_title}
                onChange={handleChange}
                placeholder="Software Engineer"
                required
              />
            </label>

            <label>
              Company Name
              <input
                name="company_name"
                value={formData.company_name}
                onChange={handleChange}
                placeholder="Example Company"
                required
              />
            </label>

            <label>
              Job Description
              <textarea
                name="job_description"
                value={formData.job_description}
                onChange={handleChange}
                placeholder="Paste the job description here..."
                rows="10"
                required
              />
            </label>

            <label>
              Resume Text
              <textarea
                name="resume_text"
                value={formData.resume_text}
                onChange={handleChange}
                placeholder="Paste your resume text here..."
                rows="10"
                required
              />
            </label>

            <button type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Job Fit"}
            </button>
          </form>

          {error && <p className="error">{error}</p>}
        </section>

        <section className="results">
          {!analysis && (
            <div className="empty-state">
              <h2>No analysis yet</h2>
              <p>
                Submit a job description and resume to see the agent results.
              </p>
            </div>
          )}

          {analysis && (
            <>
              <div className="score-card">
                <p className="score-label">{getScoreLabel(analysis.match_score)}</p>
                <h2>{analysis.match_score}%</h2>
                <p>Resume-to-job match score</p>
              </div>

              <div className="card">
                <h2>Job Requirements Extracted</h2>
                <div className="tag-list">
                  {analysis.job_requirements.map((item, index) => (
                    <span key={index} className={`tag ${item.category.replace("/", "-").replace(" ", "-")}`}>
                      {item.keyword}
                    </span>
                  ))}
                </div>
              </div>

              <div className="grid">
                <div className="card">
                  <h2>Matched Keywords</h2>
                  {analysis.matched_keywords.length > 0 ? (
                    <div className="tag-list">
                      {analysis.matched_keywords.map((skill, index) => (
                        <span key={index} className="tag matched">
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p>No strong matches found yet.</p>
                  )}
                </div>

                <div className="card">
                  <h2>Missing Keywords</h2>
                  {analysis.missing_keywords.length > 0 ? (
                    <div className="tag-list">
                      {analysis.missing_keywords.map((skill, index) => (
                        <span key={index} className="tag missing">
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p>No major missing keywords found.</p>
                  )}
                </div>
              </div>

              <div className="card">
                <h2>Suggested Resume Bullets</h2>
                <ul>
                  {analysis.suggested_resume_bullets.map((bullet, index) => (
                    <li key={index}>{bullet}</li>
                  ))}
                </ul>
              </div>

              <div className="card">
                <h2>Application Answer</h2>
                <p>{analysis.application_answer}</p>
              </div>

              <div className="card">
                <h2>Agent Execution Trace</h2>
                <ol>
                  {analysis.agent_steps.map((step, index) => (
                    <li key={index}>{step}</li>
                  ))}
                </ol>
              </div>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;