:tocdepth: 1

.. sectnum::

Abstract
========

The Rubin Science Platform will require an identity management system.
One attractive option is to build it on top of CILogon's managed COmanage service, which is designed for scientific collaborations.
This document compares COmanage's functionality with the Rubin Science Platform requirements documented in `SQR-044`_.

.. _SQR-044: https://sqr-044.lsst.io/

This analysis is based primarily on the CILogon response to the Rubin Science Platform requirements document.

.. warning::

   This tech note documents part of the process used to arrive at the current identity management design.
   Its findings have been incorporated in the design and, in many cases, substantially modified, so this tech note is primarily of historical interest.
   For documentation of the current COmanage configuration for the Science Platform, see SQR-055_.
   For a companion document analyzing GitHub, see SQR-046_.

   This is part of a tech note series on identity management for the Rubin Science Platform.
   The primary documents are DMTN-234_, which describes the high-level design; DMTN-224_, which describes the implementation; and SQR-069_, which provides a history and analysis of the decisions underlying the design and implementation.
   See the `references section of DMTN-224 <https://dmtn-224.lsst.io/#references>`__ for a complete list of related documents.

.. _DMTN-234: https://dmtn-234.lsst.io/
.. _DMTN-224: https://dmtn-224.lsst.io/
.. _SQR-046: https://sqr-046.lsst.io/
.. _SQR-055: https://sqr-055.lsst.io/
.. _SQR-069: https://sqr-069.lsst.io/

Methodology
===========

The CILogon team sorted the requirements in `SQR-044`_ into requirements that COmanage plus CILogon already meet, requirements that can be met with a plugin (along with a development estimate), and requirements that are out of scope for COmanage.
I then collected that point-by-point response into this summary.
Follow-up questions are currently included here.
This document will be revised based on the answers to those questions after a subsequent technical meeting.

Gaps
====

.. _out-of-scope:

Out of scope
------------

#. Forcing multifactor for administrators.
   Google and GitHub do not expose this information in their OAuth metadata.
   The easiest approach would probably be to use a separate authentication path for administrators that forces use of a specific Google Cloud Identity domain with appropriate multifactor authentication requirements.
   (IDM-0007)
#. Token issuance in general, including all logging and notification requirements.
   Integration could be done with a COmanage provisioning plugin to notify the token system of user status changes.
   Hosted SciTokens doesn't have the UI and flexibility that we want in our requirements.
   However, we could address this with locally-deployed SciTokens, or by enhancing Gafaelfawr.
   (IDM-01* and related issues)
#. Showing a history of web authentications for a user.
   The CILogon folks have this information logged internally but don't have a way of exposing it to downstream clients.
   We would need to capture this on the Science Platform side and generate the UI from there.
   Gafaelfawr does capture some of this information in its logs, but not the specific federated identity that was used.
   (IDM-0203, IDM-0204)

Development required
--------------------

There are three approaches to adding new functionality to COmanage: COmanage plugins, Cake plugins, and API calls.
UI interactions and actions that have to trigger immediately on object changes need to be Cake PHP plugins.
Actions that don't need an integrated UI and don't need an immediate trigger may be implemented via the REST API.
About 85% of the object model is exposed via REST.

All estimates below are in FTE-weeks for an experienced PHP developer.

#. Automated approval based on affiliation from federated identity metadata.
   (IDM-0002, Cake plugin, 1 week)
#. Revoking organizational identities and sending email notification when this happens.
   (IDM-0005, Cake plugin, 1 week for unlinking plus 2 weeks for email notification)
#. Periodicaly rechecking affiliation if we make access decisions based on organizational affiliation.
   (IDM-0009, Cake plugin for the UI aspect, 1 week)
#. Deduplication of enrollments based on email address.
   COmanage does support a lot of what we want and may be sufficient without further enhancement.
   (IDM-0013, 1 week, Cake plugin, probably not needed)
#. Notifying the token system of changes to account status so that tokens can be invalidated.
   This would not be needed if we query account status in LDAP as part of token validation.
   (IDM-01* and related issues, Cake plugin)
#. Displaying last use of a federated identity.
   This would only apply to authentications to COmanage, not to the Science Platform in general (which is covered above under :ref:`out-of-scope`).
   (IDM-0204, enhancement request that may not require Rubin work)
#. Notifying the user when a new email address is added.
   (IDM-1101, Cake event listener plugin, 2 weeks)
#. Showing that an email address is unverified in LDAP.
   Some work is already in progress (`GitHub issue <https://github.com/voperson/voperson/issues/35>`__).
   (IDM-1101, Cake provisioning plugin, 2 days)
#. Quota support.
   (IDM-12*, Cake plugin plus registry job, 4 weeks)
#. Automatic group management based on identity metadata.
   This possibly could be done via the API instead.
   (IDM-2001, Cake plugin, 4 weeks)
#. Namespace enforcement for groups.
   (IDM-2004, customization of the group name filter plugin, 2 days)
#. Ability for for the user to view their group expirations.
   (IDM-2008, Cake plugin, 1 week)
#. There may be some actions missing from the administrative API that would require an RFE.
   (IDM-3001)

Total estimate for all work is 17-18 weeks.

Other comments
==============

The default COmanage enrollment mechanism is by invitation.
We should consider using an invitation flow as the primary mechanism for onboarding users with project-specific Memorandums of Understanding, and other cases where the prospective user doesn't have an institutional affiliation.

The query API for downstream systems to get user metadata is LDAP.
We would probably need to write a REST frontend to avoid having to add LDAP dependencies to the rest of the Rubin Science Platform services.

Support for impersonation by an administrator requires adding the administrator's federated identity as an identity for the user.
This is not a good impersonation approach.
It makes the impersonation indistinguishable from the actions of the user and runs the risk of forgetting to remove the administrator's identity.
It also leaves unwanted actions from the identity changes in the logs, and doesn't warn the administrator in the UI that they are doing impersonation.
More direct support for impersonation would be preferrable, with separate log messages and a prominant UI banner.

COmanage Registry doesn't support groups owning other groups.
If we needed that feature (IDM-2009), we would need to add Grouper, provision COmanage groups into Grouper, and then use Grouper directly for other group management work.
However, COmanage does support COU sub-organizations with separate administrators, which may provide the same functionality.
Administrators could be given the ability to add and remove users from COmanage Registry groups in their COU.

Possible design
===============

A possible design for an identity management system satisfying the requirements of `SQR-044`_ and built on COmanage:

.. figure:: /_static/architecture.png
   :name: Identity management architecture

   Identity management architecture

This omits much of the detail of the Science Platform services, including only the notebook and VO services as examples.
See `SQR-039`_ for more details if needed.

.. _SQR-039: https://sqr-039.lsst.io/

Use CILogon for user authentication.
Use COmanage to handle the user enrollment flow.
This includes an approval flow where necessary, and a reauthorization flow to reconfirm identity where necessary.
Use COmanage to manage user metadata (email, full name), linked identities, and user affiliation.
Add COmanage plugins as necessary to customize the enrollment and reauthorization flows.

Use COmanage Registry groups for user ad hoc groups.
Use COUs for larger collaborations where it's necessary to delegate group ownership to a group of collabration administrators.

Write an Account UI for the user hosted in the Science Platform.
This would link to or incorporate information from COmanage and Science Platform services to present a unified view or at least a single landing page of links to the user for the services they'll need to interact with.

Manage tokens via a Token Issuer deployed in the Science Platform.
Display the user's tokens via the Account UI.

Manage quotas via a Quota Manager deployed in the Science Platform.
This would store the data in COmanage Registry as attributes on users and groups, but would provide a higher-level API to that information that handles quota math and related decisions.
Users would manage quotas via the Account UI (instead of adding another COmanage plugin).

Services in the Science Platform would ask an Authorizer service to make authorization decisions or get metadata about the user.
This would in turn reference the same backing store as the Token Issuer, as well as the LDAP directory provided by COmanage.
This avoids having to teach other Science Platform services how to speak LDAP (something that we want to avoid).

All user authentications and authorizations to the Science Platform would be logged, and that log information collected and summarized as a data source for the Account UI to show the user authentication history, token usage, etc.

.. _questions:

Questions
=========

Below are the notes from a 2020-08-11 meeting with the CILogon team with answers to some of our initial questions.

1. Did this evaluation include Grouper as the group management system?
2. If not, would Grouper provide better tools for handling quota (as group metadata) and allowing groups to own groups?

In Grouper, it's called the attribute framework; in COmanage, it's extended types.
Either can add metadata to groups.
However, neither offer any sort of logic, so summing quotas would need to be an enhancement.
Grouper would allow groups to own other groups.

COmanage Registry does have a Grouper provisioner, so you can use the organizational groups in COmanage and provision them into Grouper.

No drawback to using Grouper instead of COmanage other than the extra complexity.
Typical pattern is to use COmanage to set up organizational groups, provision them into Grouper, and then use Grouper to do set math and calculate authorization.
Grouper specializes in arbitrary set math.

Provisioning from COmanage to Grouper is unidirectional.
Bidirectional generally isn't necessary; COmanage handles organizational groups, which don't need to take information back from Grouper.

The Grouper UI may not be the best choice for exposing directly to users.
If the groups are organizational, the organization can be represented as a COU (Collaborative Organization Unit).
You can then have a group of administrators per COU, which may be a better way of doing group managing other groups.

Ad hoc groups could be done entirely in COmanage Registry; we may not need to use Grouper.

3. Is there anything more you can tell us about SciTokens and whether it would meet some of the token issuance requirements?
   I believe this is part of the full service CILogon subscription.

Would it make sense for CILogon to operate SciTokens, or for the Science Platform to deploy tokens directly?
Based on the requirements, looked like we wanted a tight coupling between tokens and the Science Platform: user-set expirations, scopes custom to the Science Platform, and so forth.
That argues for keeping the SciTokens issuer directly in the Science Platform.
The use case for the SciTokens issuer in CILogon is different: a loosely-coupled federated model where the tokens are used at multiple institutions.

SciTokens has a fairly low-level API and doesn't have the user interface elements mentioned in the requirements.

The CILogon SciTokens issuer is the Java issuer.
There is a Python library that does have an issuer and a verifier, but it doesn't have the OAuth part.

4. Could some of the work marked as requiring plugin development instead be done via the API?

Yes, some work could be done via API instead.
COmanage has a data model (about 80 objects), and the user interface is just manipulating the data model, as is the plugin.
When deciding between a plugin and an API, it's a question of how you want to manipulate the data model.
If you need a user interface and don't have one available, a plugin may be more effective since it gives you model-view-controller and they're straightforward Cake PHP plugins.
On the other hand, if you already have a UI developer and want to leverage the COmanage data model, could instead use the REST API.

Event-based operations need to be Cake PHP plugins through the event mechanism.
You're registering an event handler with the Cake PHP layer so that when CRUD operations are called, they automatically call the event handler.

Notifications are much more coarse-grained, so you won't see them for things like changing the name of a group.

There are some areas of COmanage that the API doesn't cover.
The usual development model is to add a new data object, add CRUD operations on the object, and then somewhat later write a REST API.
In general, the REST API coverage is fairly good (about 85%), but newer things may not have a REST API.
Because it's an MVC framework, it doesn't inherently rely on a REST API backend, so the addition of a REST API isn't automatic.

5. Can the user see a history of their authentications through CILogon to the Rubin Science Platform via the COmanage UI?

COmanage Registry has a notion of authentication events.
This captures every login to COmanage specifically, not all CILogon events.
There is no state saved for individual client OpenID Connect authentication flows that do not go to COmanage.

CILogon has syslog logging, but there's no API for a CILogon client to get that information.
They would need to do some brainstorming about possible approaches.
There has been some discussion of sending AWS CloudWatch events, or a new syslog aggregator, but it would be new feature development.

6. It looks from the documentation like COmanage supports deactivating an account.
   Does this have the properties that we're looking for in a frozen account?
   Specifically, we want it to stop successful authentication to anything other than the account metadata page (or to no part of the system at all), but preserve all of the data.

The typical pattern looks like this: Assume that the user has been onboarded into COmanage.
The COPerson records are generally provisioned to an external system for consumption.
The one provided out of the box is an LDAP directory.
As part of that provisioning, the user's group memberships are provisioned.
There are a couple of special groups: active users are in an "active" group, and they're also in an "all" group.

Then, you set up OIDC clients, and when someone goes to authenticate, as they flow through the proxy, the group memberships are included in claims.
The OIDC client then do authorization based on those claims.

If a user goes inactive, they can be put into a variety of states, one of which being suspended.
This can be automatic via an expiration date, or can be a security action.
COmanage then rewrites the LDAP record to remove all the group memberships except for "all."
All "active" group membership and ad hoc memberships are revoked.
Only a skeletal group is left in LDAP.
Downstream services then wouldn't see the authorization group they're looking for.

All the group memberships would then come back automatically (provided that they haven't expired).

Suspended users can view their canvas (their user record), but can't make any changes.
You can enable special enrollment flows that would allow them to renew their membership, and suspended users would then be able to get access to those.
They can select new enrollment flows from a menu.

The CILogon folks will set up a test organization for us to experiment with.
The recommendation is to add a second call for that purpose to walk us through the things the tool can do.

7. How much of the current identity.lsst.org service is using COmanage?

NCSA Savannah stuff is totally separate and unrelated to COmanage.
