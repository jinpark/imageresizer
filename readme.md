# jinageresizer (image resizer by jin)

jinageresizer is a image resizing service using flask and imagemagick inspired by [firesize](firesize.com)


Current url Scheme
------------------
`base_url/image_url/?rwidth=resize_width_in_px&rheight=resize_height&type=jpg|png`

Only the image_url is required. The query params are all optional.

If width and height are given, aspect ratio is not preserved. If only width or height is given, aspect ratio is preserved and the non specified variable is modified to fit the aspect ratio.

TO DO
-----

  * Add cropping (with gravity)
  * Move to asyncio or gevent
  * Add `deploy to heroku` button
