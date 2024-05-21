mkdir -p _generated
cat header.html index.html footer.html > _generated/index.html || exit 1
cat header.html about.html footer.html > _generated/about.html || exit 1

