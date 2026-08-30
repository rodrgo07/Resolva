interface LogoProps {
  className?: string;
  size?: number;
}

export function ResolvaLogoSvg({ className, size = 96 }: LogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 120 120"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className || "resolva-svg-logo"}
    >
      <defs>
        {/* Gradiente do Escudo / Borda */}
        <linearGradient id="shieldGrad" x1="10" y1="10" x2="110" y2="110" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="var(--accent-light, #a78bfa)" />
          <stop offset="50%" stopColor="var(--accent, #7c3aed)" />
          <stop offset="100%" stopColor="var(--accent-light, #c4b5fd)" />
        </linearGradient>

        {/* Gradiente de Preenchimento Interno */}
        <linearGradient id="shieldFill" x1="60" y1="10" x2="60" y2="110" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="var(--surface-elevated, #111c35)" stopOpacity="0.8" />
          <stop offset="100%" stopColor="var(--surface, #0b1329)" stopOpacity="0.9" />
        </linearGradient>

        {/* Gradiente da Letra R */}
        <linearGradient id="letterGrad" x1="35" y1="30" x2="85" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#ffffff" />
          <stop offset="100%" stopColor="var(--accent-light, #a78bfa)" />
        </linearGradient>

        {/* Filtro Glow Neon */}
        <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="4" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Círculo de Energia / Aura */}
      <circle
        cx="60"
        cy="60"
        r="48"
        fill="none"
        stroke="var(--accent-glow, rgba(124, 58, 237, 0.4))"
        strokeWidth="1.5"
        strokeDasharray="4 6"
        className="resolva-svg-glow-circle"
      />

      {/* Escudo Tecnológico (Hexágono Suave) */}
      <path
        d="M60 12 L100 32 V76 L60 108 L20 76 V32 Z"
        fill="url(#shieldFill)"
        stroke="url(#shieldGrad)"
        strokeWidth="3"
        strokeLinejoin="round"
        strokeLinecap="round"
        className="resolva-svg-shield"
        filter="url(#neonGlow)"
      />

      {/* Detalhes de Circuito / IA */}
      <circle cx="60" cy="18" r="2.5" fill="var(--accent-light, #a78bfa)" />
      <circle cx="95" cy="73" r="2.5" fill="var(--accent-light, #a78bfa)" />
      <circle cx="25" cy="73" r="2.5" fill="var(--accent-light, #a78bfa)" />
      <circle cx="60" cy="102" r="2.5" fill="var(--accent-light, #a78bfa)" />

      {/* Traçado Futurista da Letra 'R' */}
      <path
        d="M44 82 V38 H64 C73 38 78 43 78 50 C78 57 73 62 64 62 H44 M62 62 L78 82"
        stroke="url(#letterGrad)"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="resolva-svg-r"
      />
    </svg>
  );
}