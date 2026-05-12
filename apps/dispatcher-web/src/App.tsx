
import Board from './components/Board';
import ActivityFeed from './components/ActivityFeed';
import { RBACProvider } from './components/RBAC';
import { I18nProvider, useI18n } from './components/I18n';


function AppContent() {
  const { t, lang, setLang } = useI18n();
  return (
    <div className="app-layout">
      <header className="app-header">
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '1rem' }}>
          <h1 className="app-title">{t('appTitle')}</h1>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'monospace' }}>v1.0 (Local First)</span>
        </div>
        
        <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Token Budget</span>
            <span style={{ fontSize: '1rem', color: 'var(--accent-orange)', fontWeight: 600, fontFamily: 'monospace' }}>$12.45 / $50.00</span>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Project Health</span>
            <span style={{ fontSize: '1rem', color: 'var(--accent-green)', fontWeight: 600 }}>94%</span>
          </div>

          <select 
            value={lang} 
            onChange={e => setLang(e.target.value as 'en' | 'ru')}
            style={{ backgroundColor: 'var(--bg-card)', color: 'white', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-color)', outline: 'none', cursor: 'pointer', fontFamily: 'inherit' }}
          >
            <option value="en">EN</option>
            <option value="ru">RU</option>
          </select>

          <div className="user-profile">
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: 'var(--bg-card)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem' }}>PO</div>
          </div>
        </div>
      </header>
      <main style={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
        <Board />
        <ActivityFeed />
      </main>
    </div>
  );
}

function App() {
  return (
    <I18nProvider>
      <RBACProvider>
        <AppContent />
      </RBACProvider>
    </I18nProvider>
  );
}

export default App;
