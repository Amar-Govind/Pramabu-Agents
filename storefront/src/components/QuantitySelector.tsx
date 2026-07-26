"use client";

export function QuantitySelector({
  value,
  onChange,
  min = 1,
  max = 20,
}: {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
}) {
  return (
    <div className="inline-flex items-center rounded-md border border-forest/15 bg-white">
      <button
        type="button"
        aria-label="Decrease quantity"
        className="h-10 w-10 text-lg text-forest transition hover:bg-mist disabled:opacity-40"
        disabled={value <= min}
        onClick={() => onChange(Math.max(min, value - 1))}
      >
        −
      </button>
      <span className="min-w-10 text-center text-sm font-semibold tabular-nums text-ink">
        {value}
      </span>
      <button
        type="button"
        aria-label="Increase quantity"
        className="h-10 w-10 text-lg text-forest transition hover:bg-mist disabled:opacity-40"
        disabled={value >= max}
        onClick={() => onChange(Math.min(max, value + 1))}
      >
        +
      </button>
    </div>
  );
}
