/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2022-present David G. Simmons
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { act } from "react";

import DocsPanel from "../../components/DocsPanel";

type DocsApiResponse = {
  docs: Array<{ id: string; name: string; path: string }>;
  site_built?: boolean;
};

describe("DocsPanel", () => {
  beforeEach(() => {
    const docs: DocsApiResponse["docs"] = [
      { id: "index", name: "Home", path: "" },
      { id: "changelog", name: "Changelog", path: "changelog" },
      {
        id: "getting-started_installation",
        name: "Getting Started: Installation",
        path: "getting-started/installation",
      },
      {
        id: "getting-started_quickstart",
        name: "Getting Started: Quick Start",
        path: "getting-started/quickstart",
      },
    ];

    vi.stubGlobal(
      "fetch",
      vi.fn(async () => {
        return {
          ok: true,
          json: async () =>
            ({
              docs,
              site_built: true,
            }) satisfies DocsApiResponse,
        } as unknown as Response;
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("updates the selected doc when iframe reports navigation", async () => {
    render(<DocsPanel isOpen={true} onClose={() => {}} />);

    // Wait for initial docs to load and render a known item.
    await screen.findByText("Changelog");

    // Fetch resolves outside React's `act`; the message listener is registered in a
    // passive effect. Flush macrotasks so CI does not dispatch before `onMessage`
    // is attached (local runs often "win" by timing alone).
    await act(async () => {
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
    });

    // Simulate navigation inside the iframe to a Getting Started page.
    act(() => {
      window.dispatchEvent(
        new MessageEvent("message", {
          origin: window.location.origin,
          data: {
            type: "duckling-docs:navigate",
            pathname: "/api/docs/site/en/getting-started/installation/",
          },
        })
      );
    });

    // The panel should expand "Getting Started" and select "Installation".
    await waitFor(
      () => {
        const installationBtn = screen.getByRole("button", {
          name: "Installation",
        });
        expect(installationBtn).toHaveClass("bg-primary-500/20");
        expect(installationBtn).toHaveClass("text-primary-400");
      },
      { timeout: 5000 }
    );
  });
});

