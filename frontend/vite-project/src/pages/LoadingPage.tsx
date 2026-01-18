import popCat from "../assets/pop-cat.gif";

const loadingStates = [
  "Sharpening claws",
  "Rendering whiskers",
  "Purr-fecting script",
  "Sharpening claws",
  "Rendering whiskers",
  "Purr-fecting script",
  "Almost done!",
];

function LoadingState({ pipelineCount }: { pipelineCount: number }) {
  const loadingBarPercentage = (pipelineCount / 7) * 100;

  return (
    <section
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: "1rem",
      }}
    >
      <img
        src={popCat}
        alt='popcat'
        style={{ width: "150px", height: "auto", marginBottom: "1rem" }}
      ></img>
      <div
        style={{
          width: "500px",
          height: "12px",
          backgroundColor: "var(--clr-neutral-300)",
          borderRadius: "1rem",
          overflow: "hidden",
        }}
      >
        <div
          className='loader-bar'
          style={{
            width: `${loadingBarPercentage}%`,
            height: "100%",
            backgroundColor: "var(--clr-accent-400)",
            borderRadius: "1rem",
          }}
        />
      </div>
      <div style={{ color: "var(--clr-accent-400)" }}>
        {loadingStates[pipelineCount]}
      </div>
    </section>
  );
}

export default LoadingState;
