import { renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useFetch } from "./useFetch";

function deferred<T>() {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((done) => {
    resolve = done;
  });
  return { promise, resolve };
}

describe("useFetch", () => {
  it("ignores an older response after dependencies start a newer request", async () => {
    const first = deferred<string>();
    const second = deferred<string>();
    const { result, rerender } = renderHook(
      ({ scope }) => useFetch(() => scope === "all" ? first.promise : second.promise, [scope]),
      { initialProps: { scope: "all" } },
    );

    rerender({ scope: "profile-1" });
    second.resolve("profile response");
    await waitFor(() => expect(result.current.data).toBe("profile response"));

    first.resolve("stale household response");
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toBe("profile response");
  });
});
