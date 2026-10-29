import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { expectNoA11yViolations } from "../test/a11y";
import { renderWithApp } from "../test/render";
import type { WhatsNextItem } from "../components/WhatsNext";
import { WhatsNextPage } from "./WhatsNext";

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
  tags: [FOLLOW], state: "aired", season: 1, episode: 2, episode_id: "ep-12", episode_name: "Aldhani",
  air_date: "2026-10-01", air_at: null, available_at: null, behind: 0, runtime_minutes: 45,
  remaining: 3, total: 10, ...over,
});

function serve(respond: (params: Record<string, unknown>) => unknown) {
  apiMock.get.mockImplementation((path: string, params?: Record<string, unknown>) => {
    if (path === "/auth/status") return Promise.resolve({ bootstrapped: true, user });
    if (path === "/preferences") return Promise.resolve({ theme: "system", accent: "#f0a21a", language: "en", expert: false, default_profile: "user-1" });
    if (path === "/profiles") return Promise.resolve([]);
    if (path === "/stats/whats-next") return Promise.resolve(respond(params ?? {}));
    return Promise.reject(new Error(`Unexpected GET ${path}`));
  });
}

describe("WhatsNextPage", () => {
  beforeEach(() => { apiMock.get.mockReset(); });

  it("asks for the full list and shows every tagged series with how many episodes are left", async () => {
    serve(() => ({
      tags: [{ ...FOLLOW, count: 3 }, { ...BINGE, count: 1 }],
      items: [
        item({ key: "1", title_id: "t1", title: "Andor" }),
        item({ key: "2", title_id: "t2", title: "Shogun", state: "caught_up", season: null, episode: null,
          episode_id: null, air_date: null, remaining: 0, total: 10 }),
        item({ key: "3", title_id: "t3", title: "Silo", state: "pending", season: null, episode: null,
          episode_id: null, remaining: null, total: null }),
      ],
    }));
    const { container } = renderWithApp(<WhatsNextPage />);

    expect(await screen.findByRole("heading", { name: "What's next" })).toBeInTheDocument();
    await waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/stats/whats-next", expect.objectContaining({ all: 1 })));
    expect(screen.getByRole("link", { name: /Andor/ })).toHaveAttribute("href", "/title/t1");
    expect(screen.getByText("S1·E2 · 3 left")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Shogun/ })).toBeInTheDocument();     // fully watched, still listed
    expect(screen.getByText("Caught up")).toBeInTheDocument();
    expect(screen.getByText("Waiting for episode info")).toBeInTheDocument();
    await expectNoA11yViolations(container);
  });

  it("filters by tag and keeps asking for the full list", async () => {
    serve((params) => ({
      tags: [{ ...FOLLOW, count: 2 }, { ...BINGE, count: 1 }],
      items: params.tag === "tg-b" ? [item({ key: "b", title_id: "tb", title: "Binge Show", tags: [BINGE] })]
        : [item({ key: "a", title: "Andor" }), item({ key: "b", title_id: "tb", title: "Binge Show", tags: [FOLLOW, BINGE] })],
    }));
    renderWithApp(<WhatsNextPage />);
    fireEvent.click(await screen.findByRole("button", { name: /Binge/ }));
    await waitFor(() => expect(apiMock.get).toHaveBeenCalledWith("/stats/whats-next",
      expect.objectContaining({ tag: "tg-b", all: 1 })));
    await waitFor(() => expect(screen.queryByRole("link", { name: /Andor/ })).toBeNull());
  });

  it("explains how to tag a series while nothing is tagged", async () => {
    serve(() => ({ tags: [], items: [] }));
    renderWithApp(<WhatsNextPage />);
    expect(await screen.findByText("Nothing tagged yet")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Imports/ })).toHaveAttribute("href", "/imports");
  });
});
