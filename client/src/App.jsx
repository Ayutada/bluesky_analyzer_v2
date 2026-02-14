/* client/src/App.jsx */
import { useState } from 'react'
import './App.css' // Import styles
import AutocompleteInput from './AutocompleteInput' // Import Autocomplete Component

function App() {
  // --- State Definition ---
  // Principle: Data that changes on the UI needs to be defined as State
  const [handle, setHandle] = useState('scievents.bsky.social')
  const [lang, setLang] = useState('jp')
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  // Featured accounts for users to try
  const featuredAccounts = [
    { handle: 'ngntrtr.bsky.social', displayName: 'ナガノ' },
    { handle: 'chiitan.love', displayName: 'Chiitan🌈ちぃたん☆' },
    { handle: 'nytimes.com', displayName: 'The New York Times' },
    { handle: 'sora-sakurai.bsky.social', displayName: '桜井 政博' },
    { handle: 'mokmok-len.bsky.social', displayName: 'モクモクれん' },
    { handle: 'stephenking.bsky.social', displayName: 'Stephen King' }
  ]

  // Multi-language dictionary (can be defined outside the component or in a separate file)
  const translations = {
    cn: {
      title: "BlueSky 人格分析器",
      subtitle: "输入您的 BlueSky ID (即主页 @ 后的部分)，AI 将为您揭示 MBTI 与灵魂动物",
      btn: "开始分析",
      loading: "正在连接神经元...可能需要 10-20 秒",
      mbti: "MBTI 类型",
      animal: "灵魂动物",
      desc: "性格画像",
      alertInput: "请输入有效的 BlueSky ID！",
      placeholder: "例如: scievents.bsky.social",
      featuredTitle: "🔥 试试这些热门账号",
    },
    jp: {
      title: "BlueSky 性格診断",
      subtitle: "BlueSky ID (プロフィール @ の後ろの部分) を入力して、AIがMBTIと動物占いを明らかにします",
      btn: "診断開始",
      loading: "ニューロン接続中... 10-20秒かかる場合があります",
      mbti: "MBTI タイプ",
      animal: "動物占い",
      desc: "性格プロフィール",
      alertInput: "有効な BlueSky ID を入力してください！",
      placeholder: "例: scievents.bsky.social",
      featuredTitle: "🔥 人気アカウントを試してみる",
    },
    en: {
      title: "BlueSky Personality Analyzer",
      subtitle: "Enter your BlueSky ID (the part after @ on your profile), AI will reveal your MBTI & Spirit Animal",
      btn: "Analyze",
      loading: "Connecting neurons... may take 10-20 seconds",
      mbti: "MBTI Type",
      animal: "Spirit Animal",
      desc: "Portrait",
      alertInput: "Please enter a valid BlueSky ID!",
      placeholder: "Ex: scievents.bsky.social",
      featuredTitle: "🔥 Try these trending accounts",
    }
  }

  const t = translations[lang] // Current language package

  // --- Business Logic ---
  const handleAnalyze = async () => {
    if (!handle.trim()) {
      alert(t.alertInput)
      return
    }

    setLoading(true)
    setError('')
    setData(null) // Clear old results

    try {
      // Principle: Use fetch to make requests; path doesn't need http://localhost:5000 because proxy is configured
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ handle: handle, lang: lang })
      })

      const resData = await response.json()

      if (!response.ok) {
        throw new Error(resData.error || "请求失败")
      }

      // If successful, update data state; React will automatically render the result area
      setData(resData)
    } catch (err) {
      setError(err.message)
      alert("Error: " + err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleLangChange = (newLang) => {
    setLang(newLang)
    setData(null) // Clear previous results to avoid language mismatch
  }

  // --- View Rendering (JSX) ---
  return (
    <div className="container">
      <div className="glass-card">
        {/* Language Switch */}
        <div className="lang-switch">
          <button
            className={`lang-btn ${lang === 'cn' ? 'active' : ''}`}
            onClick={() => handleLangChange('cn')}
            title="中文">
            中文
          </button>
          <button
            className={`lang-btn ${lang === 'jp' ? 'active' : ''}`}
            onClick={() => handleLangChange('jp')}
            title="日本語">
            日本語
          </button>
          <button
            className={`lang-btn ${lang === 'en' ? 'active' : ''}`}
            onClick={() => handleLangChange('en')}
            title="English">
            English
          </button>
        </div>

        <h1 className="title">{t.title}</h1>
        <p className="subtitle">{t.subtitle}</p>

        {/* Input Area */}
        <div className="input-group">
          {/* Principle: Two-way binding; value shows state, onChange updates state */}
          <AutocompleteInput
            placeholder={t.placeholder}
            value={handle}
            onChange={setHandle}
            disabled={loading}
          />
          <button className="action-btn" onClick={handleAnalyze} disabled={loading}>
            {t.btn}
          </button>
        </div>

        {/* Featured Accounts Section */}
        <div className="featured-accounts">
          <p className="featured-title">{t.featuredTitle}</p>
          <div className="account-chips">
            {featuredAccounts.map((account) => (
              <button
                key={account.handle}
                className="account-chip"
                onClick={() => setHandle(account.handle)}
                disabled={loading}
              >
                <span className="chip-name">{account.displayName}</span>
                <span className="chip-handle">@{account.handle.split('.')[0]}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Loading State Rendering */}
        {loading && (
          <div className="loader" style={{ display: 'block' }}>
            <div className="spinner"></div>
            <p>{t.loading}</p>
          </div>
        )}

        {/* Result Rendering - Only display when data exists and is not loading */}
        {!loading && data && (
          <div id="result-section" style={{ display: 'block' }}>
            <div className="profile-header">
              <img
                src={data.profile.avatar || `https://ui-avatars.com/api/?name=${data.profile.handle}`}
                alt="Avatar"
                className="avatar"
              />
              <div className="profile-name">
                <h3>{data.profile.displayName || handle}</h3>
                <span>@{data.profile.handle}</span>
              </div>
            </div>

            <div className="result-cards">
              <div className="info-card">
                <div className="card-label">{t.mbti}</div>
                <div className="card-value">{data.analysis.mbti}</div>
              </div>
              <div className="info-card">
                <div className="card-label">{t.animal}</div>
                <div className="card-value">{data.analysis.animal}</div>
              </div>
            </div>

            <div className="analysis-text">
              <div className="card-label" style={{ textAlign: 'left', marginBottom: '1rem' }}>
                {t.desc}
              </div>
              <p>{data.analysis.description}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App