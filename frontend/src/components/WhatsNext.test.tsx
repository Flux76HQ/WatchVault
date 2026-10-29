import { fireEvent, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { expectNoA11yViolations } from "../test/a11y";
import { renderWithApp } from "../test/render";
import { WhatsNext, type WhatsNextItem } from "./WhatsNext";

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

const FOLLOW = { id: "tg-f", name: "Follow", color: "#f0a21a" };
const BINGE = { id: "tg-b", name: "Binge", color: null };

const item = (over: Partial<WhatsNextItem>): WhatsNextItem => ({
  key: "w:t1", title_id: "t1", title: "Andor", year: 2022, kind: "series", poster: null,
  tags: [FOLLOW], state: "aired", season: 1, episode: 2, episode_name: "Aldhani",
  air_date: "2026-10-01", air_at: null, available_at: null, behind: 0, runtime_minutes: 45, ...over,
});

const tags = (n = 2) => [{ ...FOLLOW, count: n }, { ...BINGE, count: 1 }];

function serve(respond: (params: Record<string, unknown>) => unknown) {
  apiMock.get.mockImplementation((path: string, params?: Record<string, unknown>) => {
    if (path === "/auth/status") return Promise.resolve({ bootstrapped: true, user });
    if (path === "/preferences") return Promise.resolve({ theme: "system", accent: "#f0a21a", language: "en", expert: false, default_profile: "user-1" });
    if (path === "/profiles") return Promise.resolve([]);
    if (path === "/stats/whats-next") return Promise.resolve(respond(params ?? {}));
    return Promise.reject(new Error(`Unexpected GET ${path}`));
  });
}

describe("WhatsNext", () => {
  beforeEach(() => { apiMock.get.mockReset(); });

  it("renders nothing while no series is tagged", async () => {
    serve(() => ({ tags: [], items: [] }));
    const { container } = renderWithApp(<WhatsNext scope="user-1" />);
    await vi.waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/stats/whats-next", { profile: "user-1" }));
    expect(container.querySelector(".poster-rail")).toBeNull();
    expect(screen.queryByText("What's next")).toBeNull();
  });

  it("shows each state with its badge and subtitle, linking to the title page", async () => {
    serve(() => ({
      tags: tags(),
      items: [
        item({ key: "1", title_id: "t1", title: "Andor", state: "ready", behind: 2 }),
        item({ key: "2", title_id: "t2", title: "Severance", state: "aired" }),
        item({ key: "3", title_id: "t3", title: "Silo", state: "upcoming", season: 3, episode: 1, air_date: "2026-11-05" }),
        item({ key: "4", title_id: "t4", title: "Slow Horses", state: "upcoming", season: 5, episode: 1, air_date: null }),
        item({ key: "5", title_id: "t5", title: "Shogun", state: "caught_up", season: null, episode: null, air_date: "2026-11-09" }),
        item({ key: "6", title_id: "t6", title: "Fresh Show", state: "pending", season: null, episode: null, air_date: null }),
      ],
    }));
    const { container } = renderWithApp(<WhatsNext scope="user-1" />);

    expect(await screen.findByRole("heading", { name: "What's next" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Andor/ })).toHaveAttribute("href", "/title/t1");
    expect(screen.getByText("S1·E2 · +2 more")).toBeInTheDocument();           // ready, two more waiting
    expect(screen.getByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Aired")).toBeInTheDocument();
    expect(screen.getByText("S3·E1")).toBeInTheDocument();
    expect(screen.getByText("TBA")).toBeInTheDocument();
    expect(screen.getByText("Caught up")).toBeInTheDocument();
    expect(screen.getByText("Waiting for episode info")).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it("filters by tag through the chips and fetches again with that tag", async () => {
    serve((params) => ({
      tags: tags(),
      items: params.tag === "tg-b" ? [item({ key: "b", title_id: "tb", title: "Binge Show", tags: [BINGE] })]
        : [item({ key: "a", title: "Andor" }), item({ key: "b", title_id: "tb", title: "Binge Show", tags: [FOLLOW, BINGE] })],
    }));
    renderWithApp(<WhatsNext scope="all" />);

    const all = await screen.findByRole("button", { name: "All" });
    expect(all).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("link", { name: /Andor/ })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Binge/ }));
    await vi.waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/stats/whats-next", { profile: "all", tag: "tg-b" }));
    await vi.waitFor(() => expect(screen.queryByRole("link", { name: /Andor/ })).toBeNull());
    expect(screen.getByRole("button", { name: /Binge/ })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "All" })).toHaveAttribute("aria-pressed", "false");

    fireEvent.click(screen.getByRole("button", { name: /Binge/ }));            // click again clears the filter
    await vi.waitFor(() => expect(screen.getByRole("link", { name: /Andor/ })).toBeInTheDocument());
  });

  it("drops a filter whose tag has nothing left to show", async () => {
    let calls = 0;
    serve((params) => {
      calls += 1;
      return params.tag === "tg-b" && calls > 1
        ? { tags: [{ ...FOLLOW, count: 1 }], items: [] }
        : { tags: tags(), items: [item({ key: "a" })] };
    });
    renderWithApp(<WhatsNext scope="all" />);
    fireEvent.click(await screen.findByRole("button", { name: /Binge/ }));
    await vi.waitFor(() => expect(apiMock.get).toHaveBeenLastCalledWith("/stats/whats-next", { profile: "all" }));
  });
});
