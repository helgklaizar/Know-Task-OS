import React, { useState, useEffect } from 'react';
import Column from './Column';
import StuckModal from './StuckModal';
import CreateTaskModal from './CreateTaskModal';
import { useRBAC } from './RBAC';
import { useI18n } from './I18n';
import './Board.css';
import type { CardType } from '../types';

const COLUMNS_KEYS = [
  { id: 'Backlog', titleKey: 'backlog' },
  { id: 'To Do', titleKey: 'todo' },
  { id: 'In Progress', titleKey: 'inProgress' },
  { id: 'Blocked', titleKey: 'blocked' },
  { id: 'Review', titleKey: 'review' },
  { id: 'Done', titleKey: 'done' }
];

const Board: React.FC = () => {
  const [cards, setCards] = useState<CardType[]>([]);
  const [selectedStuckCard, setSelectedStuckCard] = useState<CardType | null>(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { canManageAgents } = useRBAC();
  const { t } = useI18n();

  const fetchCards = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/cards');
      if (res.ok) {
        const data = await res.json();
        setCards(data);
      }
    } catch (error) {
      console.error("Failed to fetch cards. Make sure backend is running.", error);
    }
  };

  useEffect(() => {
    fetchCards();
  }, []);

  const handleCardClick = (card: CardType) => {
    if (card.isStuck) {
      setSelectedStuckCard(card);
    }
  };

  const handleStuckSubmit = async (response: string) => {
    if (selectedStuckCard) {
      try {
        await fetch(`http://localhost:8000/api/cards/${selectedStuckCard.id}/unstuck`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ response })
        });
        await fetchCards();
      } catch (error) {
        console.error("Failed to unstuck.", error);
      }
    }
    setSelectedStuckCard(null);
  };

  const handleCreateTask = async (title: string, description: string) => {
    try {
      await fetch('http://localhost:8000/api/cards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });
      await fetchCards();
    } catch (error) {
      console.error("Failed to create task", error);
    }
  };

  const handleDropCard = async (cardId: string, targetColumnId: string) => {
    // Optimistic UI update
    setCards(prevCards => 
      prevCards.map(c => c.id === cardId ? { ...c, status: targetColumnId as any } : c)
    );

    // Backend sync
    try {
      await fetch(`http://localhost:8000/api/cards/${cardId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: targetColumnId })
      });
      await fetchCards(); // Ensure sync to get new gitBranch
    } catch (error) {
      console.error("Failed to update status on backend.", error);
      await fetchCards(); // Rollback on error
    }
  };

  return (
    <div className="board-wrapper">
      <div className="board-header">
        <h2 className="board-title">
          <span>📋</span> {t('activeSprint')}
        </h2>
        {canManageAgents && (
          <button 
            onClick={() => setIsCreateModalOpen(true)}
            className="add-task-btn"
          >
            <span>+</span> {t('addTask')}
          </button>
        )}
      </div>

      <div className="board-container" style={{ flex: 1, minHeight: 0 }}>
        {COLUMNS_KEYS.map(col => (
        <Column 
          key={col.id} 
          id={col.id} 
          title={t(col.titleKey as any)} 
          cards={cards.filter(c => c.status === col.id)}
          onCardClick={handleCardClick}
          onDropCard={handleDropCard}
        />
      ))}
      </div>

      {selectedStuckCard && (
        <StuckModal 
          card={selectedStuckCard} 
          onClose={() => setSelectedStuckCard(null)}
          onSubmit={handleStuckSubmit}
        />
      )}

      {isCreateModalOpen && (
        <CreateTaskModal 
          onClose={() => setIsCreateModalOpen(false)} 
          onSubmit={handleCreateTask} 
        />
      )}
    </div>
  );
};

export default Board;
