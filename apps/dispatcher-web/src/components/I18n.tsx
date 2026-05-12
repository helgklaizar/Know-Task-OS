import React, { createContext, useContext, useState } from 'react';

type Language = 'en' | 'ru';

interface Translations {
  [key: string]: { en: string; ru: string };
}

export const translations: Translations = {
  appTitle: { en: 'AI Dispatcher', ru: 'AI Диспетчер' },
  activeSprint: { en: 'Active Sprint Board', ru: 'Активный Спринт' },
  addTask: { en: 'Add Task', ru: 'Добавить Задачу' },
  createTaskTitle: { en: '✨ Create New Agent Task', ru: '✨ Новая Задача для ИИ' },
  taskTitleLabel: { en: 'Task Title', ru: 'Название Задачи' },
  taskTitlePlaceholder: { en: 'e.g. Implement login screen', ru: 'напр. Реализовать экран логина' },
  taskDescLabel: { en: 'Description & Agent Context', ru: 'Описание и Контекст для Агента' },
  taskDescPlaceholder: { en: 'Provide exact details for the Developer Agent...', ru: 'Подробное описание для Агента...' },
  cancelBtn: { en: 'Cancel', ru: 'Отмена' },
  dispatchBtn: { en: 'Dispatch Task 🚀', ru: 'Запустить 🚀' },
  dispatching: { en: 'Dispatching...', ru: 'Запуск...' },
  backlog: { en: 'Backlog', ru: 'Бэклог' },
  todo: { en: 'To Do', ru: 'К выполнению' },
  inProgress: { en: 'Agent Thinking (In Progress)', ru: 'Агент Думает (В процессе)' },
  blocked: { en: 'Blocked (Human Needed)', ru: 'Заблокировано (Нужен Человек)' },
  review: { en: 'Gatekeeper Review', ru: 'Проверка Gatekeeper' },
  done: { en: 'Done', ru: 'Готово' },

  // Dynamic Content Translations (Mock)
  'Design Agent Architecture': { en: 'Design Agent Architecture', ru: 'Проектирование Архитектуры Агентов' },
  'Create a plan.': { en: 'Create a plan.', ru: 'Создать подробный план.' },
  'Setup React Frontend': { en: 'Setup React Frontend', ru: 'Настройка React Фронтенда' },
  'Vite project.': { en: 'Vite project.', ru: 'Проект на базе Vite.' },
  'Connect Local SQLite': { en: 'Connect Local SQLite', ru: 'Подключение Локальной SQLite' },
  'Need DB credentials to proceed.': { en: 'Need DB credentials to proceed.', ru: 'Нужны доступы к БД для продолжения.' },
  'Fix the navigation layout': { en: 'Fix the navigation layout', ru: 'Исправить верстку навигации' },
  'The top navbar is broken on mobile view.': { en: 'The top navbar is broken on mobile view.', ru: 'Верхняя панель ломается на мобильных экранах.' },
};

interface I18nContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: keyof typeof translations) => string;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLang] = useState<Language>('en');

  const t = (key: keyof typeof translations) => translations[key]?.[lang] || key;

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used within I18nProvider");
  return context;
};
