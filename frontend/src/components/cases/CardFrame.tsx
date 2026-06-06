import type { ReactNode } from "react";

type CardFrameProps = {
  title: string;
  subtitle?: string;
  children: ReactNode;
  fullSpan?: boolean;
};

export function CardFrame({ title, subtitle, children, fullSpan = false }: CardFrameProps) {
  return (
    <section className={`card ${fullSpan ? "full-span" : ""}`}>
      <div className="card-header">
        <h3>{title}</h3>
        {subtitle && <p>{subtitle}</p>}
      </div>
      <div className="card-body">{children}</div>
    </section>
  );
}
