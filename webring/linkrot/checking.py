from copy import copy
from logging import getLogger
from typing import TypedDict

import httpx
from django.conf import settings
from django.template.defaultfilters import pluralize

from ..core.models import Entry
from .models import LinkrotHistory


__all__ = ["Check", "RotResult", "check_all", "check_one"]


# TODO: get logging working
logger = getLogger(__name__)


class Check(TypedDict):
    times_failed: int
    is_dead: bool
    is_web_archive: bool


class RotResult(TypedDict):
    id: str
    url: str
    result: Check


def __can_reach_site(url: str) -> bool:
    """Check a link for rotting."""
    try:
        return httpx.head(url).status_code in {
            httpx.codes.OK,
            httpx.codes.CREATED,
            httpx.codes.NO_CONTENT,
            httpx.codes.NOT_MODIFIED,
        }
    except httpx.HTTPError:
        # logger.info({
        #     "id": "N/A",
        #     "url": url,
        #     "message": "Link could not be reached during a linkrot check.",
        # })
        return False


def __check_wayback_archive(url: str) -> str:
    """Check the Web Archive for an archived URL."""
    r = httpx.get(f"https://archive.org/wayback/available?url={url}").json()
    if not r["archived_snapshots"]:
        return ""

    # Transform the provided URL to use HTTPS for the scheme
    return str(httpx.URL(r["archived_snapshots"]["closest"]["url"]).copy_with(scheme="https"))


def __record_failure(entry: Entry, history_entry: LinkrotHistory) -> Check:
    result = Check(times_failed=0, is_dead=False, is_web_archive=False)

    # Determine how many times we've failed the rot check since the last successful check
    try:
        id_of_last_success = entry.history.filter(was_alive=True).last().id
    except AttributeError:
        id_of_last_success = 0
    times_failed = entry.history.filter(was_alive=False, id__gt=id_of_last_success).count()
    result["times_failed"] = times_failed

    # # We've failed the rot check less than the allowed threshold, only issue a warning
    if times_failed <= settings.TIMES_FAILED_THRESHOLD:
        message = (
            f"Entry has failed the linkrot check {times_failed:,} "
            f"{pluralize('time', times_failed)}."
        )
        # logger.error({
        #     "id": entry.uuid,
        #     "url": entry.url,
        #     "message": message,
        # })
        history_entry.message = message
        history_entry.save(update_fields={"message"})
        return result

    # We've failed the threshold too many times, check the Web Archive for an archived URL
    if wb_url := __check_wayback_archive(entry.url):
        # We have an WA URL, update the entry with it. Make sure we copy the old URL so we can
        # reference it in the logger message
        old_url = copy(entry.url)
        entry.url = wb_url
        entry.is_web_archive = True
        entry.save(update_fields={"url", "is_web_archive"})
        result["is_web_archive"] = True
        message = "Entry has been updated to indicate a Web Archive reference."
        # logger.info({
        #     "id": entry.uuid,
        #     "url": old_url,
        #     "message": message,
        # })
        history_entry.message = message
        history_entry.save(update_fields={"message"})
        return result

    # We can't find the site on the web archive. It's a dead entry
    entry.is_dead = True
    entry.save(update_fields={"is_dead"})
    result["is_dead"] = True
    message = "Entry has been marked as a dead link."
    # logger.critical({
    #     "id": entry.uuid,
    #     "url": entry.url,
    #     "message": message,
    # })
    history_entry.message = message
    history_entry.save(update_fields={"message"})
    return result


def check_all(slug: str) -> list[RotResult]:
    """Check all links for rotting."""
    return [
        check_one(link)
        for link in Entry.objects.filter(
            instance__slug=slug, include_dead=True, include_web_archive=False
        )
    ]


def check_one(entry: Entry | str) -> RotResult | None:
    """Check a single entry for rotting."""
    # If we got an uuid string, then we need to look up the entry.
    # If it doesn't exist in the db, we can't do anything
    if not isinstance(entry, Entry):
        try:
            entry = Entry.objects.get(uuid=entry)
        except Entry.DoesNotExist:
            return None

        # If the entry is already marked as a Web Archive entry, don't do anything more.
        # We can't do much more because it's really hard to extract the original URL
        # from a WA URL without a human looking at it
        if entry.is_web_archive:
            # logger.info({
            #     "id": entry.uuid,
            #     "url": entry.url,
            #     "message": (
            #         "Entry has previously been marked to as a Web Archive entry, not checking again."
            #     ),
            # })
            times_failed = entry.history.filter(was_alive=False).count()
            return RotResult(
                id=entry.uuid,
                url=entry.url,
                result=Check(times_failed=times_failed, is_dead=False, is_web_archive=True),
            )

    # Create a history record. It may be updated later with rot results
    history_entry = LinkrotHistory.objects.create(url=entry.url, entry=entry)

    # If the site could be pinged, then the site is alive
    if __can_reach_site(entry.url):
        # The site status hasn't changed
        if not entry.is_dead:
            message = "Entry remains online and available."
            history_entry.message = message
            history_entry.save(update_fields={"message"})
            # logger.info({
            #     "id": entry.uuid,
            #     "url": entry.url,
            #     "message": message,
            # })
            return RotResult(
                id=entry.uuid,
                url=entry.url,
                result=Check(times_failed=0, is_dead=False, is_web_archive=False),
            )

        # The entry was previously marked as dead, change that
        message = "Entry was previously determined to be dead but has been revived."
        history_entry.message = message
        history_entry.save(update_fields={"message"})
        entry.is_dead = False
        entry.is_web_archive = False
        entry.save(update_fields={"is_dead", "is_web_archive"})
        # logger.info({
        #     "id": entry.uuid,
        #     "url": entry.url,
        #     "message": message,
        # })
        return RotResult(
            id=entry.uuid,
            url=entry.url,
            result=Check(times_failed=0, is_dead=False, is_web_archive=False),
        )

    # # We could not ping the site, determine if it is dead or WA-only entry
    # # and update our history record accordingly
    history_entry.was_alive = False
    history_entry.save(update_fields={"was_alive"})
    result = __record_failure(entry, history_entry)
    return RotResult(id=entry.uuid, url=entry.url, result=result)
