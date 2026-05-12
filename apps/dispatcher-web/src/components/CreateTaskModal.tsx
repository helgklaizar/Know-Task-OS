import React, { useState } from 'react';
import { useI18n } from './I18n';

interface CreateTaskModalProps {
  onClose: () => void;
  onSubmit: (title: string, description: string) => Promise<void>;
}

const CreateTaskModal: React.FC<CreateTaskModalProps> = ({ onClose, onSubmit }) => {
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const { t } = useI18n();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await onSubmit(title, desc);
    setLoading(false);
    onClose();
  };

  return (
    <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ backgroundColor: 'var(--bg-card, #18181b)', border: '1px solid var(--border-color, #27272a)', padding: '24px', borderRadius: '12px', width: '100%', maxWidth: '450px', color: 'white', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '16px', marginTop: 0 }}>{t('createTaskTitle')}</h2>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', color: '#a1a1aa', marginBottom: '4px' }}>{t('taskTitleLabel')}</label>
            <input 
              required
              style={{ width: '100%', backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px', padding: '8px', color: 'white', outline: 'none', boxSizing: 'border-box' }}
              placeholder={t('taskTitlePlaceholder')}
              value={title}
              onChange={e => setTitle(e.target.value)}
            />
          </div>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', color: '#a1a1aa', marginBottom: '4px' }}>{t('taskDescLabel')}</label>
            <textarea 
              required
              style={{ width: '100%', backgroundColor: '#09090b', border: '1px solid #27272a', borderRadius: '8px', padding: '8px', color: 'white', outline: 'none', minHeight: '100px', resize: 'vertical', boxSizing: 'border-box' }}
              placeholder={t('taskDescPlaceholder')}
              value={desc}
              onChange={e => setDesc(e.target.value)}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
            <button type="button" onClick={onClose} style={{ padding: '8px 16px', backgroundColor: 'transparent', color: '#a1a1aa', border: 'none', cursor: 'pointer' }}>{t('cancelBtn')}</button>
            <button disabled={loading} type="submit" style={{ padding: '8px 16px', backgroundColor: '#2563eb', color: 'white', borderRadius: '8px', border: 'none', cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.5 : 1 }}>
              {loading ? t('dispatching') : t('dispatchBtn')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
export default CreateTaskModal;
