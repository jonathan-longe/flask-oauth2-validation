from flask_oauth2_api import OAuth2Decorator
import pytest
from . import mocked_keys


def test_missing_config(test_app):
    """ At least the OAUTH2_ISSUER config attribute is required.
    This test is expected to raise a TypeError as no configuration
    attribute has been provided.
    """
    with pytest.raises(TypeError):
        OAuth2Decorator(test_app)


def test_issuer_only(test_app):
    """ Only the OAUTH2_ISSUER config attribute has been set.
    Thus we expect an authorization server metadata lookup to retrieve
    the jwks_uri. Next the jwks_uri should be requested to retrieve all
    public keys the authorization server uses.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    oauth2 = OAuth2Decorator(test_app)
    assert oauth2._issuer == 'https://issuer.local/oauth2'
    assert oauth2._jwks_uri == 'https://issuer.local/oauth2/keys'
    assert oauth2._issuer_public_keys == mocked_keys


def test_issuer_and_jwks_uri_configured(test_app):
    """ The OAUTH2_ISSUER and OAUTH2_JWKS_URI config attribute have been set.
    Thus we expect no authorization server metadata lookup to retrieve
    the jwks_uri. Only the jwks_uri should be requested to retrieve all
    public keys the authorization server uses.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    test_app.config['OAUTH2_JWKS_URI'] = 'https://issuer.local/oauth2/keys'
    oauth2 = OAuth2Decorator(test_app)
    assert oauth2._issuer == 'https://issuer.local/oauth2'
    assert oauth2._jwks_uri == 'https://issuer.local/oauth2/keys'
    assert oauth2._issuer_public_keys == mocked_keys
    assert not oauth2._client_id
    assert not oauth2._client_secret
    assert not oauth2._jwks_update_interval
    assert not oauth2._executor
    assert not oauth2._introspection_endpoint
    assert not oauth2._introspection_auth_method


def test_issuer_and_jwks_refresh_configured(test_app):
    """ A refresh interval has been set.
    In that case we expect the last update timestamp and an executor
    task to be initialized.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    test_app.config['OAUTH2_JWKS_URI'] = 'https://issuer.local/oauth2/keys'
    test_app.config['OAUTH2_JWKS_UPDATE_INTERVAL'] = 1234
    oauth2 = OAuth2Decorator(test_app)
    assert oauth2._issuer == 'https://issuer.local/oauth2'
    assert oauth2._jwks_uri == 'https://issuer.local/oauth2/keys'
    assert oauth2._issuer_public_keys == mocked_keys
    assert oauth2._jwks_update_interval == 1234
    assert oauth2._executor
    assert oauth2._jwks_last_update_timestamp
    assert not oauth2._client_id
    assert not oauth2._client_secret
    assert not oauth2._introspection_endpoint
    assert not oauth2._introspection_auth_method


def test_introspection_setup(test_app):
    """ In case OAUTH2_CLIENT_ID and OAUTH2_CLIENT_SECRET
    attributes have been set we assume that we will
    validate tokens via introspection requests during
    runtime. Therefore we need to lookup the introspection
    endpoint from the authorization server metadata as well
    as the supported introspection endpoint auth methods.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    test_app.config['OAUTH2_CLIENT_ID'] = 'foo-client'
    test_app.config['OAUTH2_CLIENT_SECRET'] = 'very-secure'
    oauth2 = OAuth2Decorator(test_app)
    assert oauth2._issuer == 'https://issuer.local/oauth2'
    assert oauth2._jwks_uri == 'https://issuer.local/oauth2/keys'
    assert oauth2._issuer_public_keys == mocked_keys
    assert oauth2._client_id == 'foo-client'
    assert oauth2._client_secret == 'very-secure'
    assert oauth2._introspection_endpoint == \
        'https://issuer.local/oauth2/introspect'
    assert oauth2._introspection_auth_method == 'client_secret_post'


def test_introspection_setup_without_secret(test_app):
    """ For using the introspection endpoint for validation
    we also need a client secret.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    test_app.config['OAUTH2_CLIENT_ID'] = 'foo-client'
    with pytest.raises(TypeError):
        OAuth2Decorator(test_app)


def test_introspection_setup_with_endpoint(test_app):
    """ In case we specify an introspection endpoint
    we don't need to look it up from the metadata endpoint.
    But we need to look up the supported introspection auth
    methods from the metadata endpoint.
    """
    test_app.config['OAUTH2_ISSUER'] = 'https://issuer.local/oauth2'
    test_app.config['OAUTH2_CLIENT_ID'] = 'foo-client'
    test_app.config['OAUTH2_CLIENT_SECRET'] = 'very-secure'
    test_app.config['OAUTH2_OAUTH2_INTROSPECTION_ENDPOINT'] = \
        'https://issuer.local/oauth2/introspect'
    oauth2 = OAuth2Decorator(test_app)
    assert oauth2._issuer == 'https://issuer.local/oauth2'
    assert oauth2._jwks_uri == 'https://issuer.local/oauth2/keys'
    assert oauth2._issuer_public_keys == mocked_keys
    assert oauth2._client_id == 'foo-client'
    assert oauth2._client_secret == 'very-secure'
    assert oauth2._introspection_endpoint == \
        'https://issuer.local/oauth2/introspect'
    assert oauth2._introspection_auth_method == 'client_secret_post'
