// htmx.esm.js assigns window.htmx itself, which the hx-ws extension script relies on
import htmx from "htmx.org";

// htmx 4 swaps 4xx/5xx responses by default; keep the htmx 2 behavior of ignoring error responses entirely.
// noSwap alone still applies the error page's OOB elements and hx-push-url, so cancel the swap too.
// Elements can still opt in to swapping an error status with hx-status (e.g. hx-status:422="swap:innerHTML").
htmx.config.noSwap = [204, 304, "4xx", "5xx"];
document.addEventListener("htmx:before:swap", (evt) => {
  const ctx = evt.detail.ctx;
  if (ctx.response?.status >= 400 && ctx.swap === "none") evt.preventDefault();
});
