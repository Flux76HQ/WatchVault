import axe, { type AxeResults } from "axe-core";

export async function expectNoA11yViolations(container: Element): Promise<AxeResults> {
  const results = await axe.run(container);
  if (results.violations.length > 0) {
    const summary = results.violations
      .map((violation) => `${violation.id}: ${violation.help}`)
      .join("\n");
    throw new Error(`Accessibility violations:\n${summary}`);
  }
  return results;
}
