import { formatAttackType, getAttackColor } from '../utils/formatters';

export default function AttackChip({ type }) {
  if (!type) return null;
  
  const label = formatAttackType(type);
  const color = getAttackColor(type);

  return (
    <span
      title={label}
      className="inline-flex items-center gap-1 px-2 py-0.5 border rounded-none text-xs font-mono font-bold tracking-widest uppercase cursor-default"
      style={{
        backgroundColor: color.bg,
        borderColor: color.border,
        color: color.text,
      }}
    >
      {label}
    </span>
  );
}
