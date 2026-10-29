import { screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError } from "../lib/api";
import { fmtDate } from "../lib/format";
import { expectNoA11yViolations } from "../test/a11y";
import { renderWithApp } from "../test/render";
import { RunningSeries, type RunningSeriesItem } from "./RunningSeries";

const apiMock = vi.hoisted(() => ({
  get: vi.fn(), post: vi.fn(), put: vi.fn(), patch: vi.fn(), del: vi.fn(), upload: vi.fn(),
}));

vi.mock("../lib/api", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../lib/api")>();
  return { ...actual, api: apiMock };
});

vi.mock("../lib/branding", () => ({
  applyBrandIcons: vi.fn(),
  applyBrandManifest: vi.fn(),
}));

const user = (permissions: string[]) => ({
  id: "user-1", display_name: "Synthetic Viewer", is_admin: false,
  household_id: "household-1", household_name: "Test Household", permissions,
});

const item = (over: Partial<RunningSeriesItem>): RunningSeriesItem => ({
  sonarr_id: 12, title: "Severance", year: 2022, network: "Apple TV+", poster: null,
  next_airing: "2026-11-07T02:00:00Z", episodes_have: 18, episodes_total: 19, seasons: 2, tmdb_id: 95396,
  taggable: true, title_id: null, tags: [], ...over,
});

const FOLLOW = { id: "tag-1", name: "Follow", color: "#f0a21a" };

function serve(series: RunningSeriesItem[], { permissions = ["catalog.read", "ingest.write"], synced = "2026-10-29T00:00:00Z" } = {}) {
  apiMock.get.mockImplementation((path: string) => {
    if (path === "/auth/status") return Promise.resolve({ bootstrapped: true, user: user(permissions) });
    if (path === "/preferences") return Promise.resolve({ theme: "system", accent: "#f0a21a", language: "en", expert: false, default_profile: "user-1" });
    if (path === "/profiles") return Promise.resolve([]);
    if (path === "/connections/c1/series") return Promise.resolve({ synced_at: synced, series });
    if (path === "/tags") return Promise.resolve([FOLLOW]);
    return Promise.reject(new Error(`Unexpected GET ${path}`));
  });
}

describe("RunningSeries", () => {
  beforeEach(() => { apiMock.get.mockReset(); apiMock.post.mockReset(); apiMock.del.mockReset(); });

  it("lists the running series with episodes, next airing and tags, linking titles in the catalog", async () => {
    serve([
      item({ title_id: "t-sev", tags: [FOLLOW] }),
      item({ sonarr_id: 14, title: "Andor", year: 2022, network: "Disney+", episodes_have: 12, episodes_total: 24, next_airing: null }),
    ]);
    renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    expect(await screen.findByRole("link", { name: "Severance" })).toHaveAttribute("href", "/title/t-sev");
    expect(screen.getByText(`Apple TV+ · 18/19 episodes · next: ${fmtDate("2026-11-07T02:00:00Z")}`)).toBeInTheDocument();
    expect(screen.getByText("Disney+ · 12/24 episodes · no next date")).toBeInTheDocument();
    expect(screen.getByText("Follow")).toBeInTheDocument();                       // the existing tag
    expect(screen.queryByRole("link", { name: "Andor" })).toBeNull();             // not in the catalog yet
  });

  it("tags a series through the connection's own endpoint, not the title endpoint", async () => {
    serve([item({})]);
    apiMock.post.mockResolvedValue({ ok: true, title_id: "t-new", created: true });
    const { user: actor } = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    await actor.click(await screen.findByRole("button", { name: "Tag" }));
    await actor.click(await screen.findByRole("button", { name: "Follow" }));

    expect(apiMock.post).toHaveBeenCalledWith("/connections/c1/series/12/tags/tag-1");
  });

  it("removes a tag the same way", async () => {
    serve([item({ title_id: "t-sev", tags: [FOLLOW] })]);
    apiMock.del.mockResolvedValue({ ok: true, title_id: "t-sev" });
    const { user: actor } = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    await actor.click(await screen.findByRole("button", { name: "Remove" }));
    expect(apiMock.del).toHaveBeenCalledWith("/connections/c1/series/12/tags/tag-1");
  });

  it("explains instead of offering a tag button when Sonarr gave no TMDB id", async () => {
    serve([item({ taggable: false, tmdb_id: null })]);
    renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    expect(await screen.findByText(/no TMDB id/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Tag" })).toBeNull();
  });

  it("is read-only without ingest.write", async () => {
    serve([item({ tags: [FOLLOW], title_id: "t-sev" })], { permissions: ["catalog.read"] });
    renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    expect(await screen.findByText("Follow")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Tag" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Remove" })).toBeNull();
  });

  it("reports a failed tag and does not claim success", async () => {
    serve([item({})]);
    apiMock.post.mockRejectedValue(new ApiError(422, "Sonarr did not report a TMDB id for this series"));
    const { user: actor } = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);

    await actor.click(await screen.findByRole("button", { name: "Tag" }));
    await actor.click(await screen.findByRole("button", { name: "Follow" }));

    expect(await screen.findByText("Sonarr did not report a TMDB id for this series")).toBeInTheDocument();
    expect(screen.queryByText("Follow", { selector: ".tag-chip" })).toBeNull();
  });

  it("says what to do before the first sync, and when nothing is running", async () => {
    serve([], { synced: null as unknown as string });
    const first = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);
    expect(await screen.findByText(/Press Sync/)).toBeInTheDocument();
    first.unmount();

    serve([]);
    renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);
    expect(await screen.findByText(/No running series/)).toBeInTheDocument();
  });

  it("reloads when the parent bumps reloadKey after a Sync", async () => {
    serve([item({})]);
    const view = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);
    await screen.findByText("Severance", { exact: false });
    const calls = () => apiMock.get.mock.calls.filter((c) => c[0] === "/connections/c1/series").length;
    expect(calls()).toBe(1);
    view.rerender(<RunningSeries connectionId="c1" reloadKey={1} />);
    await waitFor(() => expect(calls()).toBe(2));
  });

  it("has no detectable accessibility violations", async () => {
    serve([item({ title_id: "t-sev", tags: [FOLLOW] }), item({ sonarr_id: 15, title: "Odd", taggable: false, tmdb_id: null })]);
    const { container } = renderWithApp(<RunningSeries connectionId="c1" reloadKey={0} />);
    await screen.findByRole("link", { name: "Severance" });
    await expectNoA11yViolations(container);
    within(container).getByText("Odd", { exact: false });
  });
});
