import { useApp } from "../lib/app";
import { useT, providerLabel } from "../lib/i18n";
import { api } from "../lib/api";
import { useFetch } from "../lib/useFetch";
import { Poster, Section } from "./ui";

export interface ContinueItem {
  key: string;
  /** 'partial' = stopped part-way (live scrobbles); 'ready' = downloaded per Sonarr/Radarr, not watched yet. */
  origin: "partial" | "ready";
  kind: "movie" | "series";
  title_id: string | null;
  title: string;
  poster: string | null;
  season: number | null;
  episode: number | null;
  episode_name: string | null;
  progress: number | null;
  remaining_minutes: number | null;
  more: number;
  provider: { key: string; name: string; color: string | null } | null;
  profile: string | null;
}

export const CONTINUE_DAYS_MAX = 30;
export const CONTINUE_DAYS_DEFAULT = 14;

/** The "ready to watch" period in whole days, 0 (today only) to 30; anything else -> the default. */
export function clampContinueDays(value: unknown): number {
  const n = typeof value === "number" ? value : Number(value);
  if (value == null || value === "" || !Number.isFinite(n)) return CONTINUE_DAYS_DEFAULT;
  return Math.max(0, Math.min(CONTINUE_DAYS_MAX, Math.floor(n)));
}

// "Continue watching": what was left half-watched, and what Sonarr/Radarr have
// downloaded that nobody has watched yet. Invisible while there is nothing to
// show, so a household without those sources never sees an empty block.
export function ContinueWatching({ scope }: { scope: string }) {
  const { t } = useT();
  const { prefs } = useApp();
  // How far back downloads from Sonarr/Radarr still count (Settings → Appearance).
  const days = clampContinueDays(prefs.continueDays);
  const { data } = useFetch<ContinueItem[]>(
    () => api.get("/stats/continue", { profile: scope, days }), [scope, days]);
  if (!data || data.length === 0) return null;

  const subtitle = (i: ContinueItem): string => {
    const ep = i.kind === "series" && i.season != null && i.episode != null ? `S${i.season}·E${i.episode}` : "";
    const detail = i.origin === "partial"
      ? (i.remaining_minutes != null ? t("continue.left", { min: i.remaining_minutes }) : "")
      : (i.more > 0 ? t("continue.more", { n: i.more }) : t("continue.ready"));
    // In the household view say whose half-watched item it is.
    const who = scope === "all" && i.origin === "partial" ? i.profile ?? "" : "";
    return [who, ep, detail].filter(Boolean).join(" · ");
  };

  return (
    <Section title={t("dashboard.continue")}>
      <div className="poster-rail" style={{ marginBottom: 24 }}>
        {data.map((i) => (
          <div className="rail-item" key={i.key}>
            <Poster
              to={i.title_id ? `/title/${i.title_id}` : undefined}
              poster={i.poster} title={i.title} kind={i.kind}
              badge={i.origin === "partial" && i.provider
                ? providerLabel(t, i.provider.key, i.provider.name)
                : t("continue.badgeReady")}
              subtitle={subtitle(i)} progress={i.progress} />
          </div>
        ))}
      </div>
    </Section>
  );
}
