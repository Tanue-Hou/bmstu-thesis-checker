"""Known executable identities; no validation transfer between releases."""
BUILDS={230:{"file_version":"1.0.0.230","sha256":"0bb43cebc4c7ee196913d2ea2240f7bc53aaac1e6b8f6394e6201024a108b8cb"},232:{"file_version":"1.0.0.232","sha256":"5c04b57acdbda79073604d6e3cacc2994bc87c5ed316e3b8706555ca92b6a8f0"}}
def require_build(build):
    if isinstance(build,bool) or build not in BUILDS:raise ValueError('Unknown TestVkr build; identify and retain evidence first')
    return BUILDS[build]
