import { Link } from "react-router-dom";
import { useApp } from "../lib/app";
import { useT } from "../lib/i18n";
import { api } from "../lib/api";
import { useFetch } from "../lib/useFetch";
import { fmtDate } from "../lib/format";
import { ErrorState, Loading } from "./ui";
import { TagChips, type Tag } from "./TagChips";
import { IconTv } from "./icons";

export interface RunningSeriesItem {
  sonarr_id: number;
  title: string;
  year: number | null;
  network: string | null;
  poster: string | null;
  next_airing: string | null;
  episodes_have: number | null;
  episodes_total: number | null;
  seasons: number | null;
  tmdb_id: number | null;
  /** false when Sonarr gave no TMDB id: the series cannot be bound to a catalog title. */
  taggable: boolean;
  title_id: string | null;
  tags: Tag[];
}

// The series a Sonarr connection reports as running, each with its tags. Tagging a
// series adds it to the WatchVault catalog (so it can feed the "What's next"
// overview); the tag endpoints are the connection's, because the title may not
// exist yet. `reloadKey` is bumped by the parent after a Sync.
export function RunningSeries({ connectionId, reloadKey }: { connectionId: string; reloadKey: number }) {
  const { t } = useT();
  const { can } = useApp();
  const { data, loading, error, reload, refresh } = useFetch<{ synced_at: string | null; series: RunningSeriesItem[] }>(
    () => api.get(`/connections/${connectionId}/series`), [connectionId, reloadKey]);

  if (loading && !data) return <Loading />;
  if (error && !data) return <ErrorState error={error} retry={reload} />;
  const series = data?.series ?? [];

  return (
    <div>
      <label>{t("imports.runningSeries")}</label>
      <p className="caption" style={{ marginBottom: 10 }}>{t("imports.series.help")}</p>
      {series.length === 0 ? (
        <p className="caption">{data?.synced_at ? t("imports.series.empty") : t("imports.series.syncFirst")}</p>
      ) : (
        <div className="col" style={{ gap: 0 }}>
          {series.map((s) => (
            <div key={s.sonarr_id} className="list-row" style={{ alignItems: "flex-start", gap: 12 }}>
              <span className="imp-thumb" aria-hidden="true">
                {s.poster ? <img src={s.poster} alt="" loading="lazy" /> : <span className="imp-thumb-ph"><IconTv width={18} height={18} /></span>}
              </span>
              <div className="col" style={{ flex: 1, gap: 4, minWidth: 0 }}>
                <strong>
                  {s.title_id ? <Link to={`/title/${s.title_id}`}>{s.title}</Link> : s.title}
                  {s.year ? <span className="caption"> ({s.year})</span> : null}
                </strong>
                <span className="caption">
                  {[s.network,
                    s.episodes_total != null ? t("imports.series.episodes", { have: s.episodes_have ?? 0, total: s.episodes_total }) : null,
                    s.next_airing ? t("imports.series.next", { date: fmtDate(s.next_airing) }) : t("imports.series.noDate"),
                  ].filter(Boolean).join(" · ")}
                </span>
                {s.taggable ? (
                  <TagChips tags={s.tags} canEdit={can("ingest.write")}
                    attach={async (tagId) => { await api.post(`/connections/${connectionId}/series/${s.sonarr_id}/tags/${tagId}`); }}
                    detach={async (tagId) => { await api.del(`/connections/${connectionId}/series/${s.sonarr_id}/tags/${tagId}`); }}
                    onChange={refresh} />
                ) : (
                  <span className="caption">{t("imports.series.noTmdb")}</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
