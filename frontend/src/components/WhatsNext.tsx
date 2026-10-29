import { useEffect, useState } from "react";
import { useApp } from "../lib/app";
import { useT } from "../lib/i18n";
import { api, ApiError } from "../lib/api";
import { useFetch } from "../lib/useFetch";
import { fmtDayMonth, todayLocalKey } from "../lib/format";
import { IconCheck, IconTag } from "./icons";
import { Link } from "react-router-dom";
import { Poster, Section } from "./ui";
import { TagChips, type Tag } from "./TagChips";

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
  /** The catalog episode shown (null while there is none to mark). */
  episode_id: string | null;
  episode_name: string | null;
  air_date: string | null;
  air_at: string | null;
  available_at: string | null;
  /** Further aired episodes waiting behind the one shown. */
  behind: number;
  runtime_minutes: number | null;
  /** Unwatched / known episodes (specials excluded); null while the catalog has none. */
  remaining: number | null;
  total: number | null;
}

export interface WhatsNextData {
  tags: (Tag & { count: number })[];
  items: WhatsNextItem[];
}

// Shared by the dashboard block and the What's next page: fetches the list (the
// full one with `all`), keeps the tag filter, and builds a card per item.
export function useWhatsNext(scope: string, all = false) {
  const { t } = useT();
  const { can, toast } = useApp();
  const canWrite = can("ingest.write");
  const [tag, setTag] = useState<string | null>(null);
  const { data, loading, error, reload, refresh } = useFetch<WhatsNextData>(
    () => api.get("/stats/whats-next", { profile: scope, ...(tag ? { tag } : {}), ...(all ? { all: 1 } : {}) }),
    [scope, tag, all]);

  // A filter whose tag no longer has anything to show would otherwise stay stuck.
  const known = data?.tags.some((x) => x.id === tag);
  useEffect(() => { if (data && tag && !known) setTag(null); }, [data, tag, known]);

  const badge = (i: WhatsNextItem): string | undefined => {
    switch (i.state) {
      case "ready": return t("whatsnext.ready");
      case "aired": return t("whatsnext.aired");
      case "upcoming": return i.air_date ? fmtDayMonth(i.air_date) : t("whatsnext.tba");
      default: return i.air_date ? fmtDayMonth(i.air_date) : undefined;
    }
  };
  const subtitle = (i: WhatsNextItem): string => {
    if (i.state === "caught_up") return t("whatsnext.caughtUp");
    if (i.state === "pending") return t("whatsnext.pending");
    const ep = i.season != null && i.episode != null ? `S${i.season}·E${i.episode}` : "";
    const left = all && i.remaining ? t("whatsnext.left", { n: i.remaining }) : "";
    return [ep, i.behind > 0 ? t("whatsnext.more", { n: i.behind }) : "", left].filter(Boolean).join(" · ");
  };

  // Same attribution rule as the title page: a chosen profile is watched for, the
  // household view records the watch for whoever is signed in.
  const markWatched = async (i: WhatsNextItem) => {
    try {
      await api.post(`/episodes/${i.episode_id}/watch`,
        scope === "all" ? { date: todayLocalKey() } : { user_id: scope, date: todayLocalKey() });
      toast(t("whatsnext.marked", { title: i.title, ep: `S${i.season}·E${i.episode}` }), "ok");
      await refresh();
    } catch (e) {
      toast(e instanceof ApiError ? e.message : t("settings.failed"), "err");
    }
  };

  const card = (i: WhatsNextItem) => (
    <>
      <Poster to={`/title/${i.title_id}`} poster={i.poster} title={i.title} kind={i.kind}
        badge={badge(i)} subtitle={subtitle(i)} />
      {canWrite && <CardActions item={i} onWatched={() => markWatched(i)} onTagsChanged={refresh} />}
    </>
  );
  return { data, loading, error, reload, tag, setTag, card };
}

// "All" plus one chip per tag with its count; a second click on a tag clears it.
export function TagFilter({ tags, tag, onChange }: {
  tags: (Tag & { count: number })[]; tag: string | null; onChange: (id: string | null) => void;
}) {
  const { t } = useT();
  if (tags.length < 2) return null;
  return (
    <div className="chips" role="group" aria-label={t("dashboard.whatsNext")} style={{ marginBottom: 12 }}>
      <button type="button" className={`chip${tag === null ? " active" : ""}`}
        aria-pressed={tag === null} onClick={() => onChange(null)}>{t("whatsnext.all")}</button>
      {tags.map((x) => (
        <button type="button" key={x.id} className={`chip${tag === x.id ? " active" : ""}`}
          aria-pressed={tag === x.id} onClick={() => onChange(tag === x.id ? null : x.id)}>
          {x.name} <span className="caption">{x.count}</span>
        </button>
      ))}
    </div>
  );
}

// "What's next": for every tagged series, the next episode nobody in scope has
// watched. Invisible while no series is tagged (or nothing is left to show).
export function WhatsNext({ scope }: { scope: string }) {
  const { t } = useT();
  const { data, tag, setTag, card } = useWhatsNext(scope);
  if (!data || (data.items.length === 0 && data.tags.length === 0)) return null;
  return (
    <Section title={t("dashboard.whatsNext")}
      right={<Link to="/whats-next" className="btn-ghost btn-sm">{t("whatsnext.seeAll")}</Link>}>
      <TagFilter tags={data.tags} tag={tag} onChange={setTag} />
      <div className="poster-rail" style={{ marginBottom: 24 }}>
        {data.items.map((i) => <div className="rail-item" key={i.key}>{card(i)}</div>)}
      </div>
    </Section>
  );
}

// Under a card: mark its episode watched, and open the series' tags (add one, or
// remove the last one to take the series out of this overview).
function CardActions({ item, onWatched, onTagsChanged }: {
  item: WhatsNextItem; onWatched: () => Promise<void>; onTagsChanged: () => void;
}) {
  const { t } = useT();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const watched = async () => {
    setBusy(true);
    try { await onWatched(); } finally { setBusy(false); }
  };
  return (
    <div className="whatsnext-actions">
      <div className="row" style={{ gap: 4 }}>
        {item.episode_id && (
          <button type="button" className="btn-ghost btn-sm" disabled={busy} onClick={watched}
            title={t("whatsnext.markWatched")} aria-label={`${t("whatsnext.markWatched")}: ${item.title}`}>
            <IconCheck width={16} height={16} />
          </button>
        )}
        <button type="button" className="btn-ghost btn-sm" aria-expanded={open}
          title={t("whatsnext.tags")} aria-label={`${t("whatsnext.tags")}: ${item.title}`}
          onClick={() => setOpen((v) => !v)}>
          <IconTag width={16} height={16} />
        </button>
      </div>
      {open && (
        <TagChips tags={item.tags} canEdit
          attach={(tagId) => api.post(`/titles/${item.title_id}/tags/${tagId}`)}
          detach={(tagId) => api.del(`/titles/${item.title_id}/tags/${tagId}`)}
          onChange={onTagsChanged} />
      )}
    </div>
  );
}
