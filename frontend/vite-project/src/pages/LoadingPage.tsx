function LoadingState() {
  return (
    <section style={{ textAlign: "center", marginTop: "4rem" }}>
      <div style={{ fontSize: "var(--fs-600)", fontWeight: 500 }}>Cooking</div>
      <div
        style={{
          width: "500px",
          height: "12px",
          backgroundColor: "var(--clr-neutral-300)",
          borderRadius: "1rem",
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
            borderRadius: "1rem",
          }}
        />
      </div>
    </section>
  );
}

export default LoadingState;
