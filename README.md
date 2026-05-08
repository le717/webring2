# Webring2

> Because everything on the Web eventually loops back onto itself.

## Features
- Multiple webrings per application instance
- JavaScript to alow simple embedding and display
- ~~Linkrot checking, with Web Archive fallback url for dead links (when possible)~~
- ~~Optional linkrot event logging to [Discord](https://discord.com/) channel~~

> ℹ️ **Note** <br>
If you are want to run an instance of Webring2 yourself, jump to [Development](#development).
Otherwise, read on to learn about its features.

### What's new in Webring2?
This project is a complete rewrite of my earlier [Webring](https://github.com/le717/webring) project.
I did this because I wanted to expand or complete functionality in the original project, but due to
time, knowledge, and tech-stack differences, it was easier to rewrite it than continue development.

The following items are new or different in Webring2:
* Developed in the [Django web framework](https://www.djangoproject.com/), rather than
  [Flask](https://flask.palletsprojects.com/en/stable/)
* Multiple rings are supported by a single hosted instance, rather than one ring per instance
* Rings are identifiable by slugs, rather than UUIDs
* Web-based admin interface for instance management of rings and entries
* ~~Rate-limiting on endpoints, to help prevent flooding and DDoS attacks~~ not yet
* Webring and entry soft-deletion, in case of accidental removals
* Entry pagination, for navigation through a ring

Due to these changes, there is no direct upgrade path from the original Webring platform. All
entries will need to be manually added or scripted over to the new platform.

### Filtering entries
Filtering options are available to restrict the requested webring's entries. These filters are
supported on both the root URL and the simple embed endpoints. They are provided through query
parameters to the URLs.

Filtering out the site requesting the webring from the webring entries requires the HTTP `ORIGIN`
header to be properly set for the request.

- `include_dead: Literal["true"] | Literal["false"] = "true"`: Include entries that have been determined to be dead links
- `include_origin: Literal["true"] | Literal["false"] = "false"`: Remove the site requesting the webring from the entries, if present
- `include_web_archive: Literal["true"] | Literal["false"] = "true"`: Include entries that can only be accessed through
  the Web Archive

These default values can also be set globally in the app configuration but will be overridden by
individual requests.

### Entry pagination
Entry pagination is supported via the `page` query string. If possible, a `page` object is provided
in each response providing information about total pages and existence of prior or additional pages.
If a page number is provided that results in no entries, the appropriate information will be
provided to navigate back to the previous, valid page.

### Automatic simple embed
A JavaScript file is provided to generate and embed a simple rendering of a requested webring onto
your website. It includes all required rendering elements in the script, preventing any additional
manual setup. It fully supports pagination and all filtering parameters.

To use it, create an HTML element in your page with a CSS ID of `webring__embed-area`.
If the selector is found and there are entries to display, the webring will be injected
into that area of your site. A simple setup might look as follows, where `<webring-slug>` is the
webring slug you are trying to load:

```html
<!-- Create an area to display the webring -->
<section id="webring__embed-area">
  <noscript>
    The webring could not be loaded because your browser doesn't support JavaScript.
  </noscript>
</section>

<!-- Load the webring -->
<script type="module" src="https://example.com/embed/<webring-slug>/webring-embed.js"></script>
```

As illustrated, a no-js fallback is recommended for visitors to your site that may have JavaScript
execution disabled or do not have JavaScript support.

The simple embed is intentionally unstyled to give creative freedom in making it match your site's
design scheme/language. All elements contain appropriate CSS classes for your styling.

Note that using the simple embed could potentially be slow and increase the page load time,
depending on the number of entries. This script is also not minified, which could also increase the
page load time. If greater control over loading and displaying the webring is desired, it is
suggested to manually call the root URL to fetch and display the entries, or put the webring on a
non-heavily trafficked page of your site.

#### Available CSS selectors
- `#webring__embed-area`
- `.webring__not-found`
- `.webring__title`
- `.webring__description`
- `.webring__entry-title`
- `.webring__entry-description`
- `.webring__navigation`
- `.webring__navigation__all_entries`
- `.webring__navigation__link-prev`
- `.webring__navigation__link-next`
- `.webring__navigation__page-counts`

## Required Secret/Configuration Keys
- Django secret key (`SECRET_KEY`)
- ~~Integer number of times supposed rotted links should be checked~~
  ~~(`TIMES_FAILED_THRESHOLD`, default: 10)~~
- ~~Discord linkrot event logging boolean (`DISCORD_LOGGING_ENABLE`, default: `False`)~~
  - ~~Discord webhook URL (`DISCORD_WEBHOOK_URL`)~~
- Webring entry filtering
  - `FILTER_ENTRIES_PER_PAGE`, default: `5`
  - `FILTER_INCLUDE_DEAD`, default: `True`
  - `FILTER_INCLUDE_ORIGIN`, default: `False`
  - `FILTER_INCLUDE_WEB_ARCHIVE`, default: `True`

## Development
1. Install Python 3.14+, [uv](https://github.com/astral-sh/uv), and VS Code
1. Set the required settings and configuration values in `webring/settings/local.py`
1. Run `uv sync`
1. ~~Run tests with `poetry run pytest` or through VS Code~~

## License
2026 Caleb

[MIT](LICENSE)

# NOTE: Nearly everything past this point is not yet relevant to this project

### Rotting links checking
Because websites can and will eventually vanish, even after
[a few months](https://brisray.com/web/linkrot.htm), link rot is a real
problem for webrings. As they are manually curated and maintained, knowing if an entry is
no longer available can be a maintenance burden. To that end, this webring has built-in rotten link
detection. However, it is not automatically set up and must be configured on your server.

The entire webring can be checked for rotten links by issuing an authenticated `POST` request to
the `/linkrot/` endpoint. Each entry that has not previously been determined to be dead will
be checked for a 200, 201, 204, or 304 HTTP response. If a URL fails that check, that failure
will be recorded. Once the check has failed more than the configured `TIMES_FAILED_THRESHOLD` limit,
the [Web Archive](https://web.archive.org/) will be checked for an archived version. If found,
the entry will be updated to use that link and the title will be adjusted to note such.
If there is no archived version, the entry will be recorded as dead and the title adjusted.

Individual entries, including dead entries, can also be checked.

One way to configure the linkrot check to run automatically is to create a Python script that
makes the aforementioned `POST` request and schedule it to automatically run via some scheduler.

Starting with version 1.4.1, a full history of linkrot checks are available for individual entries
by making an authenticated `GET` request to `/linkrot/<uuid>/history`.

### Discord channel logger
If the [Discord](https://discord.com) logger is enabled and configured, entries that are found to be
rotting or dead will be reported in a Discord channel. This can be helpful for keeping up with
the webring's health and ensuring entries are available. Configuring the Discord logger
is kept as simple as possible.

1. Set the `ENABLE_DISCORD_LOGGING` secret value to `True` to enable the logger
1. Follow the Discord documentation for [creating a webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
1. Get the Discord webhook URL from the configuration and set it as the value for
the `DISCORD_WEBHOOK_URL` secret key

A text file logger for events is always configured.

### Auth key creation/management

All administrative operations (effectively anything except fetching the webring entries) are
protected by an auth key. The system is intentionally kept extremely simple. Any string of
characters can be used as a key. All keys are defined as a JSON list called `AUTH_KEYS`. The key is
to be passed to the request via the HTTP `Authorization` header as a `Bearer` token. If the key is
not provided, a `400 BAD REQUEST` HTTP error is raised.  If it is not in the list, a `403 FORBIDDEN`
HTTP error is raised.

## Build
Webring2 uses Docker to help isolate instances. It is possible to run without Docker,
but setup or execution scripts are not provided. If you make some, please, send them over!

1. `docker build -t webring:latest .`
1. `docker-compose up -d`
