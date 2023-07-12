
# Make posts from `jupyter notebooks`

Usage:

1) Copy a notebook to this directory, or copy from the `test-post.ipynb` template.

2) Edit the header in the first source block of the notebook to include *categories* and *tags*, that will then be selectable in the post summary page.  Edit the `TITLE` block as desired, but leave `TIMESTAMP` as-is for the script to populate.

```
---
layout: post
title:  {TITLE}
date:   {TIMESTAMP}
categories: Research
tags: HST
---
{% include tags.html %}
```

3) Run the command below, where the last item is a list of jekyll properties
   to aattach to the post.
   
   ```bash
   ./update_post.sh this-is-a-new-post.ipynb
   ```

4) Commit the `md` version of the notebook and any image assets created to the repo
