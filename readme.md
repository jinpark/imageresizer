# jinageresizer (Jin's image resizer)  [![Deploy](https://www.herokucdn.com/deploy/button.png)](https://heroku.com/deploy)
----
[![Build Status](https://travis-ci.org/jinpark/imageresizer.svg?branch=master)](https://travis-ci.org/jinpark/imageresizer)
[![Coverage Status](https://coveralls.io/repos/jinpark/imageresizer/badge.svg?branch=master)](https://coveralls.io/r/jinpark/imageresizer?branch=master)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jinpark/imageresizer?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


jinageresizer is a image resizing service using flask, imagemagick and [wand](http://docs.wand-py.org/en/0.4.0/) inspired by [firesize](http://firesize.com)


Current url Scheme
------------------
`base_url/image_url/?rwidth=resize_width_in_px&rheight=resize_height&type=jpg|png`
Example:
`https://images.jinpark.net/http://i.imgur.com/AMTTUDK.jpg/?rwidth=300&type=png`

Only the image_url is required. The query params are all optional.

If width and height are given, aspect ratio is not preserved. If only width or height is given, aspect ratio is preserved and the non specified variable is modified to fit the aspect ratio.

I highly suggest putting this behind a cdn to allow for edge caching so the server is not reprocessing the same image again and again. If you are using cloudflare, as I am, you might need to force cloudflare to cache everything using page rules, since the resulting url is usually not one of the automatic cached extensions.

TO DO
-----

  * Add cropping (with gravity)
