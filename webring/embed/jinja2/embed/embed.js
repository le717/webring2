/*! webring2 v{{ app.version }} - {{ app.software }} */
class Webring {
  /**
   * Construct a simple display of a webring.
   * @param {String} base_url The base URL of the webring to fetch.
   * @param {String} slug The slug of the webring to fetch.
   * @param {Object} options Filtering options for fetching the webring.
   */
  constructor(base_url, slug, options) {
    this.base_url = base_url;
    this.options = options;
    this.selector = `.webring__embed#${slug}`;
  }

  /**
   * Fetch data from the webring.
   * @param {Number} page The page number to be loaded.
   * @returns {Promise<JSON>} The paginated webring response.
   */
  async fetch(page = 1) {
    let url = new URL(`${this.base_url}/`);

    // Set the query parameters as needed
    url.searchParams.set("page", page.toString());
    url.searchParams.set("include_dead", this.options.include_dead);
    url.searchParams.set("include_origin", this.options.include_origin);
    url.searchParams.set("include_web_archive", this.options.include_web_archive);

    return fetch(url, {
      method: "get",
    }).then((r) => r.json());
  }

  /**
   * Display the webring data.
   * @param {JSON} data The webring data to display.
   */
  display(data) {
    let qEmbedArea = document.querySelector(this.selector);

    // If there's no embed area or no weblinks, we can't do anything
    if (qEmbedArea === null) {
      console.log(`Cannot find DOM element ${this.selector}`);
      return null;
    }
    if (data.meta === null) {
      qEmbedArea.innerHTML = `<p class="webring__not-found">Unable to load webring.</p>`;
      return null;
    }

    // Display the webring title and desc
    qEmbedArea.innerHTML = `<p class="webring__title">${data.meta.name}</p>
      <p class="webring__description">${data.meta.description}</p>`;

    // Handle no entries in this webring
    if (data.entries.length === 0) {
      qEmbedArea.insertAdjacentHTML(
        "beforeend",
        `<p class="webring__no_entries">There are no entries in this webring.</p>`
      );
      return null;
    }
    // Generate the markup for each item in the webring
    const markup = ["<ul>"];
    data.entries.forEach((item) => {
      markup.push(
        `<li>
          <a class="webring__entry__title" href="${item.url}">${item.title}</a><br>
          <span class="webring__entry__description">${item.description}</span>
        </li>`,
      );
    });
    markup.push("</ul>");
    qEmbedArea.insertAdjacentHTML("beforeend", markup.join(""));

    // If there's pagination information, generate navigation controls
    if (data.pagination) {
      let qNavigationArea = document.createElement("div");
      qNavigationArea.classList.add("webring__navigation");

      // If there are no additional pages to cycle through in either direction,
      // change the pagination controls to a simple "all entries" label
      if (!data.pagination.has_prev_page && !data.pagination.has_next_page) {
        qNavigationArea.innerHTML = `<p class="webring__navigation__all_entries">Showing all entries</p>`;
        qEmbedArea.insertAdjacentElement("beforeend", qNavigationArea);
        return null;
      }

      // Create the previous page link
      let qPrevLink = document.createElement("span");
      qPrevLink.innerText = "Previous";
      qPrevLink.classList.add("webring__navigation__link-prev");

      // Describe the link properly depending if we have another page
      qPrevLink.classList.add("disabled", data.pagination.prev_page);
      qNavigationArea.insertAdjacentElement("beforeend", qPrevLink);

      // Use a pipe symbol as the link divider
      qNavigationArea.insertAdjacentHTML("beforeend", "|");

      // Create the next page link
      let qNextLink = document.createElement("span");
      qNextLink.innerText = "Next";
      qNextLink.classList.add("webring__navigation__link-next");

      // Describe the link properly depending if we have another page
      qNextLink.classList.add("disabled", data.pagination.next_page);
      qNavigationArea.insertAdjacentElement("beforeend", qNextLink);

      // Create the page counts
      let qPageCounts = document.createElement("span");
      qPageCounts.classList.add("webring__navigation__page-counts");
      qPageCounts.innerText = `(Page ${data.pagination.current_page} of ${data.pagination.total_pages})`;
      qNavigationArea.insertAdjacentElement("beforeend", qPageCounts);

      // Add the navigational elements to the page
      qEmbedArea.insertAdjacentElement("beforeend", qNavigationArea);

      // Wire up prev/next buttons to paginate
      if (data.pagination.has_prev_page) {
        qPrevLink.addEventListener("click", () => {
          this.fetch(data.pagination.prev_page).then((r) => this.display(r));
        }, { once: true });
      }
      if (data.pagination.has_next_page) {
        qNextLink.addEventListener("click", () => {
          this.fetch(data.pagination.next_page).then((r) => this.display(r));
        }, { once: true });
      }
    }
  }
}

/**
 * Init and display the webring on init page load.
 */
const webring = new Webring(
  "{{ base_url }}", "{{ slug }}", {{ options|safe }}
);

webring.fetch({{ page }}).then((data) => {
  webring.display(data);
});
