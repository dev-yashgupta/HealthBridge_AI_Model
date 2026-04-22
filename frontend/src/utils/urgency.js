// Urgency color mapping — total function (defaults to LOW for unrecognised values)
// Validates: Requirements 2.7, 2.9
const URGENCY_COLORS = {
  LOW:    { bg: 'bg-[#97f3e2]/20', text: 'text-[#97f3e2]', border: 'border-[#97f3e2]/30' },
  MEDIUM: { bg: 'bg-[#ffb694]/20', text: 'text-[#ffb694]', border: 'border-[#ffb694]/30' },
  HIGH:   { bg: 'bg-[#ba1a1a]/20', text: 'text-[#ba1a1a]',  border: 'border-[#ba1a1a]/30' },
}

export const getUrgencyStyle = (urgency) => URGENCY_COLORS[urgency] ?? URGENCY_COLORS.LOW
