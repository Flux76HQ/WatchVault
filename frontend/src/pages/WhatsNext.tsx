import { Link } from "react-router-dom";
import { useApp } from "../lib/app";
import { useT } from "../lib/i18n";
import { Loading, ErrorState, Empty, BackLink } from "../components/ui";
import { TagFilter, useWhatsNext } from "../components/WhatsNext";
import { IconImport } from "../components/icons";

// Every tagged series, not only those with something to watch: the dashboard block
// is the short version of this list.
export function WhatsNextPage() {
  const { scope } = useApp();
  const { t } = useT();
  const { data, loading, error, reload, tag, setTag, card } = useWhatsNext(scope, true);

  if (loading && !data) return <Loading />;
  if (error && !data) return <ErrorState error={error} retry={reload} />;

  return (
    <>
      <BackLink to="/" />
      <div className="section-head dash-head" style={{ marginBottom: 20 }}>
        <h1 className="large-title">{t("dashboard.whatsNext")}</h1>
      </div>
      {data && data.tags.length > 0 ? (
        <>
          <TagFilter tags={data.tags} tag={tag} onChange={setTag} />
          <div className="poster-grid">
            {data.items.map((i) => <div key={i.key}>{card(i)}</div>)}
          </div>
        </>
      ) : (
        <Empty
          title={t("whatsnext.emptyTitle")}
          hint={t("whatsnext.emptyHint")}
          action={<Link to="/imports" className="btn btn-primary"><IconImport width={18} height={18} /> {t("nav.imports")}</Link>}
        />
      )}
    </>
  );
}
