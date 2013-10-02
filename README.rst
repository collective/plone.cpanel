Introduction
============

This package will override the frontpage of a zope instance with a
panel that allows anyone create a plone site. This turns Plone into
an out of the box CMS-as-a-service platform.

User interface
==============

Welcome to Plone Cloud. This cluster currently holds 5 sites.

Name*       [                   ]

Email*      [                   ]

Site Title  [                   ]

Sub Domain  [         ].mycloud.com

Site Theme  [ Blog      |v|]

[Create]

Forgot your site or password? Enter your email below and we will mail you a link
[                    ] [Password reset]


Details
=======

1. Sites are created using random id's. The location selection method can be overridden to support site creation
in different database mount points. This can also allow pre-created sites.
2. On site creation a Administrator user is added to the site and a password reset email sent out.
3. Virtual host domains are created inside the VHM to allow easy access to the site if a central domain name
   has been configured.
4. Generic Setup profiles can be registered as Site Templates, allowing for preconfigured themes, content etc.

Management
==========

Plone is well suited to a multi-site, shared service CMS platform. The Zope inferstructure allows replication
of data to across multiple servers. Site code can be replicated in the same making plone not just a shared
hosting solution, where a single machine is dividied, a plone site can be easily be served from multiple machines.
Scaling is as simple as installing another Zope instance and including this in your load balancer.

If customisations for each plone site is limited to online changes, memory will be automatically be managed
by zope for you. The ZODB cache will keep just the often used sites in memory.
Security is ensured by the Zopes sandboxed python code.




