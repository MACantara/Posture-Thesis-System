interface TabNavProps {
  tabs: { key: string; label: string }[];
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function TabNav({ tabs, activeTab, onTabChange }: TabNavProps) {
  return (
    <div className="flex gap-1 border-b border-posture-border mb-6">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onTabChange(tab.key)}
          className={`px-4 py-2.5 text-sm font-medium transition-colors relative ${
            activeTab === tab.key
              ? 'text-cyan-400'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          {tab.label}
          {activeTab === tab.key && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-cyan-500 rounded-full" />
          )}
        </button>
      ))}
    </div>
  );
}
