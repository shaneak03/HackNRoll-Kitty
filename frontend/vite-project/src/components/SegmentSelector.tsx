type DurationOption = "30s" | "60s" | "90s";

function SegmentSelector({
  value,
  onChange,
}: {
  value: DurationOption;
  onChange: (value: DurationOption) => void;
}) {
  const options: { label: string; value: DurationOption }[] = [
    { label: "30 sec", value: "30s" },
    { label: "1 min", value: "60s" },
    { label: "1.5 min", value: "90s" },
  ];

  return (
    <div
      style={{
        display: "flex",
        borderRadius: "1rem",
        border: "1px solid var(--clr-neutral-300)",
        overflow: "hidden",
      }}
    >
      {options.map(opt => {
        const selected = value === opt.value;

        return (
          <button
            key={opt.value}
            onClick={() => {
              console.log(opt.value);
              onChange(opt.value);
            }}
            style={{
              flex: 1,
              padding: "0.75rem 0",
              border: "none",
              cursor: "pointer",
              fontWeight: 600,
              backgroundColor: selected
                ? "var(--clr-accent-400)"
                : "var(--clr-neutral-100)",
              color: selected
                ? "var(--clr-neutral-100)"
                : "var(--clr-neutral-600)",
              transition: "all 0.2s",
            }}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

export default SegmentSelector;