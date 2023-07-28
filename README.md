# intune-uploader

## Description
This project aims to simplify the process of creating and updating apps and other payloads in Intune by leveraging the power of [AutoPkg](https://github.com/autopkg/autopkg). With AutoPkg, you can automate the process of downloading, packaging, and uploading apps to Intune, saving you time and effort.

Moving forward, additional processors for Intune might be added to this project that uploads more data like Shell scripts to provide a complete automated deployment process. This is why the base class [IntuneUploaderBase](IntuneUploader/IntuneUploaderLib/IntuneUploaderBase.py) was created, to allow for easier creation of additional processors. Contributions are welcome!

Ideas for future processors:
- Teams notifier processor

For getting started help and documentation, please visit the wiki pages:
- [Intune App Uploader](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppUploader)
- [Intune App Icon Getter](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppIconGetter)
- [Intune App Cleaner](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppCleaner)
- [Intune Script Uploader](https://github.com/almenscorner/intune-uploader/wiki/IntuneScriptUploader)

### IntuneAppUploader - LOB apps (managed PKG)
LOB type apps will remain not supported by this processor. This is because LOB apps have limitations which the new PKG type does not have. For example, LOB apps does not support payload free packages, and the package must be signed. This is not the case for PKG type apps.