dir=(about guidelines moderation moderator privacy rules values spamtoctoc)
community=(doctoctoc pharmatoctoc content)
for i in ${dir[@]}; do
    echo ${i}
    cd ${i}
    for j in ${community[@]}; do
        pandoc -f markdown -t html5 -o ${j}.html ${j}.md
    done
    cd ..
done
exit 0

