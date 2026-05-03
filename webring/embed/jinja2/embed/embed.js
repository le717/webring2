/*! webring2 v{{ app.version }} - {{ app.software }} */
(async function() {
  "use strict";
  // TODO: All of this needs to be working to be a class or methods that can be invoked
  /**
   * Fetch data from the webring.
   * @param {Number} page The page number to be loaded.
   * @returns {Promise<JSON>}
   */
  async function fetchWebring(page = 1) {
    let url = new URL("{{ base_url }}/");
    url.searchParams.set("page", page.toString());
    return await fetch(url, {
      method: "get"
    }).then(r => r.json())
  }

  const qWebringEmbedArea = document.querySelector("#webring-embed-area");

  let webring = await fetchWebring();
  console.log(webring);

  // If there's no embed area or no weblinks, we can't do anything
  if (qWebringEmbedArea === null) {
    return null;
  }
  if (webring.meta === null) {
    qWebringEmbedArea.innerHTML = `<p class="webring-not-found">Unable to load webring.</p>`
    return;
  }

  // Display the webring title and desc
  qWebringEmbedArea.innerHTML = `<p class="webring-title">${webring.meta.name}</p>
  <p class="webring-description">${webring.meta.description}</p>`;

  // Generate the markup for each item in the webring
  const markup = ["<ul>"];
  webring.entries.forEach((item) => {
    markup.push(
      `<li>
        <a class="webring-entry-title" href="${item.url}">${item.title}</a><br>
        <span class="webring-entry-description">${item.description}</span>
      </li>`
    );
  });
  markup.push("</ul>");
  qWebringEmbedArea.insertAdjacentHTML("beforeend", markup.join(""));

  // TODO: Generate navigation controls
  if (webring.page) {
    const controls = [`<div class="webring-navigation">`];
    if (webring.page.current_page === webring.page.total_pages) {
      controls.push(`<p>Showing all entries</p>`)
    }
    if (webring.page.has_prev_page) {

    }
    if (webring.page.has_next_page) {

    }
    controls.push("</div>");
    qWebringEmbedArea.insertAdjacentHTML("beforeend", controls.join(""));
  }
}());
