#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-

"""
This processor posts a message to a Microsoft Teams channel using a webhook URL.
The message is formatted as an Adaptive Card and can include a link to the Intune app.
The processor is intended to be used in conjunction with the IntuneAppUploader, IntuneAppPromoter, and IntuneAppCleaner processors.

Created by Tobias Almén
"""

import requests
import os
import sys
import json
import time

from autopkglib import ProcessorError

__all__ = ["IntuneTeamsNotifier"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase


class IntuneTeamsNotifier(IntuneUploaderBase):
    """Uploads a script to Microsoft Intune using the Microsoft Graph API."""

    input_variables = {
        "webhook_url": {
            "required": True,
            "description": "Webhook URL for the Teams channel to post to.",
        },
        "intuneappuploader_summary_result": {
            "required": False,
            "description": "Results from the IntuneAppUploader processor.",
        },
        "intuneapppromoter_summary_result": {
            "required": False,
            "description": "Results from the IntuneAppPromoter processor.",
        },
        "intuneappcleaner_summary_result": {
            "required": False,
            "description": "Results from the IntuneAppCleaner processor.",
        },
    }
    output_variables = {}

    def main(self):
        """Main process"""

        teams_webhook = self.env.get("webhook_url")
        intuneappuploader_summary_results = self.env.get(
            "intuneappuploader_summary_result", {}
        )
        intuneapppromoter_summary_result = self.env.get(
            "intuneapppromoter_summary_result", {}
        )
        intuneappcleaner_summary_results = self.env.get(
            "intuneappcleaner_summary_result", {}
        )

        def _teams_message(title, message, imported=False, id=None):

            data = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "contentUrl": None,
                        "content": {
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "type": "AdaptiveCard",
                            "version": "1.6",
                            "msteams": {"width": "Full"},
                            "body": [
                                {
                                    "type": "Container",
                                    "bleed": True,
                                    "size": "stretch",
                                    "items": [{"type": "TextBlock", "text": title}],
                                },
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "text": message,
                                                    "wrap": True,
                                                },
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    }
                ],
            }

            if imported:
                data["attachments"][0]["content"]["actions"] = [
                    {
                        "type": "Action.OpenUrl",
                        "title": "View App in Intune",
                        "url": f"https://intune.microsoft.com/#view/Microsoft_Intune_Apps/SettingsMenu/~/0/appId/{id}",
                    }
                ]

            return data

        def _post_teams_message(data):
            data = json.dumps(data)
            response = requests.post(url=teams_webhook, data=data)

            retry_count = 0
            while response.status_code != 200 and retry_count < 3:
                time.sleep(2)
                response = requests.post(url=teams_webhook, data=data)
                retry_count += 1
            if response.status_code != 200:
                raise ProcessorError(
                    f"Failed to post message to Teams, status code: {response.status_code} - {response.text}"
                )

        def _updated_alerts(summary):
            name = summary["data"]["name"]
            version = summary["data"]["version"]
            result_id = summary["data"]["intune_app_id"]
            content_version_id = summary["data"]["content_version_id"]
            task_title = f"✅ Imported {name} {version}"
            task_description = (
                f"**Name:** {name}"
                + "\r \r"
                + f"**Intune App ID:** {result_id}"
                + "\r \r"
                + f"**Content Version ID:** {content_version_id}"
                + "\r \r"
            )

            self.output(f"Posting imported message to Teams for {name} {version}")
            message = _teams_message(
                task_title, task_description, imported=True, id=result_id
            )
            _post_teams_message(message)

        def _removed_alerts(summary):
            removed_count = summary["data"]["removed count"]
            if int(removed_count) == 0:
                return
            name = summary["data"]["searched name"]
            removed_versions = summary["data"]["removed versions"]
            keep_count = summary["data"]["keep count"]
            task_title = f"🗑 Removed old versions of {name}"
            task_description = ""
            task_description += (
                f"**Remove Count:** {removed_count}"
                + "\r \r"
                + f"**Removed Versions:** {removed_versions}"
                + "\r \r"
                + f"**Keep Count:** {keep_count}"
                + "\r \r"
            )

            self.output(f"Posting removed message to Teams for {name}")
            message = _teams_message(task_title, task_description)
            _post_teams_message(message)

        def _promoted_alerts(summary):
            name = summary["data"]["app name"]
            promotions = summary["data"]["promotions"]
            blacklisted_versions = summary["data"]["blacklisted versions"]
            task_title = "🚀 Promoted %s" % name
            task_description = ""
            task_description += (
                f"**Promotions:** {promotions}"
                + "\r \r"
                + f"**Blacklisted Versions:** {blacklisted_versions}"
                + "\r \r"
            )

            self.output(f"Posting promoted message to Teams for {name}")
            message = _teams_message(task_title, task_description)
            _post_teams_message(message)

        if intuneappuploader_summary_results:
            _updated_alerts(intuneappuploader_summary_results)
        if intuneappcleaner_summary_results:
            _removed_alerts(intuneappcleaner_summary_results)
        if intuneapppromoter_summary_result:
            _promoted_alerts(intuneapppromoter_summary_result)


if __name__ == "__main__":
    PROCESSOR = IntuneTeamsNotifier()
    PROCESSOR.execute_shell()
