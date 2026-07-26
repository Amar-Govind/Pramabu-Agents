type IconProps = {
  className?: string;
  title?: string;
};

function base(className?: string) {
  return `h-5 w-5 ${className ?? ""}`;
}

export function IconSearch({ className, title = "Search" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <circle cx="11" cy="11" r="7" />
      <path d="m20 20-3.5-3.5" strokeLinecap="round" />
    </svg>
  );
}

export function IconCart({ className, title = "Cart" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M3 3h2l2.2 11.2a2 2 0 0 0 2 1.6h7.6a2 2 0 0 0 2-1.5L21 7H7" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="10" cy="20" r="1.3" fill="currentColor" stroke="none" />
      <circle cx="18" cy="20" r="1.3" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function IconHeart({ className, title = "Wishlist", filled = false }: IconProps & { filled?: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={base(className)}
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="1.9"
      aria-hidden={!title}
    >
      {title ? <title>{title}</title> : null}
      <path
        d="M12 20.5s-7-4.4-9.2-8.5C1.2 9.1 2.1 5.8 5.2 4.6c2-.8 4.1-.1 5.3 1.5C11.7 4.5 13.8 3.8 15.8 4.6c3.1 1.2 4 4.5 2.4 7.4C16 16.1 12 20.5 12 20.5z"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconMenu({ className, title = "Menu" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M4 7h16M4 12h16M4 17h16" strokeLinecap="round" />
    </svg>
  );
}

export function IconClose({ className, title = "Close" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="m6 6 12 12M18 6 6 18" strokeLinecap="round" />
    </svg>
  );
}

export function IconChevronLeft({ className, title = "Previous" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="m15 5-7 7 7 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconChevronRight({ className, title = "Next" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="m9 5 7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconStar({ className, title = "Rating" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="currentColor" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="m12 3.5 2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 16.8 6.8 19.6l1-5.8L3.5 9.7l5.9-.9L12 3.5z" />
    </svg>
  );
}

export function IconLeaf({ className, title = "Natural" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M5 19c8 0 12-5 14-14-8 1-14 6-14 14z" strokeLinejoin="round" />
      <path d="M5 19c3-4 7-7 14-9" strokeLinecap="round" />
    </svg>
  );
}

export function IconTruck({ className, title = "Shipping" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M3 7h11v10H3zM14 10h4l3 3v4h-7" strokeLinejoin="round" />
      <circle cx="7.5" cy="18.5" r="1.5" />
      <circle cx="17.5" cy="18.5" r="1.5" />
    </svg>
  );
}

export function IconShield({ className, title = "Secure" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M12 3 5 6v6c0 4.5 3.1 7.8 7 9 3.9-1.2 7-4.5 7-9V6l-7-3z" strokeLinejoin="round" />
      <path d="m9 12 2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconSpark({ className, title = "Quality" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M12 3v4M12 17v4M4.5 7.5l2.8 2.8M16.7 13.7l2.8 2.8M3 12h4M17 12h4M4.5 16.5l2.8-2.8M16.7 10.3l2.8-2.8" strokeLinecap="round" />
    </svg>
  );
}

export function IconUser({ className, title = "Account" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <circle cx="12" cy="8" r="3.2" />
      <path d="M5 19c1.5-3 4-4.5 7-4.5S17.5 16 19 19" strokeLinecap="round" />
    </svg>
  );
}

export function IconCheck({ className, title = "Done" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="2" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="m5 12 5 5L20 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function IconTrash({ className, title = "Remove" }: IconProps) {
  return (
    <svg viewBox="0 0 24 24" className={base(className)} fill="none" stroke="currentColor" strokeWidth="1.7" aria-hidden={!title}>
      {title ? <title>{title}</title> : null}
      <path d="M5 7h14M9 7V5h6v2M8 7l1 12h6l1-12" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
