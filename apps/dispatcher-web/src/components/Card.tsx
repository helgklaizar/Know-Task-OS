import React from 'react';
import type { CardType } from '../types';
import { useI18n } from './I18n';
import './Card.css';

interface CardProps {
  card: CardType;
  onClick: () => void;
}

const Card: React.FC<CardProps> = ({ card, onClick }) => {
  const { t } = useI18n();

  const agentColors: Record<string, string> = {
    'Architect': 'var(--accent-purple)',
    'Coder': 'var(--accent-blue)',
    'Reviewer': 'var(--accent-green)',
    'Manager': 'var(--accent-orange)'
  };

  const badgeColor = card.agentRole ? agentColors[card.agentRole] : 'var(--text-muted)';

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>) => {
    e.dataTransfer.setData('cardId', card.id);
  };

  return (
    <div 
      className="card glass-panel" 
      onClick={onClick}
      draggable={!card.isStuck}
      onDragStart={handleDragStart}
      style={{ cursor: card.isStuck ? 'pointer' : 'grab', opacity: card.isStuck ? 0.8 : 1 }}
    >
      <div className="card-header">
        <span className="card-id">#{card.id}</span>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {card.cost !== undefined && (
            <span style={{ fontSize: '0.65rem', color: 'var(--accent-orange)', fontFamily: 'monospace' }}>${card.cost.toFixed(2)}</span>
          )}
          {card.agentRole && (
            <div className="agent-badge" style={{ borderColor: badgeColor, color: badgeColor }}>
              <span className="agent-dot" style={{ backgroundColor: badgeColor }}></span>
              {card.agentRole}
            </div>
          )}
        </div>
      </div>
      <h4 className="card-title">{t(card.title as any)}</h4>
      <p className="card-desc">{t(card.description as any)}</p>
      
      {card.isStuck && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--accent-red)', borderRadius: '6px', padding: '8px', marginBottom: '1rem', fontSize: '0.75rem', color: '#ff9999' }}>
          ⚠️ <strong>Agent Stuck:</strong> Waiting for human input.
        </div>
      )}

      <div className="card-footer">
        {card.gitBranch ? (
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: 'monospace', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M6 3v12"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>
            {card.gitBranch}
          </div>
        ) : (
          <div className="card-status">{card.status}</div>
        )}
        
        {card.gitBranch && <div className="card-status">{card.status}</div>}
      </div>
    </div>
  );
};

export default Card;
