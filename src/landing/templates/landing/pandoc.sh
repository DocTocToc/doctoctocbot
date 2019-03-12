dir=(about guidelines privacy rules values)
for i in ${dir[@]}; do
    echo ${i}
    cd ${i} && pandoc -f markdown -t html5 -o content.html content.md && cd ..
done
exit 0

