About
=====

This is a bot to help with maintenance for the Astropy project.

There are two versions deployed on Heroku:

* ``astrobot-production``, which is deployed from the ``production`` branch in
  this repository. As its name indicates, this is the version that should be
  used by most repositories. To use this version, add a webhook with the
  following details on GitHub:

  * Payload URL: https://astrobot-production.herokuapp.com/hook
  * Content type: ``application/json``
  * Secret: leave blank
  * Events: choose **Let me select individual events**, then make sure **Pull
    request** is selected (and nothing else).

* ``astrobot-experimental``, which is deployed from the ``master`` branch in
  this repository. This runs on test/low impact repositories. This version is
  truly experimental and can break at any time. To use this version, add a
  webhook with the following details on GitHub:

  * Payload URL: https://astrobot-experimental.herokuapp.com/hook
  * Content type: ``application/json``
  * Secret: leave blank
  * Events: choose **Let me select individual events**, then make sure **Pull
    request** is selected (and nothing else).

We use the Heroku automatic deployment functionality, so when changes are pushed
to the branches here, the deployment is done automatically.
