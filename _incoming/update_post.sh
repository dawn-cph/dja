#!/bin/bash

# Use this in the first raw line of a notebook

HEADER="""
---
#layout: post
#title:  {TITLE}
#date:   {TIMESTAMP}
#categories: research alma charge
---
"""

usage="""
Usage:

1) Copy a notebook to this directory.

3) Run the command below, where the last item is a list of jekyll properties
   to aattach to the post.
   
   ./update_post.sh this-is-a-new-post.ipynb \"research alma charge\"
   
"""

nbfile=$1

date_timestamp=`date -r ${nbfile} +'%Y-%m-%d'`
full_timestamp=`date -r ${nbfile} +'%Y-%m-%d %H:%M:%S %z'`

echo $nbfile
#echo $date_timestamp
#echo $full_timestamp

#echo "print('${nbfile}'.strip('.ipynb').replace('-',' ').title())" > /tmp/title.py
#title=`python /tmp/title.py`
#echo $title

#echo $categories
rm -rf ./tmp
jupyter nbconvert --to markdown ${nbfile} --output-dir ./tmp

root=`echo $nbfile | sed "s/.ipynb//"`

rm -rf ../assets/post_files/${date_timestamp}-${root}_files
mv ./tmp/${root}_files ../assets/post_files/${date_timestamp}-${root}_files
outfile="${date_timestamp}-${root}.md"
 
cp tmp/${root}.md ./${outfile}

# Auto title: first # line
title_line=`grep \# tmp/${root}.md | head -1`
title=`echo $title_line | sed "s/\#//g"`
perl -pi -e "s/${title_line}/(This page is auto-generated from the Jupyter notebook \[${root}.ipynb\](\/assets\/post_files\/${date_timestamp}-${root}.ipynb).)/" ./${outfile}
perl -pi -e "s/{TITLE}/${title}/" ${outfile}

# head -n 9 tmp/${root}.md | tail -8 > ${outfile}
# echo "" >> ${outfile} 
# echo "(This page is auto-generated from the Jupyter notebook [${root}.ipynb](/assets/post_files/${root}.ipynb).)" >> ${outfile} 
# echo "" >> ${outfile} 
# echo "======" >> ${outfile} 
# echo "" >> ${outfile} 
# tail -n +12 tmp/${root}.md >> ${outfile}

# Auto timestamp
perl -pi -e "s/{TIMESTAMP}/${full_timestamp}/" ${outfile}

cp ${root}.ipynb ../assets/post_files/${date_timestamp}-${root}.ipynb


perl -pi -e "s/${root}_files/\/assets\/post_files\/${date_timestamp}-${root}_files/" $outfile

echo "=== Post added ==="
echo "../_posts/${outfile}"
echo "../assets/post_files/${date_timestamp}-${root}_files/"
echo "../assets/post_files/${date_timestamp}-${root}.ipynb"

mv ${outfile} ../_posts
rm -rf ./tmp
