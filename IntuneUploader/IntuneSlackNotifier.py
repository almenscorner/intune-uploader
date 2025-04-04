#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-

"""
This processor posts a message to a Slack channel using a webhook URL.
The message is formatted as an Adaptive Card and can include a link to the Intune app.
The processor is intended to be used in conjunction with the IntuneAppUploader, IntuneAppPromoter, and IntuneAppCleaner processors.

Created by Tobias Almén
"""

import json
import os
import sys
import time

import requests
from autopkglib import ProcessorError

__all__ = ["IntuneSlackNotifier"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase


class IntuneSlackNotifier(IntuneUploaderBase):
    """Sends a message to a Slack channel using a webhook URL."""

    input_variables = {
        "webhook_url": {
            "required": True,
            "description": "Webhook URL for the slack channel to post to.",
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

        slack_webhook = self.env.get("webhook_url")
        intuneappuploader_summary_results = self.env.get(
            "intuneappuploader_summary_result", {}
        )
        intuneapppromoter_summary_result = self.env.get(
            "intuneapppromoter_summary_result", {}
        )
        intuneappcleaner_summary_results = self.env.get(
            "intuneappcleaner_summary_result", {}
        )

        def _slack_message(title, message, imported=False, app_id=None):
            payload = {
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": title, "emoji": True},
                    },
                    {"type": "section", "text": {"type": "mrkdwn", "text": message}},
                ]
            }

            if imported:
                payload["blocks"].append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*<https://intune.microsoft.com/#view/Microsoft_Intune_Apps/SettingsMenu/~/0/appId/{app_id} | View App In Intune>*",
                        },
                    }
                )

            return payload

        def _post_slack_message(data):
            data = json.dumps(data)
            response = requests.post(url=slack_webhook, data=data)

            retry_count = 0
            while response.status_code != 200 and retry_count < 3:
                time.sleep(2)
                response = requests.post(url=slack_webhook, data=data)
                retry_count += 1
            if response.status_code != 200:
                raise ProcessorError(
                    f"Failed to post message to slack, status code: {response.status_code} - {response.text}"
                )

        def _updated_alerts(summary):
            name = summary["data"]["name"]
            version = summary["data"]["version"]
            result_id = summary["data"]["intune_app_id"]
            content_version_id = summary["data"]["content_version_id"]
            task_title = f"✅ Imported {name} {version}"
            task_description = (
                f"*Name:* {name}"
                + "\r"
                + f"*Intune App ID:* {result_id}"
                + "\r"
                + f"*Content Version ID:* {content_version_id}"
            )

            self.output(f"Posting imported message to slack for {name} {version}")
            message = _slack_message(
                task_title, task_description, imported=True, app_id=result_id
            )
            _post_slack_message(message)

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
                f"*Remove Count:* {removed_count}"
                + "\r"
                + f"*Removed Versions:* {removed_versions}"
                + "\r"
                + f"*Keep Count:* {keep_count}"
            )

            self.output(f"Posting removed message to slack for {name}")
            message = _slack_message(task_title, task_description)
            _post_slack_message(message)

        def _promoted_alerts(summary):
            name = summary["data"]["app name"]
            promotions = summary["data"]["promotions"]
            blacklisted_versions = summary["data"]["blacklisted versions"]
            task_title = "🚀 Promoted %s" % name
            task_description = ""
            task_description += (
                f"*Promotions:* {promotions}"
                + "\r"
                + f"*Blacklisted Versions:* {blacklisted_versions}"
            )

            self.output(f"Posting promoted message to slack for {name}")
            message = _slack_message(task_title, task_description)
            _post_slack_message(message)

        if intuneappuploader_summary_results:
            _updated_alerts(intuneappuploader_summary_results)
        if intuneappcleaner_summary_results:
            _removed_alerts(intuneappcleaner_summary_results)
        if intuneapppromoter_summary_result:
            _promoted_alerts(intuneapppromoter_summary_result)


if __name__ == "__main__":
    PROCESSOR = IntuneSlackNotifier()
    PROCESSOR.execute_shell()
