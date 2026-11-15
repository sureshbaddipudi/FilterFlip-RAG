"""Verify this release without loading models or making network requests."""
from safety import verify_release
if __name__=='__main__':
    print('Verified',verify_release(),'release files. Machine-local configuration and external runs are excluded.')
