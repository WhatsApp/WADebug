# Copyright (c) Facebook, Inc. and its affiliates.

# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


class Error(Exception):
    """Base class for other exceptions"""
    pass


class FBNetworkError(Error):
    """Raised when a network connection to FB cannot be made"""
    pass


class FileAccessError(Error):
    """Raised when a file access error occurs"""
    pass


class InvalidParamType(Error):
    """Raised when trying to use an invalid param_type for a cli_param.ReusableParam"""
    pass


class LogsNotCompleteError(Error):
    """Raised when at least one log file could not be retrieved"""
    pass


class WABizAccessError(Error):
    """Raised when the API is inaccessible with given credentials"""
    pass


class WABizAuthError(Error):
    """Raised when the authentication token used is invalid"""
    pass


class WABizGeneralError(Error):
    """Raised when the API returns an unhandled error response"""
    pass


class WABizNetworkError(Error):
    """Raised when a network connection to Webapp cannot be made"""
    pass


class WABizResourceNotFound(Error):
    """Raised when the requested resource cannot be found"""
    pass
