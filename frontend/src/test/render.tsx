import { render, type RenderOptions } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement, ReactNode } from "react";
import { MemoryRouter } from "react-router-dom";

import { AppProvider } from "../lib/app";

interface AppRenderOptions extends Omit<RenderOptions, "wrapper"> {
  initialEntries?: string[];
}

export function renderWithApp(
  element: ReactElement,
  { initialEntries = ["/"], ...options }: AppRenderOptions = {},
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <MemoryRouter initialEntries={initialEntries}>
        <AppProvider>{children}</AppProvider>
      </MemoryRouter>
    );
  }

  return {
    user: userEvent.setup(),
    ...render(element, { wrapper: Wrapper, ...options }),
  };
}
