import { useEffect, useState } from "react";
import { useT } from "../lib/i18n";
import { api } from "../lib/api";
import { useFetch } from "../lib/useFetch";
import { fmtDayMonth } from "../lib/format";
import { Poster, Section } from "./ui";
import type { Tag } from "./TagChips";

export type WhatsNextState = "ready" | "aired" | "upcoming" | "caught_up" | "pending";

export interface WhatsNextItem {
  key: string;
  title_id: string;
  title: string;
  year: number | null;
  kind: "series";
  poster: string | null;
  tags: Tag[];
  state: WhatsNextState;
  season: number | null;
  episode: number | null;
  episode_name: string | null;
  air_date: string | null;
  air_at: string | null;
  available_at: string | null;
  /** Further aired episodes waiting behind the one shown. */
  behind: number;
  runtime_minutes: number | null;
}

interface WhatsNextData {
  tags: (Tag & { count: number })[];
  items: WhatsNextItem[];
}

// "What's next": for every tagged series, the next episode nobody in scope has
// watched. Invisible while no series is tagged (or nothing is left to show).
export function WhatsNext({ scope }: { scope: string }) {
  const { t } = useT();
  const [tag, setTag] = useState<string | null>(null);
  const { data } = useFetch<WhatsNextData>(
    () => api.get("/stats/whats-next", tag ? { profile: scope, tag } : { profile: scope }), [scope, tag]);

  // A filter whose tag no longer has anything to show would otherwise stay stuck.
  const known = data?.tags.some((x) => x.id === tag);
  useEffect(() => { if (data && tag && !known) setTag(null); }, [data, tag, known]);

  if (!data || (data.items.length === 0 && data.tags.length === 0)) return null;

  const badge = (i: WhatsNextItem): string | undefined => {
    switch (i.state) {
      case "ready": return t("whatsnext.ready");
      case "aired": return t("whatsnext.aired");
      case "upcoming": return i.air_date ? fmtDayMonth(i.air_date) : t("whatsnext.tba");
      case "caught_up": return i.air_date ? fmtDayMonth(i.air_date) : undefined;
      default: return i.air_date ? fmtDayMonth(i.air_date) : undefined;
    }
  };
  const subtitle = (i: WhatsNextItem): string => {
    if (i.state === "caught_up") return t("whatsnext.caughtUp");
    if (i.state === "pending") return t("whatsnext.pending");
    const ep = i.season != null && i.episode != null ? `S${i.season}·E${i.episode}` : "";
    return [ep, i.behind > 0 ? t("whatsnext.more", { n: i.behind }) : ""].filter(Boolean).join(" · ");
  };

  return (
    <Section title={t("dashboard.whatsNext")}>
      {data.tags.length > 1 && (
        <div className="chips" role="group" aria-label={t("dashboard.whatsNext")} style={{ marginBottom: 12 }}>
          <button type="button" className={`chip${tag === null ? " active" : ""}`}
            aria-pressed={tag === null} onClick={() => setTag(null)}>{t("whatsnext.all")}</button>
          {data.tags.map((x) => (
            <button type="button" key={x.id} className={`chip${tag === x.id ? " active" : ""}`}
              aria-pressed={tag === x.id} onClick={() => setTag(tag === x.id ? null : x.id)}>
              {x.name} <span className="caption">{x.count}</span>
            </button>
          ))}
        </div>
      )}
      <div className="poster-rail" style={{ marginBottom: 24 }}>
        {data.items.map((i) => (
          <div className="rail-item" key={i.key}>
            <Poster to={`/title/${i.title_id}`} poster={i.poster} title={i.title} kind={i.kind}
              badge={badge(i)} subtitle={subtitle(i)} />
          </div>
        ))}
      </div>
    </Section>
  );
}
