# intune-uploader

## Description
This project aims to simplify the process of creating and updating apps and other payloads in Intune by leveraging the power of [AutoPkg](https://github.com/autopkg/autopkg). With AutoPkg, you can automate the process of downloading, packaging, and uploading apps to Intune, saving you time and effort.

Moving forward, additional processors for Intune might be added to this project that uploads more data like Shell scripts to provide a complete automated deployment process. This is why the base class [IntuneUploaderBase](IntuneUploader/IntuneUploaderLib/IntuneUploaderBase.py) was created, to allow for easier creation of additional processors. Contributions are welcome!

Ideas for future processors:
- Shell script processor
- App removal processor
- Teams notifier processor

For getting started help and documentation, please visit the wiki pages:
- [Intune App Uploader](https://github.com/almenscorner/intune-uploader/wiki/IntuneAppUploader)

### IntuneAppUploader - PKG type apps (not LOB)
All code in this processor for PKG support is currently made on assumptions of how the API will look like. This means that the code might break if the production API looks different. Once the API is finalized, the code will be updated to reflect the production API.

LOB type apps will remain not supported by this processor. This is because LOB apps have limitations which the new PKG type will not have. For example, LOB apps does not support payload free packages, and the package must be signed. This is not the case for PKG type apps.