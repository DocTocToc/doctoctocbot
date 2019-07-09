dir=(about guidelines moderation moderator privacy rules values spamtoctoc)
for i in ${dir[@]}; do
    echo ${i}
    cd ${i} && pandoc -f markdown -t html5 -o content.html content.md && cd ..
done
exit 0

