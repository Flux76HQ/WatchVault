import { act, fireEvent, render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { edgeScrollSpeed, useEdgeAutoScroll } from "./LayoutEdit";

function Probe({ active }: { active: boolean }) {
  useEdgeAutoScroll(active);
  return null;
}

const dragover = (clientY: number) => {
  const e = new Event("dragover", { bubbles: true, cancelable: true });
  Object.defineProperty(e, "clientY", { value: clientY });
  window.dispatchEvent(e);
};

describe("edgeScrollSpeed", () => {
  it("scrolls up near the top, down near the bottom and not in between", () => {
    expect(edgeScrollSpeed(0, 800)).toBeLessThan(0);
    expect(edgeScrollSpeed(799, 800)).toBeGreaterThan(0);
    expect(edgeScrollSpeed(400, 800)).toBe(0);
    expect(edgeScrollSpeed(90, 800)).toBe(0);
  });

  it("speeds up towards the edge", () => {
    expect(Math.abs(edgeScrollSpeed(5, 800))).toBeGreaterThan(Math.abs(edgeScrollSpeed(60, 800)));
    expect(edgeScrollSpeed(795, 800)).toBeGreaterThan(edgeScrollSpeed(740, 800));
  });

  it("shrinks the zone on a very short window so the middle stays free", () => {
    expect(edgeScrollSpeed(100, 200)).toBe(0);
  });
});

describe("useEdgeAutoScroll", () => {
  let frames: FrameRequestCallback[];
  const step = () => act(() => { const run = frames; frames = []; run.forEach((f) => f(0)); });

  beforeEach(() => {
    frames = [];
    vi.spyOn(window, "requestAnimationFrame").mockImplementation((cb) => { frames.push(cb); return frames.length; });
    vi.spyOn(window, "cancelAnimationFrame").mockImplementation(() => { frames = []; });
    window.scrollBy = vi.fn();
    Object.defineProperty(window, "innerHeight", { value: 800, configurable: true });
  });
  afterEach(() => vi.restoreAllMocks());

  it("scrolls the window towards the edge the pointer is at while dragging", () => {
    render(<Probe active />);
    dragover(10); step();
    expect(window.scrollBy).toHaveBeenLastCalledWith(0, expect.any(Number));
    expect((window.scrollBy as any).mock.calls.at(-1)[1]).toBeLessThan(0);

    dragover(790); step();
    expect((window.scrollBy as any).mock.calls.at(-1)[1]).toBeGreaterThan(0);

    (window.scrollBy as any).mockClear();
    dragover(400); step();
    expect(window.scrollBy).not.toHaveBeenCalled();
  });

  it("does nothing while not dragging, and stops when the drag ends", () => {
    const { rerender, unmount } = render(<Probe active={false} />);
    dragover(5); step();
    expect(window.scrollBy).not.toHaveBeenCalled();

    rerender(<Probe active />);
    dragover(5); step();
    expect(window.scrollBy).toHaveBeenCalledTimes(1);

    rerender(<Probe active={false} />);
    dragover(5); step();
    expect(window.scrollBy).toHaveBeenCalledTimes(1);
    unmount();
    fireEvent.dragOver(window, { clientY: 5 });
  });
});
