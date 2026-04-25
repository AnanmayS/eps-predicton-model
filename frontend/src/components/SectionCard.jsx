function SectionCard({ eyebrow, title, subtitle, children, className = "" }) {
  return (
    <section className={`section-card ${className}`.trim()}>
      {(eyebrow || title || subtitle) && (
        <div className="section-card__header">
          {eyebrow ? <span className="section-card__eyebrow">{eyebrow}</span> : null}
          {title ? <h2>{title}</h2> : null}
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
      )}
      {children}
    </section>
  );
}

export default SectionCard;
