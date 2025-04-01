#!/usr/local/autopkg/python
# -*- coding: utf-8 -*-

"""
This processor will delete the app if the VirusTotal positives is greater than the configured positives.

This processor requires that io.github.hjuutilainen.VirusTotalAnalyzer/VirusTotalAnalyzer
is run before this processor.

Created by Tobias Almén
"""

import os
import sys
import time

__all__ = ["IntuneVTAppDeleter"]

sys.path.insert(0, os.path.dirname(__file__))
from IntuneUploaderLib.IntuneUploaderBase import IntuneUploaderBase


class IntuneVTAppDeleter(IntuneUploaderBase):
    """This processor cleans up apps in Intune based on the input variables."""

    description = __doc__
    input_variables = {
        "display_name": {
            "required": False,
            "description": "The name of the app to clean up.",
        },
        "version": {
            "required": False,
            "description": "The version of the app to remove",
        },
        "positives": {
            "required": False,
            "description": "The amount positives of VirusTotal results to delete the app.",
            "default": 10,
        },
        "test_mode": {
            "required": False,
            "description": "If True, will only print what would have been done.",
            "default": False,
        },
    }
    output_variables = {
        "intunevtappdeleter_summary_result": {
            "description": "Description of interesting results."
        }
    }

    def main(self):
        """Main process."""
        # Set variables
        self.BASE_ENDPOINT = (
            "https://graph.microsoft.com/beta/deviceAppManagement/mobileApps"
        )
        self.CLIENT_ID = self.env.get("CLIENT_ID")
        self.CLIENT_SECRET = self.env.get("CLIENT_SECRET")
        self.TENANT_ID = self.env.get("TENANT_ID")
        positives = self.env.get("positives")
        app_name = self.env.get("display_name")
        version = self.env.get("version")
        test_mode = self.env.get("test_mode")
        vt_results = self.env.get("virus_total_analyzer_summary_result")

        if not vt_results:
            self.output("No VirusTotal results found. Skipping app deletion.")
            return

        vt_filename = vt_results["data"]["name"]

        # When running from the command line, positives is a string, convert to int
        if isinstance(positives, str):
            positives = int(positives)

        # Get access token
        self.token = self.obtain_accesstoken(
            self.CLIENT_ID, self.CLIENT_SECRET, self.TENANT_ID
        )

        def _get_app():
            # Get macthing apps
            app = self.get_matching_apps(app_name)
            app = list(
                map(
                    lambda item: (
                        {**item, "primaryBundleVersion": item["buildNumber"]}
                        if "primaryBundleVersion" not in item and "buildNumber" in item
                        else item
                    ),
                    app,
                )
            )
            if len(app) > 1:
                app = list(
                    filter(
                        lambda item: item["primaryBundleVersion"] == version
                        and item["fileName"] == vt_filename,
                        app,
                    )
                )

            return app[0] if len(app) > 0 else None

        app = _get_app()

        retry_count = 0
        while app is None and retry_count < 5:
            self.output("No matching app found. Retrying in 5 seconds...")
            time.sleep(5)
            retry_count += 1
            # Retry getting the app
            app = _get_app()

        if not app:
            self.output(
                f"No matching app found for {app_name} and version {version}. Skipping deletion."
            )
            return

        self.output(
            f"Found matching app for {app_name}, version {version} and filename {vt_filename}"
        )

        # Only delete if not in test mode
        vt_positives = int(vt_results["data"]["ratio"].split("/")[0])

        deleted = False
        # if virus total positives is greater than or equal to the configured positives, delete the app
        if vt_positives >= positives:
            deleted = True
            self.output(
                f"VirusTotal positives is greater than {positives}. Deleting app."
            )
            if not test_mode:
                self.makeapirequestDelete(
                    self.BASE_ENDPOINT + "/" + app["id"], self.token
                )
        else:
            self.output(
                f"VirusTotal positives is less than {positives}. Not deleting app {app_name} {version}."
            )

        self.env["intunevtappdeleter_summary_result"] = {
            "summary_text": "The following items were checked for removal from Intune based on VirusTotal positives:",
            "report_fields": [
                "app_name",
                "version",
                "configured_positives",
                "virustotal_positives",
                "virustotal_ratio",
                "deleted",
            ],
            "data": {
                "app_name": app_name,
                "version": version,
                "configured_positives": str(positives),
                "virustotal_positives": str(vt_positives),
                "virustotal_ratio": str(vt_results["data"]["ratio"]),
                "deleted": str(deleted),
            },
        }


if __name__ == "__main__":
    PROCESSOR = IntuneVTAppDeleter()
    PROCESSOR.execute_shell()
