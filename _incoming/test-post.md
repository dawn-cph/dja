---
layout: post
title:  Test post
date:   {TIMESTAMP}
categories: news
tags: features
author: Gabriel Brammer
showOnHighlights: false
---
{% include components/tags.html %}

To make a new post: 

1. Copy this template to a new markdown file, e.g., `my-post-title.md`.  The filename gets rendered as the post URL permalink, so make it unique and somewhat informative as to what the post is about.
1. Edit the `title`, `categories`, `tags`, and `author` labels in the header above, which is visible in the raw file but doesn't render on the website
1. Set `showOnHighlights: true` in the header to have the post show up among the *Featured* list
1. Clear out these instructions and write the post as desired with markdown formatting
    a. References to images or other pages also in the repository should have the `site.baseurl` prefix, e.g., <img src="{{site.baseurl}}/images/dja_logo_small.png" height=20pix/>.
1. Run `$ ./update_markdown_post my-post-title.md`, which generates a timestamp and copies the file to `../_posts`.
1. Commit the `../_posts/YYYY-MM-DD-my-post-title.md` to the repo and push it 