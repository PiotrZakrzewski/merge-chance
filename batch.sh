
cat $1 | tr '\n' '\0' | xargs -0 -n1 python get_pr_gql.py
mkdir -p "$1_results"
mv *csv "$1_results"/
for f in $(ls "$1_results")
do
  python score.py "$1_results/$f"
done
mv *png "$1_results"
