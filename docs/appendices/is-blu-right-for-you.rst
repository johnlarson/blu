Is Blu Right for You?
=====================

Before using Blu, you should refer to this list of features that Blu doesn't have in order to make sure it fits your needs.

Blu doesn't pre-render client components on the server.
-------------------------------------------------------

Many React frameworks implement *server-side rendering* (SSR), where client-side components are pre-rendered to HTML on the server so that the page appears as expected before any client-side rendering code has run. Blu does not not do this; in Blu, nothing shows up on the page until the rendering code has run on the client. This has two main downsides:

- Users may briefly see a blank page before your web app appears in their browser.
- Your website can't be visited by most webcrawlers, which is bad for SEO.

Blu doesn't allow you to host client dependencies.
--------------------------------------------------

Any external Python packages you use in client-side code are served from CDNs. Blu does not provide the ability for you to host those dependencies yourself.


Blu doesn't allow you to choose client dependency versions.
-----------------------------------------------------------

When installing dependencies on the client, Blu always uses the latest versions available on the CDNs that it installs packages from. You can't configure it to install specific versions or ranges of versions of those packages.