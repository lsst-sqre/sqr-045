:tocdepth: 1

.. sectnum::

Abstract
========

The Rubin Science Platform will require an identity management system.
One attractive option is to build it on top of CILogon's managed COmanage service, which is designed for scientific collaborations.
This document compares COmanage's functionality with the Rubin Science Platform requirements documented in `SQR-044`_.

.. _SQR-044: https://sqr-044.lsst.io/

This analysis is based primarily on the CILogon response to the Rubin Science Platform requirements document.

Methodology
===========

The CILogon team sorted the requirements in `SQR-044`_ into requirements that COmanage plus CILogon already meet, requirements that can be met with a plugin (along with a development estimate), and requirements that are out of scope for COmanage.
I then collected that point-by-point response into this summary.
Follow-up questions are currently included here.
This document will be revised based on the answers to those questions after a subsequent technical meeting.

Gaps
====

Out of scope
------------

#. Forcing multifactor for administrators.
   Google and GitHub do not expose this information in their OAuth metadata.
   The easiest approach would probably be to use a separate authentication path for administrators that forces use of a specific Google Cloud Identity domain with appropriate multifactor authentication requirements.
   (IDM-0007)
#. Token issuance in general, including all logging and notification requirements.
   Integration could be done with a COmanage provisioning plugin.
   (IDM-01* and related issues)
#. Showing a history of web authentications for a user (but see :ref:`questions`).
   (IDM-0203)
#. Freezing an account (but see :ref:`questions`).
   (IDM-1000)
#. A group owning another group.
   (IDM-2009)

Plugin development required
---------------------------

COmanage plugins are Cake plugins written in PHP.
All estimates are in FTE-weeks for an experienced PHP developer.

#. Automated approval based on affiliation from federated identity metadata.
   (IDM-0002, 1 week)
#. Revoking organizational identities and sending email notification when this happens.
   (IDM-0005, 1 week for unlinking plus 2 weeks for email notification)
#. Periodicaly rechecking affiliation if we make access decisions based on organizational affiliation.
   (IDM-0009, 1 week)
#. Deduplication of enrollments based on email address.
   COmanage does support a lot of what we want and may be sufficient without further enhancement.
   (IDM-0013, 1 week, possibly not needed)
#. Displaying last use of a federated identity.
   (IDM-0204, enhancement request that may not require Rubin work)
#. Notifying the user when a new email address is added.
   (IDM-1101, 2 weeks)
#. Showing that an email address is unverified in LDAP.
   (IDM-1101, 2 days)
#. Quota support.
   (IDM-12*, 4 weeks)
#. Automatic group management based on identity metadata.
   (IDM-2001, 4 weeks)
#. Namespace enforcement for groups.
   (IDM-2004, 2 days)
#. Ability for for the user to view their group expirations.
   (IDM-2008, 1 week)
#. There may be some actions missing from the administrative API that would require an RFE.
   (IDM-3001)

Total estimate for all work is 18 weeks.

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

.. _questions:

Questions
=========

#. Did this evaluation include Grouper as the group management system?
#. If not, would Grouper provide better tools for handling quota (as group metadata) and allowing groups to own groups?
#. Is there anything more you can tell us about SciTokens and whether it would meet some of the token issuance requirements?
   I believe this is part of the full service CILogon subscription.
#. Could some of the work marked as requiring plugin development instead be done via the API?
#. Can the user see a history of their authentications through CILogon to the Rubin Science Platform via the COmanage UI?
#. It looks from the documentation like COmanage supports deactivating an account.
   Does this have the properties that we're looking for in a frozen account?
   Specifically, we want it to stop successful authentication to anything other than the account metadata page (or to no part of the system at all), but preserve all of the data.
