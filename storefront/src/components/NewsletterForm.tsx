"use client";

import { useState, type FormEvent } from "react";

export function NewsletterForm() {
  const [done, setDone] = useState(false);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setDone(true);
  }

  if (done) {
    return <p className="mt-4 text-sm text-gold-light">Thanks — you’re on the list.</p>;
  }

  return (
    <form className="mt-4 flex gap-2" onSubmit={onSubmit}>
      <input
        type="email"
        required
        placeholder="Email address"
        className="w-full rounded-md border border-sand/20 bg-white/10 px-3 py-2 text-sm text-sand placeholder:text-sand/50 outline-none"
      />
      <button type="submit" className="rounded-md bg-gold px-3 py-2 text-sm font-semibold text-ink">
        Join
      </button>
    </form>
  );
}
