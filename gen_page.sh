mkdir -p _generated
cat header.html index1.html <(python gen_example_gallery.py || exit 1) index2.html footer.html > _generated/index.html || exit 1
cat header.html about.html <(python gen_pubs.py || exit 1) footer.html > _generated/about.html || exit 1
cat header.html installation.html footer.html > _generated/installation.html || exit 1

