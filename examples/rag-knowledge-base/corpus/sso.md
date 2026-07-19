# Single Sign-On (SSO)

SSO lets your team log in to NimbusBoard using your existing identity provider instead of
a separate NimbusBoard password. It's available on the Team plan via Google and Microsoft
social login, and on the Enterprise plan via full SAML 2.0 and SCIM provisioning with any
standards-compliant identity provider (Okta, Azure AD, and OneLogin have all been
verified to work).

To configure SAML SSO, go to Settings > Security > SSO and provide your identity
provider's metadata URL (or upload the XML metadata file directly). NimbusBoard will show
you the Assertion Consumer Service (ACS) URL and Entity ID you need to enter on your
identity provider's side to complete the connection. Once enabled, you can make SSO
optional (users can still log in with a password) or required (password login is disabled
workspace-wide, including for the account that originally set up SSO - keep at least one
recovery admin contact on file with support before enforcing this).

SCIM provisioning, available on Enterprise, automatically creates and deactivates
NimbusBoard accounts as people join or leave groups in your identity provider, removing
the need to manually invite or offboard users in NimbusBoard itself. Role assignment
(member vs. admin) can be mapped from identity-provider group membership during SCIM
setup.
