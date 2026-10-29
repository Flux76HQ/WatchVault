import { screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { expectNoA11yViolations } from "../test/a11y";
import { renderWithApp } from "../test/render";
import { ContinueWatching, type ContinueItem } from "./ContinueWatching";

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

const user = {
  id: "user-1", display_name: "Synthetic Viewer", is_admin: false,
  household_id: "household-1", household_name: "Test Household",
  permissions: ["catalog.read"],
};

const item = (over: Partial<ContinueItem>): ContinueItem => ({
  key: "k", origin: "ready", kind: "movie", title_id: null, title: "Arrival", poster: null,
  season: null, episode: null, episode_name: null, progress: null, remaining_minutes: null,
  more: 0, provider: { key: "radarr", name: "Radarr", color: null }, profile: null, ...over,
});

function serve(items: ContinueItem[]) {
  apiMock.get.mockImplementation((path: string) => {
    if (path === "/auth/status") return Promise.resolve({ bootstrapped: true, user });
    if (path === "/preferences") return Promise.resolve({ theme: "system", accent: "#f0a21a", language: "en", expert: false, default_profile: "user-1" });
    if (path === "/profiles") return Promise.resolve([]);
    if (path === "/stats/continue") return Promise.resolve(items);
    return Promise.reject(new Error(`Unexpected GET ${path}`));
  });
}

describe("ContinueWatching", () => {
  beforeEach(() => { apiMock.get.mockReset(); });

  it("renders nothing while there is nothing to continue", async () => {
    serve([]);
    const { container } = renderWithApp(<ContinueWatching scope="user-1" />);
    await vi.waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/stats/continue", { profile: "user-1" }));
    expect(container.querySelector(".poster-rail")).toBeNull();
    expect(screen.queryByText("Continue watching")).toBeNull();
  });

  it("shows partial playback with what is left, and links titles that are in the catalog", async () => {
    serve([item({ key: "p", origin: "partial", kind: "series", title_id: "t-sev", title: "Severance",
      season: 2, episode: 3, progress: 40, remaining_minutes: 30,
      provider: { key: "plex", name: "Plex", color: null }, profile: "Helmer" })]);
    renderWithApp(<ContinueWatching scope="user-1" />);

    const link = await screen.findByRole("link", { name: /Severance/ });
    expect(link).toHaveAttribute("href", "/title/t-sev");
    expect(screen.getByText("S2·E3 · 30 min left")).toBeInTheDocument();
    expect(screen.getByText("Local Library")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Continue watching" })).toBeInTheDocument();
  });

  it("shows ready items without a title page as plain tiles, and collapsed episodes as '+n more'", async () => {
    serve([
      item({ key: "a", title: "Dune" }),
      item({ key: "b", kind: "series", title: "Andor", season: 1, episode: 1, more: 2 }),
    ]);
    const { container } = renderWithApp(<ContinueWatching scope="user-1" />);

    expect(await screen.findByText("Ready to watch")).toBeInTheDocument();
    expect(screen.getByText("S1·E1 · +2 more")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: /Dune/ })).toBeNull();   // nothing to open
    expect(screen.getAllByText("New")).toHaveLength(2);
    await expectNoA11yViolations(container);
  });

  it("names whose half-watched item it is in the household view only", async () => {
    const half = item({ key: "p", origin: "partial", title: "Heat", remaining_minutes: 15, profile: "Sam",
      provider: { key: "plex", name: "Plex", color: null } });
    serve([half]);
    const household = renderWithApp(<ContinueWatching scope="all" />);
    expect(await screen.findByText("Sam · 15 min left")).toBeInTheDocument();
    household.unmount();

    serve([half]);
    renderWithApp(<ContinueWatching scope="user-1" />);
    expect(await screen.findByText("15 min left")).toBeInTheDocument();
  });
});
