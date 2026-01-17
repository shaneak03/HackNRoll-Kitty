function LoadingState() {
  return (
    <section style={{ textAlign: "center", marginTop: "4rem" }}>
      <h2 style={{ fontSize: "var(--fs-600)" }}>Creating your video...</h2>
      <div
        style={{
          width: "300px",
          height: "10px",
          backgroundColor: "var(--clr-neutral-300)",
          borderRadius: "5px",
          marginTop: "1rem",
          overflow: "hidden",
        }}
      >
        <div
          className='loader-bar'
          style={{
            width: "60%", // This would ideally be animated with CSS
            height: "100%",
            backgroundColor: "var(--clr-accent-400)",
          }}
        />
      </div>
    </section>
  );
}

export default LoadingState;
